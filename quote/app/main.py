from typing import Dict, Union
from fastapi import FastAPI, HTTPException
import uvicorn
import httpx
from bs4 import BeautifulSoup

GOOGLE_FINANCE = "https://www.google.com/finance/quote/"
QUOTE = {
    "index": "INDEXNSE",
    "equity": "NSE",
}

app = FastAPI()


@app.get("/")
async def read_root() -> Dict[str, str]:
    return {"message": "Hello Google Finance"}


async def get_price(
    symbol: str, quote_option: str
) -> Dict[str, Union[str, None]]:
    url = f"{GOOGLE_FINANCE}{symbol}:{quote_option}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except httpx.HTTPError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="Symbol not found")
            else:
                raise HTTPException(
                    status_code=500,
                    detail="Failed to fetch data from Google Finance",
                )

    soup = BeautifulSoup(response.text, "lxml")

    try:
        name = soup.find("div", class_="zzDege").text
        price = soup.find("div", class_="YMlKec fxKbKc").text
    except AttributeError:
        raise HTTPException(
            status_code=500,
            detail="Failed to parse response from Google Finance. HTML structure might have changed.",
        )

    return {"name": name, "price": price}


@app.get("/index/{symbol}")
async def get_index_price(symbol: str) -> Dict[str, Union[str, None]]:
    return await get_price(symbol, QUOTE["index"])


@app.get("/equity/{symbol}")
async def get_nse_price(symbol: str) -> Dict[str, Union[str, None]]:
    return await get_price(symbol, QUOTE["equity"])


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
