import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

EMAIL_ADDRESS = "noreply@gearedmountain.com"
EMAIL_PASSWORD = "" # App password from Gmail

def configureEmail(password):
    global EMAIL_PASSWORD
    EMAIL_PASSWORD = password
    
def sendAuthCode(to_address: str, code: str):
    msg = MIMEMultipart("related")
    msg["Subject"] = "HTML Email with Inline Image"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address

    # Create the alternative part for HTML/text
    msg_alt = MIMEMultipart("alternative")
    msg.attach(msg_alt)

    # HTML content with inline image reference (via Content-ID)
    html = f"""
    <html>
        <body>
            <h2 style="color: #355b67; text-align: center;">Hello from PikeNet!</h2>
            <p style="text-align: center;">Here is your one time code:</p>
            <h1 style="text-align: center;">{code}</h1>
            <img style="width:50vw; display: block; margin: 0 auto;" src="cid:logo_image" alt="Logo" width="200"/>
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

