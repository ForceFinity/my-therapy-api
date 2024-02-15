import smtplib
import os
import ssl
from datetime import datetime, timezone, timedelta
from email.headerregistry import Address
from email.message import EmailMessage

from wrap.core.utils import crypto
from wrap.core.utils.crypto import email_hotp

sender = os.environ["EMAIL_SENDER"]
email_code = os.environ["EMAIL_CODE"]


def send_confirm_email(receiver: str, id_: int):
    otp = email_hotp.at(id_)

    em = EmailMessage()
    em["From"] = Address(display_name='MyTherapy', username='mytherapy.sender', domain='gmail.com')
    em["To"] = receiver
    em["Subject"] = "Потвърдете имейла си"

    em.set_content(
        f"<body>\n"
        f"    <div style=\"max-width: 600px; margin: 0 auto;\">\n"
        f"        <h2>Потвърждение на имейл адреса</h2>\n"
        f"        <p>Благодарим ви, че се регистрирахте на mytherapy.bg</p>\n"
        f"        <p>Вашият код за потвърждение е <h2>{otp}</h2></p>\n"
        f"        <p>Ако не сте направили тази заявка, моля, игнорирайте това съобщение.</p>\n"
        f"        <p>Благодарим ви, че избрахте mytherapy.bg ♥ </p>\n"
        f"    </div>\n"
        f"</body>\n", subtype="html"
    )

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(sender, email_code)
        smtp.sendmail(sender, receiver, em.as_string())
