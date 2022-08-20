import copy
import json
import os
import re

import requests
from lxml import etree

from dead_cells.utils import Constants, Utils
from dead_cells.translate import TRANSLATE


class BiomesCollector(object):
    DETAILS_TABLE_XPATH = "(//div[contains(text(),'Details')]/ancestor::table)"
    MORE_DETAIL_DIV_XPATH = "(//div[@align='center'][normalize-space()='Click to see more detailed information']/..)"
    
    def __init__(self, force_req=False, lang=None):
        self._force_req = force_req
        self._languages = lang or ['en', 'zh-cn']
        self._html = None
        self._names = []
        self._hided_names = []
        self._data = []
    
    def execute(self):
        self._html = self._req_html()
        self._parse_html()
        self._save()
    
    def _save(self):
        self._save_biomes_json()
        self._save_translate_json()
        self._save_biomes_excel()

    def _save_biomes_json(self):
        with open(Constants.BIOMES_JSON, 'w', encoding='utf-8') as f:
            json.dump(self._data, f, indent=4)

    def _save_translate_json(self):
        for item in self._data:
            name = item['name']
            TRANSLATE.add_word(name)
        TRANSLATE.save()

    def _save_biomes_excel(self):
        for lang in self._languages:
            path = Constants.dead_cells_excel_path(lang)
            data = copy.deepcopy(self._data)
            for item in data:
                item['name'] = TRANSLATE.trans(item['name'], lang)
                item['exits'] = TRANSLATE.trans(item['exits'], lang)
            Utils.write_excel(path, data, 'Biomes')

    def _parse_html(self):
        self._parse_names()
        self._parse_raw_data()
        self._parse_data()

    def _parse_data(self):
        for item in self._data:
            name = item['name']
            raw_scroll_info = item.pop('raw_scroll_info')
            raw_exit_names = item.pop('raw_exit_names')
            scroll_info = self._parse_scroll_info(raw_scroll_info)
            exit_names = self._parse_exit_names(name, raw_exit_names)
            item.update({
                **scroll_info,
                'exits': exit_names
            })

    def _parse_raw_data(self):
        for i, name in enumerate(self._names):
            raw_scroll_info = self._get_raw_scroll_info(i)
            raw_exit_names = self._get_raw_exit_names(i)
            self._data.append({
                'name': name,
                'raw_scroll_info': raw_scroll_info,
                'raw_exit_names': raw_exit_names,
            })
        for i, name in enumerate(self._hided_names):
            raw_hided_scroll_info = self._get_raw_hided_scroll_info(i)
            raw_hided_exit_names = self._get_raw_hided_exit_names(i)
            self._data.append({
                'name': name,
                'raw_scroll_info': raw_hided_scroll_info,
                'raw_exit_names': raw_hided_exit_names,
            })

    def _parse_names(self):
        xpath = f"{self.DETAILS_TABLE_XPATH}/preceding-sibling::h3[1]//a/text()"
        self._names = self._html.xpath(xpath)

        xpath = f"{self.MORE_DETAIL_DIV_XPATH}/div[1]/a/text()"
        self._hided_names = self._html.xpath(xpath)

    @staticmethod
    def _parse_scroll_info(raw_scroll_info):
        scroll_info_pattern = {
            'power': r'(\d+) Power',
            'guaranteed': r'\+(\d+) in a guaranteed',
            'extra_power_for_2': r'(\d+) extra power \(2\+ \)',
            'extra_power_for_3': r'(\d+) extra power \(3\+ \)',
            'extra_power_for_4': r'(\d+) extra power \(4\+ \)',
            'dual_scroll': r'(\d+) Dual Scrolls',
            'scroll_fragment_for_3': r'(\d+)  \(3 \)',
            'scroll_fragment_for_4': r'(\d+)  \(4 \)',
        }
        scroll_info = {}
        for k, pattern in scroll_info_pattern.items():
            res = re.search(pattern, raw_scroll_info)
            scroll_info[k] = int(res.group(1)) if res else 0
        return scroll_info

    def _get_raw_scroll_info(self, index):
        xpath = f"{self.DETAILS_TABLE_XPATH}[{index + 1}]//b[contains(text(),'Scrolls:')]/../text()"
        raw_scroll_info = self._html.xpath(xpath)
        return ''.join(raw_scroll_info)

    def _get_raw_hided_scroll_info(self, index):
        xpath = f"{self.MORE_DETAIL_DIV_XPATH}[{index + 1}]//b[contains(text(),'Scrolls:')]/../text()"
        raw_hided_scroll_info = self._html.xpath(xpath)
        return ''.join(raw_hided_scroll_info)

    def _parse_exit_names(self, name, exit_names):
        exit_names = [
            exit_name
            for exit_name in exit_names
            if exit_name in self._names + self._hided_names
        ]

        # 出口显示为 Seventh stage, 需要修改为 Astrolab
        # Exit: Seventh stage
        if name == 'Throne Room':
            exit_names.append('Observatory')

        # 需要剔除 Fractured Shrines
        # Exits: Clock Tower, Undying ShoresFF (requires reaching the Undying Shores
        # from the Fractured ShrinesFF with the Cultist Outfit
        # OutfitFF at least once)
        if name == 'Stilt Village':
            exit_names.remove('Fractured Shrines')
        
        return exit_names

    def _get_raw_exit_names(self, index):
        xpath = f"{self.DETAILS_TABLE_XPATH}[{index + 1}]//b[contains(text(),'Exit')]/..//a/text()"
        return self._html.xpath(xpath)

    def _get_raw_hided_exit_names(self, index):
        xpath = f"{self.MORE_DETAIL_DIV_XPATH}[{index + 1}]//b[contains(text(),'Exit')]/..//a/text()"
        return self._html.xpath(xpath)

    def _req_html(self):
        if self._force_req or not os.path.exists(Constants.BIOMES_HTML):
            url = 'https://deadcells.fandom.com/wiki/Biomes'
            res = requests.get(url)
            with open(Constants.BIOMES_HTML, 'w', encoding='utf-8') as f:
                f.write(res.text)
        with open(Constants.BIOMES_HTML, 'r', encoding='utf-8') as f:
            return etree.HTML(f.read())


def main():
    bc = BiomesCollector()
    bc.execute()


if __name__ == '__main__':
    main()
