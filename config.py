from configparser import ConfigParser
import os.path

DEFAULT_PATHS = 'config.ini', '/etc/musiclibrary/config.ini'


def get_config(path=None):
    "Load the configuration"
    config = ConfigParser()  # dict-like structure
    if path:
        config.read(path)
    else:
        for path in DEFAULT_PATHS:
            if os.path.isfile(path):
                config.read(path)
                break
        else:  # no break
            print("Config not found")  # TODO: logger
            # raise an exception?
    return config


# test
if __name__ == "__main__":
    print(dict(get_config()))
