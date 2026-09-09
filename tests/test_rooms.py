def test_criar_quarto(cliente):
    resposta = cliente.post(
        "/rooms",
        json={
            "number": "201",
            "room_type": "deluxe",
            "price_per_night": 300.0,
            "capacity": 3,
        },
    )
    assert resposta.status_code == 201
    dados = resposta.json()
    assert dados["number"] == "201"
    assert dados["room_type"] == "deluxe"
    assert dados["is_active"] is True
    assert "id" in dados


def test_criar_quarto_com_numero_duplicado_falha(cliente, criar_quarto):
    criar_quarto(number="101")
    resposta = cliente.post(
        "/rooms",
        json={
            "number": "101",
            "room_type": "standard",
            "price_per_night": 120.0,
            "capacity": 2,
        },
    )
    assert resposta.status_code == 400


def test_listar_quartos(cliente, criar_quarto):
    criar_quarto(number="101")
    criar_quarto(number="102")
    resposta = cliente.get("/rooms")
    assert resposta.status_code == 200
    assert len(resposta.json()) == 2


def test_buscar_quartos_por_tipo_e_preco(cliente, criar_quarto):
    criar_quarto(number="101", room_type="standard", price_per_night=100.0)
    criar_quarto(number="201", room_type="suite", price_per_night=500.0)

    resposta = cliente.get("/rooms", params={"room_type": "suite"})
    assert resposta.status_code == 200
    resultados = resposta.json()
    assert len(resultados) == 1
    assert resultados[0]["number"] == "201"

    resposta = cliente.get("/rooms", params={"max_price": 200})
    resultados = resposta.json()
    assert len(resultados) == 1
    assert resultados[0]["number"] == "101"


def test_buscar_quarto_por_id(cliente, criar_quarto):
    quarto = criar_quarto()
    resposta = cliente.get(f"/rooms/{quarto['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["number"] == quarto["number"]


def test_buscar_quarto_inexistente(cliente):
    resposta = cliente.get("/rooms/999")
    assert resposta.status_code == 404


def test_atualizar_quarto(cliente, criar_quarto):
    quarto = criar_quarto()
    resposta = cliente.put(f"/rooms/{quarto['id']}", json={"price_per_night": 175.0})
    assert resposta.status_code == 200
    assert resposta.json()["price_per_night"] == 175.0


def test_atualizar_quarto_para_numero_conflitante_falha(cliente, criar_quarto):
    criar_quarto(number="101")
    quarto_b = criar_quarto(number="102")
    resposta = cliente.put(f"/rooms/{quarto_b['id']}", json={"number": "101"})
    assert resposta.status_code == 400


def test_atualizar_quarto_inexistente(cliente):
    resposta = cliente.put("/rooms/999", json={"price_per_night": 100.0})
    assert resposta.status_code == 404


def test_excluir_quarto_sem_reservas_e_removido(cliente, criar_quarto):
    quarto = criar_quarto()
    resposta = cliente.delete(f"/rooms/{quarto['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["detail"] == "Quarto excluído com sucesso."

    resposta = cliente.get(f"/rooms/{quarto['id']}")
    assert resposta.status_code == 404


def test_excluir_quarto_com_reservas_e_desativado(cliente, criar_quarto):
    quarto = criar_quarto()
    cliente.post(
        "/reservations",
        json={
            "room_id": quarto["id"],
            "guest_name": "Ana Souza",
            "guest_email": "ana@example.com",
            "check_in": "2026-10-01",
            "check_out": "2026-10-05",
        },
    )

    resposta = cliente.delete(f"/rooms/{quarto['id']}")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert "desativado" in corpo["detail"]
    assert corpo["room"]["is_active"] is False

    resposta = cliente.get(f"/rooms/{quarto['id']}")
    assert resposta.status_code == 200
    assert resposta.json()["is_active"] is False


def test_excluir_quarto_inexistente(cliente):
    resposta = cliente.delete("/rooms/999")
    assert resposta.status_code == 404
