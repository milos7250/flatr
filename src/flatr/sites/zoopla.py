import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class Zoopla(Site):
    PREPEND = "zoopla.co.uk/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Zoopla.HEADERS)

    def _get_raw_listings(self) -> "ResultSet":
        return self.soup.find_all("div", {"data-testid": re.compile(r"search-result_listing_*")})

    def _get_title(self, listing: "Tag") -> str:
        try:
            raw_title = listing.select('h2[data-testid="listing-title"]')[0].string
            location = listing.select('p[data-testid="listing-description"]')[0].string
            return f"{raw_title} at {location}"
        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: "Tag") -> str:
        try:
            return str(listing.select('div[data-testid="listing-price"]')[0].p.string)
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: "Tag") -> str:
        try:
            return str(listing.find_all("span", {"data-testid": "available-from-date"})[0].string)[1:]
        except Exception:
            log.exception("Failed to get availability")
            return self.MISSING

    def _get_availability_crawl(self, soup: "BeautifulSoup") -> str:
        return self.MISSING

    def _get_link(self, listing: "Tag") -> str:
        try:
            raw_url = listing.select('a[data-testid="listing-details-link"]')[0]["href"]
            return Zoopla.PREPEND + str(re.sub(r"\?search_identifier=[a-f0-9]*", "", raw_url))
        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
