import sys
import urllib3

http = urllib3.PoolManager()

url = sys.argv[1]
response = http.request('GET', url)

print(response.data.decode('utf-8'))
