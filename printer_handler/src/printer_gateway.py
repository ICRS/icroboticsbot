import requests

class PrinterGateway:
    """
    Printer Gateway Class to query REST endpoints to get information about the printers
    """
    def __init__(self, printer_url):
        self.printer_url = printer_url
    
    def get_remaining_time(self) -> int:
        response = requests.get(f"{self.printer_url}/printer/status/time")
        if response.status_code != 200:
            return -1
        r = response.json()
        return r['time'] if 'time' in r else -1
    
    def get_percentage(self) -> int:
        response = requests.get(f"{self.printer_url}/printer/status/percentage")
        if response.status_code != 200:
            return -1
        r = response.json()
        return r['percentage'] if 'percentage' in r else -1