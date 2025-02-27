import json
import logging
import os
import sys
import warnings
from datetime import datetime
from typing import List

import bs4
import gspread
import requests
from email_client import EmailClient
from gspread.spreadsheet import Spreadsheet
from pandas import DataFrame
from rich.console import Console
from rich.logging import RichHandler
from tqdm.rich import tqdm

from flatr import sites
from flatr.sites.listing import Listing

SRC_DIR = os.path.dirname(__file__)
CONFIG_PATH = os.path.join(SRC_DIR, "./config+rightmove.json")
LOG_PATH = os.path.join(SRC_DIR, "./updater.log")
LOG_LEVEL = logging.INFO
COLUMNS = ["Title", "Price", "Available", "Link"]
FLAT_DIVIDER = "\n\n" + "-" * 50 + "\n\n"
SITE_DIVIDER = "\n\n" + "=" * 50 + "\n\n"
ROWS = 1000
COLS = 6

SITE_CLASSES = {
    "GrantProperty": sites.GrantProperty,
    "Gumtree": sites.Gumtree,
    "OnTheMarket": sites.OnTheMarket,
    "Rightmove": sites.Rightmove,
    "Spareroom": sites.Spareroom,
    "ZoneLetting": sites.ZoneLetting,
    "Zoopla": sites.Zoopla,
    "Domus": sites.Domus,
}

logging.basicConfig(
    level=LOG_LEVEL,
    format="([green]%(name)s[/green]) %(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, markup=True, tracebacks_show_locals=True),
        RichHandler(
            rich_tracebacks=True, markup=True, tracebacks_show_locals=True, console=Console(file=open(LOG_PATH, "a"))
        ),
    ],
)
log = logging.getLogger("updater")
warnings.filterwarnings("ignore", ".*rich is experimental/alpha.*")
log.info("Starting updater...")


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def listing_to_email(listing: List[str]) -> str:
    title, price, available, _, link, *_ = listing
    return f"{title}\nAvailable from: {available}\nPrice: {price}\n{link}"


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
        listings: list[Listing] = SITE_CLASSES[site](link).get_listings()

        # Cast scraped flats to DataFrame
        scraped_flats = DataFrame(list(map(dict, listings)), columns=COLUMNS)

        # Check if any new flats are found
        if not flats.empty:
            new_flats_indices = set(scraped_flats["Link"].values) - set(flats["Link"].values)
            listings = [listing for listing in listings if listing.link in new_flats_indices]

        # Try to get availability for new flats if not available
        [
            listing.crawl_availability()
            for listing in tqdm(listings, desc="Scraping availability dates...", unit="flats", leave=False)
            if listing.available == listing.site.MISSING
        ]

        # Cast new flats to DataFrame, add timestamp and notes
        new_flats = DataFrame(list(map(dict, listings)), columns=COLUMNS)
        new_flats.insert(3, "Added", now())
        new_flats["Notes"] = ""

        # Sheet for site is empty -> first flats in sheet, use all
        if flats.empty:
            headers = [new_flats.columns.values.tolist()]
            worksheet.update(headers + new_flats.values.tolist())
        else:
            worksheet.update(headers + current_entries + new_flats.values.tolist())

        return new_flats

    except Exception:
        log.exception(f"Failed to update google sheet for site {site}!")

        return DataFrame()


def main() -> None:
    if not os.path.exists(CONFIG_PATH):
        log.critical(f"[bold red]FileNotFoundError[/bold red]: Config file not found at {CONFIG_PATH}!")
        sys.exit(1)

    with open(CONFIG_PATH, "r") as config_json:
        config = json.load(config_json)

    try:
        sites = config["sites"]
        email_config = config["email"]
        spreadsheet = config["spreadsheet"]

    except KeyError as e:
        log.critical(f"[bold red]KeyError[/bold red]: key {e} is missing from the configuration file!")
        sys.exit(1)

    # Accessing the Google Sheets
    google_credentials = os.path.join(SRC_DIR, config["google_credentials"])
    gc = gspread.service_account(filename=google_credentials)
    gsheet = gc.open(spreadsheet)

    email_body = ""

    for site in sites.keys():
        flats = update_site(gsheet, site, sites[site])

        if not flats.empty:
            # Add divider between sites
            if email_body != "":
                email_body += SITE_DIVIDER

            email_body += f"{flats.shape[0]} New flat(s) on {site}" + FLAT_DIVIDER
            email_body += FLAT_DIVIDER.join(map(listing_to_email, flats.values.tolist()))

            # Save flat pages for future reference
            try:
                if site == "Domus":
                    for flat in flats.to_dict(orient="records"):
                        response = requests.get(flat["Link"], headers=SITE_CLASSES[site].HEADERS)
                        flats_dir = os.path.join(SRC_DIR, "saves")
                        if not os.path.exists(flats_dir):
                            os.mkdir(flats_dir)
                        with open(
                            flats_dir
                            + "/"
                            + "".join(x for x in flat["Title"] if (x.isalnum() or x in "._- "))
                            + ".html",
                            "w",
                        ) as f:
                            f.write(str(bs4.BeautifulSoup(response.text, "html.parser")))
            except Exception:
                log.exception("Failed to save flat pages.")

        log.info(f"Updated site {site}.")

    # Send email if any new flat is found
    if email_body != "":
        email = EmailClient(email_config)
        email.send(email_body)

    log.info("Updater completed.")
    sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Updater failed!")
        sys.exit(1)
