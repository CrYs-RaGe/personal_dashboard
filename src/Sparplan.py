import pandas as pd
from numbers import Number
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import streamlit as st

interval_map = {
    'monatlich' : 1,
    'vierteljährlich' : 3,
    'halbjährlich' : 6,
    'jährlich' : 12
}

class Sparplan():
    def __init__(self, start, end, rate, interval = 'monatlich'):
        self.set_start(start)
        self.set_end(end)
        if self.end <= self.start:
            raise Exception("Kein valides Enddatum")
        
        self.set_rate(rate)
        self.set_interval(interval)
        self.df = pd.DataFrame(columns = ["date", "payed", "value", "gained"])
        
        self.etf_endwert = 0
        self.etf_kursgewinn = 0
        self.etf_eingezahlt = 0
        self.etf_steuer = 0

    def set_rate(self, rate):
        if isinstance(rate, Number):
            self.rate = rate
        else:
            raise Exception("Die Zinsrate ist keine Zahl")
        
    def set_interval(self, interval):
        try:
            self.interval = interval_map[interval]
        except:
            raise Exception("Das gewählte Intervall ist nicht verfügbar")
        
    def set_start(self, start):
        self.start = self.convert_date(start)

    def set_end(self, end):
        self.end = self.convert_date(end)

    def convert_date(self, date_str):
        date_set = False
        try:
            date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
            date_set = True
        except:
            pass

        try:
            date_obj = datetime.strptime(date_str, "%m/%d/%Y").date()
            date_set = True
        except:
            pass

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            date_set = True
        except:
            pass

        if not date_set:
            date_obj = date_str
        
        if date_obj:
            return date_obj
        else:
            raise Exception("Kein valides Datumsformat")

    def get_start(self):
        return self.start
        
    def get_end(self):
        return self.end
    
    def get_rate(self):
        return self.rate
    
    def get_interval(self):
        return self.interval
    
    def get_endwert(self):
        return self.etf_endwert
    
    def get_kursgewinn(self):
        return self.etf_kursgewinn
    
    def get_eingezahlt(self):
        return self.etf_eingezahlt
    
    def get_steuer(self):
        return self.etf_steuer
    
    def calculate(self, cost, amount):
        if not isinstance(cost, Number):
            raise Exception("Laufende Kosten sind keine Zahl")
        
        if not isinstance(amount, Number):
            raise Exception("Sparrate ist keine Zahl")
        else:
            if amount < 0:
                raise Exception("Sparrate ist negativ")
            
        effective_rate = np.power(1 + (self.rate - cost), self.interval/12) - 1
        current_date = self.start

        while current_date < self.end:
            if current_date == self.start:
                df_to_add = pd.DataFrame({"date": [current_date], "payed":[amount], "value":[amount], "gained":[0]})
                self.df = pd.concat([self.df, df_to_add], ignore_index=True)
                current_date += relativedelta(months = self.interval)
                continue
            
            last_payed = self.df.loc[len(self.df)-1, "payed"]
            last_value = self.df.loc[len(self.df)-1, "value"]

            df_to_add = pd.DataFrame({"date": [current_date], 
                                      "payed": [last_payed + amount], 
                                      "value": [last_value * (1 + effective_rate) + amount], 
                                      "gained": [last_value * (1 + effective_rate) - last_payed]})
            self.df = pd.concat([self.df, df_to_add], ignore_index=True)

            current_date += relativedelta(months = self.interval)

        self.etf_endwert = self.df.loc[len(self.df)-1, "value"]
        self.etf_kursgewinn = self.df.loc[len(self.df)-1, "gained"]
        self.etf_eingezahlt = self.df.loc[len(self.df)-1, "payed"]
        self.etf_steuer = self.etf_kursgewinn * 0.7 * 0.28

        return self.df
    