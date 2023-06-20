from flask_wtf.csrf import generate_csrf

from ape.app import create_app
from ape.forms import UserDataForm


class TestUserDataForm:
    def test_form_when_correct_data(self):
        app, oauth = create_app()

        with app.test_request_context('/profile', ):
            form = UserDataForm()
            form.email.data = 'correct@email.address'
            form.name.data = 'Name'
            form.orgname.data = 'Org'
            form.jobtitle.data = 'Job Expert'
            form.csrf_token.data = generate_csrf()

            assert form.validate()
            assert len(form.errors) == 0

    def test_form_when_incorrect_data(self):
        app, oauth = create_app()

        with app.test_request_context('/profile', ):
            form = UserDataForm()
            form.email.data = 'incorrect@email'
            form.name.data = ''
            form.orgname.data = ''
            form.jobtitle.data = ''
            form.csrf_token.data = generate_csrf()

            assert not form.validate()
            assert len(form.errors) == 4
            assert form.errors == {
                'name': ['This field is required.'],
                'email': ['Invalid email address.'],
                'orgname': ['This field is required.'],
                'jobtitle': ['This field is required.']
            }


