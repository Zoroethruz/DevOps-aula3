from sqlalchemy.orm import Session
from sqlalchemy import and_
from app import models, schemas


def create_room(db: Session, room: schemas.RoomCreate) -> models.Room:
    db_room = models.Room(**room.model_dump())
    db.add(db_room)
    db.commit()
    db.refresh(db_room)
    return db_room


def list_rooms(db: Session, only_active: bool = True):
    query = db.query(models.Room)
    if only_active:
        query = query.filter(models.Room.is_active == True)  # noqa: E712
    return query.all()


def search_rooms(
    db: Session,
    q: str | None = None,
    room_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_capacity: int | None = None,
    only_active: bool = True,
):
    """Busca quartos com filtros combináveis (todos opcionais)."""
    query = db.query(models.Room)
    if only_active:
        query = query.filter(models.Room.is_active == True)  # noqa: E712
    if q:
        like = f"%{q}%"
        query = query.filter(
            (models.Room.number.ilike(like)) | (models.Room.room_type.ilike(like))
        )
    if room_type:
        query = query.filter(models.Room.room_type == room_type)
    if min_price is not None:
        query = query.filter(models.Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(models.Room.price_per_night <= max_price)
    if min_capacity is not None:
        query = query.filter(models.Room.capacity >= min_capacity)
    return query.all()


def get_room(db: Session, room_id: int):
    return db.query(models.Room).filter(models.Room.id == room_id).first()


def update_room(db: Session, room_id: int, room_update: schemas.RoomUpdate):
    db_room = get_room(db, room_id)
    if not db_room:
        return None
    data = room_update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_room, field, value)
    db.commit()
    db.refresh(db_room)
    return db_room


def delete_room(db: Session, room_id: int):
    """Remove o quarto. Se já tiver reservas associadas, desativa (soft delete)
    em vez de apagar, para preservar o histórico de reservas."""
    db_room = get_room(db, room_id)
    if not db_room:
        return None
    has_reservations = (
        db.query(models.Reservation).filter(models.Reservation.room_id == room_id).first()
        is not None
    )
    if has_reservations:
        db_room.is_active = False
        db.commit()
        db.refresh(db_room)
        return {"mode": "deactivated", "room": db_room}
    room_snapshot = schemas.RoomOut.model_validate(db_room)
    db.delete(db_room)
    db.commit()
    return {"mode": "deleted", "room": room_snapshot}


def is_room_available(db: Session, room_id: int, check_in, check_out, ignore_reservation_id=None) -> bool:
    """Um quarto está indisponível se houver reserva confirmada com sobreposição de datas."""
    query = db.query(models.Reservation).filter(
        models.Reservation.room_id == room_id,
        models.Reservation.status == "confirmed",
        and_(
            models.Reservation.check_in < check_out,
            models.Reservation.check_out > check_in,
        ),
    )
    if ignore_reservation_id:
        query = query.filter(models.Reservation.id != ignore_reservation_id)
    return query.first() is None


def create_reservation(db: Session, reservation: schemas.ReservationCreate) -> models.Reservation:
    db_reservation = models.Reservation(**reservation.model_dump())
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation


def list_reservations(db: Session):
    return db.query(models.Reservation).all()


def get_reservation(db: Session, reservation_id: int):
    return db.query(models.Reservation).filter(models.Reservation.id == reservation_id).first()


def cancel_reservation(db: Session, reservation_id: int):
    reservation = get_reservation(db, reservation_id)
    if reservation:
        reservation.status = "cancelled"
        db.commit()
        db.refresh(reservation)
    return reservation


def update_reservation(db: Session, reservation_id: int, reservation_update: schemas.ReservationUpdate):
    db_reservation = get_reservation(db, reservation_id)
    if not db_reservation:
        return None
    data = reservation_update.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(db_reservation, field, value)
    db.commit()
    db.refresh(db_reservation)
    return db_reservation
