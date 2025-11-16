"""
Product endpoints - CRUD operations for products
"""

from fastapi import APIRouter, HTTPException, Query
from api.models.schemas import Product, ProductListResponse, ProductDetailResponse, PaginationMeta
from typing import Optional
import sqlite3
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)

router = APIRouter()

DB_PATH = "database/products.db"


def get_db_connection():
    """Get database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/products", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    brand: Optional[str] = Query(None, description="Filter by brand"),
    category: Optional[str] = Query(None, description="Filter by category"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    in_stock: Optional[bool] = Query(None, description="Filter by stock status"),
    search: Optional[str] = Query(None, description="Search in name/description")
):
    """
    Get products with pagination and filters.

    Supports:
    - Pagination (page, limit)
    - Brand filtering
    - Category filtering
    - Price range filtering
    - Stock status filtering
    - Keyword search

    Returns paginated list of products with metadata.
    """
    try:
        logger.info(f"Get products: page={page}, limit={limit}, brand={brand}, "
                   f"category={category}, search={search}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query with filters
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if brand:
            query += " AND LOWER(brand) = LOWER(?)"
            params.append(brand)

        if category:
            query += " AND LOWER(category) = LOWER(?)"
            params.append(category)

        if min_price is not None:
            query += " AND sale_price >= ?"
            params.append(min_price)

        if max_price is not None:
            query += " AND sale_price <= ?"
            params.append(max_price)

        if in_stock is not None:
            query += " AND in_stock = ?"
            params.append(1 if in_stock else 0)

        if search:
            query += " AND (LOWER(product_name) LIKE LOWER(?) OR LOWER(description) LIKE LOWER(?))"
            search_term = f"%{search}%"
            params.extend([search_term, search_term])

        # Get total count
        count_query = query.replace("SELECT *", "SELECT COUNT(*)")
        cursor.execute(count_query, params)
        total_count = cursor.fetchone()[0]

        # Add sorting and pagination
        query += " ORDER BY product_name ASC LIMIT ? OFFSET ?"
        offset = (page - 1) * limit
        params.extend([limit, offset])

        # Execute query
        cursor.execute(query, params)
        rows = cursor.fetchall()

        # Convert to Product models
        products = []
        for row in rows:
            products.append(Product(**dict(row)))

        conn.close()

        # Calculate pagination metadata
        total_pages = (total_count + limit - 1) // limit

        logger.info(f"Returning {len(products)} products (page {page}/{total_pages})")

        return ProductListResponse(
            success=True,
            products=products,
            pagination=PaginationMeta(
                page=page,
                limit=limit,
                total_pages=total_pages,
                total_products=total_count
            )
        )

    except Exception as e:
        logger.error(f"Get products error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/products/{sku}", response_model=ProductDetailResponse)
async def get_product(sku: str):
    """
    Get single product by SKU.

    Args:
        sku: Product SKU

    Returns:
        Full product details
    """
    try:
        logger.info(f"Get product: sku={sku}")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM products
            WHERE UPPER(sku) = UPPER(?)
            LIMIT 1;
        """, (sku,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            raise HTTPException(
                status_code=404,
                detail=f"Product not found: {sku}"
            )

        product = Product(**dict(row))

        logger.info(f"Product found: {product.product_name}")

        return ProductDetailResponse(
            success=True,
            product=product
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get product error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve product: {str(e)}"
        )


@router.get("/products/category/{category}")
async def get_products_by_category(
    category: str,
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get products by category.

    Args:
        category: Category name
        limit: Maximum number of products to return

    Returns:
        List of products in the category
    """
    try:
        logger.info(f"Get products by category: {category}")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM products
            WHERE LOWER(category) = LOWER(?)
            ORDER BY product_name
            LIMIT ?;
        """, (category, limit))

        rows = cursor.fetchall()
        conn.close()

        products = [Product(**dict(row)) for row in rows]

        logger.info(f"Found {len(products)} products in category {category}")

        return {
            "success": True,
            "category": category,
            "products": products,
            "count": len(products)
        }

    except Exception as e:
        logger.error(f"Get products by category error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve products: {str(e)}"
        )


@router.get("/products/brand/{brand}")
async def get_products_by_brand(
    brand: str,
    limit: int = Query(50, ge=1, le=100)
):
    """
    Get products by brand.

    Args:
        brand: Brand name
        limit: Maximum number of products to return

    Returns:
        List of products from the brand
    """
    try:
        logger.info(f"Get products by brand: {brand}")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM products
            WHERE LOWER(brand) = LOWER(?)
            ORDER BY product_name
            LIMIT ?;
        """, (brand, limit))

        rows = cursor.fetchall()
        conn.close()

        products = [Product(**dict(row)) for row in rows]

        logger.info(f"Found {len(products)} products from brand {brand}")

        return {
            "success": True,
            "brand": brand,
            "products": products,
            "count": len(products)
        }

    except Exception as e:
        logger.error(f"Get products by brand error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve products: {str(e)}"
        )
