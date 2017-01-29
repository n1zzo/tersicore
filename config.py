from configparser import ConfigParser
import os.path


CONFIG_FILES = ['config.ini', 'logging.conf']
DEFAULT_PATHS = ['/etc/tersicore/', '/usr/local/etc/tersicore/', 'conf/']


def get_config_path():
    for p in DEFAULT_PATHS:
        if all([os.path.isfile(os.path.join(p, f)) for f in CONFIG_FILES]):
            return p
    else:
        raise Exception('Unable to find a configuration folder.')


def get_config(path=None):
    "Load the configuration"
    config = ConfigParser()  # dict-like structure
    if path:
        config.read(path)
    else:
        path = get_config_path()
        f = os.path.join(path, 'config.ini')
        config.read(f)
    return config
