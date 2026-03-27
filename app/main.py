from fastapi import FastAPI
from app.validation import ScoreRequest
from app.scoring import compute_score
from app.scoring import compute_score, compare_cities

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