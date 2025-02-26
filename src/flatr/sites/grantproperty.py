import logging
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class GrantProperty(Site):
    def __init__(self, link: str):
        super().__init__(link)

    def _get_raw_listings(self) -> ResultSet:
        return self.soup.find_all("div", {"class": "overview-property-container"})

    def _get_title(self, listing: Tag) -> str:
        try:
            bedrooms = listing.select('div[class="overview-meta"]')[0].select("li")[0].string
            bedrooms = re.sub("  ", " ", bedrooms)
            street = listing.select('div[class="overview-title"]')[0].text.strip()
            area = listing.select('div[class="overview-title"]')[1].text.strip().split("\n")
            location = ", ".join([street] + area)

            return f"{bedrooms} flat at {location}"

        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: Tag) -> str:
        try:
            return str(listing.select('div[class="overview-price"]')[0].text).strip()
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: Tag) -> str:
        return self.MISSING

    def _get_availability_crawl(self, soup: BeautifulSoup) -> str:
        return self.MISSING

    def _get_link(self, listing: Tag) -> str:
        try:
            return str(listing.a["href"])[12:]
        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
