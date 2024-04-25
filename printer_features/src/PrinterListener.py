#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

import os
import base64
import logging
from enum import Enum
from io import BytesIO
from collections import deque

import discord
import requests
from PIL import Image
from bambulabs_api import GcodeState

DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']  # noqa  # pylint: disable=invalid-envvar-default
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()


__all__ = ['PrinterListener', 'Command']


def get_env_bool(var: str, default: bool = False) -> bool:
    """
    Retrieves a boolean value from an environment variable.

    Parameters
    ----------
    var (str): The environment variable to retrieve.
    default (bool): The default value to return if the variable is not set.

    Returns
    -------
    bool: The boolean value of the environment variable, or the default value.
    """
    return os.getenv(var, str(default)).lower() in ('true', '1', 't')


LOGS = get_env_bool("ENV_VAR", True)
ERRORS = get_env_bool("ERRORS", True)
DEBUG = get_env_bool('DEBUG', DEBUG)


class Command(Enum):
    NOTIFY = {"name": "Notify", "emoji": "🔔", "description": "Notifies you when the printer is done"}      # noqa
    TIMELAPSE = {"name": "Timelapse", "emoji": "📷", "description": "Generates a timelapse of the print"}   # noqa

    @classmethod
    def _missing_(cls, value):
        return cls.NOTIFY


