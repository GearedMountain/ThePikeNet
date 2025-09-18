import smtplib
from flask import current_app
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr
from datetime import datetime, timezone
import os

EMAIL_ADDRESS = 'noreply@gearedmountain.com'
EMAIL_PASSWORDD = os.getenv("EMAIL_PASS")
display_name = "PikeNet"
email_address = EMAIL_ADDRESS

def sendAuthCheck(to_address: str, code: str):
    msg = MIMEMultipart("related")
    msg["Subject"] = "PikeNet Account Verification"
    msg["From"] = formataddr((display_name, email_address))
    msg["To"] = to_address

    # Create the alternative part for HTML/text
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    # HTML content with inline image reference (via Content-ID)
    html = f"""
    <html>
    <head>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Space+Mono:ital,wght@0,400;0,700;1,400;1,700&display=swap"
            rel="stylesheet">
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    </head>
        <body style="background-color:white; max-width:500px; margin-left:auto; margin-right:auto;">
            <h1 style="color: #355b67; text-align: center;">Hello from PikeNet!</h1>
            <h2 style="text-align: center;color:black;">Here is your one use verification link:</h2>
            <a href="https://thepikenet.com/verify-registration?val={code}">
                <h2 style="text-align: center; text-decoration: underline; color:#5898ad;">Verify Account</h2>
            </a>
            <h2 style="text-align: center;color:black;">After clicking the link, feel free to return to your original page to continue the process.</h2>
            <img style="width:80%;margin-left:10%;margin-right:10%;" src="cid:logo_image" alt="Logo" />
        </body>
    </html>
    """

    msg_alt.attach(MIMEText(html, "html"))

    # Attach the image file
    print(f"current location: {os.getcwd()}")
    with open("PikeNetLogo.png", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header("Content-ID", "<logo_image>")
        img.add_header("Content-Disposition", "inline", filename="logo.PikeNetLogo.png")
        msg.attach(img)

    try:
        with smtplib.SMTP("smtp.ionos.com", 587) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        print(f"Email sent to {to_address}")
        
    except Exception as e:
        print(f"Failed to send email: {e}")

# Helper function to  create a dictionary entry for authentication check
currentAuthorizationChecks = {}
def createAuthCheck(username: str, password: str, email: str, hash: str):
    
    epochTime = int(datetime.now(timezone.utc).timestamp())    
    currentAuthorizationChecks[hash] = (username, password, email, epochTime, False)
    
    sendAuthCheck(
        to_address=email,
        code=hash
    )
    print(f"Creating new authorization request: {currentAuthorizationChecks}")

def registerValidated(receivedHash):
    response = currentAuthorizationChecks[receivedHash][4]
    if currentAuthorizationChecks[receivedHash][4]:
        del currentAuthorizationChecks[receivedHash]
    return response

def verifyRegistrationHash(hashValue):
    if hashValue not in currentAuthorizationChecks:
        print("Fake or expired validation link")
    else:
        oldTuple = currentAuthorizationChecks[hashValue]
        newTuple = oldTuple[:4] + (True,) + oldTuple[5:]
        currentAuthorizationChecks[hashValue] = newTuple
        result = registerUserIntoDatabase(currentAuthorizationChecks[hashValue][0],currentAuthorizationChecks[hashValue][1],currentAuthorizationChecks[hashValue][2])
        print(f"new list: {currentAuthorizationChecks}")
