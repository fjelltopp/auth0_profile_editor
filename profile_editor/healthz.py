from flask import Blueprint
from healthcheck import HealthCheck


healthz_blueprint = Blueprint('healthz', __name__)


def check_profile_editor():
    return True, "profile_editor ok"


health = HealthCheck()
health.add_check(check_profile_editor())


@healthz_blueprint.route("/healthz")
def healthz():
    return health.run()
