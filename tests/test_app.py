def test_health_check(cliente):
    resposta = cliente.get("/health")
    assert resposta.status_code == 200


def test_criar_quarto(cliente):
    resposta = cliente.post(
        "/rooms",
        json={"number": "101", "room_type": "standard", "price_per_night": 150.0, "capacity": 2},
    )
    assert resposta.status_code == 201
    assert resposta.json()["number"] == "101"


def test_listar_quartos(cliente):
    cliente.post(
        "/rooms",
        json={"number": "101", "room_type": "standard", "price_per_night": 150.0, "capacity": 2},
    )
    resposta = cliente.get("/rooms")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_criar_reserva(cliente):
    quarto = cliente.post(
        "/rooms",
        json={"number": "101", "room_type": "standard", "price_per_night": 150.0, "capacity": 2},
    ).json()

    resposta = cliente.post(
        "/reservations",
        json={
            "room_id": quarto["id"],
            "guest_name": "Carlos Lima",
            "guest_email": "carlos@example.com",
            "check_in": "2026-11-01",
            "check_out": "2026-11-05",
        },
    )
    assert resposta.status_code == 201
    assert resposta.json()["status"] == "confirmed"


def test_reserva_com_datas_conflitantes_falha(cliente):
    quarto = cliente.post(
        "/rooms",
        json={"number": "101", "room_type": "standard", "price_per_night": 150.0, "capacity": 2},
    ).json()

    cliente.post(
        "/reservations",
        json={
            "room_id": quarto["id"],
            "guest_name": "Carlos Lima",
            "guest_email": "carlos@example.com",
            "check_in": "2026-11-01",
            "check_out": "2026-11-05",
        },
    )

    resposta = cliente.post(
        "/reservations",
        json={
            "room_id": quarto["id"],
            "guest_name": "Outro Hóspede",
            "guest_email": "outro@example.com",
            "check_in": "2026-11-03",
            "check_out": "2026-11-07",
        },
    )
    assert resposta.status_code == 409


def test_cancelar_reserva(cliente):
    quarto = cliente.post(
        "/rooms",
        json={"number": "101", "room_type": "standard", "price_per_night": 150.0, "capacity": 2},
    ).json()

    reserva = cliente.post(
        "/reservations",
        json={
            "room_id": quarto["id"],
            "guest_name": "Carlos Lima",
            "guest_email": "carlos@example.com",
            "check_in": "2026-11-01",
            "check_out": "2026-11-05",
        },
    ).json()

    resposta = cliente.delete(f"/reservations/{reserva['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "cancelled"
