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
        # Business code here
        utime.sleep(1)


def device_power_restart(args):
    print("device_power_restart")
    Power.powerRestart()


def psm_try_set():
    # 开机时获取 psm 是否设置，如果已经使能，则无需再次进行设置
    # Get whether psm is set when booting. If it is already enabled, there is no need to set it again.
    if pm.get_psm_time()[0] == 1:
        print("PSM has been enable, set pass")
        return 0
    else:
        return pm.set_psm_time(0, 1, 0, 15)  # T3412=10min T3324=30s


def psm_failed_handle(delay_time, autosleep_timer):
    # 启动 osTimer 重启设备, 当 psm 生效后，该 osTimer 自动失效
    # Start osTimer and restart the device. When psm takes effect, the osTimer will automatically expire.
    autosleep_timer.start(600 * 1000, 0, device_power_restart)
    print("autosleep_timer start")
    # 等待指定时长后，触发 psm 失败的处理逻辑，即使用 autosleep 并等待 osTimer 重启设备
    # After waiting for the specified time, trigger the processing logic of psm failure, that is, use autosleep and wait for osTimer to restart the device.
    utime.sleep(delay_time)

    print("Device not into psm mode. Try to set autosleep.")
    pm.autosleep(1)
    print("Wait device into autosleep and wait device reset.")


if __name__ == '__main__':
    """
    测试该脚本功能可将文件重命名为 main.py 烧录进模块中进行测试，模块 PSM 休眠唤醒后即可自动执行脚本中的功能。
    To test the script function, you can rename the file to main.py and burn it into the module for testing.
    After the module PSM wakes up from sleep, it can automatically execute the functions in the script.
    """
    pm.autosleep(0)
    if pm.get_psm_time()[0] == 1:
        if pm.set_psm_time(0) is True:
            print("Disable psm successful.")
        else:
            print("Disable psm failed.")

    if net.getModemFun() != 1:
        net.setModemFun(1)
        print("Set CFUN1")

    # PSM 的 T3324 超时 30s 后，启用错误处理逻辑
    # After PSM's T3324 times out 30s, error handling logic is enabled
    psm_failed_delay_time = 60 + 30
    stage, state = checkNet.waitNetworkReady(30)
    if stage == 3 and state == 1:
        print('Network connection successful.')
    else:
        print('Network connection failed.')
        # PSM 依赖网络，无网络时应立即使用 autosleep 代替之
        # PSM relies on the network. If there is no network, you should use autosleep immediately instead.
        psm_failed_delay_time = 1

    # 业务代码运行
    # Business code running
    Business_code_example(10)

    if stage == 3 and state == 1:
        # 网络连接成功时尝试设置PSM，如果PSM设置已经生效，则不用再次设置
        # Try to set up PSM when the network connection is successful.
        # If the PSM setting has already taken effect, there is no need to set it up again.
        res = psm_try_set()
        print("psm_try_set res", res)
    autosleep_timer = osTimer()
    print("autosleep_timer init.")
    # 运行错误处理，若模组能正常进入PSM，在sleep中就进入PSM了，该处实际的处理逻辑并不会运行
    # Run error processing. If the module can enter PSM normally, it will enter PSM in sleep,
    # and the actual processing logic there will not run.
    psm_failed_handle(psm_failed_delay_time, autosleep_timer)
