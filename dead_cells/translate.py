import os
import json
from collections import UserDict

from dead_cells.utils import Constants


class Translate(UserDict):
    def __init__(self):
        super(Translate, self).__init__(self._read())

    def zh_cn(self, word):
        return self.get(word, {}).get('zh-cn', '')

    def add_word(self, word):
        self.data.setdefault(word, {
            'zh-cn': ''
        })

    @staticmethod
    def _read():
        if not os.path.exists(Constants.TRANSLATE_JSON):
            return {}
        with open(Constants.TRANSLATE_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self):
        with open(Constants.TRANSLATE_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)


TRANSLATE = Translate()
