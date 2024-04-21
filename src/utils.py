import streamlit as st
import json
from datetime import datetime

def session_state_helper():
    if 'month_map' not in st.session_state:
        st.session_state.month_map = json.load(open('data/month_map.json'))
    else:
        st.session_state.month_map = st.session_state.month_map

    if 'energy_map' not in st.session_state:
        st.session_state.energy_map = json.load(open('data/energy_map.json'))
    else:
        st.session_state.energy_map = st.session_state.energy_map

    if 'interval_map' not in st.session_state:
        st.session_state.interval_map = json.load(open('data/interval_map.json'))
    else:
        st.session_state.interval_map = st.session_state.interval_map

def calculate_slider_values_interval(year_list: list, start_month: str) -> list:
    year_list = list(map(str, year_list))
    
    months = list(st.session_state.month_map.keys())

    selectable_options = []

    for y in year_list:
        for m in months:
            if y != year_list[0] or (y == year_list[0] and m in months[months.index(start_month):]):
                if int(y) < datetime.now().year:
                    selectable_options.append(m + ' ' + y)
                elif int(y) == datetime.now().year and st.session_state.month_map[m] < datetime.now().month:
                    selectable_options.append(m + ' ' + y)

    return selectable_options