import smtplib
from email.message import EmailMessage


class EmailClient:
    def __init__(self):
        self.gmail_user = ""  # no gmail user for the public repo
        gmail_password = ""  # no gmail user password for the public repo
        try:
            self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            self.server.ehlo()  # optional
            self.server.login(self.gmail_user, gmail_password)
        except:
            print('Could not create EmailClient!...')

    def send_notification(self, recipient):
        msg = EmailMessage()
        msg.set_content("""\
Hey!

Es kann sein, dass es wieder mögliche Termine für die zweite Impfung gibt 💉
Schau am besten gleich mal nach 🙂

Hier geht's lang:
https://003-iz.impfterminservice.de/terminservice/suche/LSTB-YGH6-WJNW/72280/L920/G7NC-LT5L-94RN

Viele Grüße,
Impftermin-Bot
        """)

        msg['Subject'] = "Mögliche Termine für Impfung gefunden"
        msg['From'] = self.gmail_user
        msg["To"] = recipient

        self.server.sendmail(self.gmail_user, recipient, msg.as_string().encode("utf-8"))

    def send_alive_notification(self, recipient, tries, failed, exceptions, successes, alive_since, time_alive):
        msg = EmailMessage()
        msg.set_content("""\
Hey!

Das ist eine Info das der Impf Bot noch läuft!

Versuche bisher: {}
Keine Termine gefunden: {}
Exceptions aufgetreten: {}
Termine gefunden: {}

Alive since: {}
Time alive: {}

Viele Grüße,
Impftermin-Bot
                        """.format(tries, failed, exceptions, successes, alive_since.strftime("%d %b (%H:%M:%S)"), time_alive))

        msg['Subject'] = "Impf-Bot: Try-Update current {}!".format(tries)
        msg['From'] = self.gmail_user
        msg["To"] = recipient

        self.server.sendmail(self.gmail_user, recipient, msg.as_string().encode("utf-8"))

    def close(self):
        self.server.close()
