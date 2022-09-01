import requests
from bs4 import BeautifulSoup
import re

class Zoopla:
    PREPEND = 'zoopla.co.uk/'

    def __init__(self, link):
        self.response = requests.get(link)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def parse_listing(self, listing):
        raw_title = listing.select('h2[data-testid="listing-title"]')[0].string
        location = listing.select('p[data-testid="listing-description"]')[0].string
        title = f'{raw_title} at {location}'
        raw_url = listing.select('a[data-testid="listing-details-link"]')[0]['href']
        link = Zoopla.PREPEND + re.sub(r'\?search_identifier=[a-f0-9]*', '', raw_url)
        price = listing.select('p[class="css-1w7anck e4hp44v31"]')[0].string
        available = listing.find_all('span', {'data-testid':'available-from-date'})[0].string[1:]

        return (title, price, available, link)

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'data-testid': re.compile(r'search-result_listing_*')})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]