from email_client import EmailClient
from gumtree import Gumtree
import os
import json
from sys import exit

SRC_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SRC_DIR, 'config.json')

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f'Config file not found at {CONFIG_PATH}')
        exit(1)

    with open(CONFIG_PATH, 'r') as config_json:
        config = json.load(config_json)

    try:
        sites = config['sites']
        email_config = config['email']

    except KeyError as e:
        print(e)


    gumtree = Gumtree(sites['Gumtree'])
    listings = gumtree.get_listings()
    divider = '\n\n' + '-' * 50 + '\n\n'
    email_body = divider.join(map(str, listings))
    # print(email_body)
    email = EmailClient(email_config)
    email.send(email_body)


    exit(0)

if __name__ == '__main__':
    main()