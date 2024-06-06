from pydantic import BaseModel
from fastapi import Response


class MyModel(BaseModel):
    name: str
    age: int


def main(req):
    data = req.get_json()
    my_model = MyModel(**data)

    return Response(content=my_model.json(), media_type="application/json")
