from urllib.parse import quote_plus, urlencode

from flask import redirect, render_template, session, url_for, flash

import logic
from app import create_app, env
from forms import UserDataForm

app, oauth = create_app()


@app.route("/")
def home():
    if session.get("user", ""):
        return redirect("/profile")
    else:
        return oauth.auth0.authorize_redirect(
            redirect_uri=url_for("callback", _external=True)
        )


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    form = UserDataForm()

    if form.validate_on_submit():
        logic.update_user_data(form, session.get("user").get("userinfo").get("sub"))
        flash(f'User profile successfully saved')
    elif not form.is_submitted():
        form = logic.load_data_from_server(form)

    return render_template(
        "profile.html",
        form=form
    )


@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/profile")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://"
        + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("home", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )


@app.errorhandler(logic.ProfileEditingError)
def exception_handler(e):
    return render_template(
        "error.html"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000), debug=True)
