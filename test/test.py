# uvicorn main:app --host 0.0.0.0 --port 80
import requests
import json

text = 'мома мьыыла рыаму.'

data = {'payload': str(text)}
rqst = requests.post('http://0.0.0.0/app', data=json.dumps(data)).content
ans = json.loads(rqst.decode('utf-8'))['payload']
print(ans)