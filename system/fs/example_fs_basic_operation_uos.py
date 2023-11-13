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

import uos

def main():
    # 创建文件 此处并没有对文件进行写入操作
    f = open("/usr/uos_test","w")
    f.close()
    del f

    # 查看文件是否存在
    t = uos.listdir("/usr")
    print("usr files:{}".format(t))

    if "uos_test" not in t:
        print("file not exist test fail")
        return

    # 查看文件状态
    a = uos.stat("/usr/uos_test")
    print("file size:{}bytes".format(a[6]))

    # 重命名文件
    uos.rename("/usr/uos_test", "/usr/uos_test_new")
    t = uos.listdir("/usr")
    print("test file renamed, usr files:{}".format(t))

    if "uos_test_new" not in t:
        print("renamed file not exist test fail")
        return

    # 删除文件
    uos.remove("/usr/uos_test_new")
    t = uos.listdir("/usr")
    print("remove test file, usr files:{}".format(t))

    if "uos_test_new" in t:
        print("remove file fail, test fail")
        return

    # 目录操作
    t = uos.getcwd()
    print("current path:{}".format(t))
    uos.chdir("/usr")
    t = uos.getcwd()
    print("current path:{}".format(t))
    if "/usr" != t:
        print("dir change fail")
        return

    uos.mkdir("testdir")
    t = uos.listdir("/usr")
    print("make dir, usr files:{}".format(t))

    if "testdir" not in t:
        print("make dir fail")
        return

    uos.rmdir("testdir")
    t = uos.listdir("/usr")
    print("remove test dir, usr files:{}".format(t))
    
    if "testdir" in t:
        print("remove dir fail")
        return

if __name__ == "__main__":
    main()