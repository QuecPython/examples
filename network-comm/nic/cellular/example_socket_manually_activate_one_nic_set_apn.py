import checkNet
import usocket
import dataCall
import utime
from misc import Power

# 用户需要配置的APN信息，根据实际情况修改
usrCfg1 = {'profileID': 1, 'apn': '3gnet', 'username': '', 'password': ''}

'''
环境配置：
1.关闭开机自动拨号功能
2.APN配置
'''
def cfgEnv(usrCfg):
    errcode = 0
    need_reboot1 = False
    need_reboot2 = False
    if "datacall_config.json" not in uos.listdir('/usr'):
        # 关闭第一路网卡开机自动激活功能
        dataCall.setAutoActivate(usrCfg['profileID'], 0)
        # 建议用户使能网卡自动重连功能
        dataCall.setAutoConnect(usrCfg['profileID'], 1)
        need_reboot1 = True

    print('Check the APN configuration.')
    # 获取网卡的APN信息，确认当前使用的是否是用户指定的APN
    pdpCtx = dataCall.getPDPContext(usrCfg['profileID'])
    if pdpCtx != -1:
        if pdpCtx[1] != usrCfg['apn']:
            # 如果不是用户需要的APN，使用如下方式配置
            ret = dataCall.setPDPContext(usrCfg['profileID'], 0, usrCfg['apn'], usrCfg['username'], usrCfg['password'], 0)
            if ret == 0:
                print('APN configuration successful.')
                need_reboot2 = True
            else:
                print('APN configuration failed.')
                errcode = -1
        else:
            print('The APN is correct and no configuration is required')
            errcode = 0
    else:
        print('Failed to get PDP Context.')
        errcode = -1
    # 重启使配置生效
    if need_reboot1 or need_reboot2:
        print('Ready to restart.')
        print('Please re-execute this program after restarting.')
        Power.powerRestart()
        utime.sleep(2)
    return errcode


def main():
    if cfgEnv(usrCfg1) == -1:
        return

    # 手动激活蜂窝无线网卡
    print('Prepare to activate the NIC{}.'.format(usrCfg1['profileID']))
    ret = dataCall.activate(usrCfg1['profileID'])
    if ret == -1:
        print('NIC activation failed.')
        return

    stage, state = checkNet.waitNetworkReady(10)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # 获取第一路网卡的IP地址等信息
        ret = dataCall.getInfo(usrCfg1['profileID'], 0)
        print('NIC{}：{}'.format(usrCfg1['profileID'], ret))

        print('---------------sock test-----------------')
        # 创建socket对象
        sock = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
        # 解析域名
        try:
            sockaddr = usocket.getaddrinfo('python.quectel.com', 80)[0][-1]
        except Exception:
            print('Domain name resolution failed.')
            sock.close()
            return
        # 建立连接
        sock.connect(sockaddr)
        # 向服务端发送消息
        ret = sock.send('GET /News HTTP/1.1\r\nHost: python.quectel.com\r\nAccept-Encoding: deflate\r\nConnection: keep-alive\r\n\r\n')
        print('send {} bytes'.format(ret))
        # 接收服务端消息
        data = sock.recv(256)
        print('recv {} bytes:'.format(len(data)))
        print(data.decode())
        # 关闭连接
        sock.close()

        # 用户根据需要决定是否需要在通信结束对网卡进行去激活
        # dataCall.deactivate(usrCfg1['profileID'])
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
