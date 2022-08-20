import copy
import json
import queue
from collections import UserList
from typing import List, Tuple

from pydantic import BaseModel

from info_collect import BIOMES_JSON
from translate import TRANS


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





@Singleton
class Biomes:
    def __init__(self):
        data = read_biomes_json()
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


class Way(UserList):
    @property
    def cur_node_name(self):
        return self[-1]

    @property
    def next_node_names(self):
        return Biomes().next_node_names(self.cur_node_name)

    @property
    def nodes(self):
        return [Biomes().node(node_name) for node_name in self]

    @property
    def power(self):
        return sum(node.power for node in self.nodes)

    @property
    def guaranteed(self):
        return sum(node.guaranteed for node in self.nodes)

    @property
    def extra_power_for_2(self):
        return sum(node.extra_power_for_2 for node in self.nodes)

    @property
    def extra_power_for_3(self):
        return sum(node.extra_power_for_3 for node in self.nodes)

    @property
    def extra_power_for_4(self):
        return sum(node.extra_power_for_4 for node in self.nodes)

    @property
    def dual_scroll(self):
        return sum(node.dual_scroll for node in self.nodes)

    @property
    def scroll_fragment_for_3(self):
        return sum(node.scroll_fragment_for_3 for node in self.nodes)

    @property
    def scroll_fragment_for_4(self):
        return sum(node.scroll_fragment_for_4 for node in self.nodes)

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


def read_biomes_json():
    with open(BIOMES_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)


def main():
    entire_ways = []
    ways = queue.Queue()
    ways.put(Way(["Prisoners' Quarters"]))
    while not ways.empty():
        way = ways.get()
        next_nodes = way.next_node_names
        if not next_nodes:
            entire_ways.append(way)
            continue
        for next_node in next_nodes:
            tmp_way = copy.deepcopy(way)
            tmp_way.append(next_node)
            ways.put(tmp_way)

    entire_ways = sorted(entire_ways, key=lambda item: item.value_for_4, reverse=True)
    for way in entire_ways:

        print('-'.join(TRANS.zh_cn(node_name) for node_name in way), end=', ')
        print(f'value={way.value_for_4}')


if __name__ == '__main__':
    main()
