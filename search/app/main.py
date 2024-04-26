from typing import Dict
from fastapi import FastAPI, HTTPException
import uvicorn
import httpx
from bs4 import BeautifulSoup

NSE_INDIA = "https://www.nseindia.com/"

app = FastAPI()


@app.get("/")
async def read_root() -> Dict[str, str]:
    return {"message": "Hello NSE"}


@app.get("/search/{query}")
async def get_index_price(query: str) -> Dict[str, str]:
    url = f"{NSE_INDIA}search?q={query}&type=quotes"
    headers = {"User-Agent": "Mozilla/5.0", "accept-language": "en-US,en"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)

    if response.status_code != httpx.codes.OK:
        raise HTTPException(
            status_code=response.status_code,
            detail="Failed to fetch data from NSE India",
        )

    try:
        soup = BeautifulSoup(response.text, "lxml")
        search_results = soup.find_all("div", class_="searchWrp")

        company_dict = {
            result.find("p", class_="searchDesc")
            .text.strip()
            .title(): result.find("a", href=True)
            .text.strip()
            for result in search_results
        }

    except AttributeError:
        raise HTTPException(
            status_code=httpx.codes.NOT_FOUND,
            detail="Symbol not found or HTML structure changed",
        )

    return company_dict


if __name__ == "__main__":
    uvicorn.run(app, port=8002, host="0.0.0.0")
