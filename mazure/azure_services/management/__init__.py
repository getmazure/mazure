from mazure.mazure_core.route_mapping import register_parent


@register_parent(path="https://graph.microsoft.com")
class GraphHost:
    pass


@register_parent(path="https://management.azure.com")
class ManagementWebsite:
    pass
