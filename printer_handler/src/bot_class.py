import base64
from io import BytesIO

import atexit
import logging
from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed
from bambulabs_api import GcodeState

from src.printer_farm import PrinterFarm


class PrinterWebhook:
    def __init__(self, webhook_url: str,
                 printer_names: list[str],
                 printer_endpoint_suffix: str,
                 prog_length: int = 45) -> None:
        self.prog_length = prog_length
        self.webhook_url = webhook_url
        self.webhook = DiscordWebhook(url=self.webhook_url,
                                      username="Printer Bot",
                                      id="Printer Bot", )

        self.__default_image = Image.open("./src/no_image.jpg")

        self.printer_farm = PrinterFarm(printer_names, printer_endpoint_suffix)
        atexit.register(self.delete_message)

        self.executed = False

    def send_message(self, printer_name: str) -> None:
        """
        Sends a message to the discord webhook with the printer's state
        and image

        Parameters
        ----------
        printer_name : str
            The name of the printer to send the message for
        """
        skip_embed = False
        embed_desc = ""
        try:
            state = self.printer_farm.get_state(printer_name)
            if state == GcodeState.UNKNOWN:
                embed_desc = f"```ps\n[{'Unknown printer state'.center(self.prog_length-2, ' ')}]\n```"         # noqa

            elif state == GcodeState.IDLE:
                embed_desc = f"```asciidoc\n {'No print in progress'.center(self.prog_length-4, ' ')}:: \n```"   # noqa

            elif state == GcodeState.PREPARE:
                embed_desc = f"```yaml\n[{'Preparing print'.center(self.prog_length-2, ' ')}]\n```"              # noqa

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

            elif state == GcodeState.FINISHED:
                embed_desc = f"```asciidoc\n {'Print finished'.center(self.prog_length-4, ' ')}:: \n```"              # noqa

            else:
                embed_desc = f"```ps\n[{'Unknown printer state'.center(self.prog_length-2, ' ')}]\n```"         # noqa

            frame = self.printer_farm.get_frame(printer_name)
            fname = f"{printer_name}_stream.png"

<<<<<<< HEAD
            if not skip_embed:
                try:
                    im = Image.open(BytesIO(base64.b64decode(frame)))
=======
            prog_length = self.prog_length
            progress_text = f"Progress: {' '*int(prog_length-12)}{percentage}%"
            progress_bar = "=" * int(percentage/100 * prog_length)
            unprogressed = "-" * int(prog_length - len(progress_bar))
>>>>>>> refs/rewritten/master-10

                except Exception as e:
                    im = self.__default_image
                    logging.error(
                        f"Error in opening image for {printer_name}: {str(e)}"
                    )

<<<<<<< HEAD
                with BytesIO() as image_binary:
                    im.save(image_binary, 'PNG')
                    image_binary.seek(0)
=======
            embed_desc = (f"```md\n{remaining_time}\n" +
                          f"{progress_text}\n{progress_bar+unprogressed}\n" +
                          "```") \
                if remaining_time != 0 \
                    else f"```ps\n[{'No printing in progress'.center(prog_length-2, ' ')}]\n```"  # noqa
>>>>>>> refs/rewritten/master-10

                    embed = DiscordEmbed(title=printer_name,
                                         description=embed_desc,     # noqa # pylint: disable=line-too-long
                                         color=242424)
                    self.webhook.add_embed(embed)
                    self.webhook.add_file(file=image_binary.getbuffer().tobytes(),      # noqa
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
            self.webhook.execute()
            self.executed = True
        else:
            self.webhook.edit()

    def delete_message(self) -> None:
        """
        Deletes the message from the discord webhook
        """
        self.webhook.delete()
