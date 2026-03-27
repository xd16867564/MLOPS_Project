from pydantic import BaseModel, Field, validator

class ScoreRequest(BaseModel):
    city: str = Field(..., description="City name (uppercase), e.g. PARIS")
    surface: float = Field(..., gt=0, description="Surface area in m²")
    price: float = Field(..., gt=0, description="Asked price in €")

    @validator("city")
    def city_uppercase(cls, v):
        return v.strip().upper()
