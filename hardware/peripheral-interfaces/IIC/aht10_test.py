'''
File: i2c_qma7981.py
Project: i2c
File Created: Sunday, 11th March 2022 3:51:22 pm
Author: elian.wang

-----
Copyright 2022 - 2022 quectel
'''

#import log
from machine import I2C
#from machine import I2C_simulation
import utime as time
"""
1. calibration校准
2. Trigger measurement触发器测量
3. read data
"""

# API  手册 http://qpy.quectel.com/wiki/#/zh-cn/api/?id=i2c
# AHT10 说明书
#  https://server4.eca.ir/eshop/AHT10/Aosong_AHT10_en_draft_0c.pdf


class aht10class():
    i2c_log = None
    i2c_dev = None
    i2c_addre = None

    # Initialization command
    AHT10_CALIBRATION_CMD = 0xE1
    # Trigger measurement
    AHT10_START_MEASURMENT_CMD = 0xAC
    # reset
    AHT10_RESET_CMD = 0xBA

    def write_data(self, data):
        print(self.i2c_addre, data, len(data))
        self.i2c_dev.write(self.i2c_addre,
                           bytearray(0x00), 0,
                           bytearray(data), len(data))
        pass

    def read_data(self, length):
        print("read_data start")
        r_data = [0x00 for i in range(length)]
        r_data = bytearray(r_data)
        print("read_data start1")
        ret = self.i2c_dev.read(self.i2c_addre,
                          bytearray(0x00), 0,
                          r_data, length,
                          0)
        print("read_data start2")
        print('ret',ret)
        print('r_data:',r_data)
        return list(r_data)

    def aht10_init(self, addre=0x38, Alise="Ath10"):
        #self.i2c_log = log.getLogger(Alise)
        self.i2c_dev = I2C(I2C.I2C1, I2C.FAST_MODE)  # 返回i2c对象 i2c类功能：用于设备之间通信的双线协议。
        print("test 11")
        #self.i2c_dev = I2C_simulation(I2C_simulation.GPIO19, I2C_simulation.GPIO20, 200)   #asr
        #self.i2c_dev = I2C_simulation(I2C_simulation.GPIO10, I2C_simulation.GPIO11, 300)  #zhanrui
        #self.i2c_dev = I2C_simulation(I2C_simulation.GPIO13, I2C_simulation.GPIO14, 500)  #BC25
        #self.i2c_dev = I2C_simulation(I2C_simulation.GPIO3, I2C_simulation.GPIO4, 600)    #gao
        self.i2c_addre = addre
        self.sensor_init()
        pass

    def aht10_transformation_temperature(self, data):
        r_data = data
        #　根据数据手册的描述来转化温度
        humidity = (r_data[0] << 12) | (
            r_data[1] << 4) | ((r_data[2] & 0xF0) >> 4)
        humidity = (humidity/(1 << 20)) * 100.0
        print("current humidity is {0}%".format(humidity))
        temperature = ((r_data[2] & 0xf) << 16) | (
            r_data[3] << 8) | r_data[4]
        temperature = (temperature * 200.0 / (1 << 20)) - 50
        print("current temperature is {0}°C".format(temperature))
        
    def sensor_init(self):
        '''
        传感器初始化，校准
        '''
        # calibration
        print("test 112")
        self.write_data([self.AHT10_CALIBRATION_CMD, 0x08, 0x00])
        print("test 113")
        time.sleep_ms(300)  # at last 300ms
        print("test 114")
        pass

    def ath10_reset(self):
        self.write_data([self.AHT10_RESET_CMD])
        time.sleep_ms(20)  # at last 20ms

    def Trigger_measurement(self):
        # Trigger data conversion
        self.write_data([self.AHT10_START_MEASURMENT_CMD, 0x33, 0x00])
        time.sleep_ms(200)  # at last delay 75ms
        # check has success
        r_data = self.read_data(6)
        # check bit7
        if (r_data[0] >> 7) != 0x0:
            print("Conversion has error")
        else:
            self.aht10_transformation_temperature(r_data[1:6])

ath_dev = None

def i2c_aht10_test():
    global ath_dev
    ath_dev = aht10class()
    ath_dev.aht10_init()
    print("test 1")

    # 测试十次
    for i in range(5):
        print("test 1 ",i)
        ath_dev.Trigger_measurement()
        print("test 1 end",i)
        time.sleep(1)


if __name__ == "__main__":
    print('start')
    i2c_aht10_test()
