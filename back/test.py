import requests
import json

data = {
    "payload": 'комиссия надбавка зависит от того, где и сколько паев открытого фонда "Рога и копыта" вы покупаете'
}

ans = requests.post('http://0.0.0.0/app', data=json.dumps(data)).content
# ans = requests.post('http://35.238.115.176:80/app', data=json.dumps(data)).content

print(json.loads(ans.decode('utf-8'))['payload'])
