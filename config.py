import configparser

class Config:
    DEFAULT_PATHS = ('config.ini', '/etc/antani/config.ini')

    path   = None
    config = configparser.ConfigParser()

    def __init__(self, path = None):
        if path == None:
            for p in DEFAULT_PATHS:
                if os.path.isfile(p):
                    self.path = p
                    break;
        else:
            self.path = path
        try:
            config.read(self.path)
        except ConfigParser.Error:
            # Handle it
            return

    def reload():
        try:
            config.read(self.path)
        except ConfigParser.Error:
            return
