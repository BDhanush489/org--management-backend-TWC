from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class OrgCreateRequest(BaseModel):
    organization_name: str = Field(..., min_length=3)
    email: EmailStr
    password: str = Field(..., min_length=6)


class OrgMeta(BaseModel):
    organization_name: str
    collection_name: str
    admin_email: EmailStr


class OrgGetRequest(BaseModel):
    organization_name: str

class OrgUpdateRequest(BaseModel):
    organization_name: str
    new_organization_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"