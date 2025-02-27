import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class Spareroom(Site):
    PREPEND = "spareroom.co.uk"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Spareroom.HEADERS)

    def _get_raw_listings(self) -> "ResultSet":
        return self.soup.find_all("li", {"class": "listing-result"})

    def _get_title(self, listing: "Tag") -> str:
        try:
            return str(listing.h2.string).strip()
        except Exception:
            log.exception("Failed to get title")
            return Spareroom.MISSING

    def _get_price(self, listing: "Tag") -> str:
        try:
            return str(listing.header.a.strong.get_text())
        except Exception:
            log.exception("Failed to get price")
            return Spareroom.MISSING

    def _get_availability_no_crawl(self, listing: "Tag") -> str:
        try:
            return str(listing.select("div.listing-results-content.desktop")[0].strong.get_text())
        except Exception:
            log.exception("Failed to get availability")
            return Spareroom.MISSING

    def _get_availability_crawl(self, soup: "BeautifulSoup") -> str:
        return self.MISSING

    def _get_link(self, listing: "Tag") -> str:
        try:
            raw_link = listing.select('a[class="advertDescription"]')[0]["href"]
            return Spareroom.PREPEND + str(re.sub(r"&search_id=.*", "", raw_link))
        except Exception:
            log.exception("Failed to get link")
            return Spareroom.MISSING
