from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from pprint import pprint

class RegistrationForm(FlaskForm):
    username = StringField('Brukernavn',
        validators = [DataRequired(),
        Length(min=2,max=20),
        ])
    email = StringField('Epost',
        validators = [DataRequired(),Email()])
    password = PasswordField('Passord',
        validators = [DataRequired()])
    confirm_password = PasswordField('Bekreft passord',
        validators = [DataRequired(),
        EqualTo('password')])

    submit = SubmitField('Registrer')

class LoginForm(FlaskForm):
    email = StringField('Epost',
        validators = [DataRequired(),Email()])
    password = PasswordField('Passord',
        validators = [DataRequired()])
    remember = BooleanField('Husk påloggingsinformasjon')


    submit = SubmitField('Logg inn')

class ContactForm(FlaskForm):
    name = StringField('Navn',
        validators = [DataRequired()])
    email = StringField('Epost',
        validators = [DataRequired(),Email()])
    inquiry = StringField('Henvendelse',
                          validators=[DataRequired(),Length(max=200)])
    submit = SubmitField('Send')
    



















