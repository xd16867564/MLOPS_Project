# MLOPS_Project — House Price Estimator API

A FastAPI-based REST API that estimates whether a French property's asking price is fair, given its city and surface area.

![Price Check](assets/Screenshot%20-%20House%20price%20estimation%20preview.png)

![City Compare](assets/Screenshot%20-%20House%20price%20comparison%20preview.png)
---

## 1. What We Did

We built a lightweight REST API that answers one simple question:

> *"Is this asking price reasonable for this city and surface area?"*

Starting from a minimal FastAPI skeleton (rule-based scorer, no data), we:

- Integrated a **real dataset** of 24,389 French cities with their average price per m² (source: DVF / official French property transactions)
- Replaced the placeholder scoring logic with a **data-driven benchmark**: `expected price = avg_price_m²(city) × surface`
- Added **input validation** via Pydantic (HTTP 422 on bad inputs)
- Added **data quality filtering**: prices above 70,000 €/m² are excluded at load time as data entry errors (e.g. DVF records where total transaction value was mistakenly recorded as unit price)
- Added a **city search endpoint** (`/search`) for real-time autocomplete
- Built a **bilingual frontend** (EN/FR) with two tabs: Price Check and City Compare, served as a static file via FastAPI
- Structured the project following MLOps separation of concerns:
  - `app/main.py` — API layer only
  - `app/scoring.py` — business logic, inference & data cleaning
  - `app/validation.py` — input schema
  - `train_model.py` — data validation & benchmark summary (offline)
- Containerised the service with **Docker**
- Managed dependencies via `pyproject.toml`

### API Endpoints

| Endpoint | Description |
|---|---|
| `GET /score?city=TOULON&surface=60&price=200000` | Returns expected price, gap in € and %, and a verdict |
| `GET /compare?cities=TOULON,BORDEAUX,NICE&surface=60` | Ranked comparison of up to 10 cities |
| `GET /search?q=PAR&limit=20` | Autocomplete city search |
| `GET /ui` | Serves the frontend |

---

## 2. Thought Process

### Part 1 — Non-Technical (What? Who? Why?)

**What?**
A tool that gives an instant market sanity check on a property's asking price.

**Who?**
Anyone evaluating a property purchase in France — a first-time buyer, an investor, or a student doing an MLOps assignment — who wants a quick, data-backed signal without needing a real-estate agent.

**Why?**
Property prices are opaque. A listing rarely tells you whether a price is justified relative to the local market. We wanted a simple, transparent tool that gives an immediate verdict: the price is in line with comparable transactions, above, or below market.

---

### Part 2 — Technical Problem Statement

**Problem:**
Given observable inputs — city name, surface area (m²), and asking price (€) — estimate a fair market price and flag whether the asking price deviates significantly from it.

**Approach:**

We use a benchmark model:
```
expected_price = avg_price_m²(city) × surface
ratio          = asked_price / expected_price
```

`avg_price_m²` per city comes from a dataset of 24,389 French communes derived from DVF (Demande de Valeur Foncière), the official French property transaction registry.

Labels are assigned by fixed thresholds on the ratio:
- `underpriced` if ratio < 0.90
- `fair`        if 0.90 ≤ ratio ≤ 1.10
- `overpriced`  if ratio > 1.10

A score ∈ [0, 1] measures proximity to the expected price:
```
score = max(0, 1 − |ratio − 1|)
```

**Why not a regression model?**
With one feature per city (avg price/m²) and no transaction-level data in our pipeline, a lookup benchmark is both interpretable and optimal. A regression would add complexity without improving accuracy at this stage. The architecture is designed so `scoring.py` can be swapped for an ML model later with no change to the API layer.

**Data cleaning decision:**
During development we discovered several DVF records with clearly erroneous unit prices (e.g. PARIS 07 at 340,092 €/m², PARIS 08 at 228,375 €/m²). These are data entry errors in the source — most likely cases where total transaction value was recorded instead of price per m². We considered IQR-based outlier detection but rejected it because French city prices are legitimately right-skewed: Paris districts are genuinely expensive and should not be filtered out alongside erroneous records. The chosen solution is a hard upper cap of 50,000 €/m², which preserves all realistic market prices while removing obvious data errors.

**Data:**
- Source: DVF open data (French government), aggregated by commune
- Coverage: 24,389 French cities (22,885 after outlier removal)
- Key column: `avg_price_m2` (average €/m² per city)
- Cleaning: rows with missing, non-numeric, or implausible prices (> 50,000 €/m²) are excluded at load time

---

## 3. Areas of Improvement

| Area | Current state | Next step |
|---|---|---|
| **Model** | City avg price lookup | Linear regression on surface + rooms + location |
| **Features** | City + surface only | Add number of rooms, floor, energy rating, build year |
| **Price range** | Single expected price | Show a ±20% estimated range to reflect real market variance |
| **Data freshness** | Static CSV | Auto-refresh from DVF API on a schedule |
| **Data quality** | Hard cap at 70,000 €/m² | Cross-validate against a secondary source (e.g. Meilleurs Agents API) |
| **Testing** | Manual via /docs | Unit tests with `pytest` + CI via GitHub Actions |
| **Monitoring** | None | Log predictions, track drift over time |
| **Deployment** | Local only | Host on serverless platform (Render, Railway) |
| **History** | In-memory (lost on refresh) | Persist queries in SQLite, export to `.xlsx` |
| **UI** | Simple HTML frontend (Price Check + City Compare) | Map view, price history chart, price trend over time |

---

## Project Structure
```
├── app/
│   ├── main.py          # FastAPI entrypoint & routing
│   ├── scoring.py       # Benchmark inference, labelling & data cleaning
│   ├── validation.py    # Pydantic input schema
│   └── index.html       # Bilingual frontend (EN/FR)
├── data/
│   └── city_price_benchmark.csv   # 24,389 French cities, avg €/m²
├── train_model.py       # Offline data validation & summary
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Quick Start
```bash
# Install dependencies
pip install fastapi uvicorn pydantic

# Validate the dataset
python train_model.py

# Run the API
uvicorn app.main:app --reload --port 8000
```

Open the frontend:
```
http://127.0.0.1:8000/ui
```

Other endpoints to test:
```
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/score?city=TOULON&surface=60&price=200000
http://127.0.0.1:8000/compare?cities=TOULON,BORDEAUX,NICE&surface=60
http://127.0.0.1:8000/search?q=PAR&limit=20
```

Docker:
```bash
docker build -t house-price-api .
docker run --rm -p 8001:8000 house-price-api
```
