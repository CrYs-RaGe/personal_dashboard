import openpyxl
import pandas as pd
import streamlit as st

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

def main():
    st.title("Finanzen")

    dfs = get_data()

    data = fin(dfs)

    year = st.selectbox('Jahr', data.dfs.keys())
    month = st.selectbox('Monat', data.dfs[year].keys())
    st.write(data.dfs[year][month])

if __name__ == '__main__':
    main()