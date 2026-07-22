"""Tests unitaires des ressources : vérifient la méthode/chemin/params émis."""

from __future__ import annotations

import httpx


def _recorder():
    """Handler qui enregistre la dernière requête et renvoie 200 vide-liste."""
    box = {}

    def handler(request):
        box["method"] = request.method
        box["path"] = request.url.path
        box["params"] = dict(request.url.params)
        return httpx.Response(200, json={"items": []})

    return box, handler


def test_appels_offres_list(make_client):
    box, handler = _recorder()
    make_client(handler).appels_offres.list(q="informatique", per_page=20, source="seao")
    assert box["method"] == "GET"
    assert box["path"] == "/v1/appels-offres"
    assert box["params"]["q"] == "informatique"
    assert box["params"]["per_page"] == "20"
    assert box["params"]["source"] == "seao"


def test_appels_offres_get(make_client):
    box, handler = _recorder()
    make_client(handler).appels_offres.get("SEAO-123")
    assert box["path"] == "/v1/appels-offres/SEAO-123"


def test_appels_offres_search_semantique(make_client):
    box, handler = _recorder()
    make_client(handler).appels_offres.search_semantique("déneigement", limit=5)
    assert box["path"] == "/v1/appels-offres/search-semantique"
    assert box["params"]["q"] == "déneigement"
    assert box["params"]["limit"] == "5"


def test_iter_all_pagine(make_client):
    pages = {
        "1": {"items": [{"id": 1}, {"id": 2}]},
        "2": {"items": [{"id": 3}]},  # page courte → stop
    }

    def handler(request):
        page = request.url.params.get("page")
        return httpx.Response(200, json=pages.get(page, {"items": []}))

    client = make_client(handler)
    ids = [ao["id"] for ao in client.appels_offres.iter_all(per_page=2)]
    assert ids == [1, 2, 3]


def test_fournisseurs_taux_succes(make_client):
    box, handler = _recorder()
    make_client(handler).fournisseurs.taux_succes("FO-12345")
    assert box["path"] == "/v1/fournisseurs/FO-12345/taux-succes"


def test_organismes_stats(make_client):
    box, handler = _recorder()
    make_client(handler).organismes.stats("ORG-9")
    assert box["path"] == "/v1/organismes/ORG-9/stats"


def test_stats_secteur_tendances(make_client):
    box, handler = _recorder()
    make_client(handler).stats.secteur_tendances("8111")
    assert box["path"] == "/v1/stats/secteur/8111/tendances"


def test_recherche_semantique_referentiels(make_client):
    box, handler = _recorder()
    make_client(handler).recherche.unspsc("logiciel", limit=3)
    assert box["path"] == "/v1/unspsc/search-semantique"
    assert box["params"]["q"] == "logiciel"


def test_compte_usage(make_client):
    box, handler = _recorder()
    make_client(handler).compte.usage()
    assert box["path"] == "/v1/usage"


def test_public_version(make_client):
    box, handler = _recorder()
    make_client(handler).public.version()
    assert box["path"] == "/v1/public/version"
