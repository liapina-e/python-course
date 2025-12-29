from typing import List
from models.product import Product


def extract_prices(products: List[Product]) -> List[float]:
    return [product.price for product in products]