# MLOPS_Project —— House Price Estimator API

## 1. What We Did

We built a FastAPI-based REST API that estimates residential property prices
from house characteristics (surface area, number of rooms, location score,
energy rating, etc.).

The project started from a deterministic, rule-based pricing function and was
progressively upgraded following MLOps principles:

- Replaced the rule-based scorer with a **regression model** trained on real
  housing transaction data
- Separated concerns: API layer (`main.py`), business logic (`scoring.py`),
  model training (`train_model.py`), input validation (`validation.py`)
- Packaged the service with **Docker** for reproducible deployment
- Managed dependencies via `pyproject.toml`
- Stored the trained model as an artifact (`artifacts/model.json`) committed
  alongside the code, so the API is self-contained and immediately runnable

The API exposes a single endpoint:
```

GET /score?surface=80&nb\_room=3&price=250000
```

It returns an estimated price, the gap to the asked price (€ and %), and a
label: `underpriced` / `fair` / `overpriced`.

---

## 2. Thought Process

### Part 1 — Non-Technical (What? Who? Why?)

**What?**
A tool that answers one simple question a property buyer asks constantly:
*"Is this asking price reasonable given what the flat actually is?"*

**Who?**
Anyone evaluating a property purchase who wants a quick, data-backed sanity
check — without needing a real-estate agent or financial expertise.

**Why?**
Property prices are opaque. Listings rarely tell you whether a price is
justified. We wanted a lightweight, transparent tool that gives an instant
signal: the price is either in line with comparable transactions, above, or
below market.

---

### Part 2 — Technical Problem Statement

**Problem:**
Given a set of observable property characteristics
(surface area *s*, number of rooms *r*, and optionally other features),
estimate a fair market price *p̂* and flag whether a listed price *p* deviates
significantly from it.

**Approach:**

We model log(price) as a linear function of the inputs:
```

log(p̂) = b₀ + b₁·s + b₂·r
```

Using log-price rather than raw price stabilises variance and captures
proportional effects (a 10 % deviation means the same thing whether the flat
costs €150 k or €500 k).

Coefficients (b₀, b₁, b₂) and residual standard deviation σ are estimated
offline via OLS regression on a labelled dataset of real transactions
(`train_model.py`), then serialised to `artifacts/model.json`.

At inference time the API:
1. Loads the frozen model artifact
2. Computes p̂ from the inputs
3. Calculates `ratio = p / p̂` and a normalised deviation score
4. Returns a label based on thresholds:
   - `underpriced` if ratio < 0.90
   - `fair`        if 0.90 ≤ ratio ≤ 1.10
   - `overpriced`  if ratio > 1.10

**Why not a more complex model?**
With a small dataset a linear model on log-price is interpretable, fast, and
avoids overfitting. Complexity can be added incrementally (see §3).

**Data:**
[Describe your dataset here — e.g. "Ames Housing dataset (1 460 transactions)"
or "DVF open data, département XX, 2024–2025"]

**Training set size:** n = [X] transactions after filtering
**Validation approach:** [e.g. 80/20 train-test split, RMSE on log-price]

---

## 3. Areas of Improvement

| Area | Current state | Next step |
|---|---|---|
| **Data** | Small / synthetic dataset | Use a richer open dataset (DVF, Ames, etc.) |
| **Model** | OLS linear regression | Try gradient boosting (XGBoost, LightGBM) |
| **Features** | Surface + rooms only | Add location, floor, energy rating, build year |
| **Validation** | Manual testing | Add unit tests (`pytest`) + CI via GitHub Actions |
| **Monitoring** | None | Log predictions; detect drift over time |
| **Deployment** | Local Docker only | Host on a serverless platform (Render, Railway…) |
| **History** | No persistence | Store queries in SQLite; export to `.xlsx` |
| **UI** | API only | Add a minimal frontend (HTML form or Streamlit) |

---

## Project Structure
```

├── app/
│ ├── main.py          # FastAPI entrypoint
│ ├── scoring.py       # Model inference & labelling
│ └── validation.py    # Input validation (HTTP 422)
├── train\_model.py     # Offline training → artifacts/model.json
├── artifacts/
│ └── model.json       # Serialised model coefficients
├── Dockerfile
├── pyproject.toml
└── README.md
```

---

## Quick Start
```bash
# Install dependencies
pip install -e .

# Train the model (offline)
python train_model.py --csv your_data.csv --out artifacts/model.json

# Run the API
uvicorn app.main:app --reload --port 8000
# → http://127.0.0.1:8000/score?surface=60&nb_room=2&price=200000

# Docker
docker build -t house-price-api .
docker run --rm -p 8001:8000 house-price-api
```

---

*Project created as part of an MLOps course assignment.*
