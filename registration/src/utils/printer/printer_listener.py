#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

import os
import logging
from enum import Enum
from collections import deque

import discord
from bambulabs_api import GcodeState

from src.utils.api import get_state

__all__ = [
    "get_env_bool",
    "Command",
    "PrinterListener"
]

DEBUG = str(os.getenv('DEBUG', False)).lower() in ['true', '1']
if DEBUG:
    from dotenv import load_dotenv
    load_dotenv()


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
    NOTIFY = {
        "name": "Notify",
        "emoji": "🔔",
        "description": "Notifies you when the printer is done"
    }

    @classmethod
    def _missing_(cls, value):
        return cls.NOTIFY


class PrinterListener:
    def __init__(self, printer_name: str,
                 printer_url: str,
                 max_printer_states: int = 10):
        # Debugging purposes
        # print(requests.get(f"http://localhost:6000/printer/status/state").json()) if DEBUG else None  # noqa
        if DEBUG:
            self.printer_url = "localhost:6000"
        else:
            self.printer_url = printer_url
        self.printer_name = printer_name

        self.__users: dict[Command, set[discord.User]] = {
            c: set() for c in Command
        }

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
        for user in self.__users[Command(comm)]:
            try:
                await user.send(f"Printer {self.printer_name} is finished.")
            except Exception as e:
                logging.error(f"{self.printer_name} Error sending message: {e}")  # noqa  # pylint: disable=logging-fstring-interpolation
        return True

    def update_state(self):
        """
        Updates the printer state.
        """
        self.__printer_state.append(
            get_state(f"http://{self.printer_url}")
        )

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
