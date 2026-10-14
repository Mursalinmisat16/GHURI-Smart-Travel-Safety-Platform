from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine
from deps import get_db, require_role

from models import User, Device, SosAlert, DeviceLocation, Listing
from schemas import (
    RegisterRequest, LoginRequest, TokenResponse,
    LocationIn, SosIn, DeviceCreate,
    ListingCreate, ListingStatusUpdate
)

from auth import (
    hash_password, verify_password, create_access_token, decode_access_token
)

app = FastAPI(title="Ghuri Backend API")

# CORS (allow frontend on web)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# ---------- AUTH ----------
@app.post("/auth/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    if data.role not in ["TRAVELER", "OWNER", "ADMIN"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    exists = db.query(User).filter(User.phone == data.phone).first()
    if exists:
        raise HTTPException(status_code=400, detail="Phone already registered")

    user = User(
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "name": user.name, "phone": user.phone, "role": user.role}


@app.post("/auth/login", response_model=TokenResponse)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"user_id": user.id, "role": user.role})
    return TokenResponse(access_token=token, role=user.role)


# ---------- TOKEN HELPER ----------
def get_current_user_payload(authorization: str) -> dict:
    """
    authorization: "Bearer <token>"
    returns payload => {"user_id": 1, "role": "OWNER", "exp": ...}
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.replace("Bearer ", "").strip()
    return decode_access_token(token)


# ---------- ESP32 DEVICE AUTH HELPER ----------
def verify_device(db: Session, device_id: str, device_key: str) -> Device:
    dev = db.query(Device).filter(Device.device_id == device_id).first()
    if not dev or dev.device_key != device_key:
        raise HTTPException(status_code=401, detail="Invalid device credentials")
    return dev


# ---------- ADMIN: REGISTER ESP32 DEVICE ----------
@app.post("/admin/devices", dependencies=[Depends(require_role("ADMIN"))])
def create_device(data: DeviceCreate, db: Session = Depends(get_db)):
    if db.query(Device).filter(Device.device_id == data.device_id).first():
        raise HTTPException(status_code=400, detail="Device already exists")

    dev = Device(
        device_id=data.device_id,
        device_key=data.device_key,
        traveler_id=data.traveler_id
    )
    db.add(dev)
    db.commit()
    return {"message": "device created"}


# ---------- ESP32: LIVE LOCATION (latest + keep last 10 history) ----------
@app.post("/devices/{device_id}/location")
def device_location(
    device_id: str,
    data: LocationIn,
    x_device_key: str = Header(default=""),
    db: Session = Depends(get_db),
):
    dev = verify_device(db, device_id, x_device_key)

    # 1) update latest fields in devices table
    dev.last_lat = data.lat
    dev.last_lng = data.lng
    db.add(dev)

    # 2) insert into history table
    db.add(DeviceLocation(device_id=device_id, lat=data.lat, lng=data.lng))
    db.commit()

    # 3) keep only latest 10 rows for this device in device_locations
    ids_to_keep = (
        db.query(DeviceLocation.id)
        .filter(DeviceLocation.device_id == device_id)
        .order_by(DeviceLocation.id.desc())
        .limit(10)
        .all()
    )
    keep_ids = [x[0] for x in ids_to_keep]

    if keep_ids:
        db.query(DeviceLocation) \
            .filter(DeviceLocation.device_id == device_id) \
            .filter(~DeviceLocation.id.in_(keep_ids)) \
            .delete(synchronize_session=False)
        db.commit()

    return {"ok": True}


# ---------- ESP32: SOS ----------
@app.post("/devices/{device_id}/sos")
def device_sos(
    device_id: str,
    data: SosIn,
    x_device_key: str = Header(default=""),
    db: Session = Depends(get_db),
):
    dev = verify_device(db, device_id, x_device_key)

    alert = SosAlert(
        device_id=device_id,
        traveler_id=dev.traveler_id,
        lat=data.lat,
        lng=data.lng,
        status="OPEN"
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return {"ok": True, "alert_id": alert.id}


# ---------- ADMIN: VIEW SOS ALERTS ----------
@app.get("/admin/alerts", dependencies=[Depends(require_role("ADMIN"))])
def get_alerts(db: Session = Depends(get_db), status: str = "OPEN"):
    q = db.query(SosAlert).order_by(SosAlert.id.desc())
    if status:
        q = q.filter(SosAlert.status == status)

    alerts = q.limit(50).all()
    return [
        {
            "id": a.id,
            "device_id": a.device_id,
            "traveler_id": a.traveler_id,
            "lat": a.lat,
            "lng": a.lng,
            "status": a.status,
            "created_at": str(a.created_at),
        }
        for a in alerts
    ]


# ---------- ADMIN: LIVE LOCATIONS (latest) ----------
@app.get("/admin/live-locations", dependencies=[Depends(require_role("ADMIN"))])
def live_locations(db: Session = Depends(get_db)):
    devices = db.query(Device).all()
    return [
        {
            "device_id": d.device_id,
            "traveler_id": d.traveler_id,
            "lat": d.last_lat,
            "lng": d.last_lng,
            "last_seen": str(d.last_seen),
        }
        for d in devices
    ]


# ---------- ADMIN: LAST 10 LOCATIONS (history) ----------
@app.get("/admin/devices/{device_id}/last-10", dependencies=[Depends(require_role("ADMIN"))])
def last_10_locations(device_id: str, db: Session = Depends(get_db)):
    rows = (
        db.query(DeviceLocation)
        .filter(DeviceLocation.device_id == device_id)
        .order_by(DeviceLocation.id.desc())
        .limit(10)
        .all()
    )
    return [
        {"id": r.id, "lat": r.lat, "lng": r.lng, "created_at": str(r.created_at)}
        for r in rows
    ]


# ==========================================================
# ===================== LISTINGS FEATURE =====================
# ==========================================================

# ---------- OWNER: CREATE LISTING ----------
@app.post("/owner/listings", dependencies=[Depends(require_role("OWNER"))])
def owner_create_listing(
    data: ListingCreate,
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
):
    payload = get_current_user_payload(authorization)
    owner_id = payload["user_id"]

    listing = Listing(
        owner_id=owner_id,
        title=data.title,
        type=data.type,
        district=data.district,
        address=data.address,
        price_per_night=data.price_per_night,
        description=data.description,
        status="PENDING",
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return {"message": "listing created", "id": listing.id}


# ---------- OWNER: VIEW MY LISTINGS ----------
@app.get("/owner/listings", dependencies=[Depends(require_role("OWNER"))])
def owner_my_listings(
    authorization: str = Header(default=""),
    db: Session = Depends(get_db),
):
    payload = get_current_user_payload(authorization)
    owner_id = payload["user_id"]

    rows = (
        db.query(Listing)
        .filter(Listing.owner_id == owner_id)
        .order_by(Listing.id.desc())
        .all()
    )
    return rows


# ---------- TRAVELER: VIEW APPROVED LISTINGS ----------
@app.get("/traveler/listings")
def traveler_listings(db: Session = Depends(get_db)):
    rows = (
        db.query(Listing)
        .filter(Listing.status == "APPROVED")
        .order_by(Listing.id.desc())
        .all()
    )
    return rows


# ---------- ADMIN: VIEW LISTINGS ----------
@app.get("/admin/listings", dependencies=[Depends(require_role("ADMIN"))])
def admin_listings(db: Session = Depends(get_db), status: str = "PENDING"):
    q = db.query(Listing).order_by(Listing.id.desc())
    if status and status != "ALL":
        q = q.filter(Listing.status == status)
    return q.limit(200).all()


# ---------- ADMIN: APPROVE / REJECT ----------
@app.patch("/admin/listings/{listing_id}", dependencies=[Depends(require_role("ADMIN"))])
def admin_update_listing_status(
    listing_id: int,
    data: ListingStatusUpdate,
    db: Session = Depends(get_db),
):
    if data.status not in ["APPROVED", "REJECTED", "PENDING"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    row = db.query(Listing).filter(Listing.id == listing_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")

    row.status = data.status
    db.commit()
    return {"message": "updated", "status": row.status}
