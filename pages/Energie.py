import streamlit as st
import pandas as pd
import openpyxl
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

month_map = {
    'Januar':0,
    'Februar':1,
    'März':2, 
    'April':3, 
    'Mai':4, 
    'Juni':5, 
    'Juli':6, 
    'August':7, 
    'September':8, 
    'Oktober':9, 
    'November':10, 
    'Dezember':11
}

energy_map = {
    'absolut': {
        'Heizung': ['Heizung [kWh]', 'Durchschnitt Heizung [kWh]'],
        'Warmwasser': ['Warmwasser [kWh]', 'Durchschnitt Warmwaser [kWh]'],
        'Gesamt': ['Energieverbrauch [kWh]', 'Durchschnitt Energieverbrauch [kWh]']
    },
    'relativ': {
        'Heizung': ['Heizung [kWh/m²]', 'Durchschnitt Heizung [kWh/m²]'],
        'Warmwasser': ['Warmwasser [kWh/m²]', 'Durchschnitt Warmwaser [kWh/m²]'],
        'Gesamt': ['Energieverbrauch [kWh/m²]', 'Durchschnitt Energieverbrauch [kWh/m²]']
    }
}

def get_list_start_to_end(start, end, begin_list):
    try:
        # Find the indices of start and end values in the list
        start_index = begin_list.index(start)
        end_index = begin_list.index(end)

        # Extract the sublist using slicing
        result_list = begin_list[start_index:end_index + 1]

        return result_list
    except:
        print('begin list was not list but array')
    
        # Find the indices where the conditions are met
        start_index = np.where(begin_list == start)[0][0]
        end_index = np.where(begin_list == end)[0][0]

        # Extract the sublist using slicing
        result_array = begin_list[start_index:end_index + 1]

        return result_array


def interval_comparison(dfs):
    years = np.array(list(dfs.keys()))
    months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

    selectable_options = []

    for y in years:
        for m in months:
            if y != '2023' or (y == '2023' and m in ['Oktober', 'November', 'Dezember']):
                if int(y) < datetime.now().year:
                    selectable_options.append(m + ' ' + y)
                elif int(y) == datetime.now().year and month_map[m] < datetime.now().month:
                    selectable_options.append(m + ' ' + y)

    start_date, end_date = st.select_slider(
        'Zeitspanne',
        options=selectable_options,
        value=(selectable_options[0], selectable_options[-3]))
 
    result_list = get_list_start_to_end(start_date, end_date, selectable_options)

    start_year = start_date.split()[1]
    start_month = start_date.split()[0]

    end_year = end_date.split()[1]
    end_month = end_date.split()[0]

    result_array = get_list_start_to_end(start_year, end_year, years)

    cols = st.columns(2)
    with cols[0]:
        comparison_type = st.selectbox('Absoluter oder relativer Vergleich', ['absolut', 'relativ'])

    with cols[1]:
        energy_type = st.selectbox('Art des Energieverbrauchs', ['Heizung', 'Warmwasser', 'Gesamt'])

    df_melted_total = pd.DataFrame()

    for option in result_array:
        
        # select dataframe for right year
        df = dfs[option]
        df.replace(np.nan, 0, inplace=True)

        if str(start_year) == str(end_year):
            df = df.loc[month_map[start_month]:month_map[end_month]]
        elif str(option) == str(start_year):
            # select dataframe for month range
            df = df.loc[month_map[start_month]:]
        elif str(option) == str(end_year):
            # select dataframe for month range
            df = df.loc[:month_map[end_month]]
                
        # Melt the DataFrame to make it suitable for grouped bar chart
        df_melted = pd.melt(df, id_vars=['Monat'], var_name='Variable', value_name='Value', 
                            value_vars=energy_map[comparison_type][energy_type])
        
        df_melted['Monat'] = df_melted['Monat'] + ' ' + option
        
        df_melted_total = pd.concat([df_melted_total,df_melted])

    # st.plotly_chart(interval_bar_chart(df_melted_total))
    st.plotly_chart(interval_line_chart(df_melted_total), use_container_width=True)

    df_melted_total_act = df_melted_total[df_melted_total['Variable'] == energy_map[comparison_type][energy_type][0]]
    df_melted_total_tar = df_melted_total[df_melted_total['Variable'] == energy_map[comparison_type][energy_type][1]]

    avg_act = np.average(df_melted_total_act['Value'])
    avg_tar = np.average(df_melted_total_tar['Value']) 

    interval_kpis(avg_act, avg_tar, comparison_type)

