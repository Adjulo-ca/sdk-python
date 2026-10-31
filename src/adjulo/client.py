"""Client synchrone de l'API Adjulo."""

from __future__ import annotations

import os
import time

import httpx

from . import __version__
from .errors import AdjuloConfigError, RateLimitError, ServerError, raise_for_status
from .resources.appels_offres import AppelsOffres
from .resources.compte import Compte
from .resources.fournisseurs import Fournisseurs
from .resources.organismes import Organismes
from .resources.public import Public
from .resources.recherche import Recherche
from .resources.stats import Stats
from .resources.vibe import Vibe

DEFAULT_BASE_URL = "https://api.adjulo.io"

#: Langues acceptées par l'option ``language`` (en-tête ``Accept-Language``).
SUPPORTED_LANGUAGES = ("fr", "en")


def _normalize_language(value):
    """Valide la langue demandée et la rend en minuscules (``None`` si absente).

    L'API ne reconnaît que la valeur nue ``en`` ; toute autre valeur, ou
    l'absence d'en-tête, donne du français. Le SDK refuse donc tout ce qui
    n'est ni ``fr`` ni ``en`` plutôt que de laisser l'API retomber en silence
    sur le français.
    """
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if normalized not in SUPPORTED_LANGUAGES:
        raise AdjuloConfigError(
            f"language invalide : {value!r} (valeurs admises : \"fr\" ou \"en\")"
        )
    return normalized


class AdjuloClient:
    """Point d'entrée du SDK Adjulo.

    Exemple
    -------
    >>> from adjulo import AdjuloClient
    >>> client = AdjuloClient(api_key="adj_…")
    >>> page = client.appels_offres.list(q="informatique", per_page=20)
    >>> for ao in page["items"]:
    ...     print(ao["titre"])

    La clé API, l'URL de base et la langue peuvent aussi provenir de
    l'environnement (``ADJULO_API_KEY``, ``ADJULO_BASE_URL`` et
    ``ADJULO_LANGUAGE``).

    Le client est utilisable comme gestionnaire de contexte pour fermer
    proprement la connexion HTTP ::

        with AdjuloClient(api_key="adj_…") as client:
            client.compte.usage()

    Paramètres
    ----------
    api_key : str, optionnel
        Clé API (header ``X-API-Key``). À défaut, lue depuis ``ADJULO_API_KEY``.
        Peut être ``None`` pour n'appeler que les endpoints publics.
    base_url : str, optionnel
        URL racine de l'API. Défaut : ``ADJULO_BASE_URL`` ou ``https://api.adjulo.io``.
    timeout : float
        Délai d'attente réseau, en secondes (défaut 30).
    max_retries : int
        Nombre de tentatives supplémentaires sur 429/5xx (défaut 2).
    language : str, optionnel
        Langue des réponses : ``"fr"`` ou ``"en"`` (insensible à la casse),
        envoyée dans l'en-tête ``Accept-Language`` de chaque requête. En
        anglais, l'API rend en anglais les messages d'erreur, le ``titre`` des
        avis (titre traduit), les résumés (``resume_en``) et les libellés
        UNSPSC ; les noms d'organismes et d'entreprises ne changent pas.
        À défaut, lue depuis ``ADJULO_LANGUAGE`` ; sinon aucun en-tête n'est
        envoyé et l'API répond en français.
    """

    def __init__(
        self,
        api_key=None,
        *,
        base_url=None,
        timeout=30.0,
        max_retries=2,
        http_client=None,
        transport=None,
        language=None,
    ):
        self.api_key = api_key or os.getenv("ADJULO_API_KEY")
        self.base_url = (base_url or os.getenv("ADJULO_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        if not self.base_url.startswith(("http://", "https://")):
            raise AdjuloConfigError(
                f"base_url invalide : {self.base_url!r} (doit commencer par http:// ou https://)"
            )
        self.max_retries = max(0, int(max_retries))
        if language is None:
            language = os.getenv("ADJULO_LANGUAGE") or None
        self.language = _normalize_language(language)

        headers = {
            "User-Agent": f"adjulo-python/{__version__}",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        if self.language:
            headers["Accept-Language"] = self.language

        self._client = http_client or httpx.Client(
            base_url=self.base_url, headers=headers, timeout=timeout, transport=transport
        )
        self._owns_client = http_client is None

        # Ressources
        self.appels_offres = AppelsOffres(self)
        self.fournisseurs = Fournisseurs(self)
        self.organismes = Organismes(self)
        self.stats = Stats(self)
        self.recherche = Recherche(self)
        self.vibe = Vibe(self)
        self.compte = Compte(self)
        self.public = Public(self)

    # ── Cœur HTTP ────────────────────────────────────────────────────────────

    def request(self, method, path, *, params=None, json=None):
        """Effectue une requête et renvoie le corps JSON décodé.

        Ré-essaie automatiquement sur 429 (en respectant ``Retry-After``) et
        sur les 5xx, jusqu'à ``max_retries`` fois, avec back-off exponentiel.
        """
        # On nettoie les paramètres None pour ne pas polluer la query string.
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        attempt = 0
        while True:
            response = self._client.request(method, path, params=params, json=json)
            try:
                raise_for_status(response)
            except (RateLimitError, ServerError) as exc:
                if attempt >= self.max_retries:
                    raise
                delay = getattr(exc, "retry_after", None)
                if delay is None:
                    delay = min(2 ** attempt, 8)
                attempt += 1
                time.sleep(delay)
                continue

            if not response.content:
                return None
            try:
                return response.json()
            except ValueError:
                return response.text

    def get(self, path, *, params=None):
        """Raccourci ``GET`` — utile comme échappatoire pour tout endpoint non
        encore exposé par une méthode dédiée du SDK."""
        return self.request("GET", path, params=params)

    def post(self, path, *, json=None, params=None):
        """Raccourci ``POST``."""
        return self.request("POST", path, params=params, json=json)

    # ── Cycle de vie ─────────────────────────────────────────────────────────

    def close(self):
        if self._owns_client:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
