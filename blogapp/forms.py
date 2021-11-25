from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms.widgets import TextArea
from blogapp.models import User
from flask_login import current_user

###########################################
####### ===FORMS===FORMS===FORMS===#######$
###########################################

class SignupForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Register")

    ### ==CUSTOM FORM VALIDATIONS=== ###
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user :
            raise ValidationError('Username Unavailable. Please Choose a Different one')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
                raise ValidationError('Email Unavailable. Please Choose a Different one')
    



class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")


class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("Post")


class AccountUpdateForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    picture = FileField("Update Profile Picture", validators=[FileAllowed(['jpeg','jpg','png'])])
    submit = SubmitField("Submit")

    ### ==CUSTOM FORM VALIDATIONS=== ###
    def validate_username(self, username):
        form = AccountUpdateForm()
        user = User.query.filter_by(username=username.data).first()
        if user and current_user.username != form.username.data:
            raise ValidationError('Username Unavailable. Please Choose a Different one')
    
    def validate_email(self, email):
        form = AccountUpdateForm()
        user = User.query.filter_by(email=email.data).first()
        if user and current_user.email != form.email.data:
            raise ValidationError('Email Unavailable. Please Choose a Different one')

    


class RequestResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request Reset")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('Email Account Unavailable. Please Register First')



class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Reset Password")