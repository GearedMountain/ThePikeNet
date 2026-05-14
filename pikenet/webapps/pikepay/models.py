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


def getMyOpenLoanCount(userId):
    sql = text(
        "SELECT COUNT(*) AS open_loans FROM pikepay_loans WHERE user_id = :userId AND state = 'Open';"
    )
    result = db.session.execute(sql, {"userId": userId})
    row = result.fetchone()
    if row:
        creditScore = row[0]
        return creditScore
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
    sql = text(
        "SELECT user_id, first_name, last_name, justification, expected_income, amount_requested state FROM pikepay_loans WHERE loan_id = :loanId"
    )
    result = db.session.execute(sql, {"loanId": loanId})
    row = result.fetchone()
    if row:

        userId, firstName, lastName, justification, expectedIncome, amountRequested = (
            row
        )
        creditScore = grabCreditScore(userId)
        return (
            creditScore,
            userId,
            firstName,
            lastName,
            justification,
            expectedIncome,
            amountRequested,
        )
    else:
        return None


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
