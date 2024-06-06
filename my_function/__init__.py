import logging
import azure.functions as func
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field
from typing import Callable

app = FastAPI()


class Item(BaseModel):
    name: str = Field(..., example="Item name")
    description: str = Field(..., example="Item description")


@app.get("/items")
async def read_item(name: str):
    return {"name": name}


@app.post("/items")
async def create_item(item: Item):
    return item


# Azure Function HttpTrigger
def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    def fastapi_app(req: Request) -> Callable:
        return app

    return func.AsgiMiddleware(fastapi_app).handle(req, context)
