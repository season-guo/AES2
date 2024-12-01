import socket
import select
import threading
def localstart(browser_socket):
    remote_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect(("155.138.234.133",1080))
    while True:
        read,write,error=select.select([remote_socket,browser_socket],[],[])
        if remote_socket in read:
            data=remote_socket.recv(4096)
            if browser_socket.send(data)<=0:
                break
        if browser_socket in read:
            data=browser_socket.recv(4096)
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

        