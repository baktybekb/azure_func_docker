import logging
import azure.functions as func
from pydantic import BaseModel
from fastapi import Response


class MyModel(BaseModel):
    name: str
    age: int


def main(req: func.HttpRequest, timer: func.TimerRequest) -> func.HttpResponse:
    logging.info('BAHAAAAAAAAAAAAAAAAAA')
    print('BAHAAAAAAAAAAAAAAAAAAAAAAAAAA-------------')
    if req:
        logging.info('Python HTTP trigger function processed a request.')

        name = req.params.get('name')
        if not name:
            try:
                req_body = req.get_json()
            except ValueError:
                pass
            else:
                name = req_body.get('name')

        if name:
            return func.HttpResponse(f"Hello, {name}!")
        else:
            return func.HttpResponse(
                "Please pass a name on the query string or in the request body",
                status_code=400
            )

    if timer:
        logging.info('Python Timer trigger function ran at %s', timer.schedule_status.last)
        data = {"name": "John Doe", "age": 30}
        my_model = MyModel(**data)
        return func.HttpResponse(content=my_model.json(), media_type="application/json")

    return func.HttpResponse("Invalid trigger", status_code=400)
