from config import get_config
from time import sleep
from os import walk
from os.path import splitext

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


class LibraryBuilder:

    supported_exts = [".mp3", ".flac", ".ogg"]

    def scanPath(self, path):
        for root, dirs, files in walk(path):
            if len(files) > 0:
                self.addFiles(files, root)

    def addFiles(self, files, path):
        for track in files:
            name, ext = splitext(path+track)
            if ext in self.supported_exts:
                print("Inserting file:")
                print(name)
                print("With extension:")
                print(ext)
                print("Having root:")
                print(path)
                # [TODO] Add file to db

if __name__ == "__main__":
    conf = get_config()
    path = conf["SCANNER"]["path"]

    builder = LibraryBuilder()
    builder.scanPath(path)

    scanner = Scanner(path)
    scanner.start()
    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        scanner.stop()
    scanner.join()
