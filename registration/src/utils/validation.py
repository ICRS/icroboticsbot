import re

__all__ = [
    "SHORTCODE_REGEX",
    "UID_REGEX",
    "DISCORD_ID_REGEX",
    "is_shortcode",
    "is_uid",
    "format_uid",
    "is_discord_id",
    "format_discord_id"
]

SHORTCODE_REGEX = r'^[a-z]{2,3}[0-9]{2,4}$'
UID_REGEX = r'^[0-9A-F]{8,14}$'
DISCORD_ID_REGEX = r'^<@[0-9]{18,19}>$'


def is_shortcode(message: str) -> bool:
    message = message.lower().strip()
    found = re.findall(SHORTCODE_REGEX, message)
    return any(found)


def is_uid(message: str) -> bool:
    message = format_uid(message)
    found = re.findall(UID_REGEX, message)
    return any(found)


def format_uid(message: str) -> bool:
    message = message.upper()
    message = message.replace(" ", "")
    message = message.replace(":", "")
    message = message.replace("-", "")
    return message


def is_discord_id(id: str) -> bool:
    found = re.findall(DISCORD_ID_REGEX, id)
    return any(found)


def format_discord_id(id: str) -> str:
    return id[2:-1]
