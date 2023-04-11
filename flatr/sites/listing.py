class Listing:
    def __init__(self, title:str, link:str, price:str, available:str):
        self.title = title
        self.link = link
        self.price = price
        self.available = available

    def to_tuple(self):
        return (self.title, self.price, self.available, self.link)

    def to_list(self):
        return (self.title, self.price, self.available, self.link)

    def __str__(self):
        return f'{self.title}\n{self.available}\nPrice: {self.price}\n{self.link}'
    
    def __eq__(self, other):
        if not isinstance(other, type(self)): return NotImplemented
        return self.title == other.title\
               and self.link == other.link\
               and self.price == other.price\
               and self.available == other.available
    
    def __hash__(self):
        return hash(self.to_tuple())
    
    def __repr__(self):
        return f"Listing('{self.title}', '{self.price}', '{self.available}', '{self.link}')"
    
    def __iter__(self):
        for attr in ['Title', 'Price', 'Available', 'Link']:
            yield (attr, getattr(self, attr.lower()))
    