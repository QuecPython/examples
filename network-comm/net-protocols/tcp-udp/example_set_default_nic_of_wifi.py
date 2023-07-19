from usr.WLAN import ESP8266
from machine import UART

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

# 将Wi-Fi网卡设置为默认网卡
wifi.set_default_NIC(ip_conf[0])
print('Wi-Fi is set as default nic.')