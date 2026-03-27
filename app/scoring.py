import csv
import os
from app.validation import ScoreRequest

# Load city benchmark data once at startup
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/city_price_benchmark.csv")

def load_benchmark() -> dict:
    benchmark = {}
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                val = row["avg_price_m2"].strip()
                if val:
                    benchmark[row["Commune"]] = float(val)
            except ValueError:
                pass  # skip rows with invalid price
    return benchmark

BENCHMARK = load_benchmark()

LABEL_THRESHOLDS = {
    "underpriced": 0.90,
    "overpriced": 1.10,
}

def compute_score(req: ScoreRequest) -> dict:
    city = req.city
    if city not in BENCHMARK:
        return {
            "error": f"City '{city}' not found in benchmark data.",
            "hint": "Use uppercase French city name, e.g. PARIS, LYON, TOULON"
        }

    avg_price_m2 = BENCHMARK[city]
    expected_price = avg_price_m2 * req.surface
    ratio = req.price / expected_price
    gap_euros = round(req.price - expected_price, 2)
    gap_pct = round((ratio - 1) * 100, 1)

    if ratio < LABEL_THRESHOLDS["underpriced"]:
        label = "underpriced"
    elif ratio > LABEL_THRESHOLDS["overpriced"]:
        label = "overpriced"
    else:
        label = "fair"

    score = round(max(0.0, 1.0 - abs(ratio - 1.0)), 4)

    return {
        "city": city,
        "surface_m2": req.surface,
        "asked_price": req.price,
        "expected_price": round(expected_price, 2),
        "avg_price_m2_city": avg_price_m2,
        "price_ratio": round(ratio, 4),
        "gap_euros": gap_euros,
        "gap_pct": gap_pct,
        "label": label,
        "score": score,
    }
