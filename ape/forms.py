from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email


def get_input_params(name, label, additional_params=None):
    params = {
        "class_": "auth0-lock-input",
        "autocomplete": "off",
        "autocapitalize": "off",
        "aria-label": name,
        "aria-invalid": "false",
        "placeholder": label
    }

    # Add additional parameters from the dictionary
    if additional_params is not None:
        params.update(additional_params)

    return params


class UserDataForm(FlaskForm):
    name = StringField('Full name', validators=[DataRequired()],
                       render_kw=get_input_params('name', 'Full name'))
    email_input_params = get_input_params(
        'Email', 'yours@example.com', {'inputmode': 'email'})
    email = EmailField('Email', validators=[Email()],
                       render_kw=email_input_params)
    orgname_input_params = get_input_params('orgname', 'Organisation name')
    orgname = StringField('Organisation name', validators=[DataRequired()],
                          render_kw=orgname_input_params)
    job_title_input_params = get_input_params('jobtitle', 'Job title')
    jobtitle = StringField('Job title',
                           validators=[DataRequired()],
                           render_kw=job_title_input_params)
    submit = SubmitField('Update', render_kw={
        "class_": "auth0-lock-submit submit",
        "style": "background-color: rgb(227, 24, 55); display: block;",
        "aria-label": "Update"
    })
