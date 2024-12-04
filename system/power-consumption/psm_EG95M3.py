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

import pm
import net
import utime
import osTimer
import checkNet
from misc import Power


def Business_code_example(run_time):
    i = 0
    for i in range(run_time):
        print("Business app running")
        # usiness code here
        utime.sleep(1)


def device_power_restart(args):
    print("device_power_restart")
    Power.powerRestart()


def psm_try_set():
    if pm.get_psm_time()[0] == 1:  # 开机时获取psm是否设置，如果已经使能，则无需再次进行设置
        print("PSM has been enable, set pass")
        return 0
    else:
        return pm.set_psm_time(0, 1, 0, 15)  # T3412=10min T3324=30s


def psm_failed_handle(delay_time, autosleep_timer):
    autosleep_timer.start(600 * 1000, 0, device_power_restart)  # 启动osTimer重启设备, 当psm生效后，该osTimer自动失效
    print("autosleep_timer start")
    utime.sleep(delay_time)  # 等待指定时长后，触发PSM失败的处理逻辑，即使用autosleep并等待osTimer重启设备

    print("Device not into psm mode. Try to set autosleep.")
    pm.autosleep(1)
    print("Wait device into autosleep and wait device reset.")


if __name__ == '__main__':
    pm.autosleep(0)
    if pm.get_psm_time()[0] == 1:
        if pm.set_psm_time(0) is True:
            print("Disable psm successful.")
        else:
            print("Disable psm failed.")

    if net.getModemFun() != 1:
        net.setModemFun(1)
        print("Set CFUN1")

    psm_failed_delay_time = 60 + 30  # PSM的 T3324超时30S后，启用错误处理逻辑
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1:
        print('Network connection successful.')
    else:
        print('Network connection failed.')
        psm_failed_delay_time = 1  # PSM依赖网络，无网络时应立即使用RTC代替之

    Business_code_example(10)  # 业务代码运行

    if stage == 3 and state == 1:
        res = psm_try_set()  # 网络连接成功时尝试设置PSM，如果PSM设置已经生效，则不用再次设置
        print("psm_try_set res", res)
    autosleep_timer = osTimer()
    print("autosleep_timer init.")
    psm_failed_handle(psm_failed_delay_time, autosleep_timer)  # 运行错误处理，若模组能正常进入PSM，在sleep中就进入PSM了，该处实际的处理逻辑并不会运行
