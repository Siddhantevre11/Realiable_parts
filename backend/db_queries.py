"""
Database Query Helper Functions for ReliableParts Products
Provides convenient functions for common database queries
"""

import sqlite3
from typing import List, Dict, Optional, Tuple


def _get_connection(db_path: str) -> sqlite3.Connection:
    """
    Create database connection with row factory.

    Args:
        db_path: Path to database file

    Returns:
        SQLite connection object
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allow dict-like access to rows
    return conn


def _dict_from_row(row: sqlite3.Row) -> dict:
    """Convert sqlite3.Row to dictionary."""
    return dict(zip(row.keys(), row))


def search_by_sku(db_path: str, sku: str) -> Optional[Dict]:
    """
    Find product by SKU.

    Args:
        db_path: Path to database file
        sku: Product SKU to search for

    Returns:
        Product dictionary or None if not found
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE sku = ?
        LIMIT 1;
    """, (sku.upper(),))

    row = cursor.fetchone()
    conn.close()

    return _dict_from_row(row) if row else None


def search_by_keyword(db_path: str, keyword: str, limit: int = 50) -> List[Dict]:
    """
    Search product names and descriptions for keyword.

    Args:
        db_path: Path to database file
        keyword: Search keyword
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    search_term = f"%{keyword}%"

    cursor.execute("""
        SELECT * FROM products
        WHERE product_name LIKE ? OR description LIKE ?
        ORDER BY
            CASE WHEN product_name LIKE ? THEN 1 ELSE 2 END,
            product_name
        LIMIT ?;
    """, (search_term, search_term, search_term, limit))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def filter_by_brand(db_path: str, brand: str, limit: int = 100) -> List[Dict]:
    """
    Get all products for a specific brand.

    Args:
        db_path: Path to database file
        brand: Brand name
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE brand = ?
        ORDER BY product_name
        LIMIT ?;
    """, (brand, limit))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def filter_by_category(db_path: str, category: str, limit: int = 100) -> List[Dict]:
    """
    Get all products in a category.

    Args:
        db_path: Path to database file
        category: Category name
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE category = ?
        ORDER BY product_name
        LIMIT ?;
    """, (category, limit))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def filter_by_price_range(db_path: str, min_price: float, max_price: float, limit: int = 100) -> List[Dict]:
    """
    Get products within a price range.

    Args:
        db_path: Path to database file
        min_price: Minimum price
        max_price: Maximum price
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE sale_price >= ? AND sale_price <= ?
        ORDER BY sale_price
        LIMIT ?;
    """, (min_price, max_price, limit))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def filter_by_stock(db_path: str, in_stock: bool = True, limit: int = 100) -> List[Dict]:
    """
    Get products by stock status.

    Args:
        db_path: Path to database file
        in_stock: True for in-stock items, False for out-of-stock
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM products
        WHERE in_stock = ?
        ORDER BY product_name
        LIMIT ?;
    """, (1 if in_stock else 0, limit))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def get_top_products(db_path: str, limit: int = 10, order_by: str = 'price_desc') -> List[Dict]:
    """
    Get top N products by various criteria.

    Args:
        db_path: Path to database file
        limit: Number of products to return
        order_by: Sorting criteria ('price_desc', 'price_asc', 'discount', 'recent')

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    # Determine ORDER BY clause
    order_clauses = {
        'price_desc': 'sale_price DESC NULLS LAST',
        'price_asc': 'sale_price ASC',
        'discount': 'discount_percent DESC NULLS LAST',
        'recent': 'scraped_at DESC'
    }

    order_clause = order_clauses.get(order_by, 'sale_price DESC')

    cursor.execute(f"""
        SELECT * FROM products
        WHERE sale_price IS NOT NULL
        ORDER BY {order_clause}
        LIMIT ?;
    """, (limit,))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def find_compatible_parts(db_path: str, model_number: str, limit: int = 50) -> List[Dict]:
    """
    Find parts compatible with a specific appliance model.

    Args:
        db_path: Path to database file
        model_number: Appliance model number
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    search_term = f"%{model_number}%"

    cursor.execute("""
        SELECT * FROM products
        WHERE compatible_models LIKE ?
        ORDER BY product_name
        LIMIT ?;
    """, (search_term, limit))

    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def get_brands(db_path: str) -> List[Tuple[str, int]]:
    """
    Get all brands with product counts.

    Args:
        db_path: Path to database file

    Returns:
        List of (brand_name, product_count) tuples
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT brand, COUNT(*) as count
        FROM products
        WHERE brand IS NOT NULL
        GROUP BY brand
        ORDER BY count DESC;
    """)

    rows = cursor.fetchall()
    conn.close()

    return [(row['brand'], row['count']) for row in rows]


