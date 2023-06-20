from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email


class UserDataForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()], render_kw={"class_": "form-control"})
    email = EmailField('Email', validators=[Email()], render_kw={"class_": "form-control"})
    orgname = StringField('Organisation name', validators=[DataRequired()], render_kw={"class_": "form-control"})
    jobtitle = StringField('Job title', validators=[DataRequired()], render_kw={"class_": "form-control"})
    submit = SubmitField('Save',  render_kw={"class_": "btn"})