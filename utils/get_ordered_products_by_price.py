from typing import List
from models.product import Product


def get_ordered_products_by_price(products: List[Product]) -> List[Product]:
    return sorted(products, key=lambda product: product.price, reverse=True)