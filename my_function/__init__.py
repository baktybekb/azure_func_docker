import sys
import os
import logging
from pydantic import BaseModel

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'python_packages')))


class Item(BaseModel):
    name: str
    description: str


def main(mytimer: func.TimerRequest) -> None:
    logging.info('Python timer trigger function ran at %s', mytimer.schedule_status.last)

    # Create a static dictionary
    static_data = {
        "name": "Example",
        "description": "This is an example item"
    }

    # Create an instance of the Item model
    try:
        item = Item(**static_data)
        logging.info(f'Created item: {item.name}, {item.description}')
    except ValidationError as e:
        logging.error(f'Validation error: {e}')
