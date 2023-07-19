import request

# 天气查询URL
url = 'http://restapi.amap.com/v3/weather/weatherInfo?key=2875b8171f67f3be3140c6779f12dcba&city=北京&extensions=base'

# 发送 HTTP GET 请求
response = request.get(url)

# 获取天气查询网站返回的原始数据
data = ''
for i in response.text:
	data += i
print('raw data responsed from website:')
print(data)