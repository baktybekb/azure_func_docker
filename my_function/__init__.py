import logging
import azure.functions as func
from pydantic import BaseModel


class MyDataModel(BaseModel):
    name: str
    age: int


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    logging.info('Bahaaaaaaaaaaaaaa')

    try:
        data = MyDataModel.parse_raw(req.get_body())
    except Exception as e:
        return func.HttpResponse(
            f"Invalid input: {e}",
            status_code=400
        )

    return func.HttpResponse(
        f"Hello {data.name}, you are {data.age} years old.",
        status_code=200
    )

