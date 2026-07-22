"""Fixtures des tests du SDK.

Deux familles de tests :

* **unitaires** — sans réseau, via ``httpx.MockTransport`` (fixture ``mock_client``) ;
* **live** (marqueur ``@pytest.mark.live``) — frappent une API réelle et exigent
  ``ADJULO_API_KEY`` + ``ADJULO_BASE_URL`` dans l'environnement ; ignorés sinon.
"""

from __future__ import annotations

import os

import httpx
import pytest

from adjulo import AdjuloClient


@pytest.fixture
def make_client():
    """Fabrique un ``AdjuloClient`` branché sur un transport httpx factice.

    Usage ::

        def handler(request):
            return httpx.Response(200, json={"ok": True})
        client = make_client(handler)
    """

    def _factory(handler, *, api_key="adj_test", **kwargs):
        transport = httpx.MockTransport(handler)
        return AdjuloClient(
            api_key=api_key,
            base_url="https://api.example.test",
            transport=transport,
            **kwargs,
        )

    return _factory


# ── Live ──────────────────────────────────────────────────────────────────

LIVE_KEY = os.getenv("ADJULO_API_KEY")
LIVE_URL = os.getenv("ADJULO_BASE_URL")


@pytest.fixture
def live_client():
    if not (LIVE_KEY and LIVE_URL):
        pytest.skip("ADJULO_API_KEY / ADJULO_BASE_URL absents — test live ignoré")
    with AdjuloClient(api_key=LIVE_KEY, base_url=LIVE_URL, timeout=30) as c:
        yield c


def pytest_collection_modifyitems(config, items):
    """Ignore les tests `live` si l'environnement n'est pas configuré."""
    if LIVE_KEY and LIVE_URL:
        return
    skip = pytest.mark.skip(reason="tests live désactivés (ADJULO_API_KEY/ADJULO_BASE_URL absents)")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip)
