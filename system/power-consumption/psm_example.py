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
import pm
from machine import RTC
from misc import Power
import checkNet

def Business_code_example(run_time):
    i = 0
    for i in range(run_time):	
        print("Business app running")
		#Business code here  
        utime.sleep(1)

    return    

def psm_try_set():
    if pm.get_psm_time()[0] == 1:#开机时获取psm是否设置，如果已经使能，则无需再次进行设置
        print("PSM has been enable, set pass")
        return 0
    else:
        return pm.set_psm_time(0,1,0,1)#T3412=10min T3324=1min

def psm_failed_handle(delay_time):
    utime.sleep(delay_time)#等待指定时长后，触发PSM失败的处理逻辑，即代之以关机+RTC关机闹钟

    rtc = RTC()
    tm_rtc_tuple = rtc.datetime()
    tm_rtc_second = utime.mktime((tm_rtc_tuple[0], tm_rtc_tuple[1], tm_rtc_tuple[2], tm_rtc_tuple[4], tm_rtc_tuple[5], tm_rtc_tuple[6], 0, 0))

    alarm_second = tm_rtc_second + 600#RTC闹钟设为当前时间 + 10min
    alarm_tuple = utime.localtime(alarm_second)

    rtc.set_alarm([alarm_tuple[0], alarm_tuple[1], alarm_tuple[2], alarm_tuple[6], alarm_tuple[3], alarm_tuple[4], alarm_tuple[5], 0])
    rtc.enable_alarm(1)

    Power.powerDown()


if __name__ == '__main__':
    psm_failed_delay_time = 60 + 30 #PSM的 T3324超时30S后，启用错误处理逻辑
    lpm_fd = pm.create_wakelock("psm_lock", len("psm_lock")) #申请功耗锁

    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1:
        print('Network connection successful.')
        psm_try_set() #网络连接成功时尝试设置PSM，如果PSM设置已经生效，则不用再次设置
    else:
        print('Network connection failed.')
        psm_failed_delay_time = 1 #PSM依赖网络，无网络时应立即使用RTC代替之

    pm.wakelock_lock(lpm_fd)#锁定功耗锁，防止业务运行过程中因sleep错误进入PSM模式
    Business_code_example(10)#业务代码运行  
    pm.wakelock_unlock(lpm_fd)#业务运行完成后，释放功耗锁。模组空闲状态且T3324超时后，自动进入PSM

    psm_failed_handle(psm_failed_delay_time)#运行错误处理，若模组能正常进入PSM，在sleep中就进入PSM了，该处实际的处理逻辑并不会运行


