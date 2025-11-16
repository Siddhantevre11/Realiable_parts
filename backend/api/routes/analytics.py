"""
Analytics endpoints - Business intelligence and statistics
"""

from fastapi import APIRouter, HTTPException, Query
from api.models.schemas import (
    AnalyticsOverview, CategoryDistribution, PriceRange,
    TopProductsResponse, TopProduct, CategoriesResponse, BrandsResponse
)
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


@router.get("/analytics/overview", response_model=AnalyticsOverview)
async def get_analytics_overview():
    """
    Get overall analytics overview.

    Returns comprehensive statistics including:
    - Total products, brands, categories
    - Stock status metrics
    - Price statistics (avg, min, max)
    - Category distribution

    Perfect for dashboard summary cards.
    """
    try:
        logger.info("Getting analytics overview")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Total products
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]

        # In stock count
        cursor.execute("SELECT COUNT(*) FROM products WHERE in_stock = 1")
        in_stock_count = cursor.fetchone()[0]

        # Brands
        cursor.execute("SELECT COUNT(DISTINCT brand) FROM products WHERE brand IS NOT NULL")
        total_brands = cursor.fetchone()[0]

        # Categories
        cursor.execute("SELECT COUNT(DISTINCT category) FROM products WHERE category IS NOT NULL")
        total_categories = cursor.fetchone()[0]

        # Price statistics
        cursor.execute("""
            SELECT
                AVG(sale_price) as avg_price,
                MIN(sale_price) as min_price,
                MAX(sale_price) as max_price
            FROM products
            WHERE sale_price IS NOT NULL AND sale_price > 0
        """)
        price_row = cursor.fetchone()
        avg_price = price_row[0] or 0
        min_price = price_row[1] or 0
        max_price = price_row[2] or 0

        # Category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM products
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY count DESC
        """)
        category_rows = cursor.fetchall()
        category_dist = [
            CategoryDistribution(category=row[0], count=row[1])
            for row in category_rows
        ]

        conn.close()

        # Calculate percentage
        in_stock_percentage = round((in_stock_count / total_products) * 100, 1) if total_products > 0 else 0

        logger.info(f"Analytics: {total_products} products, {total_brands} brands, "
                   f"{total_categories} categories")

        return AnalyticsOverview(
            success=True,
            total_products=total_products,
            total_brands=total_brands,
            total_categories=total_categories,
            in_stock_count=in_stock_count,
            in_stock_percentage=in_stock_percentage,
            avg_price=round(avg_price, 2),
            price_range=PriceRange(min=min_price, max=max_price),
            category_distribution=category_dist
        )

    except Exception as e:
        logger.error(f"Analytics overview error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve analytics: {str(e)}"
        )


@router.get("/analytics/top-products", response_model=TopProductsResponse)
async def get_top_products(
    limit: int = Query(10, ge=1, le=50, description="Number of products to return"),
    sort_by: str = Query("price", pattern="^(price|discount|category)$", description="Sort criteria")
):
    """
    Get top products by various metrics.

    Args:
        limit: Number of products to return (1-50)
        sort_by: Sorting criteria
            - price: Highest priced products
            - discount: Best discount percentages
            - category: Products by category (alphabetical)

    Returns:
        List of top products based on sort criteria
    """
    try:
        logger.info(f"Get top products: sort_by={sort_by}, limit={limit}")

        conn = get_db_connection()
        cursor = conn.cursor()

        # Build query based on sort_by parameter
        if sort_by == "price":
            query = """
                SELECT sku, product_name, brand, category, sale_price, discount_percent, in_stock
                FROM products
                WHERE sale_price IS NOT NULL
                ORDER BY sale_price DESC
                LIMIT ?
            """
        elif sort_by == "discount":
            query = """
                SELECT sku, product_name, brand, category, sale_price, discount_percent, in_stock
                FROM products
                WHERE discount_percent IS NOT NULL AND discount_percent > 0
                ORDER BY discount_percent DESC
                LIMIT ?
            """
        else:  # category
            query = """
                SELECT sku, product_name, brand, category, sale_price, discount_percent, in_stock
                FROM products
                WHERE category IS NOT NULL
                ORDER BY category, product_name
                LIMIT ?
            """

        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        conn.close()

        # Convert to TopProduct models
        top_products = []
        for row in rows:
            top_products.append(TopProduct(
                sku=row[0],
                product_name=row[1],
                brand=row[2],
                category=row[3],
                sale_price=row[4],
                discount_percent=row[5],
                in_stock=bool(row[6])
            ))

        logger.info(f"Returning {len(top_products)} top products")

        return TopProductsResponse(
            success=True,
            top_products=top_products,
            sort_by=sort_by
        )

    except Exception as e:
        logger.error(f"Top products error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve top products: {str(e)}"
        )


@router.get("/categories", response_model=CategoriesResponse)
async def get_categories():
    """
    Get all unique categories.

    Returns:
        List of all product categories in the database
    """
    try:
        logger.info("Getting categories")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT category
            FROM products
            WHERE category IS NOT NULL
            ORDER BY category
        """)

        categories = [row[0] for row in cursor.fetchall()]
        conn.close()

        logger.info(f"Found {len(categories)} categories")

        return CategoriesResponse(
            success=True,
            categories=categories
        )

    except Exception as e:
        logger.error(f"Get categories error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve categories: {str(e)}"
        )


