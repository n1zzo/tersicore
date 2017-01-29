from config import get_config_path

import os
import yaml

import logging
import logging.config


config_file = os.path.join(get_config_path(), 'logging.conf')
config_dict = yaml.load(open(config_file, 'r'))

logging.config.dictConfig(config_dict)


def get_logger(name):
    root = logging.getLogger('tersicore')
    return root.getChild(name)
