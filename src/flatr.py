from email_client import EmailClient
from gumtree import Gumtree
from onthemarket import OnTheMarket
from zoopla import Zoopla
import os
import json
from sys import exit
import gspread
import pandas as pd
from datetime import datetime

SRC_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SRC_DIR, 'config.json')
COLUMNS = ['Title', 'Price', 'Available', 'Link']
FLAT_DIVIDER = '\n\n' + '-' * 50 + '\n\n'
SITE_DIVIDER = '\n\n' + '=' * 50 + '\n\n'

def listing_to_email(listing) -> str:
    title, price, available, _, link, *_ = listing
    return f'{title}\n{available}\nPrice: {price}\n{link}'

def update_gumtree(sh, link) -> pd.DataFrame:

    # Accessing current flats for Gumtree    
    gumtree_sheet = sh.worksheet('Gumtree')
    df_gumtree = pd.DataFrame(gumtree_sheet.get_all_records())
    headers = [df_gumtree.columns.values.tolist()]
    current_entires = df_gumtree.values.tolist()

    # Getting listings from Gumtree
    listings = Gumtree(link).get_listings()
    new_flats = pd.DataFrame(listings, columns=COLUMNS)
    new_flats.insert(3, 'Added', datetime.now().strftime('%Y-%m-%d %H:%M'))
    new_flats['Notes'] = ''

    # Sheet for Gumtree is empty -> first flats in sheet
    if df_gumtree.empty:
        headers = [new_flats.columns.values.tolist()]
        gumtree_sheet.update(headers + new_flats.values.tolist())

    else:
        links = set(df_gumtree['Link'].values)
        new_flats = new_flats.loc[~new_flats['Link'].isin(links)]
        gumtree_sheet.update(headers + current_entires + new_flats.values.tolist())

    return new_flats

def update_zoopla(sh, link) -> pd.DataFrame:

    # Accessing current flats for Zoopla    
    zoopla_sheet = sh.worksheet('Zoopla')
    df_zoopla = pd.DataFrame(zoopla_sheet.get_all_records())
    headers = [df_zoopla.columns.values.tolist()]
    current_entires = df_zoopla.values.tolist()

    # Getting listings from Zoopla
    listings = Zoopla(link).get_listings()
    new_flats = pd.DataFrame(listings, columns=COLUMNS)
    new_flats.insert(3, 'Added', datetime.now().strftime('%Y-%m-%d %H:%M'))
    new_flats['Notes'] = ''

    # Sheet for Zoopla is empty -> first flats in sheet
    if df_zoopla.empty:
        headers = [new_flats.columns.values.tolist()]
        zoopla_sheet.update(headers + new_flats.values.tolist())

    else:
        links = set(df_zoopla['Link'].values)
        new_flats = new_flats.loc[~new_flats['Link'].isin(links)]
        zoopla_sheet.update(headers + current_entires + new_flats.values.tolist())

    return new_flats

def update_onthemarket(sh, link) -> pd.DataFrame:

    # Accessing current flats for OnTheMarket    
    onthemarket_sheet = sh.worksheet('OnTheMarket')
    df_onthemarket = pd.DataFrame(onthemarket_sheet.get_all_records())
    headers = [df_onthemarket.columns.values.tolist()]
    current_entires = df_onthemarket.values.tolist()

    # Getting listings from OnTheMarket
    listings = OnTheMarket(link).get_listings()
    new_flats = pd.DataFrame(listings, columns=COLUMNS)
    new_flats.insert(3, 'Added', datetime.now().strftime('%Y-%m-%d %H:%M'))
    new_flats['Notes'] = ''

    # Sheet for OnTheMarket is empty -> first flats in sheet
    if df_onthemarket.empty:
        headers = [new_flats.columns.values.tolist()]
        onthemarket_sheet.update(headers + new_flats.values.tolist())

    else:
        links = set(df_onthemarket['Link'].values)
        new_flats = new_flats.loc[~new_flats['Link'].isin(links)]
        onthemarket_sheet.update(headers + current_entires + new_flats.values.tolist())

    return new_flats

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

    # Accessing the Google Sheets
    google_credentials = config['google_credentials']
    gc = gspread.service_account(filename=google_credentials)
    sh = gc.open(spreadsheet)

    # Update flats for Gumtree
    gumtree_flats = update_gumtree(sh, sites['Gumtree'])
    
    # Update flats for Zoopla
    zoopla_flats = update_zoopla(sh, sites['Zoopla'])

    # Update flats for OnTheMarket
    onthemarket_flats = update_onthemarket(sh, sites['OnTheMarket'])

    email_body = ''

    if not gumtree_flats.empty:
        email_body += f'{gumtree_flats.shape[0]} New flat(s) on Gumtree' + FLAT_DIVIDER
        email_body += FLAT_DIVIDER.join(map(listing_to_email, gumtree_flats.values.tolist()))

    if not zoopla_flats.empty:
        if email_body != '':
            email_body += SITE_DIVIDER

        email_body += f'{zoopla_flats.shape[0]} New flat(s) on Zoopla' + FLAT_DIVIDER
        email_body += FLAT_DIVIDER.join(map(listing_to_email, zoopla_flats.values.tolist()))

    if not onthemarket_flats.empty:
        if email_body != '':
            email_body += SITE_DIVIDER

        email_body += f'{onthemarket_flats.shape[0]} New flat(s) on OnTheMarket' + FLAT_DIVIDER
        email_body += FLAT_DIVIDER.join(map(listing_to_email, onthemarket_flats.values.tolist()))

    if email_body != '':
        email = EmailClient(email_config)
        email.send(email_body)

    exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        time = datetime.now().strftime('%Y-%m-%d %H:%M')
        print(f'{time}: The following errors occured:\n\n{e}')