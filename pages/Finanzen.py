import openpyxl
import pandas as pd
pd.options.mode.copy_on_write=True
import streamlit as st
from copy import copy

from src import utils
utils.session_state_helper()

from src.Finanzdaten_manager import Finanzdaten_manager as fin

def get_data():
    # Open an existing Excel file
    workbook = openpyxl.load_workbook('data/Finanzen_gesamt.xlsx')

    # Get a list of sheet names
    sheet_names = workbook.sheetnames

    dfs = {}

    for sname in sheet_names:
        dfs[sname] = pd.read_excel('data/Finanzen_gesamt.xlsx', sheet_name=sname)

    # Close the workbook
    workbook.close()

    return dfs

def interval(data):
    years = list(data.dfs.keys())

    if st.checkbox("Jahre ausschließen"):
        max_year = st.selectbox("Alle Jahre ausschließen bis:", years)
    
        for w in years[:years.index(max_year)+1]:
            years.remove(w)

    selectable_options = utils.calculate_slider_values_interval(years, 'Januar')
    
    start_date, end_date = st.select_slider(
        'Zeitspanne',
        options=selectable_options,
        value=(selectable_options[0], selectable_options[-1]))
    
    start_year = start_date.split()[1]
    start_month = start_date.split()[0]

    end_year = end_date.split()[1]
    end_month = end_date.split()[0]

    months = list(st.session_state.month_map.keys())

    column_names_unified = ['Betrag', 'Beschreibung', 'Kategorie']
    interval_df = pd.DataFrame(columns=column_names_unified)
    dfs = copy(data.dfs)

    if start_year != end_year:

        for y in range(int(start_year), int(end_year)+1 , 1):
            if str(y) == start_year:
                for m in months[months.index(start_month):]:
                    df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
                    interval_df = pd.concat([interval_df, df], ignore_index=True)
            elif str(y) == end_year:
                for m in months[:months.index(end_month)+1]:
                    df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
                    interval_df = pd.concat([interval_df, df], ignore_index=True)
            else:
                for m in months:
                    df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
                    interval_df = pd.concat([interval_df, df], ignore_index=True)

    else:
        for m in months[months.index(start_month):months.index(end_month)+1]:
            y = int(start_year)
            df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
            interval_df = pd.concat([interval_df, df], ignore_index=True)

    with st.expander('Daten'):
        st.write(interval_df)


def main():
    st.title("Finanzen")

    dfs = get_data()

    data = fin(dfs)

    tabs = st.tabs(['Interval','Other'])

    with tabs[-1]:
        year = st.selectbox('Jahr', data.dfs.keys())
        month = st.selectbox('Monat', data.dfs[year].keys())
        st.write(data.dfs[year][month])

    with tabs[0]:
        interval(data)

if __name__ == '__main__':
    main()