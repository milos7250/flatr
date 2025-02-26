import logging
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class ClassName(Site):
    PREPEND = "prepend for website"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=ClassName.HEADERS)

    def _get_raw_listings(self) -> ResultSet:
        return self.soup.find_all("css tag", {"class": "listing class"})

    def _get_title(self, listing: Tag) -> str:
        try:
            raw_title = listing.select("CSS selector")[0].a.string
            location = listing.select("CSS selector")[0].a.string
            return f"{raw_title} at {location}"
        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: Tag) -> str:
        try:
            return str(listing.select("CSS selector")[0].string)
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: Tag) -> str:
        try:
            strdate = listing.select_one("CSS selector").text.strip()
            if strdate == "Now":
                return datetime.now().strftime("%d/%m/%Y")
            try:
                return datetime.strptime(strdate, "%d/%m/%Y").strftime(
                    "%d/%m/%Y"
                )  # format is dd/mm/yyyy, adjust as needed
            except Exception:
                log.exception(f"Failed to parse date: {strdate}")
                return strdate
        except Exception:
            log.exception("Failed to get availability")
            return self.MISSING

    def _get_availability_crawl(self, soup: BeautifulSoup) -> str:
        try:
            strdate = soup.select_one("CSS selector").text.strip()
            if strdate == "Now":
                return datetime.now().strftime("%d/%m/%Y")
            try:
                return datetime.strptime(strdate, "%d/%m/%Y").strftime(
                    "%d/%m/%Y"
                )  # format is dd/mm/yyyy, adjust as needed
            except Exception:
                log.exception(f"Failed to parse date: {strdate}")
                return strdate
        except Exception:
            log.exception("Failed to get availability")
            return self.MISSING

    def _get_link(self, listing: Tag) -> str:
        try:
            raw_link = str(listing.select("CSS selector")[0].a["href"])
            return ClassName.PREPEND + raw_link
        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
