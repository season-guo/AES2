import socket
import struct
import threading
import select
# 配置服务器端的监听地址和端口
HOST = '0.0.0.0'  # 代理服务器监听的地址
PORT = 1080    # 代理服务器监听的端口（SOCKS5默认端口是1080）

def handle_client(client_socket):
    """处理客户端的 SOCKS5 连接"""
    try:
        # Step 1: 握手 - 接受客户端的连接并确认使用 SOCKS5 协议
        version, nmethods = client_socket.recv(2)
        methods = client_socket.recv(nmethods)
        
        # 回复客户端，告诉它我们不需要认证（0x00代表无认证）
        client_socket.sendall(b'\x05\x00')
        
        # Step 2: 连接请求 - 客户端请求连接某个远程服务器
        version, cmd, _, address_type = client_socket.recv(4)
        
        # 获取目标地址和端口
        if address_type == 1:  # IPv4 地址
            address = socket.inet_ntoa(client_socket.recv(4))
        elif address_type == 3:  # 域名
            domain_length = ord(client_socket.recv(1))
            address = client_socket.recv(domain_length).decode()
        elif address_type == 4:  # IPv6 地址
            address = socket.inet_ntop(socket.AF_INET6, client_socket.recv(16))
        port = struct.unpack('>H', client_socket.recv(2))[0]
        
        # Step 3: 建立连接并转发数据
        try:
            # 与目标服务器建立连接
            print(address,port)
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((address, port))
            print("connect to destination..")
            client_socket.sendall(struct.pack('BBBB', 5, 0, 0, 1) + socket.inet_aton('0.0.0.0') + struct.pack('>H', 0))
            while True:
                rlist, _, _ = select.select([client_socket,remote_socket], [], [])
                if client_socket in rlist:
                    data = client_socket.recv(1024)
                    if data:
                        remote_socket.sendall(data)
                else:
                    break
                if remote_socket in rlist:
                    data = remote_socket.recv(1024)
                    if data:
                        client_socket.sendall(data)
                    else:
                        break
        except Exception as e:
            print(f"Connection error: {e}")
            client_socket.sendall(b'\x05\x01\x00\x01\x00\x00\x00\x00\x00\x00')
    finally:
        # 关闭与客户端和目标服务器的连接
        print("closing")
        client_socket.close()

def start_server():
    """启动 SOCKS5 代理服务器"""
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