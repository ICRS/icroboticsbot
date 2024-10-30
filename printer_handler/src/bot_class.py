import base64
from io import BytesIO
import os

import logging
from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed
from bambulabs_api import GcodeState
import requests

from src.printer_farm import PrinterFarm
import datetime

DATABASE_ADAPTER_ENDPOINT = os.getenv("DATABASE_ADAPTER_ENDPOINT",
                                      "http://database_adapter:8000")


class PrinterWebhook:
    def __init__(self, webhook_url: str,
                 printer_names: list[str],
                 printer_endpoint_suffix: str,
                 prog_length: int = 45,
                 timeout: int = 60,
                 ) -> None:
        self.prog_length = prog_length
        self.webhook_url = webhook_url
        result = requests.get(
            DATABASE_ADAPTER_ENDPOINT + "/printer-streamer/message-id/latest")

        if result.status_code == 200:
            self.executed = True
            self.webhook = DiscordWebhook(url=self.webhook_url,
                                          username="Printer Bot",
                                          id=result.json(), )
        else:
            self.executed = False
            self.webhook = DiscordWebhook(url=self.webhook_url,
                                          username="Printer Bot",
                                          )

        self.__default_image = Image.open("./src/no_image.jpg")

        self.printer_farm = PrinterFarm(printer_names, printer_endpoint_suffix)

        # Health check
        self.timeout = timeout
        self.last_executed = datetime.datetime.now()

    def send_message(self, printer_name: str) -> None:
        """
        Sends a message to the discord webhook with the printer's state
        and image

        Parameters
        ----------
        printer_name : str
            The name of the printer to send the message for
        """
        embed_desc = ""
        try:
            state = self.printer_farm.get_state(printer_name)

            if state == GcodeState.IDLE:
                embed_desc = f"```asciidoc\n {'No print in progress'.center(self.prog_length-4, ' ')}:: \n```"   # noqa

            elif state == GcodeState.PREPARE:
                embed_desc = f"```yaml\n[\
                    {'Preparing print'.center(self.prog_length-2, ' ')}]\n```"

            elif state == GcodeState.RUNNING or state == GcodeState.PAUSE:

                remaining_time = self.printer_farm.get_remaining_time(printer_name)                             # noqa
                percentage = self.printer_farm.get_percentage(printer_name)

                progress_text = f"Progress: {' '*int(self.prog_length-11-len(str(percentage)))}{percentage}%"   # noqa
                progress_bar = "=" * int(percentage/100 * self.prog_length)
                unprogressed = "-" * int(self.prog_length - len(progress_bar))

                remaining_time = "> Time remaining: " + \
                    " "*int(self.prog_length-23-len(str(remaining_time))) + \
                    str(remaining_time) + " mins"

                embed_desc = (f"```md\n{remaining_time}\n" +
                              f"{progress_text}\n{progress_bar+unprogressed}\n" +                               # noqa
                              "```")

            elif state == GcodeState.FINISH:
                embed_desc = "```asciidoc\n" + \
                    f"{'Print finished'.center(self.prog_length-4,' ')}:: " + \
                    "\n```"

            elif state == GcodeState.FAILED:
                embed_desc = "```ps\n" + \
                    f"[{'Print Failed'.center(self.prog_length-2, ' ')}]\n```"

            else:
                logging.warning(f"Unknown printer state: {state}")
                embed_desc = f"```ps\n[" + \
                    f"{'Unknown printer state'.center(self.prog_length-2, ' ')}]\n```"      # noqa

            frame = self.printer_farm.get_frame(printer_name)
            fname = f"{printer_name}_stream.png"

            try:
                im = Image.open(BytesIO(base64.b64decode(frame)))

            except Exception as e:
                im = self.__default_image
                logging.error(
                    f"Error in opening image for {printer_name}: {str(e)}"
                )

            with BytesIO() as image_binary:
                im.save(image_binary, 'PNG')
                image_binary.seek(0)
                image_bytes = image_binary.getbuffer().tobytes()

                embed = DiscordEmbed(title=printer_name,
                                     description=embed_desc,
                                     color=242424)
                self.webhook.add_embed(embed)
                self.webhook.add_file(file=image_bytes,
                                      filename=fname)
                embed.set_image(url=f'attachment://{fname}')

        except Exception as e:
            logging.error(
                f"Error in sending message for {printer_name}: {str(e)}")

    def send_message_all(self) -> None:
        """
        Sends a message to the discord webhook with the printer's state
        and image
        """
        self.webhook.remove_embeds()
        for printer_name in self.printer_farm.get_printers():
            self.send_message(printer_name)
        if not self.executed:
            response = self.webhook.execute()
            id = self.webhook.id
            if id:
                requests.post(
                    DATABASE_ADAPTER_ENDPOINT + "/printer-streamer/message-id",
                    params={"message_id": id})
            self.executed = True
        else:
            response = self.webhook.edit()

        if response.status_code != 200:
            logging.error(f"Error in sending message: {response.text}")
        else:
            self.last_executed = datetime.datetime.now()

    def health_check(self) -> bool:
        """
        Checks if the webhook is still valid. If the last execution happened
        within the timeout successfully return True, otherwise False

        Returns
        -------
        bool
            True if the webhook is valid, False otherwise
        """
        time_ = self.last_executed + datetime.timedelta(seconds=self.timeout)
        return time_ > datetime.datetime.now()
