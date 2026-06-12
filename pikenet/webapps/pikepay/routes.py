from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from . import bp
import subprocess
from .models import (
    grabCreditScore,
    getMyRecentLoanHistory,
    makeLoanRequest,
    showAllLoans,
    getLoanInfoToReview,
    denyLoan,
    initiallyApproveLoan,
    updateCustomerSignature,
)


@bp.route("/pikepay")
@role_required(2, 1, 0)
def index():
    creditScore = grabCreditScore(session.get("user_id"))
    recentLoanHistory = getMyRecentLoanHistory(session.get("user_id"))

    requestedLoans = None
    if session.get("auth_value") == 0:
        # This person is an employee, go grab all loan ids that are "Requested"
        requestedLoans = showAllLoans()
    else:
        requestedLoans = showAllLoans(session.get("user_id"))

    return render_template(
        "pikepay-index.html",
        auth=session.get("auth_value"),
        username=session.get("username"),
        creditScore=creditScore,
        recentLoanHistory=recentLoanHistory,
        requestedLoans=requestedLoans,
        userId=session.get("user_id"),
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
        state,
        firstName,
        lastName,
        justification,
        expectedIncome,
        amountRequested,
        amountOwed,
        startDate,
        loanLength,
        paymentCycle,
        signature,
    ) = getLoanInfoToReview(loanId)

    print(f"An employee is reviewing loan number {loanId}")

    if not amountOwed:
        amountOwed = 0
    return render_template(
        "loan-request-review.html",
        creditScore=creditScore,
        firstName=firstName,
        lastName=lastName,
        justification=justification,
        expectedIncome=expectedIncome,
        amountRequested=amountRequested,
        loanId=loanId,
        state=state,
        signature=signature,
        totalRepaymentAmount=f"{amountOwed:.2f}",
        paymentCycle=paymentCycle,
        loanLength=loanLength,
    )


signatureToken = "AWERSIPGJHAOIPWERJFPIOAWJEPOFKJAWEG"
createdSignature = ""


@bp.route(f"/pikepay/kiosk-signature/{signatureToken}")
@role_required(2, 1, 0)
def kiosk_signature():
    return render_template("signature.html", signatureToken=signatureToken)


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
                import http.client, urllib, sys

                conn = http.client.HTTPSConnection("api.pushover.net:443")
                conn.request(
                    "POST",
                    "/1/messages.json",
                    urllib.parse.urlencode(
                        {
                            "token": "anb67so33wfdxij6emn2qtxyyi159c",
                            "user": "udp7bfw23bhhnfzcuedsb4o8yzyuoz",
                            "message": f"{firstName} {lastName} just requested a loan for ${loanAmount}",
                        }
                    ),
                    {"Content-type": "application/x-www-form-urlencoded"},
                )
                conn.getresponse()
            else:
                print("MISSING INFO")

        except Exception as e:
            print(e)
    return jsonify({"status": "ok"})


@bp.route("/pikepay/submit_request_response", methods=["POST"])
@role_required(0)
def submit_request_response():
    if request.method == "POST":
        try:
            data = request.get_json()
            repaymentAmount = data.get("repayment_amount")
            loanLength = data.get("loan_length")
            paymentCycle = data.get("payment_cycle")
            loanStatus = data.get("loan_status")
            loanId = data.get("loan_id")
            if loanStatus and loanId:
                if loanStatus == "Approved":
                    if repaymentAmount and loanLength and paymentCycle and loanStatus:
                        initiallyApproveLoan(
                            loanId, repaymentAmount, loanLength, paymentCycle
                        )
                    else:
                        print("MISSING INFO")
                if loanStatus == "Denied":
                    denyLoan(loanId)
            else:
                return jsonify({"status": "no id or status"})
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
                    "echo Establish Route",
                ]
            )

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


@bp.route(f"/pikepay/submit-kiosk-signature/{signatureToken}", methods=["GET", "POST"])
@role_required(0, 1, 2)
def submit_kiosk_signature():
    global createdSignature
    if request.method == "POST":
        data = request.get_json()

        base64Signature = data.get("image")

        createdSignature = base64Signature
    return jsonify({"status": "ok"})


@bp.route("/pikepay/check-kiosk-signature")
@role_required(0)
def check_kiosk_signature():
    loanId = request.args.get("loanid")
    global createdSignature
    if createdSignature:
        sendSignature = createdSignature
        print(f" got signature for {loanId}")
        createdSignature = ""

        updateCustomerSignature(loanId, sendSignature)
        return jsonify({"signature": sendSignature})
    else:
        return jsonify({"signature": "WAITING"})
