import re
from .site import Site

class Spareroom(Site):
    PREPEND = 'spareroom.co.uk'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def __init__(self, link):
        super().__init__(link, headers=Spareroom.HEADERS)

    def get_title(self, listing):
        try:
            return listing.h2.string.strip()

        except:
            return Spareroom.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.select('a[class="advertDescription"]')[0]['href']
            return Spareroom.PREPEND + re.sub(r'&search_id=.*', '', raw_link)

        except:
            return Spareroom.MISSING

    def get_price(self, listing):
        try:
            return listing.header.a.strong.get_text()
        except:
            return Spareroom.MISSING

    def get_availability(self, listing):
            try:
                return listing.select('div.listing-results-content.desktop')[0].strong.get_text()

            except:
                return Spareroom.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('li', {'class': 'listing-result'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]
    