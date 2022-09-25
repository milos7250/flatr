import requests
from bs4 import BeautifulSoup
import re

class GrantProperty:
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
            bedrooms = listing.select('div[class="overview-meta"]')[0].select('li')[0].string
            bedrooms = re.sub('  ', ' ', bedrooms)
            street = listing.select('div[class="overview-title"]')[0].text.strip()
            area = listing.select('div[class="overview-title"]')[1].text.strip().split('\n')
            location = ', '.join([street] + area)

            return f'{bedrooms} flat at {location}'

        except:
            return GrantProperty.MISSING

    def get_link(self, listing):
        try:
            return listing.a['href'][12:]

        except:
            return GrantProperty.MISSING

    def get_price(self, listing):
        try:
            return listing.select('div[class="overview-price"]')[0].text.strip()
        except:
            return GrantProperty.MISSING

    def get_availability(self, listing):
            return GrantProperty.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'class': 'overview-property-container'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]