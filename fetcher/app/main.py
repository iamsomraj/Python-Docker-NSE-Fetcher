from typing import Dict, Union
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn
import httpx

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def read_root(request: Request) -> Dict[str, str]:
    stock_data = {
        "exchange": "INDEX",
        "symbol": "NIFTY_50",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"http://python-fastapi-quote:8000/index/{stock_data['symbol']}"
            )
            response.raise_for_status()
            fetched_data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Symbol not found or HTML structure changed",
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Error fetching data"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Error parsing response"
            )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "name": fetched_data.get("name"),
            "price": fetched_data.get("price"),
        },
    )


@app.get("/fetch/")
async def fetch_page(request: Request) -> Dict[str, str]:
    return templates.TemplateResponse(
        "fetch.html",
        {
            "request": request,
        },
    )


@app.post("/fetch/")
async def fetch(
    request: Request,
    exchange: str = Form(...),
    symbol: str = Form(...),
) -> Dict[str, Union[str, Dict[str, str]]]:

    urls = {
        "NSE": f"http://python-fastapi-quote:8000/nse/{symbol}",
        "INDEX": f"http://python-fastapi-quote:8000/index/{symbol}",
    }

    if exchange not in urls:
        raise HTTPException(status_code=400, detail="Invalid exchange")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(urls[exchange])
            response.raise_for_status()
            fetched_data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Symbol not found or HTML structure changed",
                )
            else:
                raise HTTPException(
                    status_code=500, detail="Error fetching data"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail="Error parsing response"
            )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "name": fetched_data.get("name"),
            "price": fetched_data.get("price"),
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8001, host="0.0.0.0")