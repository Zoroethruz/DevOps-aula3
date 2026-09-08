from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app import models, schemas, crud
from app.database import engine, get_db, Base

# Cria as tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Hotel Booking API",
    description="API REST para reserva de quartos de hotel",
    version="1.0.0",
)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}


# Quartos  

@app.post("/rooms", response_model=schemas.RoomOut, status_code=201, tags=["rooms"])
def create_room(room: schemas.RoomCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Room).filter(models.Room.number == room.number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Já existe um quarto com esse número")
    return crud.create_room(db, room)


@app.get("/rooms", response_model=list[schemas.RoomOut], tags=["rooms"])
def get_rooms(
    q: str | None = None,
    room_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_capacity: int | None = None,
    only_active: bool = True,
    db: Session = Depends(get_db),
):
    return crud.search_rooms(
        db,
        q=q,
        room_type=room_type,
        min_price=min_price,
        max_price=max_price,
        min_capacity=min_capacity,
        only_active=only_active,
    )


@app.get("/rooms/{room_id}", response_model=schemas.RoomOut, tags=["rooms"])
def get_room(room_id: int, db: Session = Depends(get_db)):
    room = crud.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    return room


@app.put("/rooms/{room_id}", response_model=schemas.RoomOut, tags=["rooms"])
def update_room(room_id: int, room_update: schemas.RoomUpdate, db: Session = Depends(get_db)):
    existing = crud.get_room(db, room_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")

    new_number = room_update.number
    if new_number and new_number != existing.number:
        conflict = db.query(models.Room).filter(models.Room.number == new_number).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Já existe um quarto com esse número")

    return crud.update_room(db, room_id, room_update)


@app.delete("/rooms/{room_id}", tags=["rooms"])
def delete_room(room_id: int, db: Session = Depends(get_db)):
    result = crud.delete_room(db, room_id)
    if not result:
        raise HTTPException(status_code=404, detail="Quarto não encontrado")
    if result["mode"] == "deactivated":
        return {
            "detail": "Quarto possui reservas associadas; foi desativado em vez de excluído.",
            "room": schemas.RoomOut.model_validate(result["room"]),
        }
    return {"detail": "Quarto excluído com sucesso.", "room": result["room"]}


# Reservas

@app.post("/reservations", response_model=schemas.ReservationOut, status_code=201, tags=["reservations"])
def create_reservation(reservation: schemas.ReservationCreate, db: Session = Depends(get_db)):
    room = crud.get_room(db, reservation.room_id)
    if not room or not room.is_active:
        raise HTTPException(status_code=404, detail="Quarto não encontrado ou inativo")

    if not crud.is_room_available(db, reservation.room_id, reservation.check_in, reservation.check_out):
        raise HTTPException(status_code=409, detail="Quarto indisponível para o período selecionado")

    return crud.create_reservation(db, reservation)


@app.get("/reservations", response_model=list[schemas.ReservationOut], tags=["reservations"])
def get_reservations(db: Session = Depends(get_db)):
    return crud.list_reservations(db)


@app.put("/reservations/{reservation_id}", response_model=schemas.ReservationOut, tags=["reservations"])
def update_reservation(
    reservation_id: int, reservation_update: schemas.ReservationUpdate, db: Session = Depends(get_db)
):
    existing = crud.get_reservation(db, reservation_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    if existing.status == "cancelled":
        raise HTTPException(status_code=400, detail="Não é possível editar uma reserva cancelada")

    new_check_in = reservation_update.check_in or existing.check_in
    new_check_out = reservation_update.check_out or existing.check_out
    if new_check_out <= new_check_in:
        raise HTTPException(status_code=422, detail="check_out deve ser posterior a check_in")

    if (reservation_update.check_in or reservation_update.check_out) and not crud.is_room_available(
        db, existing.room_id, new_check_in, new_check_out, ignore_reservation_id=reservation_id
    ):
        raise HTTPException(status_code=409, detail="Quarto indisponível para o novo período selecionado")

    return crud.update_reservation(db, reservation_id, reservation_update)


@app.delete("/reservations/{reservation_id}", response_model=schemas.ReservationOut, tags=["reservations"])
def delete_reservation(reservation_id: int, db: Session = Depends(get_db)):
    reservation = crud.cancel_reservation(db, reservation_id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva não encontrada")
    return reservation


@app.get("/rooms/{room_id}/availability", tags=["rooms"])
def check_availability(room_id: int, check_in: str, check_out: str, db: Session = Depends(get_db)):
    from datetime import date
    ci = date.fromisoformat(check_in)
    co = date.fromisoformat(check_out)
    available = crud.is_room_available(db, room_id, ci, co)
    return {"room_id": room_id, "check_in": check_in, "check_out": check_out, "available": available}


# Front-end estático 
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def serve_frontend():
    return FileResponse("static/index.html")
