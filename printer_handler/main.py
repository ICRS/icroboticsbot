import json
import logging
import os
import signal
import time

from src.bot_class import PrinterWebhook


WEBHOOK_URL = str(os.getenv("WEBHOOK_URL")).strip()
settings = json.load(open("settings.json", "r", encoding="utf-8"))
PRINTER_NAMES = list(settings["PRINTER_NAMES"])
PRINTER_GATEWAY_ENDPOINT_SUFFIX = settings["PRINTER_GATEWAY_ENDPOINT_SUFFIX"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s -  %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

if __name__ == '__main__':
    w = PrinterWebhook(WEBHOOK_URL, PRINTER_NAMES,
                       PRINTER_GATEWAY_ENDPOINT_SUFFIX)

    signal.signal(signal.SIGINT, w.delete_message)
    signal.signal(signal.SIGTERM, w.delete_message)

    while True:
        w.send_message_all()
        time.sleep(10)

