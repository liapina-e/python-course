class Product:
    def __init__(self, name: str, category: str, price: float) -> None:
        self.name = name
        self.category = category
        self.price = price
        self.sale = 0

    def edit_category(self, new_category: str) -> None:
        self.category = new_category

    def edit_price(self, new_price: float) -> None:
        self.price = new_price

    def set_sale(self, sale: int) -> None:
        self.sale = sale

    def cancel_sale(self) -> None:
        self.sale = 0

    def get_price(self) -> float:
        if self.sale > 0:
            discounted_price = self.price * (100 - self.sale) / 100
            return discounted_price
        return self.price

    def __repr__(self) -> str:
        return f"Product(name={self.name}, category={self.category}, price={self.price}, sale={self.sale}%)"