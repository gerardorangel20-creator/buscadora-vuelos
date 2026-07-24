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
async def buscar(origen: str, destino: str, fecha: str, regreso: str = None):
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
async def calendario(origen: str, destino: str, fecha: str, regreso: str = None):
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
async def chollos(origen: str = "MAD"):
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
