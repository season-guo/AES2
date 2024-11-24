import socket
HOST="127.0.0.1"
PORT=1080
test_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
http_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
test_socket.bind((HOST,PORT))
test_socket.listen(5)
browser_socket,browser_address=test_socket.accept()
print(f"connection from {browser_address}")
data=browser_socket.recv(4096)
print(data)
browser_socket.sendall(b"\x05\x00")
data=browser_socket.recv(4096)
print(data)
browser
data=browser_socket.recv(4096)
print(data)
data=browser_socket.recv(4096)
print(data)
data=browser_socket.recv(4096)
print(data)
data=browser_socket.recv(4096)
print(data)
data=browser_socket.recv(4096)
print(data)





