"""Tests unitaires du client (sans réseau, via MockTransport)."""

from __future__ import annotations

import httpx
import pytest

from adjulo import (
    AdjuloClient,
    AuthenticationError,
    NotFoundError,
    PermissionError_,
    RateLimitError,
    ServerError,
    __version__,
)
from adjulo.errors import AdjuloConfigError


def test_base_url_invalide():
    with pytest.raises(AdjuloConfigError):
        AdjuloClient(api_key="adj_x", base_url="pas-une-url")


def test_cle_depuis_environnement(monkeypatch):
    monkeypatch.setenv("ADJULO_API_KEY", "adj_env")
    monkeypatch.setenv("ADJULO_BASE_URL", "https://api.example.test")
    c = AdjuloClient()
    assert c.api_key == "adj_env"
    assert c.base_url == "https://api.example.test"
    c.close()


def test_headers_envoyes(make_client):
    captured = {}

    def handler(request):
        captured["key"] = request.headers.get("X-API-Key")
        captured["ua"] = request.headers.get("User-Agent")
        return httpx.Response(200, json={"ok": True})

    client = make_client(handler, api_key="adj_secret")
    assert client.get("/v1/usage") == {"ok": True}
    assert captured["key"] == "adj_secret"
    assert captured["ua"] == f"adjulo-python/{__version__}"


def test_params_none_filtres(make_client):
    seen = {}

    def handler(request):
        seen["url"] = str(request.url)
        return httpx.Response(200, json=[])

    client = make_client(handler)
    client.appels_offres.list(q=None, per_page=10, statut="ouvert")
    assert "statut=ouvert" in seen["url"]
    assert "per_page=10" in seen["url"]
    assert "q=" not in seen["url"]  # None retiré de la query string


@pytest.mark.parametrize(
    "status,exc",
    [
        (401, AuthenticationError),
        (403, PermissionError_),
        (404, NotFoundError),
        (429, RateLimitError),
        (500, ServerError),
    ],
)
def test_mapping_erreurs(make_client, status, exc):
    def handler(request):
        return httpx.Response(status, json={"detail": "boom"})

    # max_retries=0 pour ne pas boucler sur 429/5xx
    client = make_client(handler, max_retries=0)
    with pytest.raises(exc) as ei:
        client.get("/v1/appels-offres")
    assert ei.value.status_code == status
    assert ei.value.detail == "boom"


def test_retry_sur_429_puis_succes(make_client):
    calls = {"n": 0}

    def handler(request):
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"}, json={"detail": "quota"})
        return httpx.Response(200, json={"ok": True})

    client = make_client(handler, max_retries=2)
    assert client.get("/v1/usage") == {"ok": True}
    assert calls["n"] == 2  # une tentative + un retry


def test_reponse_vide(make_client):
    def handler(request):
        return httpx.Response(204)

    client = make_client(handler)
    assert client.request("DELETE", "/v1/pipeline/42") is None


def test_context_manager_ferme(make_client):
    def handler(request):
        return httpx.Response(200, json={})

    with make_client(handler) as client:
        client.get("/v1/usage")
    assert client._client.is_closed
