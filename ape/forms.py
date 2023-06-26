from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email


class UserDataForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()])
    email = EmailField('Email', validators=[Email()])
    orgname = StringField('Organisation name', validators=[DataRequired()])
    jobtitle = StringField('Job title', validators=[DataRequired()])
    submit = SubmitField('Save')

