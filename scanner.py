from config import get_config
from time import sleep
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler


class Handler(PatternMatchingEventHandler):
    def on_any_event(self, event):
        print(event.src_path, event.event_type)


class Scanner(Observer):
    def __init__(self, path):
        super().__init__()
        handler = Handler(ignore_directories=True)
        self.schedule(handler, path, recursive=True)


if __name__ == "__main__":
    conf = get_config()
    path = conf["SCANNER"]["path"]
    scanner = Scanner(path)
    scanner.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        scanner.stop()
    scanner.join()
