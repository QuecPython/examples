import utime
from machine import RTC
from misc import Power

def Business_code_example(run_time):
    i = 0
    for i in range(run_time):	
        print("Business app running")
		#Business code here  
        utime.sleep(1)

    return    

def rtc_alarm_set(alarm_time):
    rtc = RTC()
    tm_rtc_tuple = rtc.datetime()
    tm_rtc_second = utime.mktime((tm_rtc_tuple[0], tm_rtc_tuple[1], tm_rtc_tuple[2], tm_rtc_tuple[4], tm_rtc_tuple[5], tm_rtc_tuple[6], 0, 0))

    alarm_second = tm_rtc_second + alarm_time #RTC闹钟设为当前时间 + alarm_time, 即模组会在经过alarm_time s 后重启
    alarm_tuple = utime.localtime(alarm_second)

    rtc.set_alarm([alarm_tuple[0], alarm_tuple[1], alarm_tuple[2], alarm_tuple[6], alarm_tuple[3], alarm_tuple[4], alarm_tuple[5], 0])
    rtc.enable_alarm(1)

    utime.sleep(1)#部分模组RTC闹钟的设置是异步的，需要一定延迟，保证底层RTC信息能够被写入
    return


if __name__ == '__main__':
    alarm_time = 600 #RTC alarm 10min后触发
    Business_code_example(10)#业务代码运行
      
    rtc_alarm_set(alarm_time)
    Power.powerDown()#设置alarm后关机


