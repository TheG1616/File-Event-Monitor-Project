import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class FileEventHandler(FileSystemEventHandler):
    """
    Handles file system events (Create, Delete, Modify, Move).
    מחלקה זו יורשת מ-Watchdog ואחראית לטפל באירועים בזמן אמת.
    """

    def on_created(self, event):
        # אירוע יצירה: מופעל כאשר נוצר קובץ חדש
        if not event.is_directory:
            print(f"[+] File Created: {event.src_path}")

    def on_deleted(self, event):
        # אירוע מחיקה: מופעל כאשר קובץ נמחק
        if not event.is_directory:
            print(f"[-] File Deleted: {event.src_path}")

    def on_modified(self, event):
        # אירוע שינוי: מופעל כאשר קובץ נערך או נשמר
        if not event.is_directory:
            # סינון קבצים זמניים (כדי למנוע רעש מיותר בלוגים)
            if not event.src_path.endswith('~') and not event.src_path.endswith('.tmp'):
                print(f"[*] File Modified: {event.src_path}")

    def on_moved(self, event):
        # אירוע העברה: מופעל כאשר משנים שם לקובץ או מעבירים אותו
        if not event.is_directory:
            print(f"[>] File Moved: From {event.src_path} To {event.dest_path}")


class FileMonitor:
    """
    Manages the monitoring process (Start/Stop).
    מחלקה שמנהלת את התהליך (מתחילה ומפסיקה את ההאזנה לתיקייה).
    """

    def __init__(self, path_to_watch):
        self.path = path_to_watch
        self.observer = Observer()
        self.handler = FileEventHandler()

    def start(self):
        # התחלת הניטור
        print(f"--- Monitoring Started on: {self.path} ---")
        # schedule מחבר בין המאזין (Observer) לבין המטפל באירועים (Handler)
        self.observer.schedule(self.handler, self.path, recursive=True)
        self.observer.start()
        try:
            # לולאה אינסופית ששומרת את התוכנית רצה
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        # עצירת הניטור בצורה מסודרת
        self.observer.stop()
        self.observer.join()
        print("\n--- Monitoring Stopped ---")


# --- Test Block (בדיקה עצמית) ---
# הקוד הזה ירוץ רק אם נפעיל את הקובץ הזה ישירות
if __name__ == "__main__":
    # ננטר את התיקייה הנוכחית לצורך בדיקה
    current_folder = "./saved_files"
    monitor = FileMonitor(current_folder)
    monitor.start()