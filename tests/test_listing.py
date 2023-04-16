import pytest
from flatr.sites import Listing

listing1 = Listing('First title', '£1200', 'Now', 'www.example.com')
listing1_tuple = ('First title', '£1200', 'Now', 'www.example.com')
listing1_list = ['First title', '£1200', 'Now', 'www.example.com']
listing1_str = 'First title\nPrice: £1200\nNow\nwww.example.com'
listing1_hash = hash(listing1_tuple)
listing1_repr = "Listing('First title', '£1200', 'Now', 'www.example.com')"

listing2 = Listing('Second title', '£1300', 'Now', 'www.example.com')
listing2_tuple = ('Second title', '£1300', 'Now', 'www.example.com')
listing2_list = ['Second title', '£1300', 'Now', 'www.example.com']
listing2_str = 'Second title\nPrice: £1300\nNow\nwww.example.com'
listing2_hash = hash(listing2_tuple)
listing2_repr = "Listing('Second title', '£1300', 'Now', 'www.example.com')"

listing3 = Listing('Second title', '£1300', 'Now', 'www.example.com')
listing3_tuple = ('Second title', '£1300', 'Now', 'www.example.com')
listing3_list = ['Second title', '£1300', 'Now', 'www.example.com']
listing3_str = 'Second title\nPrice: £1300\nNow\nwww.example.com'
listing3_hash = hash(listing3_tuple)
listing3_repr = "Listing('Second title', '£1300', 'Now', 'www.example.com')"

LISTINGS = [listing1, listing2, listing3]
IDS = ['listing1', 'listing2', 'listing3']
TUPLES = [listing1_tuple, listing2_tuple, listing3_tuple]
LISTS = [listing1_list, listing2_list, listing3_list]
STRINGS = [listing1_str, listing2_str, listing3_str]
HASHES = [listing1_hash, listing2_hash, listing3_hash]
REPS = [listing1_repr, listing2_repr, listing3_repr]


@pytest.mark.parametrize('listing, expected', zip(LISTINGS, TUPLES), ids=IDS)
def test_to_tuple(listing, expected):
    assert listing.to_tuple() == expected


@pytest.mark.parametrize('listing, expected', zip(LISTINGS, LISTS), ids=IDS)
def test_to_list(listing, expected):
    assert listing.to_list() == expected


@pytest.mark.parametrize('listing, expected', zip(LISTINGS, STRINGS), ids=IDS)
def test_str(listing, expected):
    assert str(listing) == expected


def test_equal():
    assert listing2 == listing3


def test_not_equal():
    assert listing1 != listing2


@pytest.mark.parametrize('listing, expected', zip(LISTINGS, HASHES), ids=IDS)
def test_hash(listing, expected):
    assert hash(listing) == expected


@pytest.mark.parametrize('listing, expected', zip(LISTINGS, REPS), ids=IDS)
def test_repr(listing, expected):
    assert repr(listing) == expected
