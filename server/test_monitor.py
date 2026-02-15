import time
import queue
from advance_monitor import FileWatcher, EventProcessor

# 1. יצירת "שרת מזויף" (Mock)
class MockServer:
    """
    מחלקה זו מתחזה לשרת האמיתי.
    במקום לשלוח ברשת, היא פשוט מדפיסה למסך.
    """
    def broadcast(self, message):
        print(f"\n[SERVER MOCK] התקבלה הודעה לשידור:")
        print(f"   מתי: {message['timestamp']}")
        print(f"   מה קרה: {message['event_type']}")
        print(f"   איפה: {message['src_path']}")
        print("-" * 50)

# 2. הגדרות ראשוניות
path_to_watch = "."  # ננטר את התיקייה הנוכחית
event_q = queue.Queue() # יצירת התור
fake_server = MockServer() # יצירת השרת המזויף

# 3. יצירת הרכיבים שלנו (מהקוד שכתבנו)
watcher = FileWatcher(path_to_watch, event_q)
processor = EventProcessor(event_q, fake_server)

# 4. הפעלה
print(f"--- מתחיל בדיקה על התיקייה: {path_to_watch} ---")
watcher.start()     # מתחיל להאזין לקבצים
processor.start()   # מתחיל להאזין לתור

# 5. השארת התוכנית רצה
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("בדיקה הסתיימה.")