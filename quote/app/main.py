from typing import Dict, Union
from fastapi import FastAPI, HTTPException
import uvicorn
import httpx
from bs4 import BeautifulSoup

GOOGLE_FINANCE = "https://www.google.com/finance/quote/"
EXCHANGE = {
    "index": "INDEXNSE",
    "nse": "NSE",
}

app = FastAPI()


@app.get("/")
async def read_root():
    return {"Message": "Hello World"}


@app.get("/index/{symbol}")
async def get_index_price(symbol: str) -> Dict[str, Union[str, None]]:
    url = GOOGLE_FINANCE + symbol + f":{EXCHANGE['index']}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch data from Google Finance",
        )

    soup = BeautifulSoup(response.text, "lxml")

    try:
        name = soup.find("div", class_="zzDege").text
        price = soup.find("div", class_="YMlKec fxKbKc").text
    except AttributeError:
        raise HTTPException(
            status_code=404, detail="Symbol not found or HTML structure changed"
        )

    return {"name": name, "price": price}


@app.get("/nse/{symbol}")
async def get_index_price(symbol: str) -> Dict[str, Union[str, None]]:
    url = GOOGLE_FINANCE + symbol + f":{EXCHANGE['nse']}"

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch data from Google Finance",
        )

    soup = BeautifulSoup(response.text, "lxml")

    try:
        name = soup.find("div", class_="zzDege").text
        price = soup.find("div", class_="YMlKec fxKbKc").text
    except AttributeError:
        raise HTTPException(
            status_code=404, detail="Symbol not found or HTML structure changed"
        )

    return {"name": name, "price": price}


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
