# Copyright (c) Quectel Wireless Solution, Co., Ltd.All Rights Reserved.
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http://www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# ********************************************************************************************************************** #
#   WHEN            WHO              WHAT, WHERE, WHY
# ********************************************************************************************************************** #
#   23/01/2024      Francis          Add timeout handling
#   ----------      -----------      ----------------------------------------------------------------------------------  #
#   06/08/2025      Sirius           Fix port occupation issue by adding socket release in stop function, retaining del
#   ----------      -----------      ----------------------------------------------------------------------------------  #
#   11/12/2025      Sirius           Add UART configuration parameters during SLIP initialization
# *********************************************************************************************************************  #

import usocket
import log
import utime
import slip
from machine import UART
import _thread
from queue import Queue

# 设置日志输出级别
WLAN_log = log.getLogger("WiFi")
# 打开日志打印
#log.basicConfig(level=log.INFO)

class RET_CODE():
    RET_SUCCESS_CODE = 0
    RET_RESPONSE_ERROR_CODE = -1
    RET_SYS_ERROR_CODE = -2
    RET_PARAM_ERROR_CODE = -3
    RET_TIMEOUT_CODE = -4        # wait respose timeout
    RET_NOT_SUPOORT_CODE = -5    # this function not support now
    RET_NAT_NOT_OPEN_CODE = -6   # nat not open, if this error,you should restart device.


