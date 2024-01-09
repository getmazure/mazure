from typing import List

from .data.locations import LocationType, locations


class SubscriptionModel:
    def get_locations(self) -> List[LocationType]:
        return locations
