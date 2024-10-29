import json
import logging
import os
import threading
import time
import uvicorn

from src.bot_class import PrinterWebhook
from fastapi import FastAPI, Response, status

app = FastAPI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s [%(levelname)s]: %(message)s',
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        logging.StreamHandler()
    ])


WEBHOOK_URL = str(os.getenv("WEBHOOK_URL")).strip()
MESSAGE_ID = str(os.getenv("MESSAGE_ID")).strip()
settings = json.load(open("settings.json", "r", encoding="utf-8"))
PRINTER_NAMES = list(settings["PRINTER_NAMES"])
PRINTER_GATEWAY_ENDPOINT_SUFFIX = settings["PRINTER_GATEWAY_ENDPOINT_SUFFIX"]


w = PrinterWebhook(WEBHOOK_URL, PRINTER_NAMES,
                   PRINTER_GATEWAY_ENDPOINT_SUFFIX,
                   webhook_message_id=MESSAGE_ID)


@app.get("/healthz", status_code=200)
def health_check(response: Response):
    healthy = w.health_check()
    if not healthy:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return healthy


class BackgroundTasks(threading.Thread):
    def run(self, *args, **kwargs):
        while True:
            w.send_message_all()
            time.sleep(10)


if __name__ == '__main__':
    t = BackgroundTasks()
    t.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
