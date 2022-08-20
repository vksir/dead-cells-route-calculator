import copy
import queue
from collections import UserList

from dead_cells.translate import TRANSLATE
from dead_cells.biomes import BIOMES


class Way(UserList):
    @property
    def cur_node_name(self):
        return self[-1]

    @property
    def next_node_names(self):
        return BIOMES.next_node_names(self.cur_node_name)

    @property
    def nodes(self):
        return [BIOMES.node(node_name) for node_name in self]

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

        print('-'.join(TRANSLATE.zh_cn(node_name) for node_name in way), end=', ')
        print(f'value={way.value_for_4}')


if __name__ == '__main__':
    main()
