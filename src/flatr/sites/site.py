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

    def parse_listing(self, listing: Tag) -> Listing:
        title = self.get_title(listing)
        link = self.get_link(listing)
        price = self.get_price(listing)
        available = self.get_availability(listing)

        return Listing(title, link, price, available)

    def get_listings(self) -> List[Listing]:
        raw_listings = self.get_raw_listings()
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]

    @abstractmethod
    def get_title(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def get_link(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def get_price(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def get_availability(self, listing: Tag) -> str:
        pass

    @abstractmethod
    def get_raw_listings(self) -> ResultSet:
        pass
