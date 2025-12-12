from fastapi import APIRouter, HTTPException, Depends, Header
from app.models import OrgCreateRequest, OrgGetRequest, OrgUpdateRequest, OrgMeta
from app.services.org_service import OrganizationService
from typing import Optional

router = APIRouter(prefix="/org", tags=["org"])
service = OrganizationService()

@router.post('/create', response_model=OrgMeta)
async def create_org(payload: OrgCreateRequest):
    try:
        res = await service.create_org(payload.organization_name, payload.email, payload.password)
        return OrgMeta(**res)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get('/get')
async def get_org(organization_name: str):
    org = await service.get_org(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail='Organization not found')
    return org

@router.put("/update")
async def update_org(payload: OrgUpdateRequest):
    try:
        res = await service.update_org(
            old_name=payload.organization_name,
            new_name=payload.new_organization_name,
            email=payload.email,
            password=payload.password
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete('/delete')
async def delete_org(organization_name: str, x_admin_email: Optional[str] = Header(None)):
    # we expect the caller to provide admin email in header or Authorization in real setup
    if not x_admin_email:
        raise HTTPException(status_code=401, detail='Missing admin email header')
    try:
        await service.delete_org(organization_name, x_admin_email)
        return {"detail": "deleted"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))