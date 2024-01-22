import json
import re

from mazure.mazure_core import MazureRequest, ResponseType
from mazure.mazure_core.route_mapping import register

from . import sub_model


@register(
    "https://management.azure.com", path=re.compile("^/subscriptions$"), method="GET"
)
def get_subscriptions(
    request: MazureRequest,  # pylint: disable=unused-argument
) -> ResponseType:
    response = json.dumps(sub_model.get_subscriptions())

    return 200, {}, response.encode("utf-8")


@register(
    "https://management.azure.com",
    path=re.compile("^/subscriptions/[-a-z0-9A-Z]+/locations$"),
    method="GET",
)
def get_locations(request: MazureRequest) -> ResponseType:
    content = sub_model.get_locations()
    response = json.dumps({"value": content})

    # query could include includeExtendedLocations=true
    # But that returns the same result AFAICS
    subscription_id = request.path.split("/")[2]

    response = response.replace("__SUBID__", subscription_id)

    return 200, {}, response.encode("utf-8")
