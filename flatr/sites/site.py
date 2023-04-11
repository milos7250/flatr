import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from .listing import Listing
from typing import List

class Site(ABC):
    MISSING = 'Missing'

    def __init__(self, link, headers=None):
        self.response = requests.get(link, headers=headers)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def parse_listing(self, listing) -> Listing:
        title = self.get_title(listing)
        link = self.get_link(listing)
        price = self.get_price(listing)
        available = self.get_availability(listing)

        return Listing(title, link, price, available)
    
    def get_listings(self):
        raw_listings = self.get_raw_listings()
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]

    @abstractmethod
    def get_title(self, listing) -> str:
        pass
    
    @abstractmethod
    def get_link(self, listing) -> str:
        pass
    
    @abstractmethod
    def get_price(self, listing) -> str:
        pass
    
    @abstractmethod
    def get_availability(self, listing) -> str:
        pass
    
    @abstractmethod
    def get_raw_listings(self) -> List[Listing]:
        pass
