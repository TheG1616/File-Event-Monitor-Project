import socket
from advance_monitor import FileWatcher, EventProcessor
import queue

class Secure_Server:
        def __init__(self, server_ip, port):
            self.server_ip = server_ip
            self.port = port
            self.list_of_clients = []
            self.socket_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        def start(self):
            self.socket_s.bind((self.server_ip, self.port))
            self.socket_s.listen(3)
            print(f"the server is listening in {self.server_ip} , {self.port}")
            while True:
                conn , addr = self.socket_s.accept()
                print(f"new client connected, {addr} wait to acknoldge")
                try:
                    password_received = conn.recv(1024).decode("utf-8")

                    if password_received == "1234": #בהמשך לכל לקוח סיסמא שונה אימות של חיבור אל השרת
                        print("succes")
                        conn.sendall("auth_ok".encode("utf-8"))
                        #פה בהמשך אנחנו נכניס אותו לרשימת הלקוחות שלנו
                        # self.list_of_clients.append(conn)

                    else:
                        print("fail")
                        conn.sendall("auth_faild".encode('utf-8'))
                        conn.close()
                except Exception as e:
                    print(f"error with, {addr}: {e}")
                    conn.close()


my_s = Secure_Server("0.0.0.0", 1111)
my_s.start()

