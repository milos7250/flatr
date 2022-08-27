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

def listing_to_email(listing) -> str:
    title, price, available, _, link, *_ = listing
    return f'{title}\n{available}\nPrice: {price}\n{link}'

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f'Config file not found at {CONFIG_PATH}')
        exit(1)

    with open(CONFIG_PATH, 'r') as config_json:
        config = json.load(config_json)

    try:
        sites = config['sites']
        email_config = config['email']
        spreadsheet = config['spreadsheet']

    except KeyError as e:
        print(e)

    columns = ['Title', 'Price', 'Available', 'Link']

    listings = Gumtree(sites['Gumtree']).get_listings()

    new_flats = pd.DataFrame(listings, columns=columns)
    new_flats.insert(3, 'Added', datetime.now().strftime('%Y-%m-%d %H:%M'))
    new_flats['Notes'] = ''

    google_credentials = config['google_credentials']
    gc = gspread.service_account(filename=google_credentials)
    sh = gc.open(spreadsheet)
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
    
    if not new_flats.empty:
        divider = '\n\n' + '-' * 50 + '\n\n'
        email_body = divider.join(map(listing_to_email, new_flats.values.tolist()))

        email = EmailClient(email_config)
        email.send(email_body)
    else:
        print('No new flats.')

    exit(0)

if __name__ == '__main__':
    main()