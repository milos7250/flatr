from .site import Site
from bs4.element import Tag, ResultSet


class OnTheMarket(Site):
    PREPEND = 'onthemarket.co.uk'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def __init__(self, link: str):
        super().__init__(link, headers=OnTheMarket.HEADERS)

    def _get_raw_listings(self) -> ResultSet:
        return self.soup.find_all('li', {'class': 'otm-PropertyCard'})

    def _get_title(self, listing: Tag) -> str:
        try:
            raw_title = listing.select('span[class="title"]')[0].a.string
            location = listing.select('span[class="address"]')[0].a.string
            return f'{raw_title} at {location}'

        except Exception:
            return self.MISSING

    def _get_price(self, listing: Tag) -> str:
        try:
            return str(listing.select('div[class="otm-Price"]')[0].string)
        except Exception:
            return self.MISSING

    def _get_availability(self, listing: Tag) -> str:
        return self.MISSING

    def _get_link(self, listing: Tag) -> str:
        try:
            raw_link = str(listing.select('div[class="otm-PropertyCardMedia"]')[0].a['href'])
            return OnTheMarket.PREPEND + raw_link

        except Exception:
            return self.MISSING
