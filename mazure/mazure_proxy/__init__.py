import logging
import sys

logging.basicConfig(stream=sys.stdout, format="%(levelname)s %(asctime)s - %(message)s")
logger = logging.getLogger("MAZURE")
logger.setLevel(logging.INFO)


def with_color(color: int, text: object) -> str:
    return f"\x1b[{color}m{text}\x1b[0m"


def info(msg: object) -> None:
    logger.info(msg)


def debug(msg: object) -> None:
    logger.debug(msg)


def error(msg: object) -> None:
    logger.error(msg)
