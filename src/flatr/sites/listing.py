from typing import Tuple, List, Iterator


class Listing:
    def __init__(self, title: str, price: str, available: str, link: str):
        self.title = title
        self.price = price
        self.available = available
        self.link = link

    def to_tuple(self) -> Tuple[str, str, str, str]:
        return (self.title, self.price, self.available, self.link)

    def to_list(self) -> List[str]:
        return [self.title, self.price, self.available, self.link]

    def __str__(self) -> str:
        return f'{self.title}\nPrice: {self.price}\n{self.available}\n{self.link}'

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self.title == other.title\
            and self.price == other.price\
            and self.available == other.available\
            and self.link == other.link

    def __hash__(self) -> int:
        return hash(self.to_tuple())

    def __repr__(self) -> str:
        return f"Listing('{self.title}', '{self.price}', '{self.available}', '{self.link}')"

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        for attr in ['Title', 'Price', 'Available', 'Link']:
            yield (attr, getattr(self, attr.lower()))
