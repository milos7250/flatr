import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class OnTheMarket(Site):
    PREPEND = "https://www.onthemarket.com"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=OnTheMarket.HEADERS)

    def _get_raw_listings(self) -> "ResultSet":
        return self.soup.find_all("li", {"class": "otm-PropertyCard"})

    def _get_title(self, listing: "Tag") -> str:
        try:
            raw_title = " ".join(listing.select('span[class="title"]')[0].a.string.split(" ")[:2])
            location = listing.select('span[class="address"]')[0].a.string
            return f"{raw_title} at {location}"
        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: "Tag") -> str:
        try:
            return str(listing.select('div[class="otm-Price"]')[0].string)
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: "Tag") -> str:
        return self.MISSING

    def _get_availability_crawl(self, soup: "BeautifulSoup") -> str:
        # date in format "Availability date: dd mmm yyyy", or "Available now"
        date = soup.select_one("div.mb-8 ul").find(lambda tag: "Availab" in tag.text)
        if date is None:
            log.error("Failed to get availability for one flat")
            return self.MISSING
        date = date.string.strip()
        if date == "Available now":
            return datetime.now().strftime("%d/%m/%Y")
        else:
            date = date.replace("Availability date: ", "")
            return datetime.strptime(date, "%d %b %Y").strftime("%d/%m/%Y")

    def _get_link(self, listing: "Tag") -> str:
        try:
            raw_link = str(listing.select('div[class="otm-PropertyCardMedia"]')[0].a["href"])
            return OnTheMarket.PREPEND + raw_link
        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
