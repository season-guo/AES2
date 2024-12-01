import socket
import struct
import threading
import select
import pyaes
key=b"abcdefghijklmnop"
aes=pyaes.AESModeOfOperationCTR(key)
HOST = "127.0.0.1"
PORT = 1080  
key=b'\x86\xc1\xb3\x8bcF\x0c6\x93\xdf\xa0\xc2\xd63\x13w'
cipher=pyaes.AESModeOfOperationCTR(key)
decipher = pyaes.AESModeOfOperationCTR(key)
def safe(data):
    return cipher.encrypt(data)
def desafe(data):
    return decipher.decrypt(data)
def handle_client(client_socket):
        version, nmethods =desafe(client_socket.recv(2))
        methods = desafe(client_socket.recv(nmethods))
        client_socket.sendall(safe(b'\x05\x00'))
        version, cmd, _, address_type = desafe(client_socket.recv(4))
        if version !=5:
            print("not socks5")
            return
        if address_type == 1:  
            address = socket.inet_ntoa(desafe(client_socket.recv(4)))
        elif address_type == 3:  
            domain_length = ord(client_socket.recv(1))
            address = desafe(client_socket.recv(domain_length)).decode()
        elif address_type == 4:  
            address = socket.inet_ntop(socket.AF_INET6, desafe(client_socket.recv(16)))
        port = struct.unpack('>H', desafe(client_socket.recv(2)))[0]
        try:
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((address, port))
            print("connect to destination..")
            client_socket.sendall(safe(b'\x05\x00\x00\x01' + socket.inet_aton('0.0.0.0') + struct.pack('>H', 0)))
            print("Send authenfication to browser...")
            while True:
                rs, ws, es = select.select([client_socket, remote_socket], [], [])
                if client_socket in rs:
                    data = client_socket.recv(4096)
                    data=desafe(data)
                    print(f"from client:{data}")
                    if remote_socket.send(data) <= 0:
                        break
                if remote_socket in rs:
                    data = remote_socket.recv(4096)
                    print(f"from VPS:{data}")
                    if client_socket.send(safe(data)) <= 0:
                        break
        except Exception as e:
            print(f"Connection error: {e}")
            client_socket.sendall(safe(b'\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00'))
        finally:
            print("closing")
            client_socket.close()

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"SOCKS5 Proxy Server listening on {HOST}:{PORT}...")
    while True:
        client_socket, client_address = server_socket.accept()
        athread=threading.Thread(target=handle_client,args=(client_socket,))
        print(f"Connection from {client_address}")
        athread.start()

if __name__ == '__main__':
    start_server()