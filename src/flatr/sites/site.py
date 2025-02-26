import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from typing import Dict, List

    from bs4 import BeautifulSoup
    from bs4.element import ResultSet, Tag

from .listing import Listing

log = logging.getLogger(__name__)


class Site(ABC):
    MISSING = "Missing"

    def __init__(self, link: str, headers: Dict[str, str] = dict()):
        self.link = link
        try:
            self.response = requests.get(self.link, headers=headers)
            self.soup = BeautifulSoup(self.response.text, "html.parser")
        except Exception:
            log.exception("Failed to initialize site")

    def get_listings(self) -> List[Listing]:
        try:
            raw_listings = self._get_raw_listings()
            listings = []
            for listing in raw_listings:
                listings.append(self._parse_listing(listing))
            return listings[::-1]
        except Exception:
            log.exception("Failed to get listings")
            return []

    def _parse_listing(self, listing: Tag) -> Listing:
        try:
            title = self._get_title(listing)
            price = self._get_price(listing)
            available = self._get_availability(listing=listing)
            link = self._get_link(listing)
            return Listing(title, price, available, link, self)
        except Exception:
            log.exception("Failed to parse listing")
            return Listing(self.MISSING, self.MISSING, self.MISSING, self.MISSING, self)

    def _get_availability(self, listing: Tag = None, link: str = None) -> str:
        try:
            if link:
                response = requests.get(link, headers=self.HEADERS)
                soup = BeautifulSoup(response.text, "html.parser")
                return self._get_availability_crawl(soup)
            if listing:
                return self._get_availability_no_crawl(listing)
            return self.MISSING
        except Exception:
            log.exception("Failed to get availability")
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
