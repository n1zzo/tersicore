from config import get_config
from time import sleep
import os

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from fnmatch import fnmatch


def add_file(path):
    print("Adding:", path)


def update_file(path):
    print("Updating:", path)


class Scanner(Observer):
    class Handler(PatternMatchingEventHandler):
        def on_any_event(self, event):
            print(event.src_path, event.event_type)
            update_file(event.src_path)

    def __init__(self, path, patterns):
        super().__init__()

        self.patterns = patterns
        self.path = path

        handler = Scanner.Handler(patterns=patterns, ignore_directories=True)
        self.schedule(handler, path, recursive=True)

    def start(self):
        self.first_time_scan()
        super().start()

    def first_time_scan(self):
        for root, dirs, files in os.walk(path):
            for f in files:
                for pattern in self.patterns:
                    if fnmatch(f, pattern):
                        add_file(os.path.join(root, f))


if __name__ == "__main__":
    conf = get_config()
    path = conf["SCANNER"]["path"]

    # TODO: get patterns from config
    scanner = Scanner(path, ["*.mp3", "*.flac", "*.ogg"])
    scanner.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        scanner.stop()
    scanner.join()
