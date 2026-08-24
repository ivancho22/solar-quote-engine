from fastapi import FastAPI
from app.schemas.quote import QuoteRequest, QuoteResponse
from app.core.calculator import calculate_solar_quote

app = FastAPI(
    title="Solar Box Quoting Engine",
    description="Motor de cotización instantánea de sistemas solares en gabinete todo en uno",
    version="1.0.0"
)

@app.get("/")
def health_check():
    return {"status": "ok", "service": "solar-quote-engine"}

@app.post("/api/v1/quote", response_model=QuoteResponse)
def get_quote(request: QuoteRequest):
    return calculate_solar_quote(request)