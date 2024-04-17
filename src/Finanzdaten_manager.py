from copy import copy
from datetime import datetime
import pandas as pd

class Finanzdaten_manager:
    def __init__(self, base):
        self.dfs = {}
        self.base = copy(base)
        self.extract_dfs()

    def extract_dfs(self):
        for y in range(2021, datetime.now().year+1, 1):
            self.base[str(y)] = self.base[str(y)].drop([0,1,2,3,4,5,6])
            self.base[str(y)] = self.base[str(y)].reset_index()
            self.base[str(y)] = self.base[str(y)].drop(['index'], axis=1)
            num_columns = len(self.base[str(y)].columns)
            new_column_names = range(1,num_columns+1,1)
            self.base[str(y)].rename(columns=dict(zip(self.base[str(y)].columns, new_column_names)), inplace=True)
        