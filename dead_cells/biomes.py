import json
from pydantic import BaseModel

from dead_cells.utils import Constants


class Node(BaseModel):
    name: str
    power: int
    guaranteed: int
    extra_power_for_2: int
    extra_power_for_3: int
    extra_power_for_4: int
    dual_scroll: int
    scroll_fragment_for_3: int
    scroll_fragment_for_4: int

    @property
    def value(self):
        return self.power + self.guaranteed + self.dual_scroll

    @property
    def value_for_2(self):
        return self.value + self.extra_power_for_2

    @property
    def value_for_3(self):
        return self.value_for_2 + self.extra_power_for_3 + self.scroll_fragment_for_3 * 0.25

    @property
    def value_for_4(self):
        return self.value_for_3 + self.extra_power_for_4 + self.scroll_fragment_for_4 * 0.25


class Biomes:
    def __init__(self):
        data = self._read()
        self._node_mapping = {
            item['name']: Node(**item)
            for item in data
        }
        self._route_mapping = {
            item['name']: item['exit']
            for item in data
        }

    def node(self, node_name) -> Node:
        return self._node_mapping[node_name]

    def next_node_names(self, node_name):
        return self._route_mapping[node_name]

    @staticmethod
    def _read():
        with open(Constants.BIOMES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)


BIOMES = Biomes()
