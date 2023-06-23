from urllib.parse import quote_plus, urlencode

from flask import redirect, render_template, session, url_for, flash

import ape.logic as logic
import ape.forms as forms
import ape.util as util

log = util.log
ape_app, oauth = util.create_app()


@ape_app.route("/")
def home():
    if session.get("user_id", ""):
        return redirect("/profile")
    else:
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )


@ape_app.route("/profile", methods=['GET', 'POST'])
def profile():
    if not session.get("user_id", ""):
        return redirect("/")

    form = forms.UserDataForm()
    user_id = session.get("user_id")

    if form.validate_on_submit():
        logic.update_user_data(form, user_id)
        flash(f'User profile successfully saved')
    elif not form.is_submitted():
        form = logic.load_data_from_server_to_form(form, user_id)

    return render_template(
        "profile.html",
        form=form
    )


@ape_app.route("/change_password", methods=['GET', 'POST'])
def change_password():
    if not session.get("user_id", ""):
        return redirect("/")

    return redirect(location=(logic.get_password_change_url(session.get("user_id"))))


@ape_app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user_id"] = token.get("userinfo").get("sub")
    return redirect("/profile")


@ape_app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + util.env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": util.env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus
        )
    )


@ape_app.errorhandler(Exception)
def exception_handler(e):
    log.error(f"An exception was caught: {e}")
    return render_template(
        "error.html"
    )


if __name__ == "__main__":
    ape_app.run(host="0.0.0.0", port=util.env.get("PORT", 3000), debug=True)
