import ethernet

# 创建以太网卡
eth = ethernet.W5500(b'\x12\x34\x56\x78\x9a\xbc','','','',-1,38,36,37, 0)
print('W5500 ethernet nic created.')

# 开启 DHCP 功能
eth.dhcp()
print('DHCP enabled.')

# 网卡注册成功后，查看网络配置信息
ip_conf = eth.ipconfig()
print('get ip_conf:', ip_conf)

# 将以太网卡设置为默认网卡
eth.set_default_NIC(ip_conf[1][1])
print('W5500 is set as default nic.')

# 启动网卡
eth.set_up()
print('Ethernet nic enabled.')