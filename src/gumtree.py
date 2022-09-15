import requests
from bs4 import BeautifulSoup

class Gumtree:
    PREPEND = 'gumtree.co.uk'
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
            return listing.select('.listing-title')[0].string.strip('\n')
        
        except Exception:
            return Gumtree.MISSING

    def get_link(self, listing):
        try:
            return Gumtree.PREPEND + listing.select('.listing-link')[0]['href']

        except Exception:
            return Gumtree.MISSING

    def get_price(self, listing):
        try:
            return listing.select('.listing-price')[0].strong.string

        except Exception:
            return Gumtree.MISSING

    def get_availability(self, listing):
        attributes = dict()

        for li in listing.select('.listing-attributes')[0].findAll('li'):
            list(map(lambda x: x.string, li.findAll('span')))
            key, value = li.findAll('span')
            attributes[key.string] = value.string
        
        if 'Date available' in attributes:
            return attributes['Date available']

        return Gumtree.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('li', {'class':'natural'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]