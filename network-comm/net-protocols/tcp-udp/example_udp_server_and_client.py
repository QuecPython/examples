import usocket
import _thread
import utime
import checkNet
import dataCall

def udp_server(address, port):
    # 创建 socket 对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM, usocket.IPPROTO_UDP)
    print('[server] socket object created.')
    
    # 绑定服务器 IP 地址和端口
    sock.bind((address, port))
    print('[server] bind address: %s, %s' % (address, port))
    
    while True:
        # 读取客户端数据
        data, sockaddr = sock.recvfrom(1024)
        print('[server] [client addr: %s] recv data: %s' % (sockaddr, data))
        
        # 向客户端回送数据
        sock.sendto(data, sockaddr)

def udp_client(address, port):
    # 创建socket对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM, usocket.IPPROTO_UDP)
    print('[client] socket object created.')
    
    data = b'1234567890'
    while True:
        # 向服务器发送数据
        sock.sendto(data, (address, port))
        print('[client] send data:', data)
        
        # 读取服务器回发的数据
        data, sockaddr = sock.recvfrom(1024)
        print('[client] [server addr: %s] recv data: %s' % (sockaddr, data))
        print('[client] -------------------------')
        
        # 延时1s
        utime.sleep(1)
        
if __name__ == '__main__':
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1: # 网络状态正常
        print('[net] Network connection successful.')
        
        # 获取模组的 IP 地址
        server_addr = dataCall.getInfo(1, 0)[2][2]
        server_port = 80
        
        # 启动服务器线程
        _thread.start_new_thread(udp_server, (server_addr, server_port))
        
        # 延时一段时间，确保服务器启动成功
        print('sleep 3s to ensure that the server starts successfully.')
        utime.sleep(3)
        
        # 启动客户端功能
        udp_client(server_addr, server_port)
    else:
        print('[net] Network connection failed, stage={}, state={}'.format(stage, state))