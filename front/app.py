from flask import Flask
from flask import render_template, flash, redirect
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
import requests
import json
import difflib

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
        ans = json.loads(rqst.decode('utf-8'))['payload']
        message = {
            'text': ans.replace('\n', '<br>'),
            'diff': create_diff(text, ans).replace('\n', '<br>')
        }
        flash(message)
        print(ans)
    return render_template('redact.html', title='Redactor', form=form)

def create_diff(a, b):
    ans = ''
    for s in enumerate(difflib.ndiff(a, b)):
        if s[1][0] == ' ':
            ans += str(s[1][-1])
        elif s[1][0] == '-':
            ans += '<span style="background: violet">' + str(s[1][-1]) + '</span>'
    return ans