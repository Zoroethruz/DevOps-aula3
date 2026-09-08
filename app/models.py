from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base


class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, unique=True, index=True, nullable=False)
    room_type = Column(String, nullable=False)  # standard, deluxe, suite
    price_per_night = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False, default=2)
    is_active = Column(Boolean, default=True)

    reservations = relationship("Reservation", back_populates="room")


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    guest_name = Column(String, nullable=False)
    guest_email = Column(String, nullable=False)
    check_in = Column(Date, nullable=False)
    check_out = Column(Date, nullable=False)
    status = Column(String, default="confirmed")  # confirmed, cancelled

    room = relationship("Room", back_populates="reservations")
