import socket
import random
from threading import Thread
from datetime import datetime
from colorama import Fore, init
import requests
from http.server import BaseHTTPRequestHandler, HTTPServer

# init colors
init()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
          Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
          Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
          Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW]

# choose a random color for the client
client_color = random.choice(colors)

# server's IP address and port
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002
separator_token = "<SEP>"

# initialize TCP socket
s = socket.socket()
print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
# connect to the server
s.connect((SERVER_HOST, SERVER_PORT))
print("[+] Connected.")
# prompt the client for a name
username = 'хуй булыжников'




def send_request_to_database_login():
    # Вход пользователя
    global username
    login_data = {
        "username": input('Enter your name: '),
        "password": input('Enter your password: ')
    }
    username = login_data["username"]
    login_response = requests.post("http://localhost:8000/login", json=login_data)
    print(login_response.text)
    if login_response.status_code == 200:
        pass
    else:
        print("Login failed. Please try again.")
        log()
def send_request_to_database_register():
    # Регистрация пользователя
    registration_data = {
        "username": input('Enter your name: '),
        "password": input('Enter your password: ')
    }

    register_response = requests.post("http://localhost:8000/register", json=registration_data)
    print(register_response.text)
    if register_response.status_code == 200:
        print('Login in your account')
        send_request_to_database_login()
    else:
        print("Registration failed. Please try again.")
        log()
def log():
    while True:
        choice = input('Enter 1 for Login, 2 for Register: ')

        if choice == "1":
            send_request_to_database_login()
            break
        elif choice == "2":
            send_request_to_database_register()
            break

log()

def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print("\n" + message)

# Make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
t.daemon = True
t.start()

while True:
    # Input the message you want to send to the server
    to_send = input()
    # A way to exit the program
    if to_send.lower() == 'q':
        break
    # Add the datetime, name, and the color of the sender
    date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    to_send = f"{client_color}[{date_now}] {username}{separator_token}{to_send}{Fore.RESET}"
    # Finally, send the message
    s.send(to_send.encode())

# Close the socket
s.close()