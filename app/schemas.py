from datetime import date
from pydantic import BaseModel, EmailStr, field_validator


class RoomBase(BaseModel):
    number: str
    room_type: str
    price_per_night: float
    capacity: int = 2


class RoomCreate(RoomBase):
    pass


class RoomUpdate(BaseModel):
    number: str | None = None
    room_type: str | None = None
    price_per_night: float | None = None
    capacity: int | None = None
    is_active: bool | None = None


class RoomOut(RoomBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class ReservationBase(BaseModel):
    room_id: int
    guest_name: str
    guest_email: EmailStr
    check_in: date
    check_out: date

    @field_validator("check_out")
    @classmethod
    def check_out_after_check_in(cls, v, info):
        check_in = info.data.get("check_in")
        if check_in and v <= check_in:
            raise ValueError("check_out deve ser posterior a check_in")
        return v


class ReservationCreate(ReservationBase):
    pass


class ReservationUpdate(BaseModel):
    guest_name: str | None = None
    guest_email: EmailStr | None = None
    check_in: date | None = None
    check_out: date | None = None

    @field_validator("check_out")
    @classmethod
    def check_out_after_check_in(cls, v, info):
        check_in = info.data.get("check_in")
        if check_in and v and v <= check_in:
            raise ValueError("check_out deve ser posterior a check_in")
        return v


class ReservationOut(ReservationBase):
    id: int
    status: str

    class Config:
        from_attributes = True
