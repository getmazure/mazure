from typing import Any, Dict, Tuple

from peewee import SqliteDatabase

from .mazure_request import MazureRequest

ResponseType = Tuple[int, Dict[str, Any], bytes]

db = SqliteDatabase(":memory:")
