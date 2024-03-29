import base64
from io import BytesIO

import atexit
from PIL import Image
from discord_webhook import DiscordWebhook, DiscordEmbed

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

        self.printer_farm = PrinterFarm(printer_names, printer_endpoint_suffix)
        atexit.register(self.delete_message)

        self.executed = False

    def send_message(self, printer_name: str) -> None:
        try:
            remaining_time = self.printer_farm.get_remaining_time(printer_name)
            percentage = self.printer_farm.get_percentage(printer_name)
            frame = self.printer_farm.get_frame(printer_name)

            fname = f"{printer_name}_stream.png"

            prog_length = self.prog_length
            progress_text = f"Progress: {' '*int(prog_length-12)}{percentage}%"
            progress_bar = "=" * int(percentage/100 * prog_length)
            unprogressed = "-" * int(prog_length - len(progress_bar))

            remaining_time = "> Time remaining: " + \
                " "*int(prog_length-23-len(str(remaining_time))) + \
                str(remaining_time) + " mins"

            embed_desc = (f"```md\n{remaining_time}\n" +
                          f"{progress_text}\n{progress_bar+unprogressed}\n" +
                          "```") \
                if remaining_time != 0 \
                    else f"```ps\n[{'No printing in progress'.center(prog_length-2, ' ')}]\n```"  # noqa

            try:
                im = Image.open(BytesIO(base64.b64decode(frame)))
            except Exception as e:
                print(str(e))
                im = Image.open("./src/no_image.jpg")

            with BytesIO() as image_binary:
                im.save(image_binary, 'PNG')
                image_binary.seek(0)

                embed = DiscordEmbed(title=printer_name,
                                     description=embed_desc,     # noqa # pylint: disable=line-too-long
                                     color=242424)
                self.webhook.add_embed(embed)
                self.webhook.add_file(file=image_binary.getbuffer().tobytes(),
                                      filename=fname)
                embed.set_image(url=f'attachment://{fname}')

        except Exception as e:
            print(str(e))

    def send_message_all(self) -> None:
        self.webhook.remove_embeds()
        for printer_name in self.printer_farm.get_printers():
            self.send_message(printer_name)
        if not self.executed:
            self.webhook.execute()
            self.executed = True
        else:
            self.webhook.edit()

    def delete_message(self) -> None:
        self.webhook.delete()

