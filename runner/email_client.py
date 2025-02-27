import logging
import smtplib
import sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sys import exit
from typing import Dict

log = logging.getLogger(__name__)


class EmailClient:
    def __init__(self, config: Dict[str, str]):
        self.config = config

        try:
            self.message = MIMEMultipart()
            self.message["From"] = self.config["from"]
            self.message["To"] = ",".join(self.config["to"])
            self.message["Subject"] = self.config["subject"]

        except KeyError as e:
            log.critical(
                f"[bold red]KeyError[/bold red]: key {e} is missing from the configuration file! Check the 'config_temp.json' file for proper keys."
            )
            sys.exit(1)

    def send(self, email_body: str) -> None:
        try:
            session = smtplib.SMTP("smtp.gmail.com", 587)
            session.starttls()
            session.login(self.config["user"], self.config["password"])
            self.message.attach(MIMEText(email_body, "plain"))
            text = self.message.as_string()
            session.sendmail(self.config["from"], self.config["to"], text)
            session.quit()
            log.info("Email sent successfully")

        except KeyError as e:
            log.critical(
                f"[bold red]KeyError[/bold red]: key {e} is missing from the configuration file! Check the 'config_temp.json' file for proper keys."
            )
            sys.exit(1)

        except TimeoutError:
            log.critical("SMTP session timed out. Check SMTP is properly configured.")
            exit(1)

        except Exception:
            log.exception("Failed to send email")
            sys.exit(1)
