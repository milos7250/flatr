import pytest
from flatr import sites


PASS_SITES = [
    (sites.GrantProperty, 'https://www.grantproperty.com/tenants/properties/'),
    (sites.Gumtree, 'https://www.gumtree.com/search?search_category=property-to-rent'),
    (sites.OnTheMarket, 'https://www.onthemarket.com/to-rent/property/edinburgh/'),
    (sites.Rightmove, 'https://www.rightmove.co.uk/property-to-rent/find.html?searchType=RENT&locationIdentifier=REGION%5E475&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&sortByPriceDescending=&_includeLetAgreed=on&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&letType=&letFurnishType=&houseFlatShare='),
    (sites.Spareroom, 'https://www.spareroom.co.uk/flatshare/index.cgi?&search_id=1212087156&offset=0&sort_by=days_since_placed'),
    (sites.ZoneLetting, 'https://zonegroup.co.uk/search-property/rent'),
    # (sites.Zoopla, 'https://www.zoopla.co.uk/to-rent/property/edinburgh-county/?price_frequency=per_month&q=Edinburgh&search_source=home')
]

PASS_IDS = [
    'grantproperty',
    'gumtree',
    'onthemarket',
    'rightmove',
    'spareroom',
    'zoneletting',
    # 'zoopla'
]

FAIL_SITES = [
    (sites.Zoopla, 'https://www.zoopla.co.uk/to-rent/property/edinburgh-county/?price_frequency=per_month&q=Edinburgh&search_source=home')
]

FAIL_IDS = [
    'zoopla'
]


@pytest.mark.parametrize('site, link', PASS_SITES, ids=PASS_IDS)
def test_response_pass(site, link):
    assert site(link).response.status_code == 200


@pytest.mark.parametrize('site, link', FAIL_SITES, ids=FAIL_IDS)
@pytest.mark.xfail
def test_response_fail(site, link):
    assert site(link).response.status_code == 200


@pytest.mark.parametrize('site, link', PASS_SITES, ids=PASS_IDS)
def test_listings_parsed_pass(site, link):
    listings = site(link).get_listings()
    assert len(listings) >= 1


@pytest.mark.parametrize('site, link', FAIL_SITES, ids=FAIL_IDS)
def test_listings_parsed_fail(site, link):
    listings = site(link).get_listings()
    assert len(listings) == 0
