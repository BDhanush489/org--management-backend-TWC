from fastapi import APIRouter, HTTPException
from app.models import AdminLoginRequest, TokenResponse
from app.db import master_db
from app.auth import AuthService

router = APIRouter(prefix='/admin', tags=['admin'])

@router.post('/login', response_model=TokenResponse)
async def admin_login(payload: AdminLoginRequest):
    admins = master_db['admins']
    admin = await admins.find_one({"email": payload.email})
    if not admin:
        raise HTTPException(status_code=401, detail='Invalid credentials')
    if not AuthService.verify_password(payload.password, admin['password']):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    token = AuthService.create_access_token({"sub": str(admin['_id']), "email": admin['email'], "organization_name": admin['organization_name']})
    return {"access_token": token}