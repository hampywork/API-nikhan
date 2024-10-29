import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from app.models.product import Product
from app.db.session import db
from typing import List, Dict, Optional


class FaissService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index: Optional[faiss.Index] = None
        self.product_ids: List[int] = []
        self.descriptions: List[str] = []
        # Initialize the index when service is created
        self.initialize_index()

    def initialize_index(self) -> None:
        """Initialize the FAISS index with product descriptions from the database."""
        try:
            all_products = db.query(Product).all()  # Correct Access

            if not all_products:
                raise ValueError("No products found in database")

            self.descriptions = [product.description for product in all_products]
            self.product_ids = [product.id for product in all_products]

            # Create embeddings for all descriptions
            description_embeddings = self.model.encode(self.descriptions)

            # Normalize the embeddings
            description_embeddings = description_embeddings / np.linalg.norm(
                description_embeddings, axis=1, keepdims=True
            )

            # Initialize and populate the FAISS index
            self.index = faiss.IndexFlatIP(description_embeddings.shape[1])
            self.index.add(description_embeddings.astype(np.float32))

            print(
                f"Successfully initialized FAISS index with {len(all_products)} products"
            )

        except Exception as e:
            print(f"Error initializing FAISS index: {str(e)}")
            # Re-raise the exception to be handled by the caller
            raise

    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar products using the query string.

        Args:
            query: The search query string
            top_k: Number of similar products to return

        Returns:
            List of dictionaries containing product_id and description

        Raises:
            RuntimeError: If the index is not initialized
        """
        if self.index is None:
            raise RuntimeError(
                "FAISS index is not initialized. Please initialize the index first."
            )

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        try:
            # Encode and normalize the query
            query_embedding = self.model.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding)

            # Perform the search
            distances, indices = self.index.search(
                query_embedding.astype(np.float32), min(top_k, len(self.product_ids))
            )

            # Prepare results
            recommended_products = []
            for idx in indices[0]:
                recommended_products.append(
                    {
                        "product_id": self.product_ids[idx],
                        "description": self.descriptions[idx],
                        "similarity_score": float(
                            distances[0][
                                recommended_products.index(
                                    {
                                        "product_id": self.product_ids[idx],
                                        "description": self.descriptions[idx],
                                    }
                                )
                            ]
                        ),
                    }
                )

            return recommended_products

        except Exception as e:
            print(f"Error during search: {str(e)}")
            raise

    def refresh_index(self) -> None:
        """
        Refresh the FAISS index with current database content.
        Use this method when products are added or removed from the database.
        """
        self.initialize_index()
