from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.validation import ScoreRequest
from app.scoring import compute_score, compare_cities
from app import scoring

app = FastAPI(title="House Price Estimator API")

@app.get("/")
def root():
    return {"message": "House Price Estimator API is running. Use /score or /docs"}

@app.get("/score")
def score(city: str, surface: float, price: float):
    request = ScoreRequest(city=city, surface=surface, price=price)
    return compute_score(request)

@app.get("/compare")
def compare(cities: str, surface: float):
    city_list = cities.split(",")
    if len(city_list) < 2:
        return {"error": "Please provide at least 2 cities separated by commas"}
    if len(city_list) > 10:
        return {"error": "Maximum 10 cities at once"}
    return compare_cities(city_list, surface)

@app.get("/search")
def search(q: str, limit: int = 30):
    from app import scoring
    q = q.strip().upper()
    if len(q) < 2:
        return {"results": []}
    matches = [city for city in scoring.BENCHMARK.keys() if city.startswith(q)]
    matches.sort()
    return {"results": matches[:limit]}
