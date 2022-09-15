import requests
from bs4 import BeautifulSoup
import re

class Zoopla:
    PREPEND = 'zoopla.co.uk/'
    MISSING = 'Missing'

    def __init__(self, link):
        self.response = requests.get(link)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def parse_listing(self, listing):
        
        title = self.get_title(listing)
        link = self.get_link(listing)
        price = self.get_price(listing)
        available = self.get_availability(listing)
            
        return (title, price, available, link)

    def get_title(self, listing):
        try:
            raw_title = listing.select('h2[data-testid="listing-title"]')[0].string
            location = listing.select('p[data-testid="listing-description"]')[0].string
            return f'{raw_title} at {location}'

        except Exception:
            return Zoopla.MISSING

    def get_link(self, listing):
        try:
            raw_url = listing.select('a[data-testid="listing-details-link"]')[0]['href']
            return Zoopla.PREPEND + re.sub(r'\?search_identifier=[a-f0-9]*', '', raw_url)
        
        except Exception:
            return Zoopla.MISSING

    def get_price(self, listing):
        try:
            return listing.select('div[data-testid="listing-price"]')[0].p.string
        
        except Exception:
            return Zoopla.MISSING

    def get_availability(self, listing):
        try:
            return listing.find_all('span', {'data-testid':'available-from-date'})[0].string[1:]
        
        except Exception:
            return Zoopla.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'data-testid': re.compile(r'search-result_listing_*')})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]