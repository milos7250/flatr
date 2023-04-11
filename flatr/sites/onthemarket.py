from .site import Site

class OnTheMarket(Site):
    PREPEND = 'onthemarket.co.uk'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def __init__(self, link):
        super().__init__(link, headers=OnTheMarket.HEADERS)

    def get_title(self, listing):
        try:
            raw_title = listing.select('span[class="title"]')[0].a.string
            location = listing.select('span[class="address"]')[0].a.string
            return f'{raw_title} at {location}'

        except:
            return self.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.select('div[class="otm-PropertyCardMedia"]')[0].a['href']
            return OnTheMarket.PREPEND + raw_link

        except:
            return self.MISSING

    def get_price(self, listing):
        try:
            return listing.select('div[class="otm-Price"]')[0].string
        except:
            return self.MISSING

    def get_availability(self, listing):
            return self.MISSING

    def get_raw_listings(self):
        return self.soup.find_all('li', {'class': 'otm-PropertyCard'})
    