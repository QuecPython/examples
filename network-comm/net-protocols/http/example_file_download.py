import request

# http 协议的（非 https）百度URL
url = 'http://www.baidu.com'

# 发送 HTTP GET 请求
response = request.get(url)

# 创建文件baidu.html
f = open('/usr/baidu.html', 'wb')    # 'wb' 表示写入二进制数据

# 获取网页文件内容，并写入文件
for i in response.content:
	f.write(i)

# 网页数据拉取完毕，关闭文件
f.close()

# 打开文件baidu.html
with open('/usr/baidu.html', 'rb') as f:    # 'rb' 以二进制方式读取文件
	r = f.read()
    while r:
        print(r)
        r = f.read()

# 关闭文件
f.close()