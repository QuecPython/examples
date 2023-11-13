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

# 创建一个test.txt文件,注意路径在/usr下
f = open("/usr/test.txt", "w+")
i = f.write("hello world\n")
i = i + f.write("hello quecpython\n")
print("write length{}".format(i))
f.seek(0)
str = f.read(10)
print("read content:{}".format(str))
f.seek(0)
str = f.readline()
print("read line content:{}".format(str))
f.seek(0)
str = f.readlines()
print("read all lines content:{}".format(str))
f.close()
print("test end")