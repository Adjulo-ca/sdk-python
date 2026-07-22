"""Tests d'intégration « live » contre une API Adjulo réelle.

Ignorés automatiquement si ``ADJULO_API_KEY`` / ``ADJULO_BASE_URL`` sont absents
(voir ``conftest.py``). En CI (Jenkins), la clé est celle du client #16
(joey@adjulo.ca, plan Entreprise) injectée via un credential Jenkins.
"""

from __future__ import annotations

import pytest

from adjulo import AdjuloClient, AuthenticationError

pytestmark = pytest.mark.live


def test_version_publique(live_client):
    """Endpoint public — pas de quota, mais valide le transport + le parsing."""
    data = live_client.public.version()
    assert isinstance(data, dict)
    assert "version" in data or "semver" in data


def test_usage_authentifie(live_client):
    """La clé du client #16 permet de lire sa consommation."""
    usage = live_client.compte.usage()
    assert isinstance(usage, dict)


def test_liste_appels_offres(live_client):
    """Liste paginée : structure + au moins le contenant attendu."""
    page = live_client.appels_offres.list(per_page=5)
    assert isinstance(page, (dict, list))
    if isinstance(page, dict):
        # une clé d'items doit exister (l'API renvoie {data: [...], meta: {...}})
        assert any(k in page for k in ("data", "items", "resultats", "results"))


def test_recherche_semantique_ao(live_client):
    """Recherche sémantique — plan Pro/Entreprise (client #16 = Entreprise)."""
    res = live_client.appels_offres.search_semantique("services informatiques", limit=3)
    assert res is not None


def test_iter_all_borne(live_client):
    """L'itérateur paginé fonctionne de bout en bout (borné à 1 page)."""
    items = list(live_client.appels_offres.iter_all(per_page=5, max_pages=1))
    assert isinstance(items, list)


def test_cle_invalide_leve_401(live_client):
    """Une clé bidon doit produire une AuthenticationError (401)."""
    with AdjuloClient(api_key="adj_cle_invalide", base_url=live_client.base_url) as bad:
        with pytest.raises(AuthenticationError):
            bad.compte.usage()
