import logging
import logging.config


root = logging.getLogger('tersocore')


def init_logging(config):
    logging.config.dictConfig(config)


def get_logger(name):
    return root.getChild(name)
