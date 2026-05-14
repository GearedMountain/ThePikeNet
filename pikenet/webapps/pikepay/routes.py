from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from . import bp
import subprocess
from .models import (
    grabCreditScore,
    getMyOpenLoanCount,
    makeLoanRequest,
    showAllLoans,
    getLoanInfoToReview,
)


@bp.route("/pikepay")
@role_required(2, 1, 0)
def index():
    creditScore = grabCreditScore(session.get("user_id"))
    loanCount = getMyOpenLoanCount(session.get("user_id"))
    print(loanCount)

    requestedLoans = None
    if session.get("auth_value") == 0:
        # This person is an employee, go grab all loan ids that are "Requested"
        requestedLoans = showAllLoans()

    return render_template(
        "pikepay-index.html",
        auth=session.get("auth_value"),
        username=session.get("username"),
        creditScore=creditScore,
        loanCount=loanCount,
        requestedLoans=requestedLoans,
    )


@bp.route("/pikepay/loan-request-initial")
@role_required(2, 1, 0)
def loan_request_initial():
    return render_template("loan-request-initial.html")


@bp.route("/pikepay/loan-request-review")
@role_required(0)
def loan_request_review():
    loanId = request.args.get("loanid")
    (
        creditScore,
        userId,
        firstName,
        lastName,
        justification,
        expectedIncome,
        amountRequested,
    ) = getLoanInfoToReview(loanId)

    print(f"An employee is reviewing loan number {loanId}")
    return render_template(
        "loan-request-review.html",
        creditScore=creditScore,
        firstName=firstName,
        lastName=lastName,
        justification=justification,
        expectedIncome=expectedIncome,
        amountRequested=amountRequested,
    )


signatureToken = "ABC123ABC123"


@bp.route(f"/pikepay/kiosk-signature/{signatureToken}")
@role_required(2, 1, 0)
def kiosk_signature():
    return render_template("signature.html")


@bp.route("/pikepay/submit-initial-request", methods=["POST"])
@role_required(0, 1, 2)
def submit_initial_request():
    if request.method == "POST":
        try:
            data = request.get_json()
            firstName = data.get("first_name")
            lastName = data.get("last_name")
            loanAmount = data.get("loan_amount")
            loanReason = data.get("loan_reason")
            weeklyIncome = data.get("weekly_income")
            creditReview = data.get("credit_review")

            if (
                firstName
                and lastName
                and loanAmount
                and loanReason
                and weeklyIncome
                and creditReview
            ):
                result = makeLoanRequest(
                    firstName,
                    lastName,
                    loanAmount,
                    loanReason,
                    weeklyIncome,
                    session.get("user_id"),
                )
            else:
                print("MISSING INFO")

        except Exception as e:
            print(e)
    return jsonify({"status": "ok"})


@bp.route("/pikepay/open-kiosk-signature", methods=["GET", "POST"])
@role_required(0)
def open_kiosk_signature():
    if request.method == "POST":
        try:
            subprocess.run(
                [
                    "ssh",
                    "kiosk@192.168.50.9",
                    "python3",
                    "/home/kiosk/Desktop/PyTest.py",
                    f"https://thepikenet.com/pikepay/kiosk-signature/{signatureToken}",
                ]
            )
        except Exception as e:
            print(e)
    return jsonify({"status": "ok"})
