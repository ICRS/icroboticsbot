from src.bot_class import PrinterWebhook

import signal 

import os
import json 

import time

WEBHOOK_URL = str(os.getenv("WEBHOOK_URL")).strip()
settings = json.load(open("settings.json", "r", encoding="utf-8"))
PRINTER_NAMES = list(settings["PRINTER_NAMES"])
PRINTER_GATEWAY_ENDPOINT_SUFFIX = settings["PRINTER_GATEWAY_ENDPOINT_SUFFIX"]

if __name__ == '__main__':
    w = PrinterWebhook(WEBHOOK_URL, PRINTER_NAMES, PRINTER_GATEWAY_ENDPOINT_SUFFIX)
    
    signal.signal(signal.SIGINT, w.delete_message)
    signal.signal(signal.SIGTERM, w.delete_message)

    while True:
        w.send_message_all()
        time.sleep(15)
    
