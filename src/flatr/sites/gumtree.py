from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .site import Site


class Gumtree(Site):
    PREPEND = "gumtree.co.uk"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Gumtree.HEADERS)

    def _get_raw_listings(self) -> ResultSet:
        return self.soup.find_all("a", {"data-q": "search-result-anchor"})

    def _get_title(self, listing: Tag) -> str:
        try:
            return str(listing.find_all("div", {"data-q": "tile-title"})[0].string).strip()

        except Exception:
            return self.MISSING

    def _get_price(self, listing: Tag) -> str:
        try:
            return str(listing.find_all("div", {"data-q": "tile-price"})[0].string)

        except Exception:
            return self.MISSING

    def _get_availability_no_crawl(self, listing: Tag) -> str:
        try:
            div = listing.find_all("div", {"data-q": "tile-description"})[0].div
            details = [span.text for span in div.find_all("span")]
            return str(details[1].replace("Date available: ", ""))

        except Exception:
            return self.MISSING

    def _get_availability_crawl(self, soup: BeautifulSoup) -> str:
        return self.MISSING

    def _get_link(self, listing: Tag) -> str:
        try:
            return Gumtree.PREPEND + str(listing["href"])

        except Exception:
            return self.MISSING
