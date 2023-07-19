import usocket
import checkNet

def tcp_client(address, port):
    # 创建socket对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('socket object created.')
    
    # 域名解析
    sockaddr=usocket.getaddrinfo(address, port)[0][-1]
    print('DNS for %s: %s' % (address, sockaddr[0]))
    
    # 连接tcp服务器
    sock.connect(sockaddr)
    print('tcp link established.')
    
    # 打包用户数据
    data = 'GET / HTTP/1.1\r\n'
    data += 'Host: ' + address + ':' + str(port) + '\r\n'
    data += 'Connection: close\r\n'
    data += '\r\n'
    data = data.encode()
    
    # 发送数据
    sock.send(data)
    print('<-- send data:')
    print(data)
    
    #接收数据
    print('--> recv data:')
    while True:
        try:
            data = sock.recv(1024)
            print(data)
        except:
            # 数据接收完毕，连接断开
            print('tcp disconnected.')
            sock.close()
            break

if __name__ == '__main__':
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1: # 网络状态正常
        print('Network connection successful.')
        tcp_client('www.baidu.com', 80) # 启动客户端功能
    else:
        print('Network connection failed, stage={}, state={}'.format(stage, state))