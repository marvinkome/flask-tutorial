from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import Required, Email, Length, Regexp, EqualTo
from ..models import User

# Form Class
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me loged in')
    submit = SubmitField('Submit')
    
class RegistrationForm(FlaskForm):
    regexp = '^[A_Za-z][A_Za-z0-9_.]*$'
    umsg = 'Usernames must contain only letters, numbers, dot and underscore'
    pmsg = 'Password must match'

    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    username = StringField('Username', validators=[Required(), Length(1, 64), Regexp(regexp,0,umsg)])
    password = PasswordField('Password', validators=[Required()])
    password2 = PasswordField('Confirm Password', validators=[
        Required(), EqualTo('password',message=pmsg)])
    submit = SubmitField('Create Account')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already registered')
