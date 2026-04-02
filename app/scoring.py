import csv
import os
from app.validation import ScoreRequest
import statistics

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
                pass


    upper = 70000
    cleaned = {city: p for city, p in benchmark.items() if 0 < p <= upper}

    print(f"Benchmark loaded: {len(benchmark)} cities → {len(cleaned)} after outlier removal (max: {upper} €/m²)")
    return cleaned

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

def compare_cities(cities: list[str], surface: float) -> dict:
    results = []
    not_found = []

    for city in cities:
        city = city.strip().upper()
        if city not in BENCHMARK:
            not_found.append(city)
            continue
        avg_price_m2 = BENCHMARK[city]
        expected_price = round(avg_price_m2 * surface, 2)
        results.append({
            "city": city,
            "avg_price_m2": avg_price_m2,
            "expected_price": expected_price,
        })

    # sort cheapest to most expensive
    results.sort(key=lambda x: x["expected_price"])

    return {
        "surface_m2": surface,
        "comparison": results,
        "not_found": not_found,
        "cheapest": results[0]["city"] if results else None,
        "most_expensive": results[-1]["city"] if results else None,
    }
