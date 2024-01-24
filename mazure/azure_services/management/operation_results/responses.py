from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register

from .. import PathSingleSubscription


@register(
    parent=PathSingleSubscription,
    path=r"/operationresults/[-_a-z0-9A-Z]+$",
    method="GET",
)
def get_operation_result(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    return 200, {}, b""
