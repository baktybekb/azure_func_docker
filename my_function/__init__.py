import datetime
import logging
import azure.functions as func
from pydantic import BaseModel
from fastapi import FastAPI


class Item(BaseModel):
    name: str
    description: str


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    item = Item(name="Example", description="This is a test item")
    logging.info(f"Python timer trigger function ran at {utc_timestamp}")
    logging.info(f"Item: {item.json()}")
