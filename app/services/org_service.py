from app.db import master_db
from app.auth import AuthService
from typing import Optional


class OrganizationService:
    def __init__(self):
        self.orgs = master_db['organizations']
        self.admins = master_db['admins']

    # -------------------------
    # CREATE ORGANIZATION
    # -------------------------
    async def create_org(self, organization_name: str, email: str, password: str) -> dict:
        existing = await self.orgs.find_one({"organization_name": organization_name})
        if existing:
            raise ValueError("Organization already exists")

        collection_name = f"org_{organization_name}"
        coll = master_db[collection_name]

        # Atlas-safe collection creation
        await coll.insert_one({"_init": True})
        await coll.delete_one({"_init": True})

        hashed = AuthService.hash_password(password)
        admin_doc = {"email": email, "password": hashed,
                     "organization_name": organization_name}
        res = await self.admins.insert_one(admin_doc)

        org_doc = {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin_ref_id": res.inserted_id
        }

        await self.orgs.insert_one(org_doc)

        return {
            "organization_name": organization_name,
            "collection_name": collection_name,
            "admin_email": email
        }

    # -------------------------
    # GET ORGANIZATION
    # -------------------------
    async def get_org(self, organization_name: str):
        return await self.orgs.find_one(
            {"organization_name": organization_name},
            {"_id": 0, "admin_ref_id": 0})

    # -------------------------
    # UPDATE (RENAME) ORGANIZATION
    # -------------------------

    async def update_org(self, old_name: str, new_name: Optional[str] = None,
                         email: Optional[str] = None, password: Optional[str] = None):

        org = await self.orgs.find_one({"organization_name": old_name})
        if not org:
            raise ValueError("Organization not found")

        # If renaming org
        if new_name and new_name != old_name:
            existing = await self.orgs.find_one({"organization_name": new_name})
            if existing:
                raise ValueError("New organization name already exists")

            old_coll = org['collection_name']
            new_coll = f"org_{new_name}"

            new_collection = master_db[new_coll]

            # Atlas-safe create collection
            await new_collection.insert_one({"_init": True})
            await new_collection.delete_one({"_init": True})

            # Copy old documents into new
            cursor = master_db[old_coll].find({})
            async for doc in cursor:
                await new_collection.insert_one(doc)

            # Drop old collection
            await master_db[old_coll].drop()

            # Update metadata
            org['collection_name'] = new_coll
            org['organization_name'] = new_name

        # Update admin fields
        update_admin = {}
        if email:
            update_admin["email"] = email
        if password:
            update_admin["password"] = AuthService.hash_password(password)

        if update_admin:
            await self.admins.update_one(
                {"organization_name": org["organization_name"]},
                {"$set": update_admin}
            )

        # Update master DB org record
        await self.orgs.update_one(
            {"_id": org["_id"]},
            {"$set": {
                "organization_name": org["organization_name"],
                "collection_name": org["collection_name"]
            }}
        )

        return {
            "organization_name": org["organization_name"],
            "collection_name": org["collection_name"]
        }

    # -------------------------
    # DELETE ORGANIZATION
    # -------------------------
    async def delete_org(self, organization_name: str, requesting_admin_email: str):
        admin = await self.admins.find_one({
            "email": requesting_admin_email,
            "organization_name": organization_name
        })

        if not admin:
            raise PermissionError("Not authorized to delete this organization")

        org = await self.orgs.find_one({"organization_name": organization_name})
        if not org:
            raise ValueError("Organization not found")

        coll_name = org['collection_name']

        # Atlas-safe drop
        await master_db[coll_name].drop()

        # Remove all admins of this org
        await self.admins.delete_many({"organization_name": organization_name})

        # Remove org metadata
        await self.orgs.delete_one({"organization_name": organization_name})

        return True
