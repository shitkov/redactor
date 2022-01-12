# export FLASK_APP=app.py
# python3 -m flask run --host=0.0.0.0
from flask import Flask
from flask import render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
import requests
import json

app = Flask(__name__)

app.config['SECRET_KEY'] = 'you-will-never-guess'

class LoginForm(FlaskForm):
    text = TextAreaField('Enter text:', render_kw={'rows': 5})
    redact = SubmitField('Redact')

@app.route('/redactor', methods=['GET', 'POST'])
def redact():
    form = LoginForm()
    text = form.text.data
    if text:
        data = {'payload': str(text)}
        rqst = requests.post('http://back/app', data=json.dumps(data)).content
        # rqst = requests.post('http://0.0.0.0/app', data=json.dumps(data)).content
        ans = json.loads(rqst.decode('utf-8'))['payload']
        message = {
            'text': ans['text'].replace('\n', '<br>'),
            'diff': highlight_diff(text, ans['diff']).replace('\n', '<br>'),
            'err': ans['err']
        }
        flash(message)
        print(ans)
    return render_template('redact.html', title='Redactor', form=form)

def highlight_diff(clean, diff):
    ans = ''
    for i, symb in enumerate(diff):
        if symb == ' ':
            ans += clean[i]
        elif symb == '-':
            ans += '<span style="background: violet">' + clean[i]  + '</span>'
    return ans