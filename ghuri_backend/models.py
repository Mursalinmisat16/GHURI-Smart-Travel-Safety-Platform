from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from database import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # TRAVELER | OWNER | ADMIN
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Device(Base):
    __tablename__ = "devices"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, unique=True, index=True, nullable=False)
    device_key = Column(String, nullable=False)
    traveler_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    last_lat = Column(Float, nullable=True)
    last_lng = Column(Float, nullable=True)
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class SosAlert(Base):
    __tablename__ = "sos_alerts"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    traveler_id = Column(Integer, nullable=True)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    status = Column(String, default="OPEN")  # OPEN | ACK | CLOSED
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class DeviceLocation(Base):
    __tablename__ = "device_locations"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True, nullable=False)
    lat = Column(Float, nullable=False)
    lng = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Listing(Base):
    __tablename__ = "listings"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False)               # e.g. Sea View Resort
    type = Column(String, nullable=False)                # HOTEL / RESORT / HOME
    district = Column(String, nullable=False)            # Cox’s Bazar, Sylhet
    address = Column(String, nullable=True)
    price_per_night = Column(Integer, nullable=False)    # in BDT
    description = Column(Text, nullable=True)

    status = Column(String, nullable=False, default="PENDING")  # PENDING/APPROVED/REJECTED
    created_at = Column(DateTime(timezone=True), server_default=func.now())
