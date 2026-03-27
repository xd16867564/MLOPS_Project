from fastapi import FastAPI
from app.validation import ScoreRequest
from app.scoring import compute_score

app = FastAPI(title="House Price Estimator API")

@app.get("/")
def root():
    return {"message": "House Price Estimator API is running. Use /score or /docs"}

@app.get("/score")
def score(city: str, surface: float, price: float):
    request = ScoreRequest(city=city, surface=surface, price=price)
    return compute_score(request)