class PrinterListener:
    def __init__(self, printer_name: str,
                 printer_url: str,
                 timelapse_speed: float = 1.0,
                 max_printer_states: int = 10):
        # Debugging purposes
        # print(requests.get(f"http://localhost:6000/printer/status/state").json()) if DEBUG else None  # noqa
        if DEBUG:
            self.printer_url = "localhost:6000"
        else:
            self.printer_url = printer_url
        self.printer_name = printer_name

        self.__timelapse_speed: float = timelapse_speed
        self.__timelapsed: bool = False

        self.__users: dict[Command, set[discord.User]] = {
            c: set() for c in Command
        }

        self.__default_image = Image.open("./src/no_image.jpg")

        self.__timelapse_frames: list[BytesIO] = []
        self.__printer_state: deque[GcodeState] = deque(
            maxlen=max_printer_states)

    def get_state(self) -> GcodeState:
        """
        Retrieves the current state of the printer.
        """
        return GcodeState(self.__printer_state[-1]).value if \
            self.__printer_state else GcodeState.UNKNOWN.value

    def get_users(self, comm: Command) -> set[discord.User]:
        """
        Retrieves the users in a command.

        Parameters
        ----------
        comm (Command): The command to retrieve users from.

        Returns
        -------
        set[discord.User]: The users in the command.
        """
        logging.info(f"{self.printer_name} Getting users in {comm}")  # noqa  # pylint: disable=logging-fstring-interpolation
        return self.__users[Command(comm)]

    def add_user(self, user: discord.User, comm: Command) -> bool:
        """
        Adds a user to a command.

        Parameters
        ----------
        user (discord.User): The user to add.
        comm (Command): The command to add the user to.

        Returns
        -------
        bool: True if the user was added, False otherwise.
        """
        logging.info(f"{self.printer_name} Adding user {user} to {comm}")  # noqa  # pylint: disable=logging-fstring-interpolation
        self.__users[Command(comm)].add(user)
        return True

    def remove_user(self, user: discord.User, comm: Command) -> bool:
        """
        Removes a user from a command.

        Parameters
        ----------
        user (discord.User): The user to remove.
        comm (Command): The command to remove the user from.

        Returns
        -------
        bool: True if the user was removed, False otherwise.
        """
        logging.info(f"{self.printer_name} Removing user {user} from {comm}")  # noqa  # pylint: disable=logging-fstring-interpolation
        self.__users[Command(comm)].discard(user)
        return True

    def user_in(self, user: discord.User, comm: Command) -> bool:
        """
        Checks if a user is in a command.

        Parameters
        ----------
        user (discord.User): The user to check.
        comm (Command): The command to check.

        Returns
        -------
        bool: True if the user is in the command, False otherwise.
        """
        logging.info(f"{self.printer_name} Checking if user {user} is in {comm}")  # noqa  # pylint: disable=logging-fstring-interpolation
        return user in self.__users[Command(comm)]

    async def clear_users(self, comm: Command) -> bool:
        """
        Clears the users in a command.

        Parameters
        ----------
        comm (Command): The command to clear users from.

        Returns
        -------
        bool: True if the users were cleared, False otherwise.
        """
        logging.info(f"{self.printer_name} Clearing users in {comm}")  # noqa  # pylint: disable=logging-fstring-interpolation
        self.__users[Command(comm)].clear()
        return len(self.__users[Command(comm)]) == 0

    async def notify_users(self, comm: Command) -> bool:
        """
        Notifies the users in a command.

        Parameters
        ----------
        comm (Command): The command to notify users in.

        Returns
        -------
        bool: True if the users were notified, False otherwise.
        """
        logging.info(f"{self.printer_name} Notifying users in {comm}")  # noqa  # pylint: disable=logging-fstring-interpolation
        for user in self.__users[Command(comm)]:
            try:
                logging.info(f"{self.printer_name} Sending message to {user}")  # noqa  # pylint: disable=logging-fstring-interpolation
                await user.send(f"Printer {self.printer_name} is finished.")
            except Exception as e:
                logging.error(f"{self.printer_name} Error sending message: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        return True

    def start_timelapse(self) -> bool:
        """
        Starts the timelapse process.
        """
        logging.info(f"{self.printer_name} Starting timelapse")  # noqa  # pylint: disable=logging-fstring-interpolation
        self.__timelapsed = True
        return True

    def stop_timelapse(self) -> bool:
        """
        Stops the timelapse process.
        """
        logging.info(f"{self.printer_name} Stopping timelapse")  # noqa  # pylint: disable=logging-fstring-interpolation
        self.__timelapsed = False
        self.__timelapse_frames.clear()
        return False

    def enable_timelapse(self, user: discord.User) -> bool:
        """
        Enables the timelapse process for a user.

        Parameters
        ----------
        user (discord.User): The user to enable timelapse for.

        Returns
        -------
        bool: True if timelapse was enabled, False otherwise.
        """
        logging.info(f"{self.printer_name} Enabling timelapse for {user}")  # noqa  # pylint: disable=logging-fstring-interpolation
        self.__timelapsed = True
        if not self.user_in(user, Command.TIMELAPSE):
            self.add_user(user, Command.TIMELAPSE)
        return True

    def disable_timelapse(self, user: discord.User) -> bool:
        """
        Disables the timelapse process for a user.

        Parameters
        ----------
        user (discord.User): The user to disable timelapse for.

        Returns
        -------
        bool: True if timelapse was disabled, False otherwise.
        """
        logging.info(f"{self.printer_name} Disabling timelapse for {user}")  # noqa  # pylint: disable=logging-fstring-interpolation
        if self.user_in(user, Command.TIMELAPSE):
            self.remove_user(user, Command.TIMELAPSE)
        return False

    def is_timelapsed(self) -> bool:
        """
        Checks if the timelapse process is enabled.

        Returns
        -------
        bool: True if the timelapse process is enabled, False otherwise.
        """
        return self.__timelapsed

    def create_timelapse(self) -> bytes | None:
        """
        Creates a timelapse of the printer.

        Returns
        -------
        bytes | None: The timelapse bytes, or None if an error occurred.
        """
        logging.info(f"{self.printer_name} Creating timelapse")  # noqa  # pylint: disable=logging-fstring-interpolation
        im: list[Image.Image] = []
        for frame in self.__timelapse_frames:
            im.append(Image.open(frame))

        try:
            with BytesIO() as buffer:
                if len(im) == 0:
                    im.append(self.__default_image)
                im[0].save(buffer, format='GIF', save_all=True,
                           append_images=im[1:], optimize=False,
                           duration=int((1000 * 1/self.__timelapse_speed)/6),
                           loop=0)
                buffer.seek(0)
                return buffer.getbuffer().tobytes()
        except Exception as e:
            logging.error(f"{self.printer_name} Error creating timelapse: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
            return None

    async def send_timelapse(self, timelapse: bytes, time: str) -> None:
        """
        Sends the timelapse to users.

        Parameters
        ----------
        timelapse (bytes): The timelapse bytes.
        time (str): The time the timelapse was created.
        """
        filename = f"{self.printer_name}_timelapse_{time}.gif"
        logging.info(f"{self.printer_name} Sending {filename} to users: {len(self.__users[Command.TIMELAPSE])}") # noqa  # pylint: disable=logging-fstring-interpolation
        for user in self.__users[Command.TIMELAPSE]:
            try:
                with BytesIO(timelapse) as timelapse:
                    await user.send(
                        file=discord.File(
                            fp=timelapse, filename=filename))
            except Exception as e:
                logging.error(f"{self.printer_name} Error sending timelapse: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation

    def append_frame(self):
        """
        Appends a frame to the timelapse.
        """
        frame = self.__get_frame()
        if frame is not None:
            self.__timelapse_frames.append(BytesIO(base64.b64decode(frame)))

    def update_state(self):
        """
        Updates the printer state.
        """
        self.__printer_state.append(self.__get_state())
        logging.info(f"{self.printer_name} {', '.join(state.value for state in self.__printer_state[-5:])}") # noqa  # pylint: disable=logging-fstring-interpolation

    def is_starting(self) -> bool:
        """
        Checks if the printer is starting.

        Returns
        -------
        bool: True if the printer is starting, False otherwise.
        """
        if len(self.__printer_state) > 0:
            if self.__printer_state[-1] == GcodeState.PREPARE:
                return True
            if self.__printer_state[-1] == GcodeState.RUNNING and \
                    (self.__printer_state[-2] == GcodeState.IDLE or
                     self.__printer_state[-2] == GcodeState.FINISH):
                return True
        return False

    def is_done(self) -> bool:
        """
        Checks if the printer is done.

        Returns
        -------
        bool: True if the printer is done, False otherwise.
        """
        if len(self.__printer_state) < 2:
            return False
        if self.__printer_state[-1] == GcodeState.FINISH and \
                self.__printer_state[-2] == GcodeState.RUNNING:
            return True
        return False

    def is_reset(self) -> bool:
        """
        Checks if the printer is reset.

        Returns
        -------
        bool: True if the printer is reset, False otherwise.
        """
        if len(self.__printer_state) < 2:
            return False
        if self.__printer_state[-1] == GcodeState.IDLE or \
                self.__printer_state[-1] == GcodeState.FINISH:
            return True
        return False

    def __get_remaining_time(self) -> int:
        """
        Retrieves the remaining time for the printer.

        Returns
        -------
        int: The remaining time, or -1 if an error occurred.
        """
        response: requests.Response = {}
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/time",
                timeout=30)
        except Exception as e:
            logging.error(f"{self.printer_name} Error getting time: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        if response.status_code != 200:
            return -1
        r: dict = dict(response.json())
        return r.get("time", -1)

    def __get_percentage(self) -> int:
        """
        Retrieves the percentage of completion for the printer.

        Returns:
            int: The percentage of completion, or -1 if an error occurred.
        """
        response: requests.Response = {}
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/percentage",
                timeout=30)
        except Exception as e:
            logging.error(f"{self.printer_name} Error getting percentage: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        if response.status_code != 200:
            return -1
        r: dict = dict(response.json())
        return r.get("percentage", -1)

    def __get_frame(self) -> str | None:
        """
        Retrieves a frame from the printer.

        Returns
        -------
        str | None: The frame, or None if an error occurred.
        """
        response: requests.Response = requests.Response()
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/camera",
                timeout=5)
        except Exception as e:
            logging.error(f"{self.printer_name} Error getting frame: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        if response.status_code != 200:
            return None
        r: dict[str, dict] = dict(response.json())
        if "error" in r:
            logging.error(f"{self.printer_name} Error getting frame: {r['error']}")  # noqa  # pylint: disable=logging-fstring-interpolation
            return None
        return r.get("frame", {}).get("body", None)

    def __get_state(self) -> GcodeState:
        """
        Retrieves the state of the printer.

        Returns
        -------
        State: The state of the printer.
        """
        response: requests.Response = requests.Response()
        try:
            response = requests.get(
                f"http://{self.printer_url}/printer/status/state",
                timeout=5)
        except Exception as e:
            logging.error(f"{self.printer_name} Error getting state: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        if response.status_code != 200:
            return GcodeState.UNKNOWN
        r: dict = response.json()
        return GcodeState(r.get("state", "IDLE"))
