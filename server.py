import socket 
from threading import Thread 
import sqlite3 
import json 
from http.server import BaseHTTPRequestHandler, HTTPServer
 
SERVER_HOST = "0.0.0.0" 
SERVER_PORT = 5002 
separator_token = "<SEP>" 

# Устанавливаем соединение с базой данных SQLite 
connection = sqlite3.connect('users.db') 
cursor = connection.cursor() 

# Создаем таблицу Users 
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS Users ( 
id INTEGER PRIMARY KEY, 
username TEXT NOT NULL, 
password TEXT NOT NULL 
) 
''') 

# Сохраняем изменения и закрываем соединение 
connection.commit() 
connection.close() 

client_sockets = set() 
s = socket.socket() 
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
s.bind((SERVER_HOST, SERVER_PORT)) 
s.listen(5) 
print(f"[] Listening as {SERVER_HOST}:{SERVER_PORT}") 

def register_user(username, password): 
    connection = sqlite3.connect('users.db') 
    cursor = connection.cursor() 
    cursor.execute("INSERT INTO Users (username, password) VALUES (?, ?)", (username, password)) 
    connection.commit() 
    connection.close() 
    return True 

def login_user(username, password): 
    connection = sqlite3.connect('users.db') 
    cursor = connection.cursor() 
    cursor.execute("SELECT * FROM Users WHERE username = ? AND password = ?", (username, password)) 
    user = cursor.fetchone() 
    connection.close() 
    if user: 
        return True 
    else: 
        return False 

def listen_for_client(cs): 
    while True: 
        try: 
            # keep listening for a message from cs socket 
            msg = cs.recv(1024).decode() 
        except Exception as e: 
            # client no longer connected 
            # remove it from the set 
            print(f"[!] Error: {e}") 
            client_sockets.remove(cs) 
        else: 
            # if we received a message, replace the <SEP>  
            # token with ": " for nice printing 
            msg = msg.replace(separator_token, ": ") 
        # iterate over all connected sockets 
        for client_socket in client_sockets: 
            # and send the message 
            client_socket.send(msg.encode()) 

class RequestHandler(BaseHTTPRequestHandler): 
    def do_POST(self): 
        content_length = int(self.headers['Content-Length']) 
        post_data = self.rfile.read(content_length) 
        user_data = json.loads(post_data) 

        if self.path == '/register': 
            username = user_data.get('username') 
            password = user_data.get('password') 

            register_user(username, password) 

            self.send_response(200) 
            self.end_headers() 
            self.wfile.write("User registered successfully".encode()) 

        elif self.path == '/login': 
            username = user_data.get('username') 
            password = user_data.get('password') 

            if login_user(username, password): 
                self.send_response(200) 
                self.end_headers() 
                self.wfile.write("Login successful".encode()) 
            else: 
                self.send_response(401) 
                self.end_headers() 
                self.wfile.write("Invalid credentials".encode()) 

def start_server(): 
    server = HTTPServer(('localhost', 8000), RequestHandler) 
    server.serve_forever() 

server_thread = Thread(target=start_server) 
server_thread.daemon = True 
server_thread.start() 

while True: 
    client_socket, client_address = s.accept() 
    print(f"[+] {client_address} connected.") 
    client_sockets.add(client_socket) 

    t = Thread(target=listen_for_client, args=(client_socket,)) 
    t.daemon = True 
    t.start() 

for cs in client_sockets: 
    cs.close() 

s.close()