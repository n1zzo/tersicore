import argparse

from tersicore.config import Config
from tersicore.log import init_logging
from tersicore.database import Database
from tersicore.mediascanner import MediaScanner


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--config-dir')
    parser.add_argument('--tersicore-config')
    parser.add_argument('--logging-config')

    args = parser.parse_args()

    config = Config(
        basedir=args.config_dir,
        tersicore_file=args.tersicore_config,
        logging_file=args.logging_config)

    logging_config = config.logging

    init_logging(logging_config)

    config_database = config.tersicore['DATABASE']
    database = Database(**config_database)

    config_scanner = config.tersicore['SCANNER']
    config_mediascanner_paths = str(config_scanner['Path']).split(',')
    config_mediascanner_formats = str(config_scanner['Formats']).split(',')

    mediascanner = MediaScanner(
        paths=config_mediascanner_paths,
        formats=config_mediascanner_formats,
        database=database)

    mediascanner.run()


if __name__ == '__main__':
    main()
