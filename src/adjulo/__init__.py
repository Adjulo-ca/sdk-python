"""SDK Python officiel de l'API Adjulo.

Veille des marchés publics québécois (SEAO) et fédéraux (CanadaBuys).

>>> from adjulo import AdjuloClient
>>> client = AdjuloClient(api_key="adj_…")
>>> client.appels_offres.list(q="informatique")
"""

from __future__ import annotations

__version__ = "0.2.0"

from .client import AdjuloClient
from .errors import (
    AdjuloAPIError,
    AdjuloConfigError,
    AdjuloError,
    AuthenticationError,
    NotFoundError,
    PermissionError_,
    RateLimitError,
    ServerError,
)

__all__ = [
    "__version__",
    "AdjuloClient",
    "AdjuloError",
    "AdjuloConfigError",
    "AdjuloAPIError",
    "AuthenticationError",
    "PermissionError_",
    "NotFoundError",
    "RateLimitError",
    "ServerError",
]
