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

import utime
import lwm2m
import modem
import net
import checkNet
from machine import Pin
import _thread

class lwm2m_client():

    def __init__(self):

        self.lwm2m = lwm2m()
        self.network_wait_time = 60
        self.host = "220.180.239.212"
        self.port = "5563"
        self.connect_state = 0 # 0 -init, 1- registing, 2-register failed, 3-register success.
        self.connect_server_type = 0 # 0 - server, 1 - bsserver
        self.imei = modem.getDevImei()
        self.security_mode = 3 # 3 - no Pre-share key mode,  0 Pre-share key mode 
        self.epname_mode  = 3 #  3 - urn:imei:+imei .
        self.support_security_mode=[0,2,3]

        self.psk="urn:imei:{}".format(self.imei)
        self.key="30313233343536373839"

        if self.security_mode == 3:
            self.url = "coap://"+self.host +":"+ self.port
        else:
            self.url = "coaps://"+self.host +":"+ self.port

        self.config_security    =[1,1000,self.url,self.connect_server_type,3]
        self.config_epname      = ["testname"]  #  only self.epname_mode = 1 will use it
        self.config_epnamemde   = [self.epname_mode]
        self.config_foat        = [0,1]
        self.config_server      = [1, 60, 2, 60, 86400, 1, "U"]
        stage, state = checkNet.waitNetworkReady(30)
        if stage == 3 and state == 1:
            self.log('Network connection successful.')
        else:
            self.log('Network connection failed, stage={}, state={}'.format(stage, state))

    def log(self,args):
        print("[Lwm2m_client Info] {}".format(args))

    def lwm2m_set_psk(self,psk="testname"):
        if self.security_mode == 0:
            self.psk = psk
        else:
            self.log("security_mode:{},not support config psk!".format(self.security_mode))

    def lwm2m_set_key(self,key="30313233343536373839"):
        if self.security_mode == 0:
            self.key = key
        else:
            self.log("security_mode:{},not support config key!".format(self.security_mode))


    def lwm2m_set_server_host(self,url="220.180.239.212"):
        self.host = url
        self.lwm2m_update_connect_url()

    def lwm2m_update_connect_url(self):
        if self.security_mode == 3:
            self.url = "coap://"+self.host +":"+ self.port
        else:
            self.url = "coaps://"+self.host +":"+ self.port

    def lwm2m_set_epname(self,epname):
        if self.epname_mode == 1:
            self.config_epname = [epname]
        else:
            self.log("epname_mode :{},the mode not support set epame!!".format(self.epname_mode))

    def lwm2m_set_server_port(self,port="5563"):
        self.port = port
        self.lwm2m_update_connect_url()

    def lwm2m_set_security_mode(self,mode=3):
        if mode in self.support_security_mode:
            self.security_mode = mode
            self.lwm2m_update_connect_url()
        else:
            self.log("the security_mode {} not support !!".format(mode))
            self.log("current support security_mode :{}".format(self.support_security_mode))

    def lwm2m_mesage_callback(self,args):
        self.log("Get Lwm2m Server Data :{}".format(args))
        result=args[2]
        if '"ready","successfully"' in result:
            self.log('Connect Success!')
        elif '"ready","failed"' in result:
            self.log('Connect Failed!')
        else:
            pass

    def lwm2m_display_current_info(self):
        self.log("/---display config information---\\")
        self.log("lw.Security :{}".format(self.config_security))
        self.log("lw.config_server :{}".format(self.config_server))
        self.log("lw.Epnamemode :{}".format(self.config_epnamemde))
        if self.epname_mode == 1:
            self.log("lw.epname :{}".format(self.config_epname))
        self.log("lw.Fota :{}".format(self.config_foat))
        self.log("\\---display config information---/")


    def lwm2m_config_prepare(self):
        config=[]
        self.lwm2m.config(self.lwm2m.Reset,config)
        config=[1]
        self.lwm2m.config(self.lwm2m.Security,config)
        config=[0]
        self.lwm2m.config(self.lwm2m.Security,config)

    def lwm2m_set_connect_type(self,connect_type):
        if connect_type == 1 or connect_type == 0:
            self.connect_server_type = connect_type
        else:
            self.log("connect_type :{},not support!".format(connect_type))

    def register_all_callback(self):
        self.lwm2m.register_call(self.lwm2m_mesage_callback)

    def lwm2m_set_epname_mode(self,epname_mode = 3):
        if epname_mode == 1 or epname_mode == 3:
            self.epname_mode = epname_mode
        else:
           self.log("epname_mode :{},not support!".format(epname_mode))

    def lwm2m_update_all_config(self):

        if self.connect_server_type == 0 :
            # connect server
            self.config_security=[1,1000,self.url,self.connect_server_type,self.security_mode]
        if self.connect_server_type == 1 :
            # connect bsserver
            self.config_security=[0,100,self.url,self.connect_server_type,self.security_mode]

        if self.security_mode == 0:
            #  need psk
            self.config_security.append(self.psk)
            self.config_security.append(self.key)
        self.config_epnamemde=[self.epname_mode]

    def lwm2m_config(self):
        self.lwm2m_display_current_info()
        self.log("wait 1s ,will start config profile infomation!")
        utime.sleep(1)

        self.lwm2m.config(self.lwm2m.Security,self.config_security)
        self.lwm2m.config(self.lwm2m.Server,self.config_server)
        self.lwm2m.config(self.lwm2m.Epnamemode,self.config_epnamemde)
        if self.epname_mode == 1:
            self.lwm2m.config(self.lwm2m.Epname,self.config_epname)
        self.lwm2m.config(self.lwm2m.Fota,self.config_foat)


    def lwm2m_befor_run(self):

        # must clear dirty config,always run this function
        self.lwm2m_config_prepare()

        # config security_mode :3-no PSK ,0 -psk
        self.lwm2m_set_security_mode(0)

        # config lwm2mserver ip address
        self.lwm2m_set_server_host("lwm2m-test.avsystem.io")
        self.lwm2m_set_server_port("5684")
        # config epname format : 3 - urn:imei:imei 
        epname_mode = 3
        self.lwm2m_set_epname_mode(epname_mode)
        self.lwm2m_set_psk("urn:imei:869339060001965")
        self.lwm2m_set_key("30313233343536373839")

        # config connect server or bsserver 0 - server 1 -bsserver
        self.lwm2m_set_connect_type(0)

        # update config set 
        self.lwm2m_update_all_config()
        self.lwm2m_config()
        self.register_all_callback()

    def lwm2m_run(self):
        self.lwm2m_befor_run()
        self.lwm2m.register()

lw=lwm2m_client()

def th_lwm2m(args):
    print('thread th_func1 {} is running, heap_size {}'.format(args,_thread.get_heap_size()))
    global lw
    lw.lwm2m_run()

if __name__ == '__main__':

    _thread.start_new_thread(th_lwm2m, (list("r")))
