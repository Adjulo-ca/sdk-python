# Adjulo — SDK Python

SDK Python officiel de l'**API Adjulo**, la solution souveraine de veille des
marchés publics québécois (**SEAO**) et fédéraux (**CanadaBuys**).

> *L'intelligence des marchés publics.*

- **Auth** : clé API via header `X-API-Key` (obtenue depuis le portail Adjulo).
- **Transport** : `httpx` (client synchrone), retry automatique sur `429`/`5xx`.
- **Python** : 3.10+.

---

## Installation

```bash
pip install adjulo
```

En développement (depuis ce dépôt) :

```bash
uv pip install -e ".[dev]"   # ou : pip install -e ".[dev]"
```

---

## Démarrage rapide

```python
from adjulo import AdjuloClient

client = AdjuloClient(api_key="adj_votre_cle")   # ou via ADJULO_API_KEY

# Lister des appels d'offres — réponse {"data": [...], "meta": {...}}
page = client.appels_offres.list(q="informatique", per_page=20, source="seao")
for ao in page["data"]:
    print(ao["titre"])

# Pagination automatique (enchaîne les pages)
for ao in client.appels_offres.iter_all(q="informatique", max_pages=5):
    print(ao["titre"])

# Détail d'un appel d'offres
ao = client.appels_offres.get("SEAO-123456")

# Recherche sémantique (embeddings e5) — plan Pro/Entreprise
resultats = client.appels_offres.search_semantique("déneigement de rues", limit=10)

# Taux de succès réel d'un fournisseur (gagnés/soumis) — plan Pro
taux = client.fournisseurs.taux_succes("FO-000123")

# Consommation de votre compte
print(client.compte.usage())
```

La clé API et l'URL de base peuvent provenir de l'environnement :

```bash
export ADJULO_API_KEY="adj_votre_cle"
export ADJULO_BASE_URL="https://api.adjulo.io"   # défaut
```

Le client est aussi un gestionnaire de contexte :

```python
with AdjuloClient() as client:
    print(client.public.version())
```

---

## Ressources disponibles

| Accès | Endpoints couverts |
|---|---|
| `client.appels_offres` | `list` · `iter_all` · `get` · `categories` · `search` · `search_semantique` · `soumissionnaires` · `contexte` |
| `client.fournisseurs` | `top` · `recherche` · `taux_succes` · `concurrents` · `contrats` · `gold_profile` |
| `client.organismes` | `search` · `search_semantique` · `stats` |
| `client.stats` | `avenants` · `gre_a_gre` · `secteur_tendances` |
| `client.recherche` | `contrats` · `unspsc` · `scian` (recherche sémantique des référentiels) |
| `client.vibe` | `opportunites` · `soumissions` · `feedback` (InsightsVibe) |
| `client.compte` | `usage` · `plans` |
| `client.public` | `dashboard` · `contrats_recents` · `annonces` · `tendances` · `version` · `services_catalogue` (sans clé) |

### Échappatoire générique

Tout endpoint non encore exposé par une méthode dédiée reste accessible :

```python
client.get("/v1/f2f/concurrents", params={"limit": 5})
client.post("/v1/vibe/feedback", json={"ao_id": "…", "outcome": "gagne"})
```

---

## Gestion des erreurs

Toutes les erreurs héritent de `AdjuloError`.

```python
from adjulo import AdjuloClient, AuthenticationError, RateLimitError, PermissionError_

try:
    client.fournisseurs.taux_succes("FO-000123")
except AuthenticationError:
    ...  # 401 — clé absente/invalide/expirée
except PermissionError_:
    ...  # 403 — plan insuffisant / abonnement requis
except RateLimitError as e:
    ...  # 429 — quota dépassé ; e.retry_after (secondes) si fourni
```

| Exception | HTTP |
|---|---|
| `AuthenticationError` | 401 |
| `PermissionError_` | 403 |
| `NotFoundError` | 404 |
| `RateLimitError` | 429 |
| `ServerError` | 5xx |
| `AdjuloAPIError` | autres 4xx |

---

## Développement & tests

```bash
uv run pytest                     # tests unitaires (sans réseau, MockTransport)
```

Les tests d'intégration **live** frappent une API réelle et sont ignorés tant que
les variables ne sont pas définies :

```bash
export ADJULO_API_KEY="adj_…"
export ADJULO_BASE_URL="https://dev-api.adjulo.io"
uv run pytest -m live
```

En CI (Jenkins, job `adjulo-api-tests`), la clé de test est celle du **client #16**
(plan Entreprise), injectée via un credential Jenkins.

---

## Licence

Propriétaire — © Adjulo. `info@adjulo.ca`
