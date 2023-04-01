import requests
from bs4 import BeautifulSoup
import re

class ZoneLetting:
    PREPEND = 'https://zonegroup.co.uk'
    MISSING = 'Missing'

    def __init__(self, link):
        self.response = requests.get(link)
        self.soup = BeautifulSoup(self.response.text, 'html.parser')

    def parse_listing(self, listing):

        title = self.get_title(listing)
        link = self.get_link(listing)
        price = self.get_price(listing)
        available = self.get_availability(link)

        return (title, price, available, link)

    def get_title(self, listing):
        try:
            bedrooms = listing.select('div[class="zText semiSmallText semiBoldWeight propertyMetaItem"]')[-1].contents[-1]
            location = listing.select('p', {'class': 'proAddress'})[0].contents[-1]
            return f'{bedrooms} flat at {location}'
        
        except:
            return ZoneLetting.MISSING

    def get_link(self, listing):
        try:
            raw_link = listing.a['href']
            return ZoneLetting.PREPEND + raw_link

        except:
            return ZoneLetting.MISSING

    def get_price(self, listing):
        try:
            price_str = listing.h3.string
            start_idx = price_str.find('£')
            return price_str[start_idx:]
        
        except:
            return ZoneLetting.MISSING

    def get_availability(self, link):
            try:
                response = requests.get(link)
                soup = BeautifulSoup(response.text, 'html.parser')
                return soup.select('div[class="zText semiMediumText semiBoldWeight metaDataSectionItem"]')[0].span.string
            
            except:
                return ZoneLetting.MISSING

    def get_listings(self):
        raw_listings = self.soup.find_all('div', {'class': 'propertyItem'})
        listings = []
        for listing in raw_listings:
            listings.append(self.parse_listing(listing))

        return listings[::-1]