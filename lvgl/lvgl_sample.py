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

from machine import Pin
from machine import LCD
import lvgl as lv

gpio1 = Pin(Pin.GPIO25, Pin.OUT, Pin.PULL_DISABLE, 1)
gpio2 = Pin(Pin.GPIO20, Pin.OUT, Pin.PULL_DISABLE, 1)

init_param=(
0, 0, 0x11,
2, 0, 120,
0, 0, 0x00,
0, 1, 0x36,
1, 1, 0x00,
0, 1, 0x3A,
1, 1, 0x05,
0, 1, 0x35,
1, 1, 0x00,
0, 1, 0xC7,
1, 1, 0x00,
0, 1, 0xCC,
1, 1, 0x09,
0, 5, 0xB2,
1, 1, 0x0C,
1, 1, 0x0C,
1, 1, 0x00,
1, 1, 0x33,
1, 1, 0x33,
0, 1, 0xB7,
1, 1, 0x35,
0, 1, 0xBB,
1, 1, 0x36,
0, 1, 0xC0,
1, 1, 0x2C,
0, 1, 0xC2,
1, 1, 0x01,
0, 1, 0xC3,
1, 1, 0x0D,
0, 1, 0xC4,
1, 1, 0x20,
0, 1, 0xC6,
1, 1, 0x0F,
0, 2, 0xD0,
1, 1, 0xA4,
1, 1, 0xA1,
0, 14, 0xE0,
1, 1, 0xD0,
1, 1, 0x17,
1, 1, 0x19,
1, 1, 0x04,
1, 1, 0x03,
1, 1, 0x04,
1, 1, 0x32,
1, 1, 0x41,
1, 1, 0x43,
1, 1, 0x09,
1, 1, 0x14,
1, 1, 0x12,
1, 1, 0x33,
1, 1, 0x2C,
0, 14, 0xE1,
1, 1, 0xD0,
1, 1, 0x18,
1, 1, 0x17,
1, 1, 0x04,
1, 1, 0x03,
1, 1, 0x04,
1, 1, 0x31,
1, 1, 0x46,
1, 1, 0x43,
1, 1, 0x09,
1, 1, 0x14,
1, 1, 0x13,
1, 1, 0x31,
1, 1, 0x2D,
0, 0, 0x29,
0, 1, 0x36,
1, 1, 0x00,
0, 0, 0x2c,
)

XSTART_H = 0xf0
XSTART_L = 0xf1
YSTART_H = 0xf2
YSTART_L = 0xf3
XEND_H = 0xE0
XEND_L = 0xE1
YEND_H = 0xE2
YEND_L = 0xE3


XSTART = 0xD0
XEND = 0xD1
YSTART = 0xD2
YEND = 0xD3

lcd = LCD()

init_data = bytearray(init_param)



invalid_param = (
0,4,0x2a,
1,1,0xf0,
1,1,0xf1,
1,1,0xe0,
1,1,0xe1,
0,4,0x2b,
1,1,0xf2,
1,1,0xf3,
1,1,0xe2,
1,1,0xe3,
0,0,0x2c,

)
test_invalid = bytearray(invalid_param)

test3 = (
0,0,0x28,
2,0,120,
0,0,0x10,
)
test_displayoff = bytearray(test3)

test4 = (
0,0,0x11,
2,0,20,
0,0,0x29,
)
test_displayon = bytearray(test4)


lcd.lcd_init(init_data, 240, 320, 52000, 1, 4, 0, test_invalid, test_displayon, test_displayoff, None)

LCD_SIZE_W = 240
LCD_SIZE_H = 320

lv.init()

# Register SDL display driver.
disp_buf1 = lv.disp_draw_buf_t()
buf1_1 = bytearray(LCD_SIZE_W * LCD_SIZE_H * 2)
disp_buf1.init(buf1_1, None, len(buf1_1))
disp_drv = lv.disp_drv_t()
disp_drv.init()
disp_drv.draw_buf = disp_buf1
disp_drv.flush_cb = lcd.lcd_write
disp_drv.hor_res = LCD_SIZE_W
disp_drv.ver_res = LCD_SIZE_H
disp_drv.register()

lv.tick_inc(5)
lv.task_handler()

# create a screen object
screen = lv.obj()

# create a image object
img1 = lv.img(screen)
img1.set_pos(80, 80)
img1.set_src("U:/quectel.jpg")

# create a label object
label1 = lv.label(screen)
label1.set_text("Hello Quecpython")
label1.center()
label1.set_pos(0, 80)

# load the screen
lv.scr_load(screen)






