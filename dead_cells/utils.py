import os

import pandas as pd


class Constants(object):
    ROOT_PATH = os.path.dirname(__file__)
    TRANSLATE_JSON = f'{ROOT_PATH}/translate.json'
    BIOMES_JSON = f'{ROOT_PATH}/biomes.json'

    BIOMES_HTML = f'{ROOT_PATH}/output/biomes.html'
    ROUTES_JSON = f'{ROOT_PATH}/output/routes.json'
    DEAD_CELLS_EXCEL = f'{ROOT_PATH}/output/dead_cells_%s.xlsx'

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
