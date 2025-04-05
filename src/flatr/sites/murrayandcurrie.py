import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class MurrayAndCurrie(Site):
    PREPEND = ""
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=MurrayAndCurrie.HEADERS)

    def _get_raw_listings(self) -> "ResultSet":
        return self.soup.find_all("div", {"class": "item-body flex-grow-1"})

    def _get_title(self, listing: "Tag") -> str:
        try:
            bedrooms = listing.select_one("li.h-beds span.hz-figure").text.strip()
            location = listing.select_one("h2.item-title").text.strip()
            return f"{bedrooms} bedroom at {location}"
        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: "Tag") -> str:
        try:
            return listing.select_one("li.item-price").text.strip()
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: "Tag") -> str:
        return self.MISSING

    def _get_availability_crawl(self, soup: "BeautifulSoup") -> str:
        strdate = (
            soup.select_one("div[class='d-flex property-overview-data']").ul.select("li")[-1].text.strip()
        )  # in format "April 1, 2025"
        try:
            return datetime.strptime(strdate, "%B %d, %Y").strftime("%d/%m/%Y")
        except Exception:
            log.exception(f"Failed to parse date: {strdate}")
            return strdate

    def _get_link(self, listing: "Tag") -> str:
        try:
            raw_link = str(listing.select_one("h2.item-title a")["href"])
            return MurrayAndCurrie.PREPEND + raw_link
        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
