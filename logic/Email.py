import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.utils import formataddr

EMAIL_ADDRESS = "noreply@gearedmountain.com"
EMAIL_PASSWORD = "" # App password from Gmail

def configureEmail(password):
    global EMAIL_PASSWORD
    EMAIL_PASSWORD = password

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
            <a href="http://127.0.0.1:5000/verify-registration?val={code}">
                <h2 style="text-align: center; text-decoration: underline; color:#5898ad;">Verify Account</h2>
            </a>
            <h2 style="text-align: center;color:black;">After clicking the link, feel free to return to your original page to continue the process.</h2>
            <img style="width:80%;margin-left:10%;margin-right:10%;" src="cid:logo_image" alt="Logo" />
        </body>
    </html>
    """

    msg_alt.attach(MIMEText(html, "html"))

    # Attach the image file
    with open("images/official/PikeNetLogo.png", "rb") as img_file:
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

