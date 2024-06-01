import openpyxl
import pandas as pd
pd.options.mode.copy_on_write=True
import streamlit as st
from copy import copy
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from dateutil.relativedelta import relativedelta
import calendar
import locale
try:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
except:
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

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

def interval(years, tab_number):
    if st.checkbox("Jahre ausschließen", key="exclude_years_check"+str(tab_number)):
        max_year = st.selectbox("Alle Jahre ausschließen bis einschließlich:", years, key="selectbox_exclude_years"+str(tab_number))
    
        for w in years[:years.index(max_year)+1]:
            years.remove(w)

    selectable_options = utils.calculate_slider_values_interval(years, 'Januar')
    
    start_date, end_date = st.select_slider(
        'Zeitspanne',
        options=selectable_options,
        value=(selectable_options[0], selectable_options[-1]),
        key="interval_select_slider"+str(tab_number))
    
    start_year = start_date.split()[1]
    start_month = start_date.split()[0]

    end_year = end_date.split()[1]
    end_month = end_date.split()[0]

    return start_year, start_month, end_year, end_month

def yearly(years, tab_number):
    start_year = st.selectbox('Jahr', years, index=len(years)-1, key='Jahr_yearly'+str(tab_number))
    end_year = start_year

    start_month = 'Januar'
    end_month = 'Dezember'

    return start_year, start_month, end_year, end_month

def monthly(years, tab_number):
    start_year = st.selectbox('Jahr', years, index=len(years)-1, key='Jahr_monthly'+str(tab_number))
    end_year = start_year

    months = list(st.session_state.month_map.keys())

    start_month = st.selectbox('Monat', months, index=months.index(calendar.month_name[datetime.now().month]), key='Monat_monthly'+str(tab_number))
    end_month = start_month

    return start_year, start_month, end_year, end_month

def build_interval_df(data, start_year, start_month, end_year, end_month):
    months = list(st.session_state.month_map.keys())

    column_names_unified = ['Betrag', 'Beschreibung', 'Kategorie', "Year", "Month"]
    interval_df = pd.DataFrame(columns=column_names_unified)
    dfs = copy(data.dfs)

    if start_year != end_year:

        for y in range(int(start_year), int(end_year)+1 , 1):
            if str(y) == start_year:
                for m in months[months.index(start_month):]:
                    df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
                    df["Year"]=y
                    df["Month"]=st.session_state.month_map[m]+1
                    interval_df = pd.concat([interval_df, df], ignore_index=True)
            elif str(y) == end_year:
                for m in months[:months.index(end_month)+1]:
                    df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
                    df["Year"]=y
                    df["Month"]=st.session_state.month_map[m]+1
                    interval_df = pd.concat([interval_df, df], ignore_index=True)
            else:
                for m in months:
                    df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
                    df["Year"]=y
                    df["Month"]=st.session_state.month_map[m]+1
                    interval_df = pd.concat([interval_df, df], ignore_index=True)

    else:
        for m in months[months.index(start_month):months.index(end_month)+1]:
            y = int(start_year)
            df = dfs[y][m].rename(columns=dict(zip(dfs[y][m].columns, column_names_unified)))
            df["Year"]=y
            df["Month"]=st.session_state.month_map[m]+1
            interval_df = pd.concat([interval_df, df], ignore_index=True)

    return interval_df

def sunburst_chart(interval_df):
    kategorien = sorted(list(interval_df['Kategorie'].drop_duplicates()))
    
    try:
        kategorien.remove('Gehalt')
    except:
        pass

    values = []
    to_remove = []

    for k in kategorien:
        summe = interval_df.loc[interval_df['Kategorie']==k, 'Betrag'].sum()
        if summe > 0:
            to_remove.append(k)
        else:
            values.append(abs(summe))

    for k in to_remove:
        kategorien.remove(k)

    df = pd.DataFrame(columns=['Kategorie', 'Summe'])
    df['Kategorie'] = kategorien
    df['Summe'] = values

    fig = px.sunburst(df, path=['Kategorie'], values='Summe')
    fig.update_layout(margin=dict(t=0, l=0, r=0, b=0))

    return fig

