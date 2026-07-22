"""Hiérarchie d'exceptions du SDK Adjulo.

Toutes les erreurs héritent de :class:`AdjuloError`, ce qui permet d'attraper
l'ensemble des erreurs du SDK avec un seul `except AdjuloError`.
"""

from __future__ import annotations


class AdjuloError(Exception):
    """Erreur de base du SDK Adjulo."""


class AdjuloConfigError(AdjuloError):
    """Configuration invalide (clé API absente, URL malformée, …)."""


class AdjuloAPIError(AdjuloError):
    """Erreur renvoyée par l'API (réponse HTTP non 2xx).

    Attributs
    ---------
    status_code : int
        Code HTTP renvoyé par l'API.
    detail : str | None
        Message ``detail`` extrait du corps JSON (convention FastAPI).
    response : httpx.Response | None
        Réponse brute, pour inspection avancée.
    """

    def __init__(self, message, *, status_code=None, detail=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail
        self.response = response


class AuthenticationError(AdjuloAPIError):
    """Clé API manquante, invalide, désactivée ou session expirée (401)."""


class PermissionError_(AdjuloAPIError):
    """Accès refusé — plan insuffisant ou abonnement requis (403)."""


class NotFoundError(AdjuloAPIError):
    """Ressource introuvable (404)."""


class RateLimitError(AdjuloAPIError):
    """Quota journalier dépassé ou rate limit applicatif (429).

    ``retry_after`` (secondes) est renseigné si l'API fournit l'en-tête
    ``Retry-After``.
    """

    def __init__(self, message, *, retry_after=None, **kwargs):
        super().__init__(message, **kwargs)
        self.retry_after = retry_after


class ServerError(AdjuloAPIError):
    """Erreur côté serveur (5xx)."""


def raise_for_status(response):
    """Lève l'exception typée correspondant au code HTTP, sinon ne fait rien."""
    if response.is_success:
        return

    # La convention FastAPI place le message d'erreur dans ``detail``.
    detail = None
    try:
        body = response.json()
        if isinstance(body, dict):
            detail = body.get("detail")
    except Exception:  # corps non-JSON (proxy, WAF, HTML…)
        detail = (response.text or "").strip()[:500] or None

    status = response.status_code
    message = f"HTTP {status}"
    if detail:
        message += f" — {detail}"

    kwargs = {"status_code": status, "detail": detail, "response": response}

    if status == 401:
        raise AuthenticationError(message, **kwargs)
    if status == 403:
        raise PermissionError_(message, **kwargs)
    if status == 404:
        raise NotFoundError(message, **kwargs)
    if status == 429:
        retry_after = response.headers.get("Retry-After")
        try:
            retry_after = int(retry_after) if retry_after is not None else None
        except (TypeError, ValueError):
            retry_after = None
        raise RateLimitError(message, retry_after=retry_after, **kwargs)
    if status >= 500:
        raise ServerError(message, **kwargs)
    raise AdjuloAPIError(message, **kwargs)
