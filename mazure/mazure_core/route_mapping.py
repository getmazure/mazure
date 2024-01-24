from typing import Callable, Dict, Pattern

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest

registered_services: Dict[
    str, Dict[str, Dict[Pattern[str], Callable[[MazureRequest], ResponseType]]]
] = {}


def register(
    host: str, path: Pattern[str], method: str
) -> Callable[
    [Callable[[MazureRequest], ResponseType]], Callable[[MazureRequest], ResponseType]
]:
    def _decorator(
        func: "Callable[[MazureRequest], ResponseType]",
    ) -> "Callable[[MazureRequest], ResponseType]":
        if method not in registered_services:
            registered_services[method] = {}
        if host not in registered_services[method]:
            registered_services[method][host] = {}
        registered_services[method][host][path] = func

        return func

    return _decorator
