import pytest
from flatr import sites


PASS_SITES = [
    (sites.GrantProperty, 'https://www.grantproperty.com/tenants/properties/'),
    (sites.Gumtree, 'https://www.gumtree.com/search?search_category=property-to-rent'),
    (sites.OnTheMarket, 'https://www.onthemarket.com/to-rent/property/edinburgh/'),
    (sites.Rightmove, 'https://www.rightmove.co.uk/property-to-rent/find.html?searchLocation=Edinburgh&useLocationIdentifier=true&locationIdentifier=REGION%5E475&radius=0.0&_includeLetAgreed=on&includeLetAgreed=false'),
    (sites.Spareroom, 'https://www.spareroom.co.uk/flatshare/?sort_by=days_since_placed'),
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
def test_response_fail(site, link):
    assert site(link).response.status_code != 200


@pytest.mark.parametrize('site, link', PASS_SITES, ids=PASS_IDS)
def test_listings_parsed_pass(site, link):
    listings = site(link).get_listings()
    assert len(listings) >= 1


@pytest.mark.parametrize('site, link', FAIL_SITES, ids=FAIL_IDS)
def test_listings_parsed_fail(site, link):
    listings = site(link).get_listings()
    assert len(listings) == 0