class ESP8266:
    AP = 0  # SLIP_INNER
    STA = 1 # SLIP_OUTER

    def __init__(self, uart=UART.UART2, mode=STA, callback=None,baudrate=921600,data_bit=8,parity_bit=0,flow_ctrl=0):
        self.__uart = uart
        self.__mode = mode
        self.__message = ''
        self.__err = 0
        self.__callback = callback
        self.__value = None
        self.__wait_resp = 0
        self.__send_time = 0
		self.__baudrate = baudrate
        self.__data_bit = data_bit
        self.__parity_bit = parity_bit
        self.__flow_ctrl = flow_ctrl
        slip.destroy()
        ret = slip.construct(self.__uart, self.__mode,'',self.__baudrate, self.__data_bit,self.__parity_bit,self.__flow_ctrl)
        if ret == RET_CODE.RET_NAT_NOT_OPEN_CODE:
            return ValueError("nat is not open, you should restart device, and try again.")
        elif ret != RET_CODE.RET_SUCCESS_CODE:
            raise ValueError("slip init failure")
        self.__queue = Queue(1)
        self.__sock = self.__socket_init()
        self.__threadid = _thread.start_new_thread(self.__Socket_Thread, ())

    def __socket_init(self):
        # 创建一个socket实例
        sock = usocket.socket(usocket.AF_INET, usocket.SOCK_DGRAM, usocket.TCP_CUSTOMIZE_PORT)
        sock.setsockopt(usocket.SOL_SOCKET, usocket.SO_REUSEADDR, 1)
        # 绑定IP
        bind_addr = ('172.16.1.2', 5000)
        sock.bind(bind_addr)
        sock.settimeout(10)
        return sock

    def __socket_reinit(self):
        return self.__socket_init()
    
    def __socket_reponse(self):
        if self.__err == 1:
            return RET_CODE.RET_TIMEOUT_CODE
        if self.__value[2] == 'NOT SUPPORT':
            return RET_CODE.RET_NOT_SUPOORT_CODE
        elif self.__value[2] != 'OK':
            return RET_CODE.RET_RESPONSE_ERROR_CODE
        return RET_CODE.RET_SUCCESS_CODE

	# station模式
    def station(self, user, password):
        self.clear_remain()
        __head = 'F3'
        self.user = str(user)
        self.password = str(password)
        if self.__mode == self.STA:
            self.__message = self.user + ',' + self.password
        else:
            return RET_CODE.RET_PARAM_ERROR_CODE
        self.__Socket_UDP(__head, self.__message)
        return self.__socket_reponse()

	#ap 模式
    def ap(self, user, password):
        self.clear_remain()
        __head = 'F2'
        self.user = str(user)
        self.password = str(password)

        if self.__mode == self.AP:
            self.__message = self.user + ',' + self.password
        else:
            return RET_CODE.RET_PARAM_ERROR_CODE
        self.__Socket_UDP(__head, self.__message)
        return self.__socket_reponse()

	# web配网模式
    def web_config(self, user, password):
        self.clear_remain()
        __head = 'F0'
        if user == '' and password == '':
            self.__message = '0'
        else:
            self.user = str(user)
            self.password = str(password)
            self.__message = self.user + ',' + self.password
        self.__Socket_UDP(__head, self.__message)
        return self.__socket_reponse()

    def clear_remain(self):
        if self.__queue.empty() == False:
            self.__queue.get()
        self.__err = 0
        self.__value = None

	# 查询网卡状态
    def status(self):
        self.clear_remain()
        self.__Socket_UDP('F1', '0')
        if self.__err == 1:
            return RET_CODE.RET_SUCCESS_CODE
        return int(self.__value[2])

	# 查询网卡版本信息
    def version(self):
        self.clear_remain()
        self.__Socket_UDP('F5', '0')
        if self.__err == 1:
            return RET_CODE.RET_TIMEOUT_CODE
        return self.__value[2]

	# ota升级
    def ota(self, url):
        self.clear_remain()
        __head = 'F4'
        self.__message = str(url)
        self.__Socket_UDP(__head, self.__message)
        return self.__socket_reponse()

	# smartconfig配置
    def smartconfig(self, mode):
        self.clear_remain()
        __head = 'F6'
        self.__message = str(mode)
        self.__Socket_UDP(__head, self.__message)
        return self.__socket_reponse()

	# 配置查询
    def config(self, param):
        self.clear_remain()
        __head = 'F7'
        self.__message = str(param)
        self.__Socket_UDP(__head, self.__message)
        if self.__err == 1:
            return RET_CODE.RET_TIMEOUT_CODE
        return self.__value[2]

	#添加路由信息
    def router_add(self, ip='192.168.4.1', mask='255.255.255.0'):
        self.ip = ip
        self.mask = mask
        return slip.router_add('192.168.4.1', '255.255.255.0')

	# 获取slip的网络配置
    def ipconfig(self):
        return slip.ipconfig()

	# 设置dns服务器
    def set_dns(self, pri_dns='8.8.8.8', sec_dns='114.114.114.114'):
        self.pri_dns = pri_dns
        self.sec_dns = sec_dns
        ret = slip.set_dns(self.pri_dns,self.sec_dns)
        if ret == 0:
            return RET_CODE.RET_SUCCESS_CODE
        return RET_CODE.RET_PARAM_ERROR_CODE 
    
	# 设置默认网卡
    def set_default_NIC(self, ip_str):
        self.ip_str = ip_str
        ret = slip.set_default_netif(self.ip_str)
        if ret == 0:
            return RET_CODE.RET_SUCCESS_CODE
        return RET_CODE.RET_PARAM_ERROR_CODE
    
	# 释放slip网卡
    def stop(self):
        _thread.stop_thread(self.__threadid)
        slip.destroy()
	self.__sock.close()#释放socket
        return RET_CODE.RET_SUCCESS_CODE

	# 封装tlv数据包
    def __pack_tlv_format(self, head, content):
        self.head = head
        self.content = content
        if len(self.content) == 0 or len(self.content) > 9999 or len(self.head) != 2:
            return RET_CODE.RET_PARAM_ERROR_CODE
        len_str ='%04d' % len(self.content)
        tlv_pack = self.head+len_str+self.content
        return tlv_pack

	# 解码tlv数据包
    def __unpack_tlv_format(self, msg):
        self.msg = str(msg)
        tag = self.msg[0:2]
        length = self.msg[2:6]
        value = self.msg[6:]
        len_str ='%04d' % len(value)
        if len(value) == 0 or len(value) > 9999 or len(tag) != 2 or len_str != self.msg[2:6]:
            return RET_CODE.RET_RESPONSE_ERROR_CODE
        unpack = (tag,length,value)
        return unpack
	    
	# socket通信(UDP)模块
    def __Socket_UDP(self, head, content):
        self.head = head
        self.content = content

        # 消息处理
        msg = self.__pack_tlv_format(self.head, self.content)

        # 向服务端发送消息
        server_addr = ('172.16.1.5',1000)
        #WLAN_log.debug(msg)
        self.__err = 0
        self.__sock.sendto(msg,server_addr)
        self.__wait_resp = 1
        self.__send_time = utime.ticks_ms()
        data = self.__queue.get()
        self.__wait_resp = 0
        return data
    
    def __def__(self):
	self.stop()
   
	# socket通信(UDP)模块
    def __Socket_Thread(self):
        while True:
            try:
                data=self.__sock.recv(1024)
            except Exception as recverr:
                if "110" in str(recverr):
                    if utime.ticks_diff(utime.ticks_ms(), self.__send_time) < 9000:
                        continue
                    self.__err = 1
                    if self.__wait_resp == 1:
                        self.__queue.put('0')
                else:
                    utime.sleep(1)
                    self.__sock = self.__socket_reinit()
            else :
                value = self.__unpack_tlv_format(data.decode())
                #WLAN_log.debug('mode: {0}, recv {1} bytes, Data: {2}'.format (value[0],len(data), value[2]))
                if value[0] == 'FF':
                    if self.__callback != None:
                        self.__callback(value[2])
                else:
                    self.__value = value
                    self.__queue.put('1')
