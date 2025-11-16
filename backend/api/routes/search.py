"""
Search endpoints
"""

from fastapi import APIRouter, HTTPException
from api.models.schemas import SearchRequest, SearchResponse, ProductResult
from semantic_search import search_products, hybrid_search
from gpt_query_processor import extract_query_intent
import time
import logging
import os
import sys

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)

router = APIRouter()

DB_PATH = "database/products.db"


@router.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """
    Semantic search for products using AI-powered embeddings.

    This endpoint uses:
    - GPT-3.5-turbo for query understanding
    - Vector embeddings for semantic similarity
    - Hybrid search (SQL filters + vector similarity)

    Returns top matching products with similarity scores.
    """
    start_time = time.time()

    try:
        logger.info(f"Search request: query='{request.query}', top_k={request.top_k}")

        # Parse query with GPT to extract intent and entities
        parsed_query = None
        try:
            parsed_query = extract_query_intent(request.query)
            logger.info(f"Parsed query: {parsed_query}")
        except Exception as e:
            logger.warning(f"Query parsing failed: {e}, continuing with basic search")

        # Perform semantic search
        search_results = search_products(
            db_path=DB_PATH,
            query_text=request.query,
            top_k=request.top_k
        )

        # Handle both list and dict return types from search_products
        if isinstance(search_results, dict):
            results = search_results.get('results', [])
        else:
            results = search_results

        # Apply additional filters if provided
        if request.filters:
            results = apply_filters(results, request.filters)

        # Convert to ProductResult models
        product_results = []
        for product in results[:request.top_k]:
            product_results.append(ProductResult(
                sku=product.get('sku', ''),
                product_name=product.get('product_name', ''),
                brand=product.get('brand'),
                category=product.get('category'),
                regular_price=product.get('regular_price'),
                sale_price=product.get('sale_price'),
                discount_percent=product.get('discount_percent'),
                in_stock=product.get('in_stock'),
                stock_status=product.get('stock_status'),
                description=product.get('description'),
                compatible_models=product.get('compatible_models'),
                main_image_url=product.get('main_image_url'),
                product_url=product.get('product_url'),
                similarity=product.get('similarity') or product.get('similarity_score')
            ))

        # Calculate response time
        response_time = int((time.time() - start_time) * 1000)

        logger.info(f"Search completed: {len(product_results)} results in {response_time}ms")

        return SearchResponse(
            success=True,
            query=request.query,
            parsed_query=parsed_query,
            results=product_results,
            total_results=len(product_results),
            response_time_ms=response_time
        )

    except Exception as e:
        logger.error(f"Search error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


def apply_filters(results: list, filters) -> list:
    """
    Apply additional filters to search results.

    Args:
        results: List of product dictionaries
        filters: SearchFilters object

    Returns:
        Filtered list of products
    """
    filtered = results.copy()

    # Filter by brand
    if filters.brand:
        filtered = [
            p for p in filtered
            if p.get('brand', '').lower() == filters.brand.lower()
        ]

    # Filter by category
    if filters.category:
        filtered = [
            p for p in filtered
            if p.get('category', '').lower() == filters.category.lower()
        ]

    # Filter by price range
    if filters.min_price is not None:
        filtered = [
            p for p in filtered
            if p.get('sale_price', 0) >= filters.min_price
        ]

    if filters.max_price is not None:
        filtered = [
            p for p in filtered
            if p.get('sale_price', float('inf')) <= filters.max_price
        ]

    # Filter by stock status
    if filters.in_stock is not None:
        filtered = [
            p for p in filtered
            if p.get('in_stock', False) == filters.in_stock
        ]

    return filtered
