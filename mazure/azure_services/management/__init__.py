from mazure.mazure_core.route_mapping import register_parent


@register_parent(path="https://graph.microsoft.com")
class PathGraph:
    pass


@register_parent(path="https://management.azure.com")
class PathManagement:
    pass


@register_parent(r"/subscriptions/[-a-z0-9A-Z]+")
class PathSingleSubscription(PathManagement):
    pass
