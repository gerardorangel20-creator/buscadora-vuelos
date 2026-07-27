# buscadora-vuelos

Buscador de vuelos baratos publicado en [cruzaelcharco.com](https://cruzaelcharco.com). Combina una web estática con una API en FastAPI que consulta precios a través de [Travelpayouts](https://www.travelpayouts.com/).

## Estructura

- `index.html`, `como-encontrar-vuelos-baratos.html` — frontend estático (se sirve vía GitHub Pages, ver `CNAME`).
- `main.py` — API en FastAPI que hace de proxy hacia Travelpayouts.
- `requirements.txt` — dependencias de Python del backend.

## Backend (API)

### Requisitos

```bash
pip install -r requirements.txt
```

### Configuración

La API necesita un token de Travelpayouts en la variable de entorno `TP_TOKEN`:

```bash
export TP_TOKEN="tu_token_aqui"
```

### Ejecutar en local

```bash
uvicorn main:app --reload
```

### Endpoints

| Método | Ruta          | Descripción                                             |
|--------|---------------|----------------------------------------------------------|
| GET    | `/`           | Comprobación de estado (health check).                   |
| GET    | `/buscar`     | Precios de vuelos para un origen, destino y fecha dados.  |
| GET    | `/calendario` | Precio más barato por día del mes (para el gráfico).      |
| GET    | `/chollos`    | Vuelos más baratos desde una ciudad de origen.            |

Todos requieren `origen`/`destino` en formato de código IATA.
