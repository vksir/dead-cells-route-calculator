import json
from collections import UserDict

from dead_cells.utils import Constants


class Stages(UserDict):
    def __init__(self):
        super(Stages, self).__init__(self._read())

    def biomes(self, stage):
        return self[stage]

    def stage(self, biome):
        stages = [stage for stage, biomes in self.items() if biome in biomes]
        if len(stages) != 1:
            raise Exception('wrong stage mapping info')
        return stages[0]

    @staticmethod
    def _read():
        with open(Constants.STAGES_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)


STAGES = Stages()
