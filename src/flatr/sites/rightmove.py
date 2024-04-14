import re
from .site import Site
from bs4.element import Tag, ResultSet


class Rightmove(Site):
    PREPEND = 'rightmove.co.uk'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Rightmove.HEADERS)

    def _get_raw_listings(self) -> ResultSet:
        return self.soup.find_all('div', {'id': re.compile(r'property-[0-9]{9}')})

    def _get_title(self, listing: Tag) -> str:
        try:
            location = listing.select('meta[itemprop="streetAddress"]')[0]['content'].strip()
            return f'2 bedroom property at {location}'

        except Exception:
            return self.MISSING

    def _get_price(self, listing: Tag) -> str:
        try:
            return str(listing.select('span[class="propertyCard-priceValue"]')[0].string)
        except Exception:
            return self.MISSING

    def _get_availability(self, listing: Tag) -> str:
        return self.MISSING

    def _get_link(self, listing: Tag) -> str:
        try:
            raw_link = listing.select('a.propertyCard-link')[0]['href']
            return Rightmove.PREPEND + str(re.sub(r'#/\?channel=RES_LET', '', raw_link))

        except Exception:
            return self.MISSING
