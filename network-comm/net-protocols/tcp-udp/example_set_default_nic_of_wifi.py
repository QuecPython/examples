from usr.WLAN import ESP8266
from machine import UART

# Create a Wi-Fi NIC
wifi = ESP8266(UART.UART2, ESP8266.STA)
print('Wi-Fi nic created.')

# Configure the SSID and password, and connect to the router
ssid = 'ssid'
password = 'password'
wifi.station(ssid,password)
print('Wi-Fi connected：%s, %s.' % (ssid, password))

# Configure the DNS server address for the Wi-Fi NIC
wifi.set_dns('8.8.8.8', '114.114.114.114')
print('Wi-Fi DNS server configured.')

# Check the network configuration information
ip_conf = wifi.ipconfig()
print('get ip_conf:', ip_conf)

# Set the Wi-Fi NIC as the default NIC
wifi.set_default_NIC(ip_conf[0])
print('Wi-Fi is set as default nic.')