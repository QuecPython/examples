import request

# 天气查询URL
url = 'http://restapi.amap.com/v3/weather/weatherInfo?key=2875b8171f67f3be3140c6779f12dcba&city=北京&extensions=base'

# 发送 HTTP GET 请求
response = request.get(url)

# 获取天气查询网站返回的原始数据，并解析为dict
data = response.json()
data = data['lives'][0]
for k,v in data.items():
	print('%s: %s' % (k, v))