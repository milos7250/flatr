from .site import Site
from bs4.element import Tag, ResultSet


class Gumtree(Site):
    PREPEND = 'gumtree.co.uk'
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    }

    def __init__(self, link: str):
        super().__init__(link, headers=Gumtree.HEADERS)

    def get_title(self, listing: Tag) -> str:
        try:
            return str(listing.select('.listing-title')[0].string).strip('\n')

        except Exception:
            return self.MISSING

    def get_link(self, listing: Tag) -> str:
        try:
            return Gumtree.PREPEND + str(listing.select('.listing-link')[0]['href'])

        except Exception:
            return self.MISSING

    def get_price(self, listing: Tag) -> str:
        try:
            return str(listing.select('.listing-price')[0].strong.string)

        except Exception:
            return self.MISSING

    def get_availability(self, listing: Tag) -> str:
        attributes = dict()

        for li in listing.select('.listing-attributes')[0].findAll('li'):
            list(map(lambda x: str(x.string), li.findAll('span')))
            key, value = li.findAll('span')
            attributes[key.string] = value.string

        if 'Date available' in attributes:
            return str(attributes['Date available'])

        return self.MISSING

    def get_raw_listings(self) -> ResultSet:
        return self.soup.find_all('li', {'class': 'natural'})
