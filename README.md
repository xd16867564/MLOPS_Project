# MLOPS_Project —— House Price Estimator API

A FastAPI-based REST API that estimates whether a French property's asking
price is fair, given its city and surface area.

## 1. What We Did

We built a lightweight REST API that answers one simple question:

> *"Is this asking price reasonable for this city and surface area?"*

Starting from a minimal FastAPI skeleton (rule-based scorer, no data), we:

- Integrated a **real dataset** of 24,389 French cities with their average
  price per m² (source: DVF / official French property transactions)
- Replaced the placeholder scoring logic with a **data-driven benchmark**:
  expected price = `avg_price_m²(city) × surface`
- Added **input validation** via Pydantic (HTTP 422 on bad inputs)
- Structured the project following MLOps separation of concerns:
  - `app/main.py` — API layer only
  - `app/scoring.py` — business logic & inference
  - `app/validation.py` — input schema
  - `train_model.py` — data validation & benchmark summary (offline)
- Containerised the service with **Docker**
- Managed dependencies via `pyproject.toml`

The API endpoint:
```
GET /score?city=TOULON&surface=60&price=200000
```
Returns: expected price, gap in € and %, and a label (`underpriced` /
`fair` / `overpriced`).

---

## 2. Thought Process

### Part 1 — Non-Technical (What? Who? Why?)

**What?**
A tool that gives an instant market sanity check on a property's asking price.

**Who?**
Anyone evaluating a property purchase in France — a first-time buyer, an
investor, or a student doing an MLOps assignment — who wants a quick,
data-backed signal without needing a real-estate agent.

**Why?**
Property prices are opaque. A listing rarely tells you whether a price is
justified relative to the local market. We wanted a simple, transparent tool
that gives an immediate verdict: the price is in line with comparable
transactions, above, or below market.

---

### Part 2 — Technical Problem Statement

**Problem:**
Given observable inputs — city name, surface area (m²), and asking price (€)
— estimate a fair market price and flag whether the asking price deviates
significantly from it.

**Approach:**

We use a benchmark model:
```
expected_price = avg_price_m²(city) × surface
ratio          = asked_price / expected_price
```

`avg_price_m²` per city comes from a dataset of 24,389 French communes
derived from DVF (Demande de Valeur Foncière), the official French
property transaction registry.

Labels are assigned by fixed thresholds on the ratio:
- `underpriced` if ratio < 0.90
- `fair`        if 0.90 ≤ ratio ≤ 1.10
- `overpriced`  if ratio > 1.10

A score ∈ [0, 1] measures proximity to the expected price:
```
score = max(0, 1 − |ratio − 1|)
```

**Why not a regression model?**
With one feature per city (avg price/m²) and no transaction-level data in
our pipeline, a lookup benchmark is both interpretable and optimal. A
regression would add complexity without improving accuracy at this stage.
The architecture is designed so `scoring.py` can be swapped for an ML model
later with no change to the API layer.

**Data:**
- Source: DVF open data (French government), aggregated by commune
- Coverage: 24,389 French cities
- Key column: `avg_price_m2` (average €/m² per city)
- Cleaning: rows with missing or non-numeric prices are skipped at load time

---

## 3. Areas of Improvement

| Area | Current state | Next step |
|---|---|---|
| **Model** | City avg price lookup | Linear regression on surface + rooms + location |
| **Features** | City + surface only | Add number of rooms, floor, energy rating, build year |
| **Data freshness** | Static CSV | Auto-refresh from DVF API on a schedule |
| **Validation** | Pydantic schema | Add city existence check with helpful error message |
| **Testing** | Manual via /docs | Unit tests with `pytest` + CI via GitHub Actions |
| **Monitoring** | None | Log predictions, track drift over time |
| **Deployment** | Local / Codespaces | Host on serverless platform (Render, Railway) |
| **History** | No persistence | Store queries in SQLite, export to `.xlsx` |
| **UI** | JSON API only | Add a simple HTML form frontend |

---

## Project Structure
```
├── app/
│   ├── main.py          # FastAPI entrypoint
│   ├── scoring.py       # Benchmark inference & labelling
│   └── validation.py    # Pydantic input validation
├── data/
│   └── city_price_benchmark.csv   # 24 389 French cities, avg €/m²
├── train_model.py       # Offline data validation & summary
├── artifacts/           # Reserved for future model artifacts
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

Test it:
```
http://127.0.0.1:8000/docs
http://127.0.0.1:8000/score?city=TOULON&surface=60&price=200000
```

Docker:
```bash
docker build -t house-price-api .
docker run --rm -p 8001:8000 house-price-api
```
