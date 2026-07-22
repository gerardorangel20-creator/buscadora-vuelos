import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

TOKEN = os.environ.get("TP_TOKEN")

@app.get("/")
def salud():
    return {"estado": "ok"}

@app.get("/buscar")
async def buscar(origen: str, destino: str, fecha: str):
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

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=20)

    if r.status_code != 200:
        raise HTTPException(502, "Error consultando Travelpayouts")

    return r.json()

@app.get("/calendario")
async def calendario(origen: str, destino: str, fecha: str):
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

    async with httpx.AsyncClient() as client:
        r = await client.get(url, params=params, timeout=20)

    if r.status_code != 200:
        raise HTTPException(502, "Error consultando Travelpayouts")

    return r.json()
