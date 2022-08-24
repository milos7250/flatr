import requests
from bs4 import BeautifulSoup
from listing import Listing

class Gumtree:
    PREPEND = 'gumtree.co.uk'

    def __init__(self, link):
        self.response = requests.get(link)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def parse_listing(self, listing):
        title = listing.select('.listing-title')[0].string.strip('\n')
        link = Gumtree.PREPEND + listing.select('.listing-link')[0]['href']
        price = listing.select('.listing-price')[0].strong.string
        available = listing.select('.listing-attributes')[0].findAll('li')[1].findAll('span')[-1].string
        posted = listing.select('.listing-posted-date')[0].span.contents[-1].strip('\n')

        return Listing(title, link, price, available, posted)

    def get_listings(self):
        raw_listings = self.soup.find_all('li', {'class':'natural'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings