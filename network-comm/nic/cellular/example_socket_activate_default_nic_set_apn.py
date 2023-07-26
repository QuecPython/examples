import checkNet
import usocket
import dataCall
from misc import Power

# 用户需要配置的APN信息，根据实际情况修改
usrCfg = {'apn': '3gnet', 'username': '', 'password': ''}


def checkAPN():
    # 获取第一路网卡的APN信息，确认当前使用的是否是用户指定的APN
    pdpCtx = dataCall.getPDPContext(1)
    if pdpCtx != -1:
        if pdpCtx[1] != usrCfg['apn']:
            # 如果不是用户需要的APN，使用如下方式配置
            ret = dataCall.setPDPContext(1, 0, usrCfg['apn'], usrCfg['username'], usrCfg['password'], 0)
            if ret == 0:
                print('APN configuration successful. Ready to restart to make APN take effect.')
                print('Please re-execute this program after restarting.')
                # 重启后按照配置的信息进行拨号
                Power.powerRestart()
            else:
                print('APN configuration failed.')
                return False
        else:
            print('The APN is correct and no configuration is required')
            return True
    else:
        print('Failed to get PDP Context.')
        return False


def main():
    checkpass = checkAPN()
    if not checkpass:
        return

    stage, state = checkNet.waitNetworkReady(20)
    if stage == 3 and state == 1:
        print('Network connected successfully.')
        # 创建一个socket对象
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
    else:
        print('Network connected failed, stage={}, state={}'.format(stage, state))


if __name__ == '__main__':
    main()
