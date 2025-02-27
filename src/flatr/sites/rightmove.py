import logging
import re
from datetime import datetime

from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class Rightmove(Site):
    PREPEND = "https://rightmove.co.uk"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Rightmove.HEADERS)

    def _get_raw_listings(self) -> "ResultSet":
        return self.soup.find_all("div", {"data-testid": re.compile(r"propertyCard-[0-9]{1}")})

    def _get_title(self, listing: "Tag") -> str:
        try:
            location = listing.select("address")[0].text.strip()
            bedrooms = listing.select("span[class=PropertyInformation_bedroomsCount___2b5R]")[0].string.strip()
            return f"{bedrooms} bedroom(s) property at {location}"

        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: "Tag") -> str:
        try:
            return str(listing.select("div[class=PropertyPrice_price__VL65t]")[0].string.strip())
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: "Tag") -> str:
        return self.MISSING

    def _get_availability_crawl(self, soup) -> str:
        try:
            strdate = soup.select_one("div[class=_2RnXSVJcWbWv4IpBC1Sng6]").select_one("dd").text.strip()
            if strdate == "Now":
                return datetime.now().strftime("%d/%m/%Y")
            try:
                return datetime.strptime(strdate, "%d/%m/%Y").strftime("%d/%m/%Y")
            except Exception:
                log.exception(f"Failed to parse date: {strdate}.")
                return strdate
        except Exception:
            log.exception("Failed to get availability")
            return self.MISSING

    def _get_link(self, listing: "Tag") -> str:
        try:
            raw_link = listing.select("a[class=propertyCard-link]")[0]["href"]
            return Rightmove.PREPEND + str(re.sub(r"#/\?channel=RES_LET", "", raw_link))

        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