def waterfall_chart(interval_df):
    kategorien = sorted(list(interval_df['Kategorie'].drop_duplicates()))

    values = []
    total = 0
    measure = []

    for k in kategorien:
        summe = interval_df.loc[interval_df['Kategorie']==k, 'Betrag'].sum()
        total = total + summe
        values.append(round(summe,2))
        measure.append('relative')

    kategorien.append('Summe')
    values.append(round(total,2))
    measure.append('total')

    fig = go.Figure(go.Waterfall(
        orientation = "v",
        measure = measure,
        x = kategorien,
        textposition = "outside",
        text = values,
        y = values,
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))

    return fig

def pareto_chart(interval_df):
    kategorien = sorted(list(interval_df['Kategorie'].drop_duplicates()))

    values = []
    to_remove = []

    for k in kategorien:
        summe = interval_df.loc[interval_df['Kategorie']==k, 'Betrag'].sum()
        if summe > 0:
            to_remove.append(k)
        else:
            values.append(abs(summe))

    for k in to_remove:
        kategorien.remove(k)

    df = pd.DataFrame(columns=['Kategorie', 'Betrag', 'Betrag single'])
    df['Kategorie'] = kategorien
    df['Betrag single'] = values
    total = sum(values)
    threshold = 0
    is_threshold = False
    df.sort_values(by=['Betrag single'], ascending=False, inplace=True, ignore_index=True)

    for k in range(len(kategorien)):
        trace_values = []

        for i in range(k):
            trace_values.append(0.0)

        for i in range(len(kategorien)-k):
            trace_values.append(round(float(df.loc[k, 'Betrag single']) / total,2))

        threshold += round(float(df.loc[k, 'Betrag single']) / total,2)
        if threshold > 0.8 and not is_threshold:
            threshold_index = k
            is_threshold = True
        
        df.loc[k, 'Betrag'] = str(trace_values)

    for k in range(threshold_index+1):
        if k == 0:
            fig = go.Figure(go.Bar(x=df.loc[:threshold_index,'Kategorie'], y=eval(df.loc[k,'Betrag']), name=df.loc[k,'Kategorie']))
        else:
            fig.add_trace(go.Bar(x=df.loc[:threshold_index,'Kategorie'], y=eval(df.loc[k,'Betrag']), name=df.loc[k,'Kategorie']))

    fig.update_layout(barmode='stack', xaxis={'categoryorder':'total ascending'})

    return fig

def collect_data(data, tab_number):
    option = st.selectbox('Addition über welche Art von Zeitraum?',['Intervall', 'Jährlich', 'Monat'], key="option_selectbox_interval"+str(tab_number))

    if option == 'Intervall':
        start_year, start_month, end_year, end_month = interval(list(data.dfs.keys()), tab_number)
    
    elif option == 'Jährlich':
        start_year, start_month, end_year, end_month = yearly(list(data.dfs.keys()), tab_number)
    
    elif option == 'Monat':
        start_year, start_month, end_year, end_month = monthly(list(data.dfs.keys()), tab_number)
    
    interval_df = build_interval_df(data, start_year, start_month, end_year, end_month)
    with st.expander('Daten'):
        st.write(interval_df)

    return interval_df

def collect_data_forecast(data, tab_number):
   
    start_year, start_month, end_year, end_month = interval(list(data.dfs.keys()), tab_number)

    interval_df = build_interval_df(data, start_year, start_month, end_year, end_month)
    with st.expander('Daten'):
        st.write(interval_df)

    return interval_df

        
def create_date(row):
    return datetime.strptime(f"01.{str(row['Month'])}.{str(row['Year'])}", "%d.%m.%Y").date()

