import os.path
from configparser import ConfigParser
import yaml


DEFAULT_FILES = {
    'tersicore': 'tersicore.conf',
    'logging': 'logging.conf'
    }

DEFAULT_PATHS = ['/etc/tersicore/', '/usr/local/etc/tersicore/', '.']


def get_default_path():
    for p in DEFAULT_PATHS:
        files = [f for f in DEFAULT_FILES.values()]
        are_files = [
            os.path.isfile(os.path.join(p, f))
            for f in files
        ]
        if all(are_files):
            return p
    else:
        raise Exception('Unable to find a configuration folder.')


class Config:
    def __init__(self, basedir=None, tersicore_file=None, logging_file=None):
        if basedir is None:
            self.basedir = get_default_path()
        else:
            self.basedir = basedir

        if tersicore_file is None:
            tersicore_file = DEFAULT_FILES['tersicore']

        if logging_file is None:
            logging_file = DEFAULT_FILES['logging']

        self.tersicore_config_path = os.path.join(self.basedir, tersicore_file)
        self.logging_config_path = os.path.join(self.basedir, logging_file)

        self.tersicore = ConfigParser()
        self.logging = None

        self.read()

    def read(self):
        self.tersicore.read(self.tersicore_config_path)
        self.logging = yaml.load(open(self.logging_config_path, 'r'))
