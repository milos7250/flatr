import requests
from bs4 import BeautifulSoup

class ClassName:
    PREPEND = 'prepend for website'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }
    MISSING = 'Missing'

    def __init__(self, link):
        self.response = requests.get(link, headers=ClassName.HEADERS)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def parse_listing(self, listing):

        title = self.get_title(listing)
        link = self.get_link(listing)
        price = self.get_price(listing)
        available = self.get_availability(listing)

        return (title, price, available, link)

    def get_title(self, listing):
        try:
            raw_title = listing.select('CSS selector')[0].a.string
            location = listing.select('CSS selector')[0].a.string
            return f'{raw_title} at {location}'

        except:
            return ClassName.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.select('CSS selector')[0].a['href']
            return ClassName.PREPEND + raw_link

        except:
            return ClassName.MISSING

    def get_price(self, listing):
        try:
            return listing.select('CSS selector')[0].string
        except:
            return ClassName.MISSING

    def get_availability(self, listing):
            return ClassName.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('css tag', {'class': 'listing class'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]