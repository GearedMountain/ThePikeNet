from pikenet.utils.database import db
from sqlalchemy import text


def grabCreditScore(userId):
    sql = text("SELECT credit_score FROM users WHERE id = :userId")
    result = db.session.execute(sql, {"userId": userId})
    row = result.fetchone()
    if row:
        creditScore = row[0]
        return creditScore
    else:
        return None


def getMyLoanHistory(userId):
    sql = text("SELECT * FROM pikepay_loans WHERE user_id = :userId")
    result = db.session.execute(sql, {"userId": userId})
    rows = result.fetchall()
    if rows:
        return rows
    else:
        return None


def getMyRecentLoanHistory(userId):
    sql = text(
        "SELECT * FROM pikepay_loans WHERE user_id = :userId ORDER BY loan_id DESC LIMIT 5"
    )
    result = db.session.execute(sql, {"userId": userId})
    rows = result.fetchall()
    if rows:
        return rows
    else:
        return None


def showAllLoans():
    sql = text("SELECT loan_id, state FROM pikepay_loans;")
    result = db.session.execute(sql)
    rows = result.fetchall()
    if rows:
        return rows
    else:
        return None


def getLoanInfoToReview(loanId):
    sql = text("SELECT * FROM pikepay_loans WHERE loan_id = :loanId")
    result = db.session.execute(sql, {"loanId": loanId})
    row = result.fetchone()
    if row:

        (
            loanId,
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
        ) = row
        creditScore = grabCreditScore(userId)
        return (
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
        )
    else:
        return None


def initiallyApproveLoan(loanId, repaymentAmount, loanLength, paymentCycle):
    # It now needs to be signed, this isnt the loan being finalized and paid out
    try:
        sql = text(
            "UPDATE pikepay_loans SET state='SignatureNeeded', amount_owed= :repaymentAmount, repayment_length= :loanLength, payment_cycle= :paymentCycle WHERE loan_id= :loanId"
        )
        db.session.execute(
            sql,
            {
                "loanId": loanId,
                "repaymentAmount": repaymentAmount,
                "loanLength": loanLength,
                "paymentCycle": paymentCycle,
            },
        )
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def denyLoan(loanId):
    try:
        sql = text("UPDATE pikepay_loans SET state='Denied' WHERE loan_id= :loanId")
        db.session.execute(sql, {"loanId": loanId})
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def updateCustomerSignature(loanId, customerSignature):
    try:
        sql = text(
            "UPDATE pikepay_loans SET state='Open', requester_signature= :customerSignature WHERE loan_id= :loanId"
        )
        db.session.execute(
            sql, {"loanId": loanId, "customerSignature": customerSignature}
        )
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def makeLoanRequest(firstName, lastName, loanAmount, loanReason, weeklyIncome, userId):
    sql = text("""
    INSERT INTO pikepay_loans (
        user_id,
        first_name,
        last_name,
        amount_requested,
        justification,
        expected_income,
        state
    )
    VALUES (
        :userId,
        :firstName,
        :lastName,
        :loanAmount,
        :loanReason,
        :weeklyIncome,
        'Requested'
    )
""")
    try:
        db.session.execute(
            sql,
            {
                "userId": int(userId),
                "firstName": firstName,
                "lastName": lastName,
                "loanAmount": float(loanAmount),
                "loanReason": loanReason,
                "weeklyIncome": float(weeklyIncome),
            },
        )
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False
