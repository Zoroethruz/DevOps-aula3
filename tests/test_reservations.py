def _payload_reserva(room_id, **sobrescritas):
    payload = {
        "room_id": room_id,
        "guest_name": "Carlos Lima",
        "guest_email": "carlos@example.com",
        "check_in": "2026-11-01",
        "check_out": "2026-11-05",
    }
    payload.update(sobrescritas)
    return payload


def test_criar_reserva(cliente, criar_quarto):
    quarto = criar_quarto()
    resposta = cliente.post("/reservations", json=_payload_reserva(quarto["id"]))
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["room_id"] == quarto["id"]
    assert dados["status"] == "confirmed"


def test_criar_reserva_com_quarto_inexistente(cliente):
    resposta = cliente.post("/reservations", json=_payload_reserva(999))
    assert resposta.status_code == 404


def test_criar_reserva_em_quarto_inativo_falha(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.put(f"/rooms/{quarto['id']}", json={"is_active": False})
    resposta = cliente.post("/reservations", json=_payload_reserva(quarto["id"]))
    assert resposta.status_code == 404


def test_criar_reserva_com_datas_invalidas_falha(cliente, criar_quarto):
    quarto = criar_quarto()
    resposta = cliente.post(
        "/reservations",
        json=_payload_reserva(quarto["id"], check_in="2026-11-05", check_out="2026-11-01"),
    )
    assert resposta.status_code == 422


def test_criar_reserva_com_conflito_de_datas_falha(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.post("/reservations", json=_payload_reserva(quarto["id"]))

    resposta = cliente.post(
        "/reservations",
        json=_payload_reserva(
            quarto["id"], guest_name="Outro Hóspede", check_in="2026-11-03", check_out="2026-11-07"
        ),
    )
    assert resposta.status_code == 409


def test_criar_reserva_sem_conflito_de_datas_funciona(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.post("/reservations", json=_payload_reserva(quarto["id"]))

    resposta = cliente.post(
        "/reservations",
        json=_payload_reserva(quarto["id"], check_in="2026-11-05", check_out="2026-11-10"),
    )
    assert resposta.status_code == 201


def test_listar_reservas(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.post("/reservations", json=_payload_reserva(quarto["id"]))
    resposta = cliente.get("/reservations")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_atualizar_datas_da_reserva(cliente, criar_quarto):
    quarto = criar_quarto()
    criada = cliente.post("/reservations", json=_payload_reserva(quarto["id"])).json()

    resposta = cliente.put(
        f"/reservations/{criada['id']}",
        json={"check_in": "2026-11-10", "check_out": "2026-11-12"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["check_in"] == "2026-11-10"


def test_atualizar_reserva_inexistente(cliente):
    resposta = cliente.put("/reservations/999", json={"guest_name": "Novo Nome"})
    assert resposta.status_code == 404


def test_atualizar_reserva_para_datas_conflitantes_falha(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.post("/reservations", json=_payload_reserva(quarto["id"]))
    segunda = cliente.post(
        "/reservations",
        json=_payload_reserva(quarto["id"], check_in="2026-11-10", check_out="2026-11-12"),
    ).json()

    resposta = cliente.put(
        f"/reservations/{segunda['id']}",
        json={"check_in": "2026-11-02", "check_out": "2026-11-04"},
    )
    assert resposta.status_code == 409


def test_cancelar_reserva(cliente, criar_quarto):
    quarto = criar_quarto()
    criada = cliente.post("/reservations", json=_payload_reserva(quarto["id"])).json()

    resposta = cliente.delete(f"/reservations/{criada['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "cancelled"


def test_nao_pode_atualizar_reserva_cancelada(cliente, criar_quarto):
    quarto = criar_quarto()
    criada = cliente.post("/reservations", json=_payload_reserva(quarto["id"])).json()
    cliente.delete(f"/reservations/{criada['id']}")

    resposta = cliente.put(f"/reservations/{criada['id']}", json={"guest_name": "Novo Nome"})
    assert resposta.status_code == 400


def test_cancelar_reserva_inexistente(cliente):
    resposta = cliente.delete("/reservations/999")
    assert resposta.status_code == 404


def test_verificar_disponibilidade(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.post("/reservations", json=_payload_reserva(quarto["id"]))

    resposta = cliente.get(
        f"/rooms/{quarto['id']}/availability",
        params={"check_in": "2026-11-02", "check_out": "2026-11-04"},
    )
    assert resposta.status_code == 200
    assert resposta.json()["available"] is False

    resposta = cliente.get(
        f"/rooms/{quarto['id']}/availability",
        params={"check_in": "2026-12-01", "check_out": "2026-12-05"},
    )
    assert resposta.json()["available"] is True
