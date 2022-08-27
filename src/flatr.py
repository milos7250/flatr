from email_client import EmailClient
from gumtree import Gumtree
import os
import json
from sys import exit
import gspread
import pandas as pd
from datetime import datetime

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

    columns = ['Title', 'Price', 'Available', 'Posted', 'Link']

    listings = gumtree.get_listings()

    # new_flats = pd.DataFrame(list(map(lambda x: x.to_list(), listings)), columns=columns)
    new_flats = pd.DataFrame(listings, columns=columns)
    new_flats['Added'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    new_flats['Notes'] = ''

    google_credentials = config['google_credentials']
    gc = gspread.service_account(filename=google_credentials)
    sh = gc.open('flathunt2022')
    gumtree_sheet = sh.worksheet('Gumtree')
    df_gumtree = pd.DataFrame(gumtree_sheet.get_all_records())
    headers = [df_gumtree.columns.values.tolist()]
    current_entires = df_gumtree.values.tolist()

    if df_gumtree.empty:
        headers = [new_flats.columns.values.tolist()]
        gumtree_sheet.update(headers + new_flats.values.tolist())

    else:
        links = set(df_gumtree['Link'].values)
        new_flats = new_flats.loc[~new_flats['Link'].isin(links)]
        gumtree_sheet.update(headers + current_entires + new_flats.values.tolist())
    


    # divider = '\n\n' + '-' * 50 + '\n\n'
    # email_body = divider.join(map(str, listings))

    # email = EmailClient(email_config)
    # email.send(email_body)


    exit(0)

if __name__ == '__main__':
    main()