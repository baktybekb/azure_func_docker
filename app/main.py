from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str = Field(..., example="Item name")
    description: str = Field(..., example="Item description")


@app.get("/items/")
async def read_item(name: str = Query(..., min_length=3, max_length=50)):
    return {"name": name}


@app.post("/items/")
async def create_item(item: Item):
    return item
