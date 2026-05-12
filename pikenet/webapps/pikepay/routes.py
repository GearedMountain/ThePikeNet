from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from . import bp


@bp.route("/pikepay")
@role_required(2, 1, 0)
def index():
    return render_template(
        "pikepay-index.html",
        auth=session.get("auth_value"),
        username=session.get("username"),
    )


@bp.route("/pikepay/loan-request-initial")
@role_required(2, 1, 0)
def loan_request_initial():
    return render_template("loan-request-initial.html")
