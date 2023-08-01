from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email
from flask_babel import lazy_gettext as _l


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
    name = StringField(_l('Full name'), validators=[DataRequired()],
                       render_kw=get_input_params('name', _l('Full name')))
    email_input_params = get_input_params(
        _l('Email'), _l('yours@example.com'), {'inputmode': 'email'})
    email = EmailField(_l('Email'), validators=[Email()],
                       render_kw=email_input_params)
    orgname_input_params = get_input_params('orgname', _l('Organisation name'))
    orgname = StringField(_l('Organisation name'), validators=[DataRequired()],
                          render_kw=orgname_input_params)
    job_title_input_params = get_input_params('jobtitle', _l('Job title'))
    jobtitle = StringField(_l('Job title'),
                           validators=[DataRequired()],
                           render_kw=job_title_input_params)
    submit = SubmitField(_l('Update'), render_kw={
        "class_": "auth0-lock-submit submit",
        "style": "background-color: rgb(227, 24, 55); display: block;",
        "aria-label": _l("Update")
    })
