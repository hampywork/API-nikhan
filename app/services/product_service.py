from typing import List
from app.schemas.product import ProductSchema
from app.embeddings import faiss_service
from app.db.session import db  # Import db from session.py


def get_similar_products(query: str, top_k: int = 5) -> List[ProductSchema]:
    """Get similar products using FAISS."""
    results = faiss_service.search(query, top_k)
    similar_products = []
    for result in results:
        product = (
            db.query(Product).filter(Product.id == result["product_id"]).first()
        )  # Correct Access
        if product:
            similar_products.append(
                ProductSchema(
                    id=product.id,
                    name=product.name,
                    description=product.description,
                    category=product.category,
                    tags=product.tags,
                )
            )
    return similar_products
