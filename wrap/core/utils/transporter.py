import aiosmtplib
import os
import ssl
from datetime import datetime, timezone, timedelta
from email.headerregistry import Address
from email.message import EmailMessage

from wrap.applications.user import UserCRUD
from wrap.core.utils import crypto
from wrap.core.utils.crypto import email_hotp

sender = os.environ["EMAIL_SENDER"]
email_code = os.environ["EMAIL_CODE"]


async def send_confirm_email(receiver: str, id_: int):
    otp = email_hotp.at(id_)

    em = EmailMessage()
    em["From"] = Address(display_name='MyTherapy', username='mytherapy.sender', domain='gmail.com')
    em["To"] = receiver
    em["Subject"] = "Потвърдете имейла си"

    em.set_content(
        f"<body>\n"
        f"    <div style=\"max-width: 600px; margin: 0 auto;\">\n"
        f"        <h2>Потвърждение на имейл адреса</h2>\n"
        f"        <p>Благодарим ви, че се регистрирахте на my-therapy.vercel.app</p>\n"
        f"        <p>Вашият код за потвърждение е <h2>{otp}</h2></p>\n"
        f"        <p>Ако не сте направили тази заявка, моля, игнорирайте това съобщение.</p>\n"
        f"        <p>Благодарим ви, че избрахте MyTherapy ♥ </p>\n"
        f"    </div>\n"
        f"</body>\n", subtype="html"
    )

    context = ssl.create_default_context()

    async with aiosmtplib.SMTP(
        hostname="smtp.gmail.com",
        port=465,
        use_tls=True,
        tls_context=context
    ) as smtp:
        await smtp.login(sender, email_code)
        await smtp.send_message(em, sender=sender, recipients=receiver)


async def send_tos_changes():
    emails = [user.email for user in await UserCRUD.get_all() if user.is_confirmed]

    em = EmailMessage()
    em["From"] = Address(display_name='MyTherapy', username='mytherapy.sender', domain='gmail.com')
    em["Subject"] = "Известие за актуализация на Условията за ползване"

    em.set_content(
        "<body style=\"font-family: Arial, sans-serif; margin: 0; padding: 0;\">"
        "  <table align=\"center\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"600\" style=\"border-collapse: collapse;\">"
        "    <tr>"
        "      <td bgcolor=\"#ffffff\" style=\"padding: 40px 30px;\">"
        "        <table border=\"0\" cellpadding=\"0\" cellspacing=\"0\" width=\"100%\">"
        "          <tr>"
        "            <td style=\"text-align: center;\">"
        "              <h2 style=\"margin: 0;\">Известие за актуализация на Условията за ползване</h2>"
        "            </td>"
        "          </tr>"
        "          <tr>"
        "            <td style=\"padding: 20px 0;\">"
        "              <p>Уважаеми потребители,</p>"
        "              <p>Искаме да ви информираме, че наскоро актуализирахме нашите Условия за ползване (TOS). Тези промени са насочени към подобряване на нашите услуги и осигуряване на съответствие с последните регулации.</p>"
        "              <p>Можете да прегледате актуализираните Условия за ползване, като посетите следния линк:</p>"
        "              <p><a href=\"my-therapy.vercel.app/articles/terms-of-service\" style=\"color: #007bff; text-decoration: none;\">Преглед на актуализираните Условия за ползване</a></p>"
        "              <p>Продължаването ви да използвате нашите услуги подразбира вашето приемане на тези актуализирани условия.</p>"
        "              <p>Ако имате въпроси или проблеми относно тези промени, не се колебайте да се свържете с нас.</p>"
        "              <p>Благодарим ви за вниманието.</p>"
        "              <p>С уважение, </p>"
        "              <p>MyTherapy Team</p>"
        "            </td>"
        "          </tr>"
        "        </table>"
        "      </td>"
        "    </tr>"
        "  </table>"
        "</body>", subtype="html"
    )

    context = ssl.create_default_context()

    async with aiosmtplib.SMTP(
            hostname="smtp.gmail.com",
            port=465,
            use_tls=True,
            tls_context=context
    ) as smtp:
        await smtp.login(sender, email_code)
        await smtp.sendmail(sender, emails, em.as_string())
