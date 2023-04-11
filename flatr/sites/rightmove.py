import re
from .site import Site

class Rightmove(Site):
    PREPEND = 'rightmove.co.uk'
    def __init__(self, link):
        super().__init__(link)

    def get_title(self, listing):
        try:
            location = listing.select('meta[itemprop="streetAddress"]')[0]['content'].strip()
            return f'2 bedroom property at {location}'

        except:
            return self.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.select('a.propertyCard-link')[0]['href']
            return Rightmove.PREPEND + re.sub(r'#/\?channel=RES_LET', '', raw_link)

        except:
            return self.MISSING

    def get_price(self, listing):
        try:
            return listing.select('span[class="propertyCard-priceValue"]')[0].string
        except:
            return self.MISSING

    def get_availability(self, listing):
            return self.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'id': re.compile(r'property-[0-9]{9}')})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]
    