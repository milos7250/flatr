import re
from .site import Site
from bs4.element import Tag, ResultSet


class Rightmove(Site):
    PREPEND = 'rightmove.co.uk'

    def __init__(self, link: str):
        super().__init__(link)

    def get_title(self, listing: Tag) -> str:
        try:
            location = listing.select('meta[itemprop="streetAddress"]')[0]['content'].strip()
            return f'2 bedroom property at {location}'

        except Exception:
            return self.MISSING

    def get_link(self, listing: Tag) -> str:
        try:
            raw_link = listing.select('a.propertyCard-link')[0]['href']
            return Rightmove.PREPEND + re.sub(r'#/\?channel=RES_LET', '', raw_link)

        except Exception:
            return self.MISSING

    def get_price(self, listing: Tag) -> str:
        try:
            return listing.select('span[class="propertyCard-priceValue"]')[0].string
        except Exception:
            return self.MISSING

    def get_availability(self, listing: Tag) -> str:
        return self.MISSING

    def get_raw_listings(self) -> ResultSet:
        return self.soup.find_all('div', {'id': re.compile(r'property-[0-9]{9}')})
