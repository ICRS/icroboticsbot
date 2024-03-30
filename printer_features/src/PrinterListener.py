import base64
from enum import Enum
from io import BytesIO

import discord
import requests
from PIL import Image

__all__ = ['PrinterListener', 'State']


class State(Enum):
    IDLE = "IDLE"
    PREPARING = "PREPARE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSE"
    FINISHED = "FINISH"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN


class Command(Enum):
    LET_ME_KNOW = "letmeknow"
    TIMELAPSE = "timelapse"

    @classmethod
    def _missing_(cls, value):
        return cls.LET_ME_KNOW


class PrinterListener:
    def __init__(self, printer_url: str, timelapse_speed: float = 1.0):
        self.printer_url = printer_url
        self.__timelapse_speed: float = timelapse_speed
        self.__timelapsed: bool = False
        self.__users: dict[Command, list[discord.User]] = {
            Command.LET_ME_KNOW: [],
            Command.TIMELAPSE: []
        }
        self.__timelapse_frames: list[BytesIO] = []
        self.__printer_state: list[State] = []

    def add_user(self, user: discord.User, comm: Command) -> bool:
        self.__users[Command(comm)].append(user)
        return user in self.__users[Command(comm)]

    def remove_user(self, user: discord.User, comm: Command) -> bool:
        self.__users[Command(comm)].remove(user)
        return user not in self.__users[Command(comm)]

    def user_in(self, user: discord.User, comm: Command) -> bool:
        return user in self.__users[Command(comm)]

    def clear_users(self, comm: Command) -> bool:
        self.__users[Command(comm)].clear()
        return len(self.__users[Command(comm)]) == 0

    def notify_users(self, comm: Command) -> str:
        discord_msg = f"Printer {self.printer_url.split(".")[0]} is done! "
        for user in self.__users[Command(comm)]:
            discord_msg += user.mention + " "
        return discord_msg

    def enable_timelapse(self, user: discord.User) -> bool:
        self.__timelapsed = True
        if not self.user_in(user, Command.TIMELAPSE):
            self.add_user(user, Command.TIMELAPSE)
        return True

    def disable_timelapse(self, user: discord.User) -> bool:
        if self.user_in(user, Command.TIMELAPSE):
            self.remove_user(user, Command.TIMELAPSE)
        if len(self.__users[Command.TIMELAPSE]) == 0:
            self.__timelapsed = False
            return True
        return False

    def is_timelapsed(self) -> bool:
        return self.__timelapsed

    def create_timelapse(self) -> bytes:
        im: list[Image.Image] = []
        for frame in self.__timelapse_frames:
            im.append(Image.open(frame))

        with BytesIO() as buffer:
            im[0].save(buffer, format='GIF', save_all=True,
                       append_images=im[1:], optimize=False,
                       duration=int((1000 * 1/self.__timelapse_speed)/6),
                       loop=0)
            buffer.seek(0)
            return buffer.getbuffer().tobytes()

    async def send_timelapse(self, timelapse: bytes) -> None:
        for user in self.__users[Command.TIMELAPSE]:
            await user.send(file=discord.File(timelapse, 'timelapse.gif'))
        self.clear_users(Command.TIMELAPSE)

    def append_frame(self):
        if self.__timelapsed:
            frame = self.__get_frame()
            if frame is not None:
                self.__timelapse_frames.append(BytesIO(base64.b64decode(frame)))

    def is_done(self) -> bool:
        self.__printer_state.append(self.__get_state())

        if len(self.__printer_state) < 2:
            return False
        if self.__printer_state[-1] == State.FINISHED and \
                self.__printer_state[-2] == State.RUNNING:
            return True
        return False

    def __get_remaining_time(self) -> int:
        response = requests.get(f"http://{self.printer_url}/printer/status/time")
        if response.status_code != 200:
            return -1
        r = response.json()
        return r['time'] if 'time' in r else -1

    def __get_percentage(self) -> int:
        response = requests.get(
            f"http://{self.printer_url}/printer/status/percentage")
        if response.status_code != 200:
            return -1
        r = response.json()
        return r['percentage'] if 'percentage' in r else -1

    def __get_frame(self) -> str | None:
        response = requests.get(f"http://{self.printer_url}/printer/camera")
        if response.status_code != 200:
            return None
        r: dict = response.json()
        return r['frame'].get("body", "") if 'frame' in r else None

    def __get_state(self) -> State:
        response = requests.get(f"http://{self.printer_url}/printer/status/state")
        if response.status_code != 200:
            return State.UNKNOWN
        r: dict = response.json()
        return State(r.get("state", "IDLE"))
