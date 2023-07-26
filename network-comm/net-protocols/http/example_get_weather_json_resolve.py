import request

# Weather query URL
url = 'http://restapi.amap.com/v3/weather/weatherInfo?key=2875b8171f67f3be3140c6779f12dcba&city=北京&extensions=base'

# Send the HTTP GET request
response = request.get(url)

# Get raw data from the website and parse it into a dict type by calling the json() method of response object
data = response.json()
data = data['lives'][0]
for k,v in data.items():
	print('%s: %s' % (k, v))