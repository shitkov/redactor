import requests
import json

data = {
    "payload": 'комиссия надбавка зависит от того, где и сколько паев открытого фонда "Рога и копыта" вы покупаете'
}

ans = requests.post('http://127.0.0.1:8000/app', data=json.dumps(data)).content

print(json.loads(ans.decode('utf-8'))['payload'])
