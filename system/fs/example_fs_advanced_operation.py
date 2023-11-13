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

import ql_fs

def main():
    # 递归式创建文件夹, 传入文件夹路径
    ql_fs.mkdirs("usr/a/b")

    # 查看文件或文件夹是否存在
    ret = ql_fs.path_exists("/usr/a/b")
    if ret:
        print("make dir success")
    else:
        print("make dir fail")
        return

    # 创建文件或者更新文件数据
    data = {"test":1}
    ql_fs.touch("/usr/a/b/config.json", data)
	
    # 查看文件或文件夹是否存在
    ret = ql_fs.path_exists("/usr/a/b/config.json")
    if ret:
        print("create file success")
    else:
        print("create file fail")
        return
	
	# 读取json文件
    data = ql_fs.read_json("/usr/a/b/config.json")
    print("config json read content:{}".format(data))
    data = ql_fs.read_json("/usr/system_config.json")
    len = ql_fs.path_getsize('usr/system_config.json')
    print("system_config json length:{}".format(len))
    print("system_config json read content:{}".format(data))
	
	# 文件拷贝
    ql_fs.file_copy("/usr/a/b/config.json", "usr/system_config.json")
    data = ql_fs.read_json("/usr/a/b/config.json")
    print("copy json read content:{}".format(data))
	
	# 获取文件所在文件夹路径
    ret = ql_fs.path_dirname("/usr/a/b/config.json")
    print("path of the file:{}".format(ret))
	
	# 删除文件夹和其下的文件
    ql_fs.rmdirs("usr/a")

    # 查看文件或文件夹是否存在
    ret = ql_fs.path_exists("/usr/a/b/config.json")
    if ret:
        print("remove file fail, test fail")

    ret = ql_fs.path_exists("/usr/a/b")
    if ret:
        print("remove dir2 fail, test fail")
		
    ret = ql_fs.path_exists("/usr/a")
    if ret:
        print("remove dir1 fail, test fail")


if __name__ == "__main__":
    main()