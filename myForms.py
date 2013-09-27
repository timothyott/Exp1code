from flask.ext.wtf import Form
from wtforms import TextField, HiddenField, SubmitField, PasswordField, validators

class ChoiceForm(Form):
    pass

class LoginForm(Form):
    userID = TextField('User ID')
    password = PasswordField('Password')
    submit = SubmitField('Login')

class RegistrationForm(Form):
    userID = HiddenField('User ID')
    password = HiddenField('Password')
    submit = SubmitField('Start')
