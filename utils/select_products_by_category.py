from typing import List
from models.product import Product


def select_products_by_category(products: List[Product], category: str) -> List[Product]:
    return [product for product in products if product.category == category]