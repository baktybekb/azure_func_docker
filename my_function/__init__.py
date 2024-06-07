import logging
import azure.functions as func
from my_function.settings import settings
from pydantic import BaseModel


def main(mytimer: func.TimerRequest) -> None:
    logging.info(f"API Key: {settings.api_key}")
    logging.info('Buuhaaaaaaaaaaaaaaaaaaaaaaa')
    logging.info('Docker image deployment version')
