from flask import Blueprint
from healthcheck import HealthCheck


healthz_blueprint = Blueprint('healthz', __name__)


def check_ape():
    return True, "ape ok"


health = HealthCheck()
health.add_check(check_ape())


@healthz_blueprint.route("/healthz")
def healthz():
    return health.run()

