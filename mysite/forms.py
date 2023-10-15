from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField, HiddenField
from wtforms.validators import DataRequired, EqualTo


class LoginForm(FlaskForm):
    csrf = True

    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    submit = SubmitField()


class SignUpForm(FlaskForm):
    csrf = True

    email = EmailField(validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    confirm_password = PasswordField(
        validators=[EqualTo('password', message="Passwords must match")])
    submit = SubmitField()


class QuestionForm(FlaskForm):
    csrf = True

    question_number = HiddenField()
    question_id = HiddenField()
    answer = StringField(validators=[DataRequired()])
    submit = SubmitField()
