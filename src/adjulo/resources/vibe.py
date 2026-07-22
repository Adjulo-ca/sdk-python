"""Ressource : InsightsVibe — prédiction P(le fournisseur gagne un AO)."""

from __future__ import annotations

from . import _Resource


class Vibe(_Resource):
    """Prédictions de probabilité de gain et concurrents possibles par AO."""

    def opportunites(self, **params):
        """Opportunités scorées pour le profil du client (P(gagne))."""
        return self._get("/v1/vibe/opportunites", **params)

    def soumissions(self, seao_id):
        """Historique des soumissions d'un fournisseur (par identifiant SEAO)."""
        return self._get(f"/v1/vibe/fournisseurs/{seao_id}/soumissions")

    def feedback(self, *, json=None):
        """Envoie un retour (outcome) alimentant la boucle d'active learning."""
        return self._post("/v1/vibe/feedback", json=json)
