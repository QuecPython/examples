import ethernet

# Create an Ethernet NIC
eth = ethernet.W5500(b'\x12\x34\x56\x78\x9a\xbc','','','',-1,38,36,37, 0)
print('W5500 ethernet nic created.')

# Enable DHCP
eth.dhcp()
print('DHCP enabled.')

# After the NIC is registered, check the network configuration information
ip_conf = eth.ipconfig()
print('get ip_conf:', ip_conf)

# Set the Ethernet NIC as the default NIC
eth.set_default_NIC(ip_conf[1][1])
print('W5500 is set as default nic.')

# Enable the NIC
eth.set_up()
print('Ethernet nic enabled.')