def interval_bar_chart(df):
    # Create an interactive grouped bar chart using Plotly Express
    fig = px.bar(df, x='Monat', y='Value', color='Variable',
                 # title='Unser gegen den durchschnittlichen Energieverbrauch',
                 labels={'Value': 'Energieverbrauch', 'Monat': 'Monat', 'Variable': 'Variables'},
                 barmode='group')  # Use 'stack' for stacked bar

    # Show the interactive chart
    return fig

def interval_line_chart(df):
    # Create a line chart using Plotly Graph Objects
    fig = go.Figure()

    # Create lines for each variable
    for variable in df['Variable'].unique():
        df_variable = df[df['Variable'] == variable]
        fig.add_trace(go.Scatter(x=df_variable['Monat'], y=df_variable['Value'],
                                 mode='lines+markers',  # You can choose 'lines' or 'markers' as needed
                                 name=variable))

    # Update layout
    fig.update_layout(xaxis_title='Monat',
                      yaxis_title='Energieverbrauch',
                      legend_title='Variables')

    # Show the interactive chart
    return fig

def interval_kpis(avg_act, avg_tar, comparison_type):
    if avg_tar != 0:
        comparison_kpi = round(( 1 - avg_act / avg_tar ) * 100, 2)
    else:
        comparison_kpi = None

    if comparison_kpi is not None:
        if comparison_type == 'absolut':
            if comparison_kpi > 0:
                st.write(f'''Der durchschnittliche Energieverbrauch ist mit {round(avg_act, 2)}kWh etwa 
                         :green[{comparison_kpi}%] niedriger als der Energieverbrauch des durchschnittlichen Haushalts.''')
            else:
                st.write(f'''Der durchschnittliche Energieverbrauch ist mit {round(avg_act, 2)}kWh etwa 
                         :red[{abs(comparison_kpi)}%] höher als der Energieverbrauch des durchschnittlichen Haushalts.''')
        else:
            if comparison_kpi > 0:
                st.write(f'''Der durchschnittliche Energieverbrauch ist mit {round(avg_act, 2)}kWh/m² etwa 
                         :green[{comparison_kpi}%] niedriger als der Energieverbrauch des durchschnittlichen Haushalts.''')
            else:
                st.write(f'''Der durchschnittliche Energieverbrauch ist mit {round(avg_act, 2)}kWh/m² etwa 
                         :red[{abs(comparison_kpi)}%] höher als der Energieverbrauch des durchschnittlichen Haushalts.''')
    else:
        st.write('No data')

def get_data():
    # Open an existing Excel file
    workbook = openpyxl.load_workbook('data/Energieverbrauch.xlsx')

    # Get a list of sheet names
    sheet_names = workbook.sheetnames

    dfs = {}

    for sname in sheet_names:
        dfs[sname] = pd.read_excel('data/Energieverbrauch.xlsx', sheet_name=sname)

    # Close the workbook
    workbook.close()

    return dfs

def yearly_comparison(dfs):
    cols = st.columns(2)
    with cols[0]:
        comparison_type = st.selectbox('Absoluter oder relativer Vergleich', ['absolut', 'relativ'], key='comparison_type_2')

    with cols[1]:
        energy_type = st.selectbox('Art des Energieverbrauchs', ['Heizung', 'Warmwasser', 'Gesamt'], key='energy_type_2')

    st.plotly_chart(yearly_line_chart(dfs, comparison_type, energy_type), use_container_width=True)

