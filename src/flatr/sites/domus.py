from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from . import Site


class Domus(Site):
    PREPEND = ""
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Domus.HEADERS)

    def _get_raw_listings(self) -> ResultSet:
        return self.soup.find_all("div", {"class": "property-overview-wrapper"})

    def _get_title(self, listing: Tag) -> str:
        try:
            raw_title = listing.select("div[class=property-excerpt]")[0].text.strip().strip(".")
            location = ", ".join(
                [listing.select("div[class=title-address-col]")[0].select("h3")[0].string]
                + [
                    det
                    for det in [det.strip() for det in listing.select("p[class=property-address]")[0].text.split("\n")]
                    if det != ""
                ]
            )
            return f"{raw_title} at {location}"

        except Exception:
            return self.MISSING

    def _get_price(self, listing: Tag) -> str:
        try:
            return str(listing.select_one("span[class=rental-price]").text)
        except Exception:
            return self.MISSING

    def _get_availability_no_crawl(self, listing: Tag) -> str:
        return self.MISSING

    def _get_availability_crawl(self, soup: BeautifulSoup) -> str:
        try:
            strdate = soup.select_one("p[class=available-from]").text.replace("Available from: ", "").strip()
            try:
                return datetime.strptime(strdate, "%d/%m/%Y").strftime("%d/%m/%Y")
            except Exception as e:
                print(f"Failed to parse date: {strdate} due to {e}\n")
                return strdate
        except Exception:
            return self.MISSING

    def _get_link(self, listing: Tag) -> str:
        try:
            raw_link = str(listing.select_one("a[class=property-title-link]")["href"])
            return Domus.PREPEND + raw_link

        except Exception:
            return self.MISSING
