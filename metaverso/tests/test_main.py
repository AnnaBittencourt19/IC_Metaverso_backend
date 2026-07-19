"""
Testes automatizados (pytest) para os endpoints leves da API, sem exigir
servidor rodando, GROQ_API_KEY real ou download de modelos de embeddings
(o RAG só é inicializado sob demanda, dentro de /api/v1/ask e /api/v1/ask-audio).
"""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_ok():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_info_ok():
    response = client.get("/api/v1/info")
    assert response.status_code == 200
    assert response.json()["name"] == "IC Metaverso RAG API"


def test_health_reflects_real_rag_state():
    """
    Regressão: /api/v1/health já retornou `rag_initialized: true` fixo,
    mesmo com o RAG nunca inicializado (ver documentacao/revisao_bugs_IC_METAVERSO.md).
    Sem nenhuma chamada a /api/v1/ask antes, o RAG não deve estar inicializado.
    """
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["rag_initialized"] is False


def test_ask_without_api_key_returns_403():
    response = client.post("/api/v1/ask", json={"question": "O que é 6G?"})
    assert response.status_code == 403


def test_ask_with_wrong_api_key_returns_403():
    response = client.post(
        "/api/v1/ask",
        json={"question": "O que é 6G?"},
        headers={"X-API-Key": "chave-invalida"},
    )
    assert response.status_code == 403
