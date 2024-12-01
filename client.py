import socket
from urllib.parse import urlparse
proxy_host = '127.0.0.1'  
proxy_port = 1080         
def create_proxy_socket(url,port):
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((proxy_host, proxy_port))
    proxy_socket.sendall(b'\x05\x01\x00')  
    response = proxy_socket.recv(2)
    if response != b'\x05\x00':  
        print("SOCKS5 handshake failed")
        proxy_socket.close()
        return None
    target_host = url  
    target_port = port          
    request = b'\x05\x01\x00\x03' + bytes([len(target_host)]) + target_host.encode() + target_port.to_bytes(2, 'big')
    proxy_socket.sendall(request)    
    return proxy_socket
def request_via_proxy(url):
    proxy_socket = create_proxy_socket(url[7:])
    if not proxy_socket:
        return
    parsed_url = urlparse(url)
    http_request = f"GET {parsed_url.path or '/'} HTTP/1.1\r\nHost: {parsed_url.netloc}\r\nConnection: close\r\n\r\n"
    proxy_socket.sendall(http_request.encode())
    response = proxy_socket.recv(4096)
    while response:
        print(response.decode(),end="")
        response = proxy_socket.recv(4096)
url = input()
port=input()
request_via_proxy(url,port)