import socket
import struct
import select
import threading
# SOCKS5 握手
def socks5_handshake(client_socket):
    # 第一步：接收客户端请求（握手请求）
    version, nmethods = struct.unpack("BB", client_socket.recv(2))  # SOCKS5 版本和方法数
    methods = client_socket.recv(nmethods)  # 支持的身份验证方法列表

    # 第二步：告知客户端接受不需要认证的方法
    client_socket.sendall(struct.pack("BB", 0x05, 0x00))  # 选择无认证方法

# 处理客户端请求（SOCKS5 转发）
def handle_socks5_request(client_socket):
    # 第三步：接收客户端连接请求（目标地址和端口）
    version, cmd, reserved, atyp = struct.unpack("BBBB", client_socket.recv(4))
    
    if version != 5:
        print("不支持的 SOCKS 版本")
        client_socket.close()
        return
    
    if cmd != 1:  # 只支持连接命令（CMD = 1）
        print("不支持的命令")
        client_socket.close()
        return
    
    # 解析目标地址
    if atyp == 1:  # IPv4 地址
        addr = socket.inet_ntoa(client_socket.recv(4))
    elif atyp == 3:  # 域名
        addr_len = ord(client_socket.recv(1))
        addr = client_socket.recv(addr_len).decode()
    elif atyp == 4:  # IPv6 地址（这里不做处理）
        print("不支持 IPv6")
        client_socket.close()
        return
    else:
        print("不支持的地址类型")
        client_socket.close()
        return
    
    port = struct.unpack(">H", client_socket.recv(2))[0]

    print(f"目标地址: {addr}, 端口: {port}")

    # 第四步：建立与目标服务器的连接
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((addr, port))

        # 第五步：返回连接成功响应
        client_socket.sendall(struct.pack("BBBB", 0x05, 0x00, 0x00, 0x01) + socket.inet_aton("0.0.0.0") + struct.pack(">H", 0))

        # 第六步：进行数据转发
        while True:
            rlist, _, _ = select.select([client_socket, server_socket], [], [])
            if client_socket in rlist:
                data = client_socket.recv(1024)
                if data:
                    server_socket.sendall(data)
                else:
                    break

            if server_socket in rlist:
                data = server_socket.recv(1024)
                if data:
                    client_socket.sendall(data)
                else:
                    break
    except Exception as e:
        print(f"连接目标服务器失败: {e}")
        client_socket.close()
        return
    
    # 关闭连接
    server_socket.close()
    client_socket.close()

# SOCKS5 代理服务器监听
def start_socks5_proxy(host='0.0.0.0', port=1080):
    # 创建 TCP 套接字用于监听客户端请求
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    
    print(f"SOCKS5 代理服务器已启动，监听 {host}:{port} ...")

    while True:
        # 接受客户端连接
        client_socket, addr = server_socket.accept()
        print(f"接收到来自 {addr} 的连接")

        # 握手并处理客户端请求
        socks5_handshake(client_socket)
        handle_socks5_request(client_socket)

if __name__ == "__main__":
    start_socks5_proxy()