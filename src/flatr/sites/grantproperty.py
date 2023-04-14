import re
from .site import Site
from bs4.element import Tag, ResultSet


class GrantProperty(Site):
    def __init__(self, link: str):
        super().__init__(link)

    def get_title(self, listing: Tag) -> str:
        try:
            bedrooms = listing.select('div[class="overview-meta"]')[0].select('li')[0].string
            bedrooms = re.sub('  ', ' ', bedrooms)
            street = listing.select('div[class="overview-title"]')[0].text.strip()
            area = listing.select('div[class="overview-title"]')[1].text.strip().split('\n')
            location = ', '.join([street] + area)

            return f'{bedrooms} flat at {location}'

        except Exception:
            return self.MISSING

    def get_link(self, listing: Tag) -> str:
        try:
            return listing.a['href'][12:]

        except Exception:
            return self.MISSING

    def get_price(self, listing: Tag) -> str:
        try:
            return listing.select('div[class="overview-price"]')[0].text.strip()
        except Exception:
            return self.MISSING

    def get_availability(self, listing: Tag) -> str:
        return self.MISSING

    def get_raw_listings(self) -> ResultSet:
        return self.soup.find_all('div', {'class': 'overview-property-container'})