def yearly_line_chart(dfs, comparison_type, energy_type):
    years = np.array(list(dfs.keys()))

    years = st.multiselect('Welche Jahre sollen verglichen werden?',years,default=years)

    # Create a line chart using Plotly Graph Objects
    fig = go.Figure()

    show_average = st.checkbox('Zeige den durchschnittlichen Verbrauch')

    df_trendline = dfs[years[0]][['Monat', energy_map[comparison_type][energy_type][0]]]

    # Create lines for each variable
    for y in years:
        if y != years[0]:
            df_add = dfs[y][energy_map[comparison_type][energy_type][0]]
            df_add[df_add.isnull()] = 0
            df_trendline[energy_map[comparison_type][energy_type][0]] = df_trendline[energy_map[comparison_type][energy_type][0]]+df_add

        fig.add_trace(go.Scatter(x=dfs[y]['Monat'], y=dfs[y][energy_map[comparison_type][energy_type][0]],
                                 mode='lines+markers',  # You can choose 'lines' or 'markers' as needed
                                 name=y+' - '+energy_map[comparison_type][energy_type][0]))
        
        if show_average:
            fig.add_trace(go.Scatter(x=dfs[y]['Monat'], y=dfs[y][energy_map[comparison_type][energy_type][1]],
                                     mode='lines+markers',  # You can choose 'lines' or 'markers' as needed
                                     name=y+' - '+energy_map[comparison_type][energy_type][1]))

    if energy_type == 'Heizung':
        df_trendline[energy_map[comparison_type][energy_type][0]] = df_trendline[energy_map[comparison_type][energy_type][0]] / len(years)
        sum_value = np.sum(df_trendline[energy_map[comparison_type][energy_type][0]])
        
        if comparison_type == 'relativ':
            df_trendline[energy_map[comparison_type][energy_type][0]] = df_trendline[energy_map[comparison_type][energy_type][0]] * 26 / sum_value
        else:
            df_trendline[energy_map[comparison_type][energy_type][0]] = df_trendline[energy_map[comparison_type][energy_type][0]] * 2028 / sum_value

        fig.add_trace(go.Scatter(x=df_trendline['Monat'], y=df_trendline[energy_map[comparison_type][energy_type][0]],
                                 mode='lines+markers',  # You can choose 'lines' or 'markers' as needed
                                 name='Energieausweis'))

    # Update layout
    fig.update_layout(xaxis_title='Monat',
                      yaxis_title='Energieverbrauch',
                      legend_title='Jahre')

    # Show the interactive chart
    return fig

def monthly_comparison(dfs):
    cols = st.columns(2)
    with cols[0]:
        comparison_type = st.selectbox('Absoluter oder relativer Vergleich', ['absolut', 'relativ'], key='comparison_type_3')

    with cols[1]:
        energy_type = st.selectbox('Art des Energieverbrauchs', ['Heizung', 'Warmwasser', 'Gesamt'], key='energy_type_3')

    st.plotly_chart(monthly_bar_chart(dfs, comparison_type, energy_type), use_container_width=True)

def monthly_bar_chart(dfs, comparison_type, energy_type):
    years = np.array(list(dfs.keys()))

    years = st.multiselect('Welche Jahre sollen verglichen werden?',years,default=years, key='choose_year_2')

    # Create a line chart using Plotly Graph Objects
    fig = go.Figure()

    show_average = st.checkbox('Zeige den durchschnittlichen Verbrauch', key='average_2')

    months = ['Januar', 'Februar', 'März', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']
    month = st.selectbox('Monat', months)

    df_long = pd.DataFrame()
    df_long_average = pd.DataFrame()

    # Create lines for each variable
    for y in years:
        df = dfs[y]
        df = df.loc[df['Monat'] == month]
        df['Jahr'] = y
        
        df_long = pd.concat([df_long, df[['Jahr', energy_map[comparison_type][energy_type][0]]]]) 
    
        df_long_average = pd.concat([df_long_average, df[['Jahr', energy_map[comparison_type][energy_type][1]]]])

    fig.add_trace(go.Bar(x=df_long['Jahr'], y=df_long[energy_map[comparison_type][energy_type][0]],
                             # mode='lines+markers',  # You can choose 'lines' or 'markers' as needed
                             name=y+' - '+energy_map[comparison_type][energy_type][0]))

    if show_average:
        fig.add_trace(go.Bar(x=df_long_average['Jahr'], y=df_long_average[energy_map[comparison_type][energy_type][1]],
                             # mode='lines+markers',  # You can choose 'lines' or 'markers' as needed
                             name=y+' - '+energy_map[comparison_type][energy_type][1]))

    # Update layout
    fig.update_layout(xaxis_title='Jahr',
                      yaxis_title='Energieverbrauch',
                      legend_title='Jahre',
                      xaxis_type='category')

    # Show the interactive chart
    return fig

def main():
    st.title('Energieverbrauch')

    dfs = get_data()

    tabs = st.tabs(['Interval', 'Jährlicher Vergleich', 'Monatlicher Vergleich'])

    with tabs[0]:
        interval_comparison(dfs)

    with tabs[1]:
        yearly_comparison(dfs)

    with tabs[2]:
        monthly_comparison(dfs)
    

if __name__ == "__main__":
    main()
    
    
