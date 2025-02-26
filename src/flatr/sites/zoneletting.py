import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site

log = logging.getLogger(__name__)


class ZoneLetting(Site):
    PREPEND = "https://zonegroup.co.uk"

    def __init__(self, link: str):
        super().__init__(link)

    def _get_raw_listings(self) -> "ResultSet":
        return self.soup.find_all("div", {"class": "propertyItem"})

    def _get_title(self, listing: "Tag") -> str:
        try:
            bedrooms = listing.select('div[class="zText semiSmallText semiBoldWeight propertyMetaItem"]')[-1].contents[
                -1
            ]
            location = listing.select("p", {"class": "proAddress"})[0].contents[-1]
            return f"{bedrooms} flat at {location}"
        except Exception:
            log.exception("Failed to get title")
            return self.MISSING

    def _get_price(self, listing: "Tag") -> str:
        try:
            price_str = str(listing.h3.string)
            start_idx = price_str.find("£")
            return price_str[start_idx:]
        except Exception:
            log.exception("Failed to get price")
            return self.MISSING

    def _get_availability_no_crawl(self, listing: "Tag") -> str:
        return self.MISSING

    def _get_availability_crawl(self, soup: "BeautifulSoup") -> str:
        try:
            return str(
                soup.select('div[class="zText semiMediumText semiBoldWeight metaDataSectionItem"]')[0].span.string
            )
        except Exception:
            log.exception("Failed to get availability")
            return self.MISSING

    def _get_link(self, listing: "Tag") -> str:
        try:
            raw_link = str(listing.a["href"])
            return ZoneLetting.PREPEND + raw_link
        except Exception:
            log.exception("Failed to get link")
            return self.MISSING
