import copy
import json
import queue
from collections import UserList

from dead_cells.biomes import BIOMES
from dead_cells.translate import TRANSLATE
from dead_cells.stages import STAGES
from dead_cells.utils import Constants
from dead_cells.utils import Utils


class Way(UserList):
    @property
    def next_node_names(self):
        return BIOMES.next_node_names(self[-1])

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
    def extra_power_for_1(self):
        return sum(node.extra_power_for_1 for node in self.nodes)

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
    def value_for_1(self):
        return self.value + self.extra_power_for_1

    @property
    def value_for_2(self):
        return self.value_for_1 + self.extra_power_for_2

    @property
    def value_for_3(self):
        return self.value_for_2 + self.extra_power_for_3 + int(self.scroll_fragment_for_3 * 0.25)

    @property
    def value_for_4(self):
        return self.value_for_2 + self.extra_power_for_3 + self.extra_power_for_4 \
               + int(self.scroll_fragment_for_4 * 0.25)

    @property
    def _power_data(self):
        data = {}
        for attr in [
            'power',
            "guaranteed",
            'extra_power_for_1',
            "extra_power_for_2",
            "extra_power_for_3",
            "extra_power_for_4",
            "dual_scroll",
            "scroll_fragment_for_3",
            "scroll_fragment_for_4",
            "value",
            "value_for_1",
            "value_for_2",
            "value_for_3",
            "value_for_4"
        ]:
            value = getattr(self, attr)
            data[attr] = value
        return data

    @property
    def _stage_data(self):
        data = {}
        for stage, biomes in STAGES.items():
            biomes = list(set(self) & set(biomes))
            if len(biomes) not in [0, 1]:
                raise Exception('wrong stage mapping info')
            data[stage] = biomes[0] if biomes else ''
        return data

    def dict(self):
        data = {
            'way': self.data,
            **self._power_data,
            **self._stage_data
        }
        return data

    def dict_for_5(self):
        power = self.power + self.extra_power_for_1 + self.extra_power_for_2 \
                + self.extra_power_for_3 + self.extra_power_for_4 \
                + int(self.scroll_fragment_for_4 * 0.25)
        data = {
            'way': self.data,
            'power': power,
            "guaranteed": self.guaranteed,
            "dual_scroll": self.dual_scroll,
            "value": self.value_for_4,
            **self._stage_data
        }
        return data


class RouteCalculator(object):
    def __init__(self, lang=None):
        self._languages = lang or ['en', 'zh-cn']
        self._entire_ways = []
        self._data = []
        self._stage_data = []

    def execute(self):
        self._calc_all_ways()
        self._save()

    def _calc_all_ways(self):
        ways = queue.Queue()
        ways.put(Way(["Prisoners' Quarters"]))
        while not ways.empty():
            way = ways.get()
            next_nodes = way.next_node_names
            if not next_nodes:
                self._entire_ways.append(way)
                continue
            for next_node in next_nodes:
                tmp_way = copy.deepcopy(way)
                tmp_way.append(next_node)
                ways.put(tmp_way)

    def _save(self):
        self._save_routes_json()
        self._save_translate_json()
        self._save_routes_excel()

    def _save_routes_json(self):
        self._data = [way.dict() for way in self._entire_ways]
        with open(Constants.ROUTES_JSON, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=4)

    def _save_translate_json(self):
        if not self._data:
            return
        for key in self._data[0]:
            TRANSLATE.add_word(key)
        TRANSLATE.save()

    def _save_routes_excel(self):
        self._write_route_excel(self._data, 'routes')

        self._entire_ways = sorted(self._entire_ways,
                                   key=lambda way: [
                                       -way.value_for_4,
                                       way.guaranteed,
                                       way.dual_scroll,
                                   ])
        data = [way.dict_for_5() for way in self._entire_ways]
        self._write_route_excel(data, 'best_routes_for_5')

    def _write_route_excel(self, raw_data, sheet):
        for lang in self._languages:
            path = Constants.dead_cells_excel_path(lang)
            data = copy.deepcopy(raw_data)
            for i in range(len(data)):
                new_data = {}
                for k, v in data[i].items():
                    if k in ['way']:
                        v = '--'.join(TRANSLATE.trans(v, lang))
                    else:
                        v = TRANSLATE.trans(v, lang)
                    k = TRANSLATE.trans(k, lang)
                    new_data[k] = v
                data[i] = new_data
            Utils.write_excel(path, data, TRANSLATE.trans(sheet, lang))

def main():
    rc = RouteCalculator()
    rc.execute()


if __name__ == '__main__':
    main()
