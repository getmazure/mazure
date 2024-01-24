import re

from mazure.mazure_core import ResponseType
from mazure.mazure_core.mazure_request import MazureRequest
from mazure.mazure_core.route_mapping import (
    register,
    register_parent,
    registered_parents,
    registered_services,
)


@register_parent(path="https://website.com")
class WebsiteRoot:
    pass


@register_parent(path="/static")
class WebsiteData(WebsiteRoot):
    pass


@register_parent(path="/js")
class WebsiteJS(WebsiteData):
    pass


@register(WebsiteRoot, "/path", "GET")
def get_path(request: MazureRequest) -> ResponseType:
    return 404, {}, f"{request.host} never called".encode("utf-8")


@register(WebsiteData, "/index.css", "GET")
def get_css(request: MazureRequest) -> ResponseType:
    return 404, {}, f"{request.host} never called".encode("utf-8")


@register(WebsiteJS, "/f1.js", "GET")
def get_js1(request: MazureRequest) -> ResponseType:
    return 404, {}, f"{request.host} never called".encode("utf-8")


@register(WebsiteJS, "/f2.js", "GET")
def get_js2(request: MazureRequest) -> ResponseType:
    return 404, {}, f"{request.host} never called".encode("utf-8")


def test_roots_are_registered_correctly() -> None:
    assert registered_parents[WebsiteRoot] == "https://website.com"
    assert registered_parents[WebsiteData] == "https://website.com/static"
    assert registered_parents[WebsiteJS] == "https://website.com/static/js"


def test_paths_are_registered_correctly() -> None:
    assert "GET" in registered_services

    get_paths = registered_services["GET"]
    assert (  # pylint: disable=comparison-with-callable
        get_paths[re.compile("https://website.com/static/index.css")] == get_css
    )
    assert (  # pylint: disable=comparison-with-callable
        get_paths[re.compile("https://website.com/static/js/f1.js")] == get_js1
    )
    assert (  # pylint: disable=comparison-with-callable
        get_paths[re.compile("https://website.com/static/js/f2.js")] == get_js2
    )
