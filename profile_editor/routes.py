import logging

from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from flask import redirect, render_template, session, url_for, \
    flash, Blueprint, request, current_app
from flask_babel import _

import profile_editor.logic as logic
import profile_editor.forms as forms

log = logging.getLogger(__name__)
oauth = OAuth()
app_blueprint = Blueprint('main', __name__)


@app_blueprint.route("/")
def home():
    lang = request.args.get("lang", None)
    if lang and lang in current_app.config['LANGUAGES']:
        session["lang"] = lang
    set_or_clear_session_variable("back_url")
    set_or_clear_session_variable("after_save_url")
    set_or_clear_session_variable("flash_message")

    if session.get("user_id", ""):
        return redirect("/profile")
    else:
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("main.callback", _external=True)
        )


def set_or_clear_session_variable(variable_name):
    value = request.args.get(variable_name, None)

    if value:
        session[variable_name] = value
    else:
        session.pop(variable_name, default=None)


@app_blueprint.route("/profile", methods=['GET', 'POST'])
def profile():
    if not session.get("user_id", ""):
        return redirect("/")

    form = forms.UserDataForm()
    user_id = session.get("user_id")

    if form.validate_on_submit():
        logic.update_user_data(form, user_id)
        flash(_('User profile successfully saved'))
        return redirect(url_for("main.profile", success=True))
    elif not form.is_submitted():
        form = logic.load_data_from_server_to_form(form, user_id)

    back_url = session.get("back_url") if session.get("back_url", "") else None
    after_save_url = session.get("after_save_url") \
        if session.get("after_save_url", "") else None
    flash_message = session.pop("flash_message", None)
    if flash_message:
        flash(flash_message)
    success = request.args.get("success", False)

    return render_template(
        "profile.html",
        form=form,
        back_url=back_url,
        after_save_url=after_save_url,
        success=success
    )


@app_blueprint.route("/change_password", methods=["GET", "POST"])
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
        + current_app.config["AUTH0_DOMAIN"]
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("main.home", _external=True),
                "client_id": current_app.config["AUTH0_CLIENT_ID"],
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
