import re
from typing import Callable, Dict, Pattern

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest

registered_parents: Dict[type[object], str] = {}

registered_services: Dict[
    str, Dict[Pattern[str], Callable[[MazureRequest], ResponseType]]
] = {}


def register_parent(path: str) -> Callable[[type[object]], type[object]]:
    def _decorator(
        func: type[object],
    ) -> type[object]:
        if len(func.__mro__) > 2:
            registered_parents[func] = registered_parents[func.__mro__[1]] + path
        else:
            registered_parents[func] = path

        return func

    return _decorator


def register(
    parent: type[object], path: str, method: str
) -> Callable[
    [Callable[[MazureRequest], ResponseType]], Callable[[MazureRequest], ResponseType]
]:
    def _decorator(
        func: "Callable[[MazureRequest], ResponseType]",
    ) -> "Callable[[MazureRequest], ResponseType]":
        if method not in registered_services:
            registered_services[method] = {}
        parent_path = registered_parents[parent]

        registered_services[method][re.compile(parent_path + path)] = func

        return func

    return _decorator
