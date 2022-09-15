from email_client import EmailClient
from gumtree import Gumtree
from onthemarket import OnTheMarket
from zoopla import Zoopla
import os
import json
from sys import exit
import gspread
from pandas import DataFrame
from datetime import datetime

SRC_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SRC_DIR, 'config.json')
COLUMNS = ['Title', 'Price', 'Available', 'Link']
FLAT_DIVIDER = '\n\n' + '-' * 50 + '\n\n'
SITE_DIVIDER = '\n\n' + '=' * 50 + '\n\n'

SITE_CLASSES = {
    'Gumtree': Gumtree,
    'Zoopla': Zoopla,
    'OnTheMarket': OnTheMarket
}

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def listing_to_email(listing) -> str:
    title, price, available, _, link, *_ = listing
    return f'{title}\n{available}\nPrice: {price}\n{link}'

def update_site(gsheet, site, link) -> DataFrame:

    try:

        # Accessing current flats for site
        worksheet = gsheet.worksheet(site)
        flats = DataFrame(worksheet.get_all_records())
        headers = [flats.columns.values.tolist()]
        current_entries = flats.values.tolist()

        # Getting listings from site
        listings = SITE_CLASSES[site](link).get_listings()
        new_flats = DataFrame(listings, columns=COLUMNS)
        new_flats.insert(3, 'Added', now())
        new_flats['Notes'] = ''

        # Sheet for site is empty -> first flats in sheet
        if flats.empty:
            headers = [new_flats.columns.values.tolist()]
            worksheet.update(headers + new_flats.values.tolist())

        else:
            links = set(flats['Link'].values)
            new_flats = new_flats.loc[~new_flats['Link'].isin(links)]
            worksheet.update(headers + current_entries + new_flats.values.tolist())

        return new_flats

    except Exception as e:
        print(f'[ {now()} ]: Update to {site} failed due to exception!\n\n{e}')
        
        return DataFrame()

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f'[ {now()} ]: Config file not found at {CONFIG_PATH}')
        exit(1)

    with open(CONFIG_PATH, 'r') as config_json:
        config = json.load(config_json)

    try:
        sites = config['sites']
        email_config = config['email']
        spreadsheet = config['spreadsheet']

    except KeyError as e:
        print(e)
        exit(1)

    # Accessing the Google Sheets
    google_credentials = os.path.join(SRC_DIR, config['google_credentials'])
    gc = gspread.service_account(filename=google_credentials)
    gsheet = gc.open(spreadsheet)

    email_body = ''

    for site in sites.keys():
        flats = update_site(gsheet, site, sites[site])
        
        if not flats.empty:
            # Add divider between sites
            if email_body != '':
                email_body += SITE_DIVIDER

            email_body += f'{flats.shape[0]} New flat(s) on {site}' + FLAT_DIVIDER
            email_body += FLAT_DIVIDER.join(map(listing_to_email, flats.values.tolist()))                        

    # Send email if any new flat is found
    if email_body != '':
        email = EmailClient(email_config)
        email.send(email_body)

    exit(0)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'[ {now()} ]: The following errors occured:\n\n{e}')