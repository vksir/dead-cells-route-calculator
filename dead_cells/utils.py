import os

import pandas as pd


class Constants(object):
    TRANSLATE_JSON = './translate.json'
    BIOMES_JSON = './biomes.json'

    BIOMES_HTML = './output/biomes.html'
    ROUTES_JSON = './output/routes.json'
    DEAD_CELLS_EXCEL = './output/dead_cells_%s.xlsx'

    @classmethod
    def dead_cells_excel_path(cls, lang):
        return cls.DEAD_CELLS_EXCEL % lang


class Utils(object):
    @staticmethod
    def write_excel(path, data, sheet):
        exist = os.path.exists(path)
        mode = 'w' if not exist else 'a'
        if_sheet_exists = None if not exist else 'overlay'
        with pd.ExcelWriter(path,
                            mode=mode,
                            if_sheet_exists=if_sheet_exists) as writer:
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet)
