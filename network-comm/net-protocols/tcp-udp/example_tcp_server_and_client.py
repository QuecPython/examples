import usocket
import _thread
import utime
import checkNet
import dataCall

def _client_conn_proc(conn, ip_addr, port):
    while True:
        try:
            # 接收客户端发送的数据
            data = conn.recv(1024)
            print('[server] [client addr: %s, %s] recv data:' % (ip_addr, port), data)
            
            # 向客户端回送数据
            conn.send(data)
        except:
            # 出现异常，连接断开
            print('[server] [client addr: %s, %s] disconnected' % (ip_addr, port))
            conn.close()
            break

def tcp_server(address, port):
    # 创建 socket 对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP_SER)
    print('[server] socket object created.')
    
    # 绑定服务器 IP 地址和端口
    sock.bind((address, port))
    print('[server] bind address: %s, %s' % (address, port))
    
    # 监听客户端连接请求
    sock.listen(10)
    print('[server] started, listening ...')
    
    while True:
        # 接受客户端连接请求
        cli_conn, cli_ip_addr, cli_port = sock.accept()
        print('[server] accept a client: %s, %s' % (cli_ip_addr, cli_port))
        
        # 每接入一个客户端连接，新建一个线程，即连接并行处理
        _thread.start_new_thread(_client_conn_proc, (cli_conn, cli_ip_addr, cli_port))

def tcp_client(address, port):
    # 创建socket对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('[client] socket object created.')
    
    # 连接tcp服务器
    print('[client] connecting: %s, %s' % (address, port))
    sock.connect((address, port))
    print('[client] connected.')
    
    data = b'1234567890'
    while True:
        try:
            # 向服务器发送数据
            sock.send(data)
            print('[client] send data:', data)
            
            # 读取服务器回发的数据
            data = sock.recv(1024)
            print('[client] recv data:', data)
            print('[client] -------------------------')
            
            # 延时1s
            utime.sleep(1)
        except:
            # 数据接收完毕，连接断开
            print('[client] disconnected.')
            sock.close()
            break

if __name__ == '__main__':
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1: # 网络状态正常
        print('[net] Network connection successful.')
        
        # 获取模组的 IP 地址
        server_addr = dataCall.getInfo(1, 0)[2][2]
        server_port = 80
        
        # 启动服务器线程，一直监听客户端连接请求
        _thread.start_new_thread(tcp_server, (server_addr, server_port))
        
        # 延时一段时间，确保服务器启动成功
        print('sleep 3s to ensure that the server starts successfully.')
        utime.sleep(3)
        
        # 启动客户端功能
        tcp_client(server_addr, server_port)
    else:
        print('[net] Network connection failed, stage={}, state={}'.format(stage, state))