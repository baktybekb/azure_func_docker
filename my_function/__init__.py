import logging
import azure.functions as func
from pydantic import BaseModel


class Item(BaseModel):
    name: str
    description: str


def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = mytimer.schedule_status.last
    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # Static dictionary
    data = {
        "name": "Baha",
        "description": "Engineer"
    }

    try:
        item = Item(**data)
        logging.info(f"Item created: {item}")
    except ValidationError as e:
        logging.error(f"Validation error: {e.json()}")

    logging.info('Timer trigger function executed successfully.')
