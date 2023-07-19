import ethernet
import usocket

# 创建以太网卡
eth = ethernet.W5500(b'\x12\x34\x56\x78\x9a\xbc','','','',-1,38,36,37, 0)
print('W5500 ethernet nic created.')

# 开启 DHCP 功能
eth.dhcp()
print('DHCP enabled.')

# 启动网卡
eth.set_up()
print('Ethernet nic enabled.')

# 网卡注册成功后，查看网络配置信息
ip_conf = eth.ipconfig()
print('get ip_conf:', ip_conf)

def tcp_client(address, port):
    # 创建socket对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('socket object created.')
	
    # 创建完成socket对象以后，并且连接服务器之前 绑定以太网卡IP地址
    local_address = ip_conf[1][1]
    sock.bind((local_address, 0))
    print('bind ethernet address: %s', local_address)
	
    # 域名解析
    sockaddr=usocket.getaddrinfo(address, port)[0][-1]
    print('DNS for %s: %s' % (address, sockaddr[0]))
    
    # 连接tcp服务器
    sock.connect(sockaddr)
    print('tcp link established.')
    
    # 更多代码请参考前面关于 TCP 客户端的代码示例