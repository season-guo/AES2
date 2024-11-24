import socket
from urllib.parse import urlparse

# SOCKS5代理的设置
proxy_host = '127.0.0.1'  # 代理服务器地址
proxy_port = 1080         # 代理端口
proxy_username = 'your_username'  # 如果需要认证，请填入用户名
proxy_password = 'your_password'  # 如果需要认证，请填入密码

# 创建一个通过 SOCKS5 代理进行的连接
def create_proxy_socket(url):
    # 连接到SOCKS5代理
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.connect((proxy_host, proxy_port))
    
    # 发送 SOCKS5 握手请求
    proxy_socket.sendall(b'\x05\x01\x00')  # version 5, no authentication
    
    # 获取代理的响应
    response = proxy_socket.recv(2)
    if response != b'\x05\x00':  # 如果响应不为 OK
        print("SOCKS5 handshake failed")
        proxy_socket.close()
        return None
    
    # 向代理发送连接请求 (目标主机和端口)
    target_host = url  # 目标地址
    target_port = 80            # 目标端口
    request = b'\x05\x01\x00\x03' + bytes([len(target_host)]) + target_host.encode() + target_port.to_bytes(2, 'big')
    proxy_socket.sendall(request)    
    return proxy_socket

# 使用代理请求 HTTP
def request_via_proxy(url):
    # 创建通过 SOCKS5 代理的 socket
    proxy_socket = create_proxy_socket(url[7:])
    if not proxy_socket:
        return

    # 发送 HTTP 请求
    parsed_url = urlparse(url)
    http_request = f"GET {parsed_url.path or '/'} HTTP/1.1\r\nHost: {parsed_url.netloc}\r\nConnection: close\r\n\r\n"
    proxy_socket.sendall(http_request.encode())

    # 接收并打印响应
    response = proxy_socket.recv(4096)
    while response:
        print(response.decode(),end="")
        response = proxy_socket.recv(4096)
# 发送通过 SOCKS5 代理的请求
url = input()
request_via_proxy(url)