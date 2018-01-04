from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField, ValidationError
from wtforms.validators import Required, Length, Email, Regexp
from flask_pagedown.fields import PageDownField
from ..models import Role, User

# Form Class
class EditProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField("About You")
    submit = SubmitField('Save Changes')

class AdminEditProfileForm(FlaskForm):
    usr_reg = '^[A-Za-z][A-Za-z0-9_.]*$'
    usr_msg = 'Usernames must have only letters, numbers, dot(.) or underscore(_)'
    email = StringField('Email', validators=[Length(1,64), Required(), Email()])
    username = StringField('UserName', validators=[Length(1,64), Required(), Regexp(usr_reg,0,usr_msg)])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role',coerce=int)
    name = StringField('Name', validators=[Length(0,64)])
    location = StringField('Location', validators=[Length(0,64)])
    about_me = TextAreaField('About Yourself')
    submit = SubmitField('Save Changes')

    def __init__(self, user, *args, **kwargs):
        super(AdminEditProfileForm, self).__init__(*args,**kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user  = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already exists')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('username already exists')

class PostsForm(FlaskForm):
    body = PageDownField('Whats on your mind?', validators=[Required()])
    submit = SubmitField('Post')