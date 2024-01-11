from typing import Dict


class ResourceGroupsModel:
    def __init__(self) -> None:
        self.resource_groups: Dict[str, str] = {}

    def create_resource_group(self, name: str, location: str) -> None:
        self.resource_groups[name] = location

    def has_resource_group(self, name: str) -> bool:
        return name in self.resource_groups
