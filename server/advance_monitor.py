import threading
import queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time


class FileEvent:
    """
    אריזה של נתוני האירוע כדי שיהיה נוח להעביר אותם הלאה.
    """

    def __init__(self, event_type, src_path, dest_path=None, is_directory=False):
        self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.event_type = event_type
        self.src_path = src_path
        self.dest_path = dest_path
        self.is_directory = is_directory

    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'event_type': self.event_type,
            'src_path': self.src_path,
            'dest_path': self.dest_path,
            'is_directory': self.is_directory
        }


class _FSHandler(FileSystemEventHandler):
    """
    המחלקה שמקשיבה למערכת ההפעלה.
    הוספנו כאן מנגנון Cooldown כדי למנוע כפילויות.
    """

    def __init__(self, event_queue):
        super().__init__()
        self.event_queue = event_queue
        # מילון לשמירת הזמן האחרון שבו הקובץ שונה
        # המבנה: { 'path/to/file': timestamp }
        self.last_modified_times = {}
        self.cooldown_seconds = 1.0  # זמן המתנה בשניות בין התראות כפולות

    def on_created(self, event):
        if not event.is_directory:
            self.event_queue.put(FileEvent('created', event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            return

        current_time = time.time()

        # בדיקה האם הקובץ הזה כבר דווח בשנייה האחרונה
        if event.src_path in self.last_modified_times:
            last_time = self.last_modified_times[event.src_path]
            # אם עבר פחות זמן מה-Cooldown, אנחנו מתעלמים (יוצאים מהפונקציה)
            if current_time - last_time < self.cooldown_seconds:
                return

        # מעדכנים את הזמן האחרון ושולחים את האירוע
        self.last_modified_times[event.src_path] = current_time
        self.event_queue.put(FileEvent('modified', event.src_path))

    def on_deleted(self, event):
        if not event.is_directory:
            # אם קובץ נמחק, מסירים אותו גם מהזיכרון של ה-Cooldown כדי לא לתפוס מקום
            if event.src_path in self.last_modified_times:
                del self.last_modified_times[event.src_path]
            self.event_queue.put(FileEvent('deleted', event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self.event_queue.put(FileEvent('moved', event.src_path, dest_path=event.dest_path))


class FileWatcher(threading.Thread):
    def __init__(self, path, event_queue):
        super().__init__(daemon=True)
        self.path = path
        self.event_queue = event_queue
        self.observer = Observer()

    def run(self):
        handler = _FSHandler(self.event_queue)
        self.observer.schedule(handler, self.path, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()


class EventProcessor(threading.Thread):
    def __init__(self, event_queue, server):
        super().__init__(daemon=True)
        self.event_queue = event_queue
        self.server = server

    def run(self):
        while True:
            event = self.event_queue.get()
            # שליחה לשרת
            self.server.broadcast(event.to_dict())
            self.event_queue.task_done()