from copy import copy
from datetime import datetime
import pandas as pd

class Finanzdaten_manager:
    def __init__(self, base):
        self.dfs = {}
        self.base = copy(base)
        self.cleanup_header()

    def cleanup_header(self):
        for y in range(2021, datetime.now().year+1, 1):
            self.base[str(y)] = self.base[str(y)].drop([0,1,2,3,4,5,6])
            self.base[str(y)] = self.base[str(y)].reset_index()
            self.base[str(y)] = self.base[str(y)].drop(['index'], axis=1)
            num_columns = len(self.base[str(y)].columns)
            new_column_names = range(1,num_columns+1,1)
            self.base[str(y)].rename(columns=dict(zip(self.base[str(y)].columns, new_column_names)), inplace=True)
            self.dfs[y] = self.build_df_dict(y)

    def build_df_dict(self, year):
        yearly_dict = {}
        months = ['Januar',
                  'Februar',
                  'März',
                  'April',
                  'Mai',
                  'Juni',
                  'Juli',
                  'August',
                  'September',
                  'Oktober',
                  'November',
                  'Dezember']
        
        m_index = 1

        for m in months:
            monthly_df = self.base[str(year)][[m_index, m_index+1, m_index+2]]
            monthly_df.rename(columns=monthly_df.iloc[0], inplace=True)
            monthly_df.drop(monthly_df.index[0], inplace=True)
            monthly_df.dropna(axis=0, how='all', inplace=True)
            yearly_dict[m] = monthly_df
            m_index = m_index + 3

        return yearly_dict