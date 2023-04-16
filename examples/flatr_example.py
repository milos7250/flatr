import os
import sys
import json
import gspread
from gspread.spreadsheet import Spreadsheet
from flatr import sites
from pandas import DataFrame
from datetime import datetime
from typing import List
from email_client import EmailClient

SRC_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SRC_DIR, './config.json')
COLUMNS = ['Title', 'Price', 'Available', 'Link']
FLAT_DIVIDER = '\n\n' + '-' * 50 + '\n\n'
SITE_DIVIDER = '\n\n' + '=' * 50 + '\n\n'
ROWS = 1000
COLS = 6

SITE_CLASSES = {
    'Gumtree': sites.Gumtree,
    'Zoopla': sites.Zoopla,
    'OnTheMarket': sites.OnTheMarket,
    'Rightmove': sites.Rightmove,
    'Spareroom': sites.Spareroom,
    'ZoneLetting': sites.ZoneLetting,
    'GrantProperty': sites.GrantProperty
}


def now() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M')


def listing_to_email(listing: List[str]) -> str:
    title, price, available, _, link, *_ = listing
    return f'{title}\n{available}\nPrice: {price}\n{link}'


def open_worksheet(gsheet: Spreadsheet, site: str):
    try:
        return gsheet.worksheet(site)

    except gspread.WorksheetNotFound:
        return gsheet.add_worksheet(title=site, rows=ROWS, cols=COLS)


def update_site(gsheet: Spreadsheet, site: str, link: str) -> DataFrame:

    try:
        # Accessing current flats for site
        worksheet = open_worksheet(gsheet, site)
        flats = DataFrame(worksheet.get_all_records())
        headers = [flats.columns.values.tolist()]
        current_entries = flats.values.tolist()

        # Getting listings from site
        listings = SITE_CLASSES[site](link).get_listings()

        # Cast Listings to dictionaries
        listings = list(map(dict, listings))

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
        print(f'[ {now()} ]: Update to {site} failed due to exception!\n{e}')

        return DataFrame()


def main() -> None:
    if not os.path.exists(CONFIG_PATH):
        print(f'[ {now()} ]: Config file not found at {CONFIG_PATH}')
        sys.exit(1)

    with open(CONFIG_PATH, 'r') as config_json:
        config = json.load(config_json)

    try:
        sites = config['sites']
        email_config = config['email']
        spreadsheet = config['spreadsheet']

    except KeyError as e:
        print(f'[ {now()} ]: KeyError: key {e} is missing from the configuration file!')
        sys.exit(1)

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

    sys.exit(0)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'[ {now()} ]: The following errors occured:\n{e}')
