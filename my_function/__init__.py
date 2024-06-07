import logging
import azure.functions as func
from my_function.settings import settings


def main(mytimer: func.TimerRequest) -> None:
    logging.info(f"API Key: {settings.api_key}")
    logging.info('Buuhaaaaaaaaaaaaaaaaaaaaaaa')
