from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx

app = FastAPI()

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def home_page(request: Request) -> templates.TemplateResponse:
    stock_data = {
        "quote_option": "INDEX",
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
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "error_message": "Symbol not found or HTML structure changed",
                        "status_code": e.response.status_code,
                        "request": request,
                    },
                )
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "error_message": "Error fetching data from the quote service",
                        "status_code": e.response.status_code,
                        "request": request,
                    },
                )
        except httpx.RequestError as e:
            return templates.TemplateResponse(
                "error.html",
                {
                    "error_message": "Request to quote service failed",
                    "status_code": 500,
                    "request": request,
                },
            )
        except Exception as e:
            return templates.TemplateResponse(
                "error.html",
                {
                    "error_message": "An unexpected error occurred",
                    "status_code": 500,
                    "request": request,
                },
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
async def fetch_page(request: Request) -> templates.TemplateResponse:
    return templates.TemplateResponse("fetch.html", {"request": request})


@app.post("/fetch/")
async def fetch(
    request: Request,
    quote_option: str = Form(...),
    symbol: str = Form(...),
) -> templates.TemplateResponse:

    urls = {
        "EQUITY": f"http://python-fastapi-quote:8000/equity/{symbol}",
        "INDEX": f"http://python-fastapi-quote:8000/index/{symbol}",
    }

    if quote_option not in urls:
        raise HTTPException(status_code=400, detail="Invalid quote option")

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(urls[quote_option])
            response.raise_for_status()
            fetched_data = response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "error_message": "Symbol not found or HTML structure changed",
                        "status_code": e.response.status_code,
                        "request": request,
                    },
                )
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "error_message": "Error fetching data from the quote service",
                        "status_code": e.response.status_code,
                        "request": request,
                    },
                )
        except httpx.RequestError as e:
            return templates.TemplateResponse(
                "error.html",
                {
                    "error_message": "Request to quote service failed",
                    "status_code": 500,
                    "request": request,
                },
            )
        except Exception as e:
            return templates.TemplateResponse(
                "error.html",
                {
                    "error_message": "An unexpected error occurred",
                    "status_code": 500,
                    "request": request,
                },
            )

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "name": fetched_data.get("name"),
            "price": fetched_data.get("price"),
        },
    )


@app.post("/search/")
async def search(
    request: Request,
    search_str: str = Form(...),
) -> templates.TemplateResponse:

    url = f"http://python-fastapi-search:8002/search/{search_str}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            fetched_data = response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "error_message": "Data not found",
                        "status_code": e.response.status_code,
                        "request": request,
                    },
                )
            else:
                return templates.TemplateResponse(
                    "error.html",
                    {
                        "error_message": "Error fetching data",
                        "status_code": e.response.status_code,
                        "request": request,
                    },
                )
        except httpx.RequestError as e:
            return templates.TemplateResponse(
                "error.html",
                {
                    "error_message": "Request to search service failed",
                    "status_code": 500,
                    "request": request,
                },
            )
        except Exception as e:
            return templates.TemplateResponse(
                "error.html",
                {
                    "error_message": "An unexpected error occurred",
                    "status_code": 500,
                    "request": request,
                },
            )

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "search_result": fetched_data,
        },
    )


if __name__ == "__main__":
    uvicorn.run(app, port=8001, host="0.0.0.0")
