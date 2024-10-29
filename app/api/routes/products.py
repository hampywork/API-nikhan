from flask_restx import Namespace, Resource
from flask import request


from app.services.product_service import get_similar_products

products_ns = Namespace("products", description="Product operations")


@products_ns.route("/")
class ProductList(Resource):
    def post(self):
        try:
            # Get query parameters
            query = request.json.get("query")
            top_k = request.json.get("top_k", 5)

            if not query:
                products_ns.abort(400, "Query parameter is required")

            similar_products = get_similar_products(query, top_k)
            return similar_products

        except RuntimeError as e:
            products_ns.abort(503, f"Search service unavailable: {str(e)}")
        except ValueError as e:
            products_ns.abort(400, str(e))
        except Exception as e:
            products_ns.abort(500, f"Internal server error: {str(e)}")
