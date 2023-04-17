import requests
from bs4 import BeautifulSoup
from bs4.element import Tag, ResultSet
from abc import ABC, abstractmethod
from .listing import Listing
from typing import List, Dict


class Site(ABC):
    MISSING = 'Missing'

    def __init__(self, link: str, headers: Dict[str, str] = dict()):
        self.link = link
        self.response = requests.get(self.link, headers=headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def get_listings(self) -> List[Listing]:
        raw_listings = self._get_raw_listings()
        listings = []
        for listing in raw_listings:
            listings.append(self._parse_listing(listing))

        return listings[::-1]

    def _parse_listing(self, listing: Tag) -> Listing:
        title = self._get_title(listing)
        price = self._get_price(listing)
        available = self._get_availability(listing)
        link = self._get_link(listing)

        return Listing(title, price, available, link)

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
    def _get_availability(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def _get_link(self, listing: Tag) -> str:
        pass
