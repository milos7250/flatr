import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from sys import exit
from typing import Dict


class EmailClient:
    def __init__(self, config: Dict[str, str]):
        self.config = config

        try:
            self.message = MIMEMultipart()
            self.message['From'] = self.config['from']
            self.message['To'] = ','.join(self.config['to'])
            self.message['Subject'] = self.config['subject']

        except KeyError as e:
            print(f'Invalid configuration key {e}. Check the "config_temp.json" file for proper keys.')
            exit(1)

    def send(self, email_body: str) -> None:
        try:
            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(self.config['user'], self.config['password'])
            self.message.attach(MIMEText(email_body, 'plain'))
            text = self.message.as_string()
            session.sendmail(self.config['from'], self.config['to'], text)

        except KeyError as e:
            print(f'Invalid configuration key {e}. Check the "config_temp.json" file for proper keys.')
            exit(1)

        except TimeoutError as e:
            print(f'SMTP session timed out. Check SMTP is properly configured.\n{e}')
            exit(1)
