import copy
import json
import os
import re

import requests
from lxml import etree
import pandas as pd


BIOMES_HTML = './biomes.html'
BIOMES_EXCEL = './biomes.xlsx'
BIOMES_EXCEL_ZH_CN = './biomes_zh_cn.xlsx'
BIOMES_JSON = './biomes.json'
TRANSLATE_JSON = './translate.json'


def biomes_html_req():
    if not os.path.exists(BIOMES_HTML):
        url = 'https://deadcells.fandom.com/wiki/Biomes'
        res = requests.get(url)
        with open(BIOMES_HTML, 'w', encoding='utf-8') as f:
            f.write(res.text)
    with open(BIOMES_HTML, 'r', encoding='utf-8') as f:
        return etree.HTML(f.read())


def biomes_html_parse(html):
    data = []
    details_table_xpath = "(//div[contains(text(),'Details')]/ancestor::table)"
    names = html.xpath(f"{details_table_xpath}/preceding-sibling::h3[1]//a/text()")
    for i, name in enumerate(names):
        raw_scroll_info = html.xpath(f"{details_table_xpath}[{i + 1}]//b[contains(text(),'Scrolls:')]/../text()")
        raw_scroll_info = ''.join(raw_scroll_info)
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
        print(raw_scroll_info)
        print(scroll_info)

        exit_names = html.xpath(f"{details_table_xpath}[{i + 1}]//b[contains(text(),'Exit')]/..//a/text()")
        exit_names = [exit_name for exit_name in exit_names if exit_name in names]
        if name == 'Throne Room':
            exit_names.append('Observatory')
        if name == 'Stilt Village':
            exit_names.remove('Fractured Shrines')

        data.append({
            'name': name,
            **scroll_info,
            'exit': exit_names,
        })
    data.append({
        'name': 'Observatory',
        'power': 0,
        'guaranteed': 0,
        'extra_power_for_2': 0,
        'extra_power_for_3': 0,
        'extra_power_for_4': 0,
        'dual_scroll': 0,
        'scroll_fragment_for_3': 0,
        'scroll_fragment_for_4': 0,
        'exit': [],
    })
    return data


def save_biomes_result(data):
    with open(BIOMES_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

    if not os.path.exists(TRANSLATE_JSON):
        translate_data = {}
    else:
        with open(TRANSLATE_JSON, 'r', encoding='utf-8') as f:
            translate_data = json.load(f)
    for item in data:
        name = item['name']
        translate_data.setdefault(name, {
            'zh-cn': ''
        })
    with open(TRANSLATE_JSON, 'w', encoding='utf-8') as f:
        json.dump(translate_data, f, indent=4, ensure_ascii=False)

    pd.DataFrame(data).to_excel(BIOMES_EXCEL)
    for item in data:
        item['name'] = translate_data[item['name']]['zh-cn']
        item['exit'] = [translate_data[name]['zh-cn'] for name in item['exit']]
    pd.DataFrame(data).to_excel(BIOMES_EXCEL_ZH_CN)


def main():
    html = biomes_html_req()
    data = biomes_html_parse(html)
    print(json.dumps(data, indent=4))
    save_biomes_result(data)


if __name__ == '__main__':
    main()
