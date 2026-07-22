"""Exemple minimal d'utilisation du SDK Adjulo.

Prérequis :
    export ADJULO_API_KEY="adj_votre_cle"
    export ADJULO_BASE_URL="https://api.adjulo.io"   # ou dev-api.adjulo.io
    python examples/quickstart.py
"""

from __future__ import annotations

from adjulo import AdjuloClient


def main():
    with AdjuloClient() as client:  # clé/URL lues depuis l'environnement
        print("Version de l'API :", client.public.version())
        print("Consommation :", client.compte.usage())

        page = client.appels_offres.list(q="informatique", per_page=5, source="seao")
        for ao in page.get("data", []):
            print("-", ao.get("titre") or ao.get("id"))

        print("\nRecherche sémantique « déneigement » :")
        res = client.appels_offres.search_semantique("déneigement de rues", limit=3)
        print(res)


if __name__ == "__main__":
    main()
