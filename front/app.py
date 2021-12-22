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
        rqst = requests.post('http://172.17.0.2/app', data=json.dumps(data)).content
        ans = json.loads(rqst.decode('utf-8'))['payload']
        flash(ans)
    else:
        ans = ''
    return render_template('redact.html', title='Redactor', form=form)
