import json

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register

from .. import PathManagement, PathSingleSubscription
from . import sub_model


@register(parent=PathManagement, path=r"/subscriptions$", method="GET")
def get_subscriptions(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    response = json.dumps(sub_model.get_subscriptions())

    return 200, {}, response.encode("utf-8")


@register(parent=PathSingleSubscription, path=r"/locations$", method="GET")
def get_locations(request: MazureRequest) -> ResponseType:
    content = sub_model.get_locations()
    response = json.dumps({"value": content})

    # query could include includeExtendedLocations=true
    # But that returns the same result AFAICS
    subscription_id = request.path.split("/")[2]

    response = response.replace("__SUBID__", subscription_id)

    return 200, {}, response.encode("utf-8")
