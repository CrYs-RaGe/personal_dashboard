from smb.SMBConnection import SMBConnection
import pathlib

import multiprocessing
import time

def worker(queue, conn, ip):
    try:
        result = conn.connect(ip, 139)
        queue.put(result)
    except Exception as e:
        queue.put(e)

class DatabaseConnectionHandler():

    def __init__(self, ip, share, username, password):
        self._ip_address = ip
        self._share_name = share
        self._username = username
        self._password = password

    def connect_to_network_storage(self):
        conn = SMBConnection(self._username, self._password, "your_client_name", "server_name", use_ntlm_v2=True)
        
        # Set the timeout value in seconds
        timeout_seconds = 3

        # Create a multiprocessing Queue to communicate with the worker process
        result_queue = multiprocessing.Queue()

        # Create a Process and start it
        process = multiprocessing.Process(target=worker, args=(result_queue, conn, self._ip_address,))
        process.start()

        # Wait for the process to finish or timeout
        process.join(timeout=timeout_seconds)

        # Check if the process is still alive
        if process.is_alive():
            # Terminate the process if it's still running
            process.terminate()
            process.join()

            print("Function execution timed out")
        else:
            conn_new = result_queue.get()

            if isinstance(conn, Exception):
                print(f"Function execution failed: {conn_new}")
            else:
                print("Function executed successfully")
                conn.connect(self._ip_address, 139)

        # Connect to the share
        share_list = conn.listShares()
        for share in share_list:
            if self._share_name.lower() == share.name.lower():
                self._connection = conn
                self._share = share

        if not self._connection:
            raise Exception(f"Share '{self._share_name}' not found on the server.")
    
        print('Succesfully connected to server')

    def end_connection(self):
        if self._connection:
            self._connection.close()
            print('Disconnected')

    def update_database(self):
        
        smb_paths = [
            "/Dokumente/Finanzen/Finanzen gesamt.xlsx",
            "/Dokumente/Finanzen/Energieverbrauch.xlsx"
        ]

        local_paths = [
            "./data/Finanzen_gesamt.xlsx",
            "./data/Energieverbrauch.xlsx"
        ]

        # create data folder if not already exists
        pathlib.Path('data').mkdir(parents=True, exist_ok=True) 

        for i in range(len(smb_paths)):

            with open(local_paths[i], 'wb') as local_file:
                self._connection.retrieveFile(self._share.name, smb_paths[i], local_file)
            
            print(f"File '{smb_paths[i]}' copied to '{local_paths[i]}'")

    def list_files_in_directory(self, path_to_print : str = "/Dokumente/Finanzen/"):
        files = self._connection.listPath(self._share.name, path_to_print)
        print(f"Files in {path_to_print}")
        for file_info in files:
            print(file_info.filename)