def main():
    st.title("Finanzen")

    dfs = get_data()

    data = fin(dfs)

    tabs = st.tabs(['Addition','Kategorie','Prognose'])

    with tabs[0]:

        interval_df = collect_data(data, 0)

        subtabs = st.tabs(['Sunburst', 'Wasserfall', 'Pareto'])    

        with subtabs[0]:
            st.plotly_chart(sunburst_chart(interval_df))

        with subtabs[1]:
            st.plotly_chart(waterfall_chart(interval_df))

        with subtabs[2]:
            st.plotly_chart(pareto_chart(interval_df))        


    with tabs[1]:
        
        interval_df = collect_data(data, 1)

        grouped_df = interval_df.groupby(['Kategorie', 'Year', 'Month'])['Betrag'].sum().reset_index()
        
        distinct_categories = grouped_df['Kategorie'].unique()
        category = st.selectbox("Kategorie", distinct_categories)
        filtered_df = grouped_df.query(f"Kategorie == '{category}'")

        # Apply the function to each row
        filtered_df['Datum'] = filtered_df.apply(create_date, axis=1)
        with st.expander("Gefilterte Daten"):
            st.write(filtered_df)

        delta = relativedelta(filtered_df['Datum'].max(), filtered_df['Datum'].min())
    
        # Calculate the total number of months
        count_value = delta.years * 12 + delta.months + 1
       
        sum_value = filtered_df['Betrag'].sum()
        year_fraction = count_value / 12

        filtered_df['Durchschnitt'] = sum_value/count_value

        subtabs_category = st.columns(3)

        with subtabs_category[0]:
            with st.container(border = True):
                st.write("**Summe**")
                st.write(str(locale.currency(sum_value)))

        with subtabs_category[1]:
            with st.container(border = True):
                st.write("**Monatlich**")
                st.write(str(locale.currency(sum_value/count_value)))

        with subtabs_category[2]:
            with st.container(border = True):
                st.write("**Jährlich**")
                st.write(str(locale.currency(sum_value/year_fraction)))

        fig = px.bar(filtered_df, x='Datum', y='Betrag')
        fig.add_scatter(x=filtered_df['Datum'], y=filtered_df['Durchschnitt'], mode='lines', name="Durchschnitt", line=dict(color='rgba(255, 0, 0, 1)'))
        st.plotly_chart(fig, use_container_width=True)

    with tabs[2]:
        interval_df = collect_data_forecast(data, 2)

        interval_df['Datum'] = interval_df.apply(create_date, axis=1)

        delta = relativedelta(interval_df['Datum'].max(), interval_df['Datum'].min())
    
        # Calculate the total number of months
        count_value = delta.years * 12 + delta.months + 1

        grouped_df = interval_df.groupby(['Datum'])['Betrag'].sum().reset_index()
        
        monthly_mean = grouped_df["Betrag"].mean()
        grouped_df["Durchschnitt"] = monthly_mean
        grouped_df["Durchschnitt acc"] = 0.0
        grouped_df["Betrag acc"] = 0.0

        for i in range(len(grouped_df)):
            if i == 0:
                grouped_df.loc[i, "Durchschnitt acc"] = grouped_df["Durchschnitt"].loc[i]
                grouped_df.loc[i, "Betrag acc"] = grouped_df["Betrag"].loc[i]
            else:
                grouped_df.loc[i, "Durchschnitt acc"] = grouped_df["Durchschnitt acc"].loc[i-1] + grouped_df["Durchschnitt"].loc[i]
                grouped_df.loc[i, "Betrag acc"] = grouped_df["Betrag acc"].loc[i-1] + grouped_df["Betrag"].loc[i]

        Sparziel = st.number_input("Sparziel", min_value=0, max_value=1000000, value=200000, step=1)
        ausgangspunkt = grouped_df.loc[grouped_df.index[-1], "Durchschnitt acc"]
        anzahl_monate = (Sparziel-ausgangspunkt)/monthly_mean

        endzeitpunkt = grouped_df["Datum"].max() + relativedelta(months=int(anzahl_monate + 1))
        st.write("Ziel wird erreicht werden: " + str(endzeitpunkt))

        neuer_index = grouped_df.index[-1]+1
        grouped_df.loc[neuer_index, "Durchschnitt acc"] = ausgangspunkt  + monthly_mean * int(anzahl_monate+1)
        grouped_df.loc[neuer_index, "Datum"] = endzeitpunkt

        fig = px.line(grouped_df, x='Datum', y='Betrag acc')
        fig.add_scatter(x=grouped_df['Datum'], y=grouped_df['Durchschnitt acc'], name="Durchschnitt", mode="lines")
        st.plotly_chart(fig, use_container_width=True)
            

if __name__ == '__main__':
    main()