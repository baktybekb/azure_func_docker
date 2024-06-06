import logging
import azure.functions as func
from pydantic import BaseModel, ValidationError
import json


class Item(BaseModel):
    name: str
    description: str


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )

    try:
        item = Item(**req_body)
    except ValidationError as e:
        return func.HttpResponse(
            f"Validation error: {e}",
            status_code=400
        )

    return func.HttpResponse(
        json.dumps(item.dict()),
        mimetype="application/json",
        status_code=200
    )
