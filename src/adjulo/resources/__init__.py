"""Regroupements de ressources de l'API Adjulo."""

from __future__ import annotations


class _Resource:
    """Base commune : garde une référence au client pour déléguer les requêtes."""

    def __init__(self, client):
        self._client = client

    def _get(self, path, **params):
        return self._client.request("GET", path, params=params)

    def _post(self, path, *, json=None, **params):
        return self._client.request("POST", path, params=params, json=json)
