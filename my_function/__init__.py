import logging
import azure.functions as func
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field
from typing import Callable

app = FastAPI()


class Item(BaseModel):
    name: str = Field(..., example="Item name")
    description: str = Field(..., example="Item description")


@app.get("/items")
async def read_item(name: str):
    logging.info(f"Received GET request with name: {name}")
    return {"name": name}


@app.post("/items")
async def create_item(item: Item):
    logging.info(f"Received POST request with item: {item}")
    return item


# Azure Function HttpTrigger
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        def fastapi_app(req: Request) -> Callable:
            return app

        return func.AsgiMiddleware(fastapi_app).handle(req, context)
    except Exception as e:
        logging.error(f"Error processing request: {e}")
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
