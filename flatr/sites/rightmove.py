import requests
from bs4 import BeautifulSoup
import re

class Rightmove:
    PREPEND = 'rightmove.co.uk'
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
            location = listing.select('meta[itemprop="streetAddress"]')[0]['content'].strip()
            return f'2 bedroom property at {location}'

        except:
            return Rightmove.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.select('a.propertyCard-link')[0]['href']
            return Rightmove.PREPEND + re.sub(r'#/\?channel=RES_LET', '', raw_link)

        except:
            return Rightmove.MISSING

    def get_price(self, listing):
        try:
            return listing.select('span[class="propertyCard-priceValue"]')[0].string
        except:
            return Rightmove.MISSING

    def get_availability(self, listing):
            return Rightmove.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'id': re.compile(r'property-[0-9]{9}')})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]