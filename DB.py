import configparser
import pyodbc

#class DB:
#    def _init()
#    def add_track(path, tag) -> ID
#    def update_track(ID, tag)
#    def get_path(ID) -> path
#    def get_tag(ID) -> tag
#    def search_keyword(keyword) -> IDlist

class DB:
    cnxn = None

    def __init__(self):
        # Parse configuration file and generate connection string
        config = configparser.ConfigParser()
        config.read('config.ini')

        driver = config['DATABASE']['Driver']
        server = config['DATABASE']['Server']
        port = config['DATABASE']['Port']
        database = config['DATABASE']['Database']
        uid = config['DATABASE']['UID']
        password = config['DATABASE']['Password']

        conn_string = ('DRIVER='+driver+';SERVER='+server+';PORT='+port+
                     ';DATABASE='+database+';UID='+uid+';PWD='+password)
        self.cnxn = pyodbc.connect(conn_string)

if __name__ == "__main__":
    db = DB()

