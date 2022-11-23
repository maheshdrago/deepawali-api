import requests

url = 'http://127.0.0.1:5000/domainData'
domains = [
"gg.co",
]
myobj = {'domains': domains}

x = requests.post(url, json = myobj)

print(x.text)