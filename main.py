from typing import Optional
import os
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

app = FastAPI()

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://cruzaelcharco.com",
        "https://www.cruzaelcharco.com",
        "https://gerardorangel20-creator.github.io",
    ],
    allow_methods=["GET"],
    allow_headers=["*"],
)

TOKEN = os.environ.get("TP_TOKEN")

@app.get("/")
def salud():
    return {"estado": "ok"}

@app.get("/buscar")
@limiter.limit("60/minute")
async def buscar(request: Request, origen: str, destino: str, fecha: str, regreso: Optional[str] = None):
    if not TOKEN:
        raise HTTPException(500, "Token no configurado")

    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    params = {
        "origin": origen.upper(),
        "destination": destino.upper(),
        "departure_at": fecha,
        "currency": "eur",
        "sorting": "price",
        "limit": 10,
        "token": TOKEN,
    }

    # Si viene mes de regreso, pedimos ida y vuelta; si no, solo ida
    if regreso:
        params["return_at"] = regreso
        params["one_way"] = "false"
    else:
        params["one_way"] = "true"

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=20)

    if r.status_code != 200:
        raise HTTPException(502, "Error consultando Travelpayouts")

    return r.json()

@app.get("/calendario")
@limiter.limit("60/minute")
async def calendario(request: Request, origen: str, destino: str, fecha: str, regreso: Optional[str] = None):
    """Precio más barato por cada día del mes (para el gráfico de barras)."""
    if not TOKEN:
        raise HTTPException(500, "Token no configurado")

    url = "https://api.travelpayouts.com/aviasales/v3/grouped_prices"
    params = {
        "origin": origen.upper(),
        "destination": destino.upper(),
        "departure_at": fecha,
        "group_by": "departure_at",
        "currency": "eur",
        "token": TOKEN,
    }

    if regreso:
        params["return_at"] = regreso

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=20)

    if r.status_code != 200:
        raise HTTPException(502, "Error consultando Travelpayouts")

    return r.json()

@app.get("/chollos")
@limiter.limit("60/minute")
async def chollos(request: Request, origen: str = "MAD"):
    """Vuelos más baratos que salen de una ciudad hacia cualquier destino."""
    if not TOKEN:
        raise HTTPException(500, "Token no configurado")

    url = "https://api.travelpayouts.com/v1/city-directions"
    params = {
        "origin": origen.upper(),
        "currency": "eur",
        "token": TOKEN,
    }

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=20)

    if r.status_code != 200:
        raise HTTPException(502, "Error consultando Travelpayouts")

    return r.json()