@router.get("/brands", response_model=BrandsResponse)
async def get_brands():
    """
    Get all unique brands.

    Returns:
        List of all product brands in the database
    """
    try:
        logger.info("Getting brands")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT DISTINCT brand
            FROM products
            WHERE brand IS NOT NULL
            ORDER BY brand
        """)

        brands = [row[0] for row in cursor.fetchall()]
        conn.close()

        logger.info(f"Found {len(brands)} brands")

        return BrandsResponse(
            success=True,
            brands=brands
        )

    except Exception as e:
        logger.error(f"Get brands error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve brands: {str(e)}"
        )


@router.get("/analytics/brand-distribution")
async def get_brand_distribution():
    """
    Get product count by brand.

    Returns:
        Distribution of products across brands
    """
    try:
        logger.info("Getting brand distribution")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT brand, COUNT(*) as count
            FROM products
            WHERE brand IS NOT NULL
            GROUP BY brand
            ORDER BY count DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        distribution = [
            {"brand": row[0], "count": row[1]}
            for row in rows
        ]

        return {
            "success": True,
            "brand_distribution": distribution
        }

    except Exception as e:
        logger.error(f"Brand distribution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve brand distribution: {str(e)}"
        )


@router.get("/analytics/price-distribution")
async def get_price_distribution():
    """
    Get product count by price range.

    Returns:
        Distribution of products across price ranges
    """
    try:
        logger.info("Getting price distribution")

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                CASE
                    WHEN sale_price < 25 THEN 'Under $25'
                    WHEN sale_price >= 25 AND sale_price < 50 THEN '$25-$50'
                    WHEN sale_price >= 50 AND sale_price < 100 THEN '$50-$100'
                    WHEN sale_price >= 100 AND sale_price < 200 THEN '$100-$200'
                    ELSE 'Over $200'
                END as price_range,
                COUNT(*) as count
            FROM products
            WHERE sale_price IS NOT NULL
            GROUP BY price_range
            ORDER BY
                CASE price_range
                    WHEN 'Under $25' THEN 1
                    WHEN '$25-$50' THEN 2
                    WHEN '$50-$100' THEN 3
                    WHEN '$100-$200' THEN 4
                    ELSE 5
                END
        """)

        rows = cursor.fetchall()
        conn.close()

        distribution = [
            {"price_range": row[0], "count": row[1]}
            for row in rows
        ]

        return {
            "success": True,
            "price_distribution": distribution
        }

    except Exception as e:
        logger.error(f"Price distribution error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve price distribution: {str(e)}"
        )
