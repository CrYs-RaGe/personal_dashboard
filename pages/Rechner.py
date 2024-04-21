import streamlit as st
from src.Sparplan import Sparplan
from datetime import datetime
import locale
try:
    locale.setlocale(locale.LC_ALL, 'de_DE.utf-8')
except:
    locale.setlocale(locale.LC_ALL, 'de_DE.UTF-8')

from src import utils
utils.session_state_helper()

def main():
    with st.expander("**ETF Sparplan**"):

        cols  = st.columns(2)
   
        with cols[0]:
            start_str = st.date_input("Beginn des Sparplans", format="DD.MM.YYYY")
            rate = st.number_input("Wertentwicklung in % p.a.", value=8.0) / 100
            interval = st.selectbox("Zahlungsintervall", ["monatlich","vierteljährlich","halbjährlich", "jährlich"])

        with cols[1]:
            end_str = st.date_input("Ende des Sparplans", format="DD.MM.YYYY", value=datetime.strptime("01.05.2067", "%d.%m.%Y").date())
            cost = st.number_input("Laufende Kosten in % p.a.", value=0.2) / 100
            amount = st.number_input("Sparrate in €", value=500)
        
        sp = Sparplan(start_str, end_str, rate, interval)

        sp.calculate(cost, amount)

        if st.checkbox("Zeige vollständige Berechnung"):
            st.table(sp.df)

        st.write("\n\n")        
        
        cols = st.columns(3)

        with cols[0]:
            with st.container(border = True):
                st.write("**Endwert**")
                st.write(str(locale.currency(sp.get_endwert(), grouping=True)))

        with cols[1]:
            with st.container(border = True):
                st.write("**Gewinn**")
                st.write(str(locale.currency(sp.get_kursgewinn(), grouping=True)))

        with cols[2]:
            with st.container(border = True):
                st.write("**Eingezahlt**")
                st.write(str(locale.currency(sp.get_eingezahlt(), grouping=True)))

        cols = st.columns(3)

        with cols[0]:
            with st.container(border = True):
                st.write("**Netto Endwert**")
                st.write(str(locale.currency(sp.get_endwert() - sp.get_steuer(), grouping=True)))

        with cols[1]:
            with st.container(border = True):
                st.write("**Netto Gewinn**")
                st.write(str(locale.currency(sp.get_kursgewinn() - sp.get_steuer(), grouping=True)))

        with cols[2]:
            with st.container(border = True):
                st.write("**Steuer**")
                st.write(str(locale.currency(sp.get_steuer(), grouping=True)))

        

if __name__ == '__main__':
    main()