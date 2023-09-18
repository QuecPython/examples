import dataCall
import ethernet

nic = None

def netStatusCallback(args):
    pdp = args[0]
    datacallState = args[1]
    if datacallState == 0:
        print('modem network {} disconnected.'.format(pdp))
    elif datacallState == 1:
        print('modem network {} connected.'.format(pdp))
        if nic != None:
            lte=dataCall.getInfo(1, 0)
            print(lte)
            nic.set_default_NIC(lte[2][2])

def eth_init():
    lte=dataCall.getInfo(1, 0)
    print('modem net config: {}'.format(lte))
    workMode=1
    global nic
    print('eth init start')
    nic = ethernet.W5500(b'\x12\x34\x56\x78\x9a\xbc','192.168.1.1','','',-1,-1,-1,-1, workMode)
    if lte != -1 and lte[2][0] == 1:
        print('eth set default nic {}'.format(lte[2][2]))
        nic.set_default_NIC(lte[2][2])
    nic.set_dns('8.8.8.8', '114.114.114.114')
    print('eth net config: {}'.format(nic.ipconfig()))
    nic.set_up()
    print('eth startup success')

dataCall.setCallback(netStatusCallback)
eth_init()




    


