import logging
import os
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import redirect, render_template, session, url_for, \
    flash, Blueprint, request

import ape.logic as logic
import ape.forms as forms

log = logging.getLogger(__name__)
oauth = OAuth()
app_blueprint = Blueprint('main', __name__)
env = os.environ


@app_blueprint.route("/")
def home():
    return_url = request.args.get("return_url", None)
    if return_url:
        session["return_url"] = return_url
    if session.get("user_id", ""):
        return redirect("/profile")
    else:
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("main.callback", _external=True)
        )


@app_blueprint.route("/profile", methods=['GET', 'POST'])
def profile():
    if not session.get("user_id", ""):
        return redirect("/")

    form = forms.UserDataForm()
    user_id = session.get("user_id")

    if form.validate_on_submit():
        logic.update_user_data(form, user_id)
        flash('User profile successfully saved')
        return redirect(url_for("main.profile"))
    elif not form.is_submitted():
        form = logic.load_data_from_server_to_form(form, user_id)

    url = session.get("return_url") if session.get("return_url", "") else None

    return render_template(
        "profile.html",
        form=form,
        return_url=url
    )


@app_blueprint.route("/change_password", methods=['GET', 'POST'])
def change_password():
    if not session.get("user_id", ""):
        return redirect("/")

    pw_change_url = logic.get_password_change_url(session.get("user_id"))
    return redirect(location=pw_change_url)


@app_blueprint.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user_id"] = token.get("userinfo").get("sub")
    return redirect("/profile")


@app_blueprint.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("main.home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus
        )
    )


@app_blueprint.errorhandler(Exception)
def exception_handler(e):
    log.error(f"An exception was caught: {e}", e)
    return render_template(
        "error.html"
    )
