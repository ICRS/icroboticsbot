#!/usr/bin/env python
# -*- coding: utf-8 -*-

# mypy: ignore-errors

"""
Utility functions used by the bot
"""
import time

__all__ = ["print"]

# ===== Get the API key =====
BASE_PATH = "./"
# =========================================


def print(*args, **kwargs) -> None:  # pylint: disable=redefined-builtin
    """
    print is a wrapper around the built-in print function

    Parameters
    ----------
    args : list
        List of arguments to pass to the print function
    kwargs : dict
        Dictionary of keyword arguments to pass to the print function
    """
    built_in_print = __builtins__['print']              # type: ignore
    args = list(args)                                   # type: ignore
    args.insert(0, f'{time.strftime("%H:%M:%S")} :')    # type: ignore
    built_in_print(*args, **kwargs)


if __name__ == '__main__':
    pass
