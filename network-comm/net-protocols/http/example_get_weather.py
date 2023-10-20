import request

# Weather query URL
url = 'http://restapi.amap.com/v3/weather/weatherInfo?key=2875b8171f67f3be3140c6779f12dcba&city=北京&extensions=base'

# Send the HTTP GET request
response = request.get(url)

# Get the raw data returned by the weather query website
data = ''
for i in response.text:
	data += i
print('raw data responsed from website:')
print(data)