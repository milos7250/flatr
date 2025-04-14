from __future__ import annotations

from typing import TYPE_CHECKING

import requests

if TYPE_CHECKING:
    from typing import Any, Iterator, List, Tuple

    from .site import Site

from bs4 import BeautifulSoup


class Listing:
    COLUMNS = ["Title", "Price", "Available", "Link"]

    def __init__(self, title: str, price: str, available: str, link: str, site: Site):
        self.title = title
        self.price = price
        self.available = available
        self.link = link
        self.site = site
        self._soup: BeautifulSoup = None
        self.meta: "dict[str, Any]" = {"Tags": {}}

    def to_tuple(self) -> Tuple[str, str, str, str]:
        return (self.title, self.price, self.available, self.link)

    def to_list(self) -> List[str]:
        return [self.title, self.price, self.available, self.link]

    def to_dict(self) -> dict[str, str]:
        return dict(zip(self.COLUMNS, self.to_list()))

    @property
    def soup(self) -> BeautifulSoup:
        if not self._soup:
            response = requests.get(self.link, headers=self.site.HEADERS)
            self._soup = BeautifulSoup(response.text, "html.parser")
        return self._soup

    @property
    def tags(self) -> list[str]:
        return list(self.meta["Tags"].keys())

    def get_tags(self, tags: List[str] = []) -> list[str]:
        """
        Collects tags from the listings and returns them as a list.
        """
        found_tags = []
        for tag in tags:
            if tag in self.soup.text.lower():
                found_tags.append(tag)
                self.meta["Tags"][tag] = None
        return found_tags

    def __str__(self) -> str:
        return f"{self.title}\nPrice: {self.price}\n{self.available}\n{self.link}"

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return (
            self.title == other.title
            and self.price == other.price
            and self.available == other.available
            and self.link == other.link
        )

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __repr__(self) -> str:
        return f"Listing('{self.title}', '{self.price}', '{self.available}', '{self.link}')"

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        for attr in ["Title", "Price", "Available", "Link"]:
            yield (attr, getattr(self, attr.lower()))
