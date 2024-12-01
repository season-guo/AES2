import socket
import pyaes
import select
import threading
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
def localstart(browser_socket):
    remote_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect(("127.0.0.1",1080))
    while True:
        read,write,error=select.select([remote_socket,browser_socket],[],[])
        if remote_socket in read:
            data=desafe(remote_socket.recv(4096))
            print(f"from proxy:{data}")
            if browser_socket.send(data)<=0:
                break
        if browser_socket in read:
            data=browser_socket.recv(4096)
            print(f"from browser:{data}")
            data=safe(data)
            if remote_socket.send(data)<=0:
                break
    browser_socket.close()
if __name__=="__main__":
    listen_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    listen_socket.bind(("127.0.0.1",2019))
    listen_socket.listen(5)
    while True:
        browser_socket,address=listen_socket.accept()
        print(f"connction from {address}")
        threading.Thread(target=localstart,args=(browser_socket,)).start()

        