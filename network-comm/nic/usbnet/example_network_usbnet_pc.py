from misc import USBNET,Power
import utime
import dataCall


if USBNET.get_worktype() != USBNET.Type_RNDIS:
    USBNET.set_worktype(USBNET.Type_RNDIS)
    Power.powerRestart()
while True:
    info = dataCall.getInfo(1, 0)
    if info[2][2] != '0.0.0.0':
        print('data:',info)
        break
    print('Wait for data calling')
    utime.sleep(2)

USBNET.open()
print('USBNET open successed.')
