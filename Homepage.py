import streamlit as st

from src import utils
utils.session_state_helper()

from src.NAS_connection import DatabaseConnectionHandler as DBCHandler

def main():
    st.title('NAS Verbindung für Daten-Update')

    with st.form('NAS_credentials'):
        cols = st.columns(2)
        
        with cols[0]:
            ip = st.text_input('IP:')
            share = st.text_input('Verzeichnis:')

        with cols[1]:
            usr = st.text_input('Benutzer:')
            pwd = st.text_input('Passwort:', type="password")

        st.form_submit_button('Update')

    if usr != '':
        nas = DBCHandler(ip=ip, share=share, username=usr, password=pwd)

        try:
            nas.connect_to_network_storage()
            print('Connection established')

            try:
                nas.update_database()
                print('Updated the database')
            except:
                st.write(':red[Could not complete update]')

            try:
                nas.end_connection()
                print('Terminate connection')
            except:
                st.write(':red[Termination of connection went wrong]')

            try:
                nas.list_files_in_directory()
            except:
                st.write('Done.')
                print('Succesfully terminated connection')

        except:
            st.write(':red[Could not connect to NAS]')         


if __name__ == '__main__':
    main()