import json
import logging
import os
import sys
import warnings
from datetime import datetime
from typing import List, Literal, Tuple

import bs4
import gspread
import pandas as pd
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
    "MurrayAndCurrie": sites.MurrayAndCurrie,
}
SITE_KEYS = Literal[
    "GrantProperty", "Gumtree", "OnTheMarket", "Rightmove", "Spareroom", "ZoneLetting", "Zoopla", "Domus"
]

logging.basicConfig(
    level=logging.WARN,
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
log.setLevel(LOG_LEVEL)
warnings.filterwarnings("ignore", ".*rich is experimental/alpha.*")
log.info("Starting updater...")


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def listing_to_email(listing: List[str]) -> str:
    # Listing has 9 columns: Title, Price, Available, Added, Link, Notes, Score, Good Tags, Bad Tags
    title, price, available, _, link, _, _, good_tags, *_ = listing
    return f"{title}\nAvailable from: {available}\nPrice: {price}\nLikely contains: {good_tags}\n{link}"


def listings_to_dataframe(listings: List[Listing]) -> DataFrame:
    records = [listing.to_dict() | listing.meta for listing in listings]
    df = DataFrame.from_records(records, columns=Listing.COLUMNS + ["Score", "Good Tags", "Bad Tags"])
    df.insert(3, "Added", now())
    df.insert(5, "Notes", "")
    return df


def open_worksheet(gsheet: Spreadsheet, site: str):
    try:
        return gsheet.worksheet(site)

    except gspread.exceptions.WorksheetNotFound:
        return gsheet.add_worksheet(title=site, rows=ROWS, cols=COLS)


def is_available_after(date: str, listing: Listing) -> bool:
    return isinstance(listing.site, sites.Domus) or (
        datetime.strptime(listing.available, "%d/%m/%Y") >= datetime.strptime(date, "%d/%m/%Y")
    )


def filter_listings(filter_date: str, listings: List[Listing]) -> Tuple[List[Listing], List[Listing]]:
    for listing in tqdm(listings, desc="Filtering listings...", unit="listing"):
        listing.site._get_availability(listing)
        gt = listing.get_tags(["unfurnished", "double glaz", "gas"])
        gt = [{"unfurnished": "Unfurnished", "double glaz": "Double glazing", "gas": "Gas heating"}[tag] for tag in gt]
        bt = listing.get_tags(["ground", "studio", "basement", "electric heating", "single glaz"])
        s = len(gt) - len(bt)
        p = len(bt) == 0 and is_available_after(filter_date, listing)
        listing.meta |= {"Score": s, "Good Tags": ", ".join(gt), "Bad Tags": ", ".join(bt), "Passed": p}

    return (
        [listing for listing in listings if listing.meta["Passed"]],
        [listing for listing in listings if not listing.meta["Passed"]],
    )


def update_site(gsheet: Spreadsheet, site: SITE_KEYS, link: str, filter_date: str) -> DataFrame:
    try:
        # Accessing current flats for site
        worksheet = open_worksheet(gsheet, f"{site}-all")
        flats = DataFrame(worksheet.get_all_records())

        # Getting listings from site
        listings: list[Listing] = SITE_CLASSES[site](link).get_listings()

        # Cast scraped flats to DataFrame
        scraped_flats = listings_to_dataframe(listings)
        log.debug(f"Scraped {len(scraped_flats)} flats:\n{scraped_flats}")
        if scraped_flats.empty:
            return scraped_flats

        # Check if any new flats are found
        if flats.empty:
            new_listings = listings
        else:
            new_flats_links = set(scraped_flats["Link"].values) - set(flats["Link"].values)
            new_listings = [listing for listing in listings if listing.link in new_flats_links]
        del listings

        # Cast new flats to DataFrame, add timestamp and notes
        new_flats = listings_to_dataframe(new_listings)
        log.debug(f"Found {len(new_listings)} new flats:\n{new_flats}")
        if new_flats.empty:
            return new_flats
        del new_flats

        # Filter new flats by availability and custom criteria
        listings_passed, listings_failed = filter_listings(filter_date, new_listings)
        del new_listings

        # Save all listings to the all sheet
        new_flats = listings_to_dataframe(listings_failed + listings_passed)
        if flats.empty:
            flats = new_flats
        else:
            flats = pd.concat([flats, new_flats], ignore_index=True).fillna("")
        worksheet.update([flats.columns.values.tolist()] + flats.values.tolist())
        del new_flats, listings_failed

        # Save only passed listings to the passed sheet
        if not listings_passed:
            return DataFrame()

        worksheet = open_worksheet(gsheet, site)
        flats_passed = DataFrame(worksheet.get_all_records())

        # Cast new flats to DataFrame, add timestamp and notes
        new_flats_passed = listings_to_dataframe(listings_passed)
        new_flats_passed["Available"] = pd.to_datetime(new_flats_passed["Available"], format="%d/%m/%Y")
        new_flats_passed = new_flats_passed.sort_values(by="Available")
        new_flats_passed["Available"] = new_flats_passed["Available"].dt.strftime("%d/%m/%Y")

        log.info(f"{len(listings_passed)} new flats passed date filtering:\n{new_flats_passed}")

        # Sheet for site is empty -> first flats in sheet, use all
        if flats_passed.empty:
            flats_passed = new_flats_passed
        else:
            flats_passed = pd.concat([flats_passed, new_flats_passed], ignore_index=True).fillna("")
        worksheet.update([flats_passed.columns.values.tolist()] + flats_passed.values.tolist())

        return new_flats_passed

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
        sites = {key: value for key, value in sites.items() if key in ["OnTheMarket"]}
        email_config = config["email"]
        spreadsheet = config["spreadsheet"]

    except KeyError as e:
        log.critical(f"[bold red]KeyError[/bold red]: key {e} is missing from the configuration file!")
        sys.exit(1)

    # Accessing the Google Sheets
    google_credentials = os.path.join(SRC_DIR, config["google_credentials"])
    gc = gspread.auth.service_account(filename=google_credentials)
    gsheet = gc.open(spreadsheet)

    email_body = ""

    for site in sites.keys():
        flats = update_site(gsheet, site, sites[site], config["filter_date"])

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
