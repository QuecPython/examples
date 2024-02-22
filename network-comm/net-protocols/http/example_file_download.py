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

import request

# Baidu URL over HTTP protocol (not HTTPS)
url = 'http://www.baidu.com'

# Send the HTTP GET request
response = request.get(url)

# Create file baidu.html
f = open('/usr/baidu.html', 'wb')    # 'wb' 表示写入二进制数据

# Get web page content and write to the file
for i in response.content:
	f.write(i)

# Close the file after fetching the web page data
f.close()

# Open file baidu.html
with open('/usr/baidu.html', 'rb') as f:    # 'rb' means reading the file in binary mode
	r = f.read()
    while r:
        print(r)
        r = f.read()

# Close the file
f.close()