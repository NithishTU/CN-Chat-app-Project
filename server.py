import threading
import socket
import os

host = ''
port = 59001
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()
clients = []
aliases = []
ip_addresses = []  # List to keep track of connected IP addresses


def broadcast(message):
    for client in clients:
        client.send(message)


def handle_client(client):
    alias = setup_client(client)

    if not alias:
        return

    # Get the IP address of the connected client
    client_address = client.getpeername()[0]

    if client_address in ip_addresses:
        client.send('You were blocked. The IP address is already in use.'.encode('utf-8'))
        client.close()
        return

    ip_addresses.append(client_address)

    aliases.append(alias)
    clients.append(client)
    broadcast(f'{alias} has connected to the chat room'.encode('utf-8'))
    client.send('You are now connected!'.encode('utf-8'))

    while True:
        try:
            message = client.recv(1024)
            if not message:
                # Client disconnected
                index = clients.index(client)
                alias = aliases[index]
                clients.remove(client)
                aliases.remove(alias)
                ip_addresses.remove(client_address)
                broadcast(f'{alias} has left the chat room!'.encode('utf-8'))
                client.close()
                break
            if message.startswith(b'/file'):
                # The client wants to send a file
                _, filename, filesize = message.split(b'|')
                filename = filename.decode('utf-8')
                filesize = int(filesize)
                with open(filename, 'wb') as file:
                    remaining_bytes = filesize
                    while remaining_bytes > 0:
                        data = client.recv(min(4096, remaining_bytes))
                        file.write(data)
                        remaining_bytes -= len(data)
                print(f'{alias} has shared a file: {filename}')
                broadcast(f'{alias} has shared a file: {filename}'.encode('utf-8'))
            else:
                broadcast(message)
        except Exception as e:
            print(f'Error: {e}')
            client.close()
            break


def receive():
    while True:
        print('Server is running and listening ...')
        client, address = server.accept()
        print(f'Connection is established with {str(address)}')

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()


def setup_client(client):
    client.send("Enter your alias : ".encode('utf-8'))
    alias = client.recv(1024).decode('utf-8')

    if alias in aliases:
        client.send('Cannot Connect The User Already exists.'.encode('utf-8'))
        client.close()
        return None

    client.send('You are now connected!'.encode('utf-8'))
    return alias


if __name__ == "__main__":
    receive()
