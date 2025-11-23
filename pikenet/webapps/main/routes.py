from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from .models import checkLoginCredentials, isAccountUnique, registerAccount
import hashlib
from .emailRegistrar import registerValidated, createAuthCheck, verifyRegistrationHash
from . import bp


@bp.route("/")
def index():
    if session.get("auth_value") is None:
        return redirect(url_for("login"))
    print(session.get("auth_value"))
    return render_template(
        "index.html",
        username=session.get("username"),
        auth_value=session.get("auth_value"),
    )


#################################### Authenticating ####################################
activeAccounts = set()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # fake login example
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")
        response = checkLoginCredentials(username, password)
        if response == None:
            return render_template("login.html", error="Invalid credentials")
        else:
            userId, authValue = response
            session["user_id"] = userId
            session["username"] = username
            session["auth_value"] = authValue
            activeAccounts.add(userId)
        return redirect(url_for("main.index"))
    if session.get("user_id"):
        return redirect(url_for("main.index"))
    return render_template("login.html")


@bp.route("/guest-login", methods=["GET", "POST"])
def guestLogin():
    if request.method == "POST":
        i = 0
        print(f"All active: {activeAccounts}")

        while True:

            candidate = f"g{i}"
            if candidate not in activeAccounts:
                activeAccounts.add(candidate)
                session["auth_value"] = 2
                session["user_id"] = candidate
                session["username"] = request.form.get("username")
                print(f"Added guest id: {candidate}")
                break  # Exit the loop after finding and adding the first available one
            i += 1
    if session.get("user_id"):
        return redirect(url_for("main.index"))

    return render_template("guest-register.html")


@bp.route("/logout", methods=["GET"])
def logout():
    session.clear()
    return redirect(url_for("main.login"))


#################################### Registering a new account ####################################


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # fake login example
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        result = isAccountUnique(username, password, email)

        if not result:
            print("Username Taken")
            return jsonify({"message": "Not unique"}), 400

        # If valid and unique, start verification process before officially adding it to the database
        hashValue = sha1Hash(username + email + password)
        if not username.isalnum():
            return jsonify({"message": "Invalid characters in username"}), 400

        # Password must be 8 characters
        if not len(password) >= 8:
            return jsonify({"message": "Password not long enough"}), 400

        # No spaces or illegal characters in email
        email = email.replace(" ", "")
        try:
            createAuthCheck(username, password, email, hashValue)
            return jsonify({"message": "WaitToValidate", "hashValue": hashValue}), 200
        except Exception as e:
            print(f"Failed to start auth check: {e}")
    return render_template("register.html")


# Repeated ping by client
@bp.route("/register-check", methods=["POST"])
def registerCheck():
    data = request.get_json()
    receivedHash = data.get("hash")
    response = registerValidated(receivedHash)
    return jsonify({"message": response}), 200


# Clicking confirmation link in email
@bp.route("/verify-registration")
def verifyRegistration():
    # Get the 'id' parameter from the URL query string
    hashValue = request.args.get("val")
    informationArray = verifyRegistrationHash(hashValue)
    registerAccount(informationArray[0], informationArray[1], informationArray[2])
    return render_template("login.html"), 200


# Registration helper function
def sha1Hash(message: str) -> str:
    sha1 = hashlib.sha1()
    sha1.update(message.encode("utf-8"))
    return sha1.hexdigest()


#################################### Dashboard handling ####################################
