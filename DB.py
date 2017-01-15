import configparser
import pyodbc

#class DB:
#    def _init()
#    def connect()
#    def add_track(path, tag) -> ID
#    def update_track(ID, tag)
#    def get_path(ID) -> path
#    def get_tag(ID) -> tag
#    def search_keyword(keyword) -> IDlist

class DB:
    conn_string = None
    cnxn = None
    cursor = None

    def __init__(self):
        # Parse configuration file and generate connection string
        config = configparser.ConfigParser()
        config.read('config.ini')

        driver = config['DATABASE']['Driver']
        server = config['DATABASE']['Server']
        port = config['DATABASE']['Port']
        database = config['DATABASE']['Database']
        socket = config['DATABASE']['Socket']
        uid = config['DATABASE']['UID']
        password = config['DATABASE']['Password']

        self.conn_string = ('DRIVER='+driver+';SERVER='+server+
                            ';PORT='+port+';DATABASE='+database+
                            ';SOCKET='+socket+';UID='+uid+';PWD='+password)

    def connect(self):
        self.cnxn = pyodbc.connect(self.conn_string)
        self.cursor = self.cnxn.cursor()

        self.cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        self.cnxn.setencoding(encoding='utf-8')

if __name__ == "__main__":
    db = DB()
    db.connect()

