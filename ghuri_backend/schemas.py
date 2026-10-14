from pydantic import BaseModel
from typing import Optional

class RegisterRequest(BaseModel):
    name: str
    phone: str
    password: str
    role: str  # TRAVELER | OWNER | ADMIN

class LoginRequest(BaseModel):
    phone: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str

class LocationIn(BaseModel):
    lat: float
    lng: float
    timestamp: int | None = None

class SosIn(BaseModel):
    lat: float
    lng: float
    timestamp: int | None = None

class DeviceCreate(BaseModel):
    device_id: str
    device_key: str
    traveler_id: int | None = None



class ListingCreate(BaseModel):
    title: str
    type: str            # HOTEL/RESORT/HOME
    district: str
    address: Optional[str] = None
    price_per_night: int
    description: Optional[str] = None

class ListingOut(BaseModel):
    id: int
    owner_id: int
    title: str
    type: str
    district: str
    address: Optional[str] = None
    price_per_night: int
    description: Optional[str] = None
    status: str

    class Config:
        from_attributes = True

class ListingStatusUpdate(BaseModel):
    status: str  # APPROVED / REJECTED
