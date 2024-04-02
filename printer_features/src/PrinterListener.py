#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

import time
import base64
from enum import Enum
from io import BytesIO

import discord
import requests
from PIL import Image

from src.utils import print  # pylint: disable=redefined-builtin, import-error

__all__ = ['PrinterListener', 'State', 'Command']

LOGS = True
ERRORS = True
DEBUG = False

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
    NOTIFY = "Notify"
    TIMELAPSE = "Timelapse"

    @classmethod
    def _missing_(cls, value):
        return cls.NOTIFY


class PrinterListener:
    def __init__(self, printer_name: str,
                 printer_url: str,
                 timelapse_speed: float = 1.0):

        # Debugging purposes
        # print(requests.get(f"http://localhost:6000/printer/status/state").json()) if DEBUG else None
        if DEBUG:
            self.printer_url = "localhost:6000"
        else:
            self.printer_url = printer_url
        self.printer_name = printer_name

        self.__timelapse_speed: float = timelapse_speed
        self.__timelapsed: bool = False

        self.__users: dict[Command, set[discord.User]] = {
            Command.NOTIFY: set(),
            Command.TIMELAPSE: set()
        }

        self.__default_image = Image.open("./src/no_image.jpg")

        self.__timelapse_frames: list[BytesIO] = []
        self.__printer_state: list[State] = []

    def get_state(self) -> State:
        return State(self.__printer_state[-1]).value if \
            len(self.__printer_state) > 0 else State.UNKNOWN.value

    def get_users(self, comm: Command) -> set[discord.User]:
        print(self.printer_name, f"Getting users in {comm}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        return self.__users[Command(comm)]

    def add_user(self, user: discord.User, comm: Command) -> bool:
        print(self.printer_name, f"Adding user {user} to {comm}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        self.__users[Command(comm)].add(user)
        return True

    def remove_user(self, user: discord.User, comm: Command) -> bool:
        print(self.printer_name, f"Removing user {user} from {comm}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        self.__users[Command(comm)].discard(user)
        return True

    def user_in(self, user: discord.User, comm: Command) -> bool:
        print(self.printer_name, f"Checking if user {user} is in {comm}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        return user in self.__users[Command(comm)]

    async def clear_users(self, comm: Command) -> bool:
        print(self.printer_name, f"Clearing users from {comm}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        self.__users[Command(comm)].clear()
        return len(self.__users[Command(comm)]) == 0

    async def notify_users(self, comm: Command) -> bool:
        print(self.printer_name, f"Notifying users in {comm}") if LOGS else None
        for user in self.__users[Command(comm)]:
            print(self.printer_name, f"Sending message to {user}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
            await user.send(f"Printer {self.printer_name} is finished.")
        return True

    def start_timelapse(self) -> bool:
        print(self.printer_name, "Starting timelapse") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        self.__timelapsed = True
        return True

    def stop_timelapse(self) -> bool:
        print(self.printer_name, "Stopping timelapse") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        self.__timelapsed = False
        return False

    def enable_timelapse(self, user: discord.User) -> bool:
        print(self.printer_name, f"Enabling timelapse for {user}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        self.__timelapsed = True
        if not self.user_in(user, Command.TIMELAPSE):
            self.add_user(user, Command.TIMELAPSE)
        return True

    def disable_timelapse(self, user: discord.User) -> bool:
        print(self.printer_name, f"Disabling timelapse for {user}") if LOGS else None  # noqa # pylint: disable=expressions-not-assigned
        if self.user_in(user, Command.TIMELAPSE):
            self.remove_user(user, Command.TIMELAPSE)
        return False

    def is_timelapsed(self) -> bool:
        return self.__timelapsed

    def create_timelapse(self) -> bytes|None:
        print(self.printer_name, "Creating timelapse") if LOGS else None  # noqa
        im: list[Image.Image] = []
        for frame in self.__timelapse_frames:
            im.append(Image.open(frame))

        with BytesIO() as buffer:
            if len(im) == 0:
                im.append(self.__default_image)
            im[0].save(buffer, format='GIF', save_all=True,
                    append_images=im[1:], optimize=False,
                    duration=int((1000 * 1/self.__timelapse_speed)/6),
                    loop=0)
            buffer.seek(0)
            return buffer.getbuffer().tobytes()

    async def send_timelapse(self, timelapse: bytes) -> None:
        print(self.printer_name, "Sending timelapse") if LOGS else None  # noqa
        filename = f"{self.printer_name}_timelapse_{time.strftime(time.time(), '%Y%m%d%H%M%S')}.gif"
        for user in self.__users[Command.TIMELAPSE]:
            try:
                with BytesIO(timelapse) as timelapse:
                    await user.send(file=discord.File(fp=timelapse, filename=filename))
            except Exception as e:
                print(self.printer_name, f"Error sending timelapse: {e}") if ERRORS else None

    def append_frame(self):
        frame = self.__get_frame()
        if frame is not None:
            self.__timelapse_frames.append(BytesIO(base64.b64decode(frame)))

    def update_state(self):
        self.__printer_state.append(self.__get_state())
        print(self.printer_name, ", ".join(state.value for state in self.__printer_state)) if LOGS else None  # noqa

    def is_starting(self) -> bool:
        if len(self.__printer_state) > 0:
            if self.__printer_state[-1] == State.PREPARING:
                return True
            if len(self.__printer_state) < 2:
                return False
            if self.__printer_state[-1] == State.RUNNING and \
                    self.__printer_state[-2] == State.IDLE:
                return True
        return False

    def is_done(self) -> bool:
        if len(self.__printer_state) < 2:
            return False
        if self.__printer_state[-1] == State.FINISHED and \
                self.__printer_state[-2] == State.RUNNING:
            return True
        return False

    def is_reset(self) -> bool:
        if len(self.__printer_state) < 2:
            return False
        if self.__printer_state[-1] == State.IDLE or \
                self.__printer_state[-1] == State.FINISHED:
            return True
        return False

    def __get_remaining_time(self) -> int:
        response: requests.Response = {}
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/time",
                timeout=30)
        except Exception as e:
            print(self.printer_name, f"Error getting remaining time: {e}") if ERRORS else None  # noqa # pylint: disable=expression-not-assigned
        if response.status_code != 200:
            return -1
        r: dict = dict(response.json())
        return r.get("time", -1)

    def __get_percentage(self) -> int:
        response: requests.Response = {}
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/percentage",
                timeout=30)
        except Exception as e:
            print(self.printer_name, f"Error getting percentage: {e}") if ERRORS else None  # noqa # pylint: disable=expression-not-assigned
        if response.status_code != 200:
            return -1
        r: dict = dict(response.json())
        return r.get("percentage", -1)

    def __get_frame(self) -> str | None:
        response: requests.Response = requests.Response()
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/camera",
                timeout=30)
        except Exception as e:
            print(self.printer_name, f"Error getting frame: {e}") if ERRORS else None  # noqa # pylint: disable=expression-not-assigned
        if response.status_code != 200:
            return None
        r: dict[str, dict] = dict(response.json())
        if "error" in r:
            print(self.printer_name, f"Error getting frame: {r.get('error', 'error')}") if ERRORS else None  # noqa # pylint: disable=expression-not-assigned
            return None
        return r.get("frame", {}).get("body", None)

    def __get_state(self) -> State:
        response: requests.Response = requests.Response()
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/state",
                timeout=30)
        except Exception as e:
            print(self.printer_name, f"Error getting status: {e}") if ERRORS else None  # noqa # pylint: disable=expression-not-assigned
        if response.status_code != 200:
            return State.UNKNOWN
        r: dict = dict(response.json())
        return State(r.get("state", "IDLE"))
