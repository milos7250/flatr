import requests
from bs4 import BeautifulSoup
import re

class ZoneLetting:
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
            bedrooms = listing.select('div[class="col-xs-2 bedrooms"]')[0].string
            location = listing.select('div[class="col-sm-7 no-space"]')[0].h2.a.string
            return f'{bedrooms} bedroom{"" if bedrooms == "1" else "s"} flat at {location}'

        except:
            return ZoneLetting.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.select('div[class="col-sm-5 listimage res"]')[0].a['href']
            return raw_link[12:]

        except:
            return ZoneLetting.MISSING

    def get_price(self, listing):
        try:
            return listing.select('div[class="col-xs-6 price"]')[0].string.strip()
        except:
            return ZoneLetting.MISSING

    def get_availability(self, listing):
            try:
                available = listing.select('div[class="col-xs-4 available"]')[0].text.strip()
                return re.sub('  ', ' ', available)
            
            except:
                return ZoneLetting.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'class': 'row list'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]