def get_categories(db_path: str) -> List[Tuple[str, int]]:
    """
    Get all categories with product counts.

    Args:
        db_path: Path to database file

    Returns:
        List of (category_name, product_count) tuples
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM products
        WHERE category IS NOT NULL
        GROUP BY category
        ORDER BY count DESC;
    """)

    rows = cursor.fetchall()
    conn.close()

    return [(row['category'], row['count']) for row in rows]


def advanced_search(db_path: str,
                    keyword: Optional[str] = None,
                    brand: Optional[str] = None,
                    category: Optional[str] = None,
                    min_price: Optional[float] = None,
                    max_price: Optional[float] = None,
                    in_stock: Optional[bool] = None,
                    limit: int = 50) -> List[Dict]:
    """
    Advanced search with multiple filters.

    Args:
        db_path: Path to database file
        keyword: Search keyword (optional)
        brand: Brand filter (optional)
        category: Category filter (optional)
        min_price: Minimum price (optional)
        max_price: Maximum price (optional)
        in_stock: Stock filter (optional)
        limit: Maximum number of results

    Returns:
        List of product dictionaries
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    # Build WHERE clause
    where_clauses = []
    params = []

    if keyword:
        where_clauses.append("(product_name LIKE ? OR description LIKE ?)")
        search_term = f"%{keyword}%"
        params.extend([search_term, search_term])

    if brand:
        where_clauses.append("brand = ?")
        params.append(brand)

    if category:
        where_clauses.append("category = ?")
        params.append(category)

    if min_price is not None:
        where_clauses.append("sale_price >= ?")
        params.append(min_price)

    if max_price is not None:
        where_clauses.append("sale_price <= ?")
        params.append(max_price)

    if in_stock is not None:
        where_clauses.append("in_stock = ?")
        params.append(1 if in_stock else 0)

    # Build query
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    query = f"""
        SELECT * FROM products
        WHERE {where_sql}
        ORDER BY product_name
        LIMIT ?;
    """
    params.append(limit)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [_dict_from_row(row) for row in rows]


def get_product_count(db_path: str) -> int:
    """
    Get total number of products in database.

    Args:
        db_path: Path to database file

    Returns:
        Total product count
    """
    conn = _get_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as count FROM products;")
    result = cursor.fetchone()
    conn.close()

    return result['count'] if result else 0


if __name__ == '__main__':
    # Test queries
    import sys

    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    else:
        db_path = 'database/products.db'

    print(f"Testing queries on: {db_path}\n")

    # Test product count
    count = get_product_count(db_path)
    print(f"Total products: {count}")

    # Test brands
    brands = get_brands(db_path)
    print(f"\nTop 5 brands:")
    for brand, count in brands[:5]:
        print(f"  {brand}: {count} products")

    # Test categories
    categories = get_categories(db_path)
    print(f"\nCategories:")
    for category, count in categories:
        print(f"  {category}: {count} products")

    # Test search
    results = search_by_keyword(db_path, "filter", limit=3)
    print(f"\nSearch results for 'filter': {len(results)} found")
    for product in results[:3]:
        print(f"  - {product['product_name']} (${product['sale_price']})")
