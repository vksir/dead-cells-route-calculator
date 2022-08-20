import os
import json
from collections import UserDict

from dead_cells.utils import Constants


class Translate(UserDict):
    def __init__(self):
        super(Translate, self).__init__(self._read())

    def trans(self, word, lang):
        if isinstance(word, str):
            return self.get(word, {}).get(lang, '')
        elif isinstance(word, list):
            return [self.trans(w, lang) for w in word]
        raise Exception(f'invalid word: {word}')

    def en(self, word):
        return self.trans(word, 'en')

    def zh_cn(self, word):
        return self.trans(word, 'zh-cn')

    def add_word(self, word):
        self.data.setdefault(word, {})

    def _set_default(self):
        for k in self:
            self.setdefault(k, {})
            self[k].setdefault('en', k)
            self[k].setdefault('zh-cn', '')

    @staticmethod
    def _read():
        if not os.path.exists(Constants.TRANSLATE_JSON):
            return {}
        with open(Constants.TRANSLATE_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save(self):
        self._set_default()
        with open(Constants.TRANSLATE_JSON, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)


TRANSLATE = Translate()


if __name__ == '__main__':
    print(TRANSLATE.trans("Prisoners' Quarters", 'zh-cn'))

