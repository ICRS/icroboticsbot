from src.printer_gateway import PrinterGateway

class PrinterFarm:
    
    def __init__(self, printer_names : list[str], printer_suffix : str) -> None:
        self.printers = { name: PrinterGateway(name + printer_suffix) for name in printer_names }
    
    def printer_exists(func):
        def wrapper(self, printer_name):
            if printer_name not in self.printers:
                raise Exception("Printer not found")
            return func(self, printer_name)
        return wrapper

    @printer_exists
    def get_remaining_time(self, printer_name: str) -> int:        
        print("Printer name: ", printer_name)
        return self.printers[printer_name].get_remaining_time()
    
    @printer_exists    
    def get_percentage(self, printer_name : str) -> int:
        print("Printer name: ", printer_name)
        return self.printers[printer_name].get_percentage()
    
    def get_printers(self) -> list[str]:
        return list(self.printers.keys())
    
    