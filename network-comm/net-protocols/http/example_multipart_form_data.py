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

url = 'http://www.example.com'
boundary = '----WebKitFormBoundaryrGKCBY7qhFd3TrwA'
headers = {'Content-Type': 'multipart/form-data; boundary=' + boundary}

data = ''
data += '--' + boundary + '\r\n'
data += 'Content-Disposition: form-data; name="text"\r\n'
data += '\r\n'
data += 'title\r\n'
data += '--' + boundary + '\r\n'
data += 'Content-Disposition: form-data; name="file"; filename="test.png"\r\n'
data += 'Content-Type: image/png\r\n'
data += '\r\n'

data = bytes(data.encode())

with open('/usr/test.png', 'rb') as f:
    data += f.read()

data += b'\r\n'
data += b'--' + bytes(boundary.encode()) + b'--'

request.post(url, headers=headers, data=data)