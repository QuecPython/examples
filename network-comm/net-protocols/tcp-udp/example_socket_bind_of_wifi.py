from usr.WLAN import ESP8266
from machine import UART
import usocket

# 创建Wi-Fi网卡
wifi = ESP8266(UART.UART2, ESP8266.STA)
print('Wi-Fi nic created.')

# 配置连接的SSID和password，并连接路由器
ssid = 'ssid'
password = 'password'
wifi.station(ssid,password)
print('Wi-Fi connected：%s, %s.' % (ssid, password))

# 给Wi-Fi网卡配置DNS服务器地址
wifi.set_dns('8.8.8.8', '114.114.114.114')
print('Wi-Fi DNS server configured.')

# 查看网络配置信息
ip_conf = wifi.ipconfig()
print('get ip_conf:', ip_conf)

def tcp_client(address, port):
    # 创建socket对象
    sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM, usocket.IPPROTO_TCP)
    print('socket object created.')
	
    # 创建完成socket对象以后，并且连接服务器之前 绑定Wi-Fi网卡IP地址
    local_address = ip_conf[0]
    sock.bind((local_address, 0))
    print('bind ethernet address: %s', local_address)
	
    # 域名解析
    sockaddr=usocket.getaddrinfo(address, port)[0][-1]
    print('DNS for %s: %s' % (address, sockaddr[0]))
    
    # 连接tcp服务器
    sock.connect(sockaddr)
    print('tcp link established.')
    
    # 更多代码请参考前面关于 TCP 客户端的代码示例