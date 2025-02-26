from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from typing import Dict, List

    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .listing import Listing


class Site(ABC):
    MISSING = "Missing"

    def __init__(self, link: str, headers: Dict[str, str] = dict()):
        self.link = link
        self.response = requests.get(self.link, headers=headers)
        self.soup = BeautifulSoup(self.response.text, "html.parser")

    def get_listings(self) -> List[Listing]:
        raw_listings = self._get_raw_listings()
        listings = []
        for listing in raw_listings:
            listings.append(self._parse_listing(listing))

        return listings[::-1]

    def _parse_listing(self, listing: Tag) -> Listing:
        title = self._get_title(listing)
        price = self._get_price(listing)
        available = self._get_availability(listing=listing)
        link = self._get_link(listing)

        return Listing(title, price, available, link, self)

    def _get_availability(self, listing: Tag = None, link: str = None) -> str:
        if link:
            response = requests.get(link, headers=self.HEADERS)
            soup = BeautifulSoup(response.text, "html.parser")
            return self._get_availability_crawl(soup)
        if listing:
            return self._get_availability_no_crawl(listing)
        return self.MISSING

    @abstractmethod
    def _get_raw_listings(self) -> ResultSet:
        pass

    @abstractmethod
    def _get_title(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def _get_price(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def _get_availability_no_crawl(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def _get_availability_crawl(self, soup: BeautifulSoup) -> str:
        pass

    @abstractmethod
    def _get_link(self, listing: Tag) -> str:
        pass
