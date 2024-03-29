from src.printer_gateway import PrinterGateway

__all__ = ["PrinterFarm", "IDLE", "PRINTING", "PAUSED", "FINISHED", "UNKNOWN"]


IDLE = "IDLE"
PRINTING = "PRINTING"
PAUSED = "PAUSE"
FINISHED = "FINISH"
UNKNOWN = "UNKNOWN"


class PrinterFarm:
    def __init__(self, printer_names: list[str], printer_suffix: str) -> None:
        self.printers = {name: PrinterGateway(
            name + printer_suffix) for name in printer_names}
        self.__printer_cache: dict = {name: {} for name in printer_names}

    def printer_exists(func):                           # noqa # pylint: disable=missing-function-docstring, no-self-argument
        def wrapper(self, printer_name):
            if printer_name not in self.printers:
                raise Exception("Printer not found")
            return func(self, printer_name)             # noqa # pylint: disable=not-callable
        return wrapper

    @printer_exists
    def get_remaining_time(self, printer_name: str) -> int:
        print("Printer name: ", printer_name)
        remaining_time = self.printers[printer_name].get_remaining_time()
        return remaining_time if remaining_time > 0 else 0

    @printer_exists
    def get_percentage(self, printer_name: str) -> int:
        print("Printer name: ", printer_name)
        percentage = self.printers[printer_name].get_percentage()
        return percentage if percentage > 0 else 0

    @printer_exists
    def get_frame(self, printer_name: str) -> str:
        print("Printer name: ", printer_name)
        frame = self.printers[printer_name].get_frame()
        self.__printer_cache[printer_name]["frame"] = frame if frame else self.__printer_cache[printer_name]["frame"]  # noqa # pylint: disable=line-too-long
        return self.__printer_cache[printer_name]["frame"]

    @printer_exists
    def get_state(self, printer_name: str) -> str:
        print("Printer name: ", printer_name)
        state = self.printers[printer_name].get_state()
        return state if state else UNKNOWN

    def get_printers(self) -> list[str]:
        return list(self.printers.keys())
