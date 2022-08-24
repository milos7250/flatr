class Listing:
    def __init__(self, title: str, link: str, price: str, available: str, posted: str):
        self.title = title
        self.link = link
        self.price = price
        self.available = available
        self.posted = posted

    def to_list(self):
        return [self.title, self.price, self.available, self.posted, self.link]

    def __str__(self):
        return f'{self.title}\n{self.available}\nPrice: {self.price}\nPosted {self.posted}\n{self.link}'