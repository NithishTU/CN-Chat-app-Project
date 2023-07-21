import threading
import socket   
import os   #this package allows 2 different os to work 
import time #this package is used to set time limit

alias = input('Enter The Unique Id : ') #Allows the user to set his own identity so others can't copy
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('172.18.192.1', 59001))

# Function to receive messages on the client side
def client_receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                print('Connection to the server is closed.')
                break
            if message.startswith(f'{alias} has shared a file:'):
                _, filename = message.split(': ')
                filename = filename.strip()
                print(f'Receiving file: {filename}')
                receive_file(filename)
            else:
                print(message)
        except ConnectionResetError:
            print('Connection to the server was reset.')
            break
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break

# Function to send messages from the client to another client
def client_send():
    while True:
        message = input("")
        if not client:
            break  # Exit the loop if the client socket is closed

        if message.startswith("/file"):
            _, file_path = message.split(" ")
            file_path = file_path.strip()
            send_file(file_path)
        else:
            if client:
                message = f'{alias}: {message}'
                client.send(message.encode('utf-8'))

# Function to send Files
def send_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)

        if file_size > 30 * 1024 * 1024:  # 30 MB in bytes
            print("Error: The File Cannot Be Sent,Exceeds the 30 MB limit..")
            return

        client.send(f'/file|{file_name}|{file_size}'.encode('utf-8'))

        with open(file_path, 'rb') as file:
            while True:
                data = file.read(4096)
                if not data:
                    break
                client.send(data)
        # Increase the delay to 1 second (you can adjust this value if needed)
        time.sleep(1)
        client.send(b'<END_OF_FILE>')
        print(f'{file_name} sent successfully!')
    except Exception as e:
        print(f'Error while sending file: {e}')
        client.close()  # Close the connection in case of an error

# Function to receive files
def receive_file(file_name):
    try:
        with open(file_name, 'wb') as file:
            while True:
                data = client.recv(4096)
                if data == b'<END_OF_FILE>':
                    break
                file.write(data)
        print(f'{file_name} received successfully!')
    except Exception as e:
        print(f'Error while receiving file: {e}')

receive_thread = threading.Thread(target=client_receive)
receive_thread.start()

send_thread = threading.Thread(target=client_send)
send_thread.start()
