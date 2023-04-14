from .site import Site
from bs4.element import Tag, ResultSet


class ClassName(Site):
    PREPEND = 'prepend for website'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def __init__(self, link: str):
        super().__init__(link, headers=ClassName.HEADERS)

    def get_title(self, listing: Tag) -> str:
        try:
            raw_title = listing.select('CSS selector')[0].a.string
            location = listing.select('CSS selector')[0].a.string
            return f'{raw_title} at {location}'

        except Exception:
            return self.MISSING

    def get_link(self, listing: Tag) -> str:
        try:
            raw_link = listing.select('CSS selector')[0].a['href']
            return ClassName.PREPEND + raw_link

        except Exception:
            return self.MISSING

    def get_price(self, listing: Tag) -> str:
        try:
            return listing.select('CSS selector')[0].string
        except Exception:
            return self.MISSING

    def get_availability(self, listing: Tag) -> str:
        try:
            return listing.select('CSS selector')[0].string
        except Exception:
            return self.MISSING

    def get_raw_listings(self) -> ResultSet:
        return self.soup.find_all('css tag', {'class': 'listing class'})
