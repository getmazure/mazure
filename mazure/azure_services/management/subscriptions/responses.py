import json

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import register

from .. import PathManagement, PathSingleSubscription
from .data.locations import locations
from .model import Subscription


@register(parent=PathManagement, path=r"/subscriptions$", method="GET")
def get_subscriptions(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    if Subscription.select().count() == 0:  # pylint: disable=E1120
        Subscription.create()
    subs = [sub.to_json() for sub in Subscription.select()]
    resp = {"count": {"type": "Total", "value": len(subs)}, "value": subs}

    return 200, {}, json.dumps(resp).encode("utf-8")


@register(parent=PathSingleSubscription, path=r"/locations$", method="GET")
def get_locations(request: MazureRequest) -> ResponseType:
    response = json.dumps({"value": locations})

    # query could include includeExtendedLocations=true
    # But that returns the same result AFAICS
    subscription_id = request.path.split("/")[2]

    response = response.replace("__SUBID__", subscription_id)

    return 200, {}, response.encode("utf-8")
