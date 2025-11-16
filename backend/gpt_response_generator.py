"""
Generate conversational responses using GPT
Includes product recommendations and upsell suggestions
"""

from openai import OpenAI
import sqlite3
import os
from dotenv import load_dotenv
import config


# GPT System Prompt for Response Generation
RESPONSE_SYSTEM_PROMPT = """
You are a helpful sales assistant for an appliance parts company. A customer has asked about parts, and you've found some matches.

Your job:
1. Provide clear, concise product recommendations
2. Highlight compatibility with their appliance model (if mentioned)
3. Mention pricing clearly with any discounts
4. Suggest 1-2 complementary products (upsells) if appropriate
5. Be friendly, professional, and helpful

Guidelines:
- Keep responses under 150 words
- Use bullet points for product details
- Highlight best value or most popular options
- Mention stock status
- Be conversational but professional

Format each product recommendation with:
- Product name and SKU
- Price (show discount if applicable)
- Key features or compatibility
- Stock status
"""


def format_products_for_gpt(products, include_descriptions=True):
    """
    Format product data for GPT context.

    Args:
        products: List of product dictionaries
        include_descriptions: Whether to include full descriptions

    Returns:
        str: Formatted product information
    """
    if not products:
        return "No products found matching the criteria."

    formatted_parts = []

    for i, product in enumerate(products, 1):
        parts = [f"\nProduct {i}:"]
        parts.append(f"- Name: {product.get('product_name', 'N/A')}")
        parts.append(f"- SKU: {product.get('sku', 'N/A')}")

        if product.get('brand'):
            parts.append(f"- Brand: {product['brand']}")

        # Price information
        regular_price = product.get('regular_price')
        sale_price = product.get('sale_price')

        if sale_price:
            if regular_price and regular_price > sale_price:
                discount = product.get('discount_percent', 0)
                parts.append(f"- Price: ${sale_price:.2f} (was ${regular_price:.2f}, {discount:.0f}% off)")
            else:
                parts.append(f"- Price: ${sale_price:.2f}")

        # Stock status
        stock_status = product.get('stock_status', 'Unknown')
        in_stock = product.get('in_stock', False)
        if in_stock:
            parts.append(f"- Stock: {stock_status} ✓")
        else:
            parts.append(f"- Stock: {stock_status}")

        # Compatible models
        if product.get('compatible_models'):
            models = product['compatible_models'][:200]  # Limit length
            parts.append(f"- Compatible Models: {models}")

        # Description (truncated)
        if include_descriptions and product.get('description'):
            desc = product['description'][:150]  # Truncate
            parts.append(f"- Description: {desc}...")

        # Similarity score (if available)
        if product.get('similarity_score') is not None:
            parts.append(f"- Match Score: {product['similarity_score']:.2f}/1.00")

        formatted_parts.append("\n".join(parts))

    return "\n".join(formatted_parts)


def format_upsells_for_gpt(upsell_products):
    """
    Format upsell products for GPT context.

    Args:
        upsell_products: List of upsell product dictionaries

    Returns:
        str: Formatted upsell information
    """
    if not upsell_products:
        return "No upsell suggestions available."

    formatted_parts = []

    for product in upsell_products:
        parts = [f"- {product.get('product_name')} (${product.get('sale_price', 0):.2f})"]

        if product.get('category'):
            parts.append(f"  Category: {product['category']}")

        formatted_parts.append(" ".join(parts))

    return "\n".join(formatted_parts)


def suggest_upsells(db_path, primary_products, num_suggestions=2):
    """Find complementary products for upselling"""
    
    if not primary_products:
        return []
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get primary product info
        primary_brand = primary_products[0].get('brand', '')
        primary_category = primary_products[0].get('category', '')
        primary_skus = [p.get('sku') for p in primary_products if p.get('sku')]
        
        # Build exclusion list
        sku_placeholders = ','.join(['?' for _ in primary_skus])
        
        # Find related products
        query = f"""
            SELECT * FROM products 
            WHERE sku NOT IN ({sku_placeholders})
            AND brand = ?
            AND in_stock = 1
            LIMIT ?
        """
        
        cursor.execute(query, primary_skus + [primary_brand, num_suggestions])
        upsells = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return upsells
        
    except Exception as e:
        print(f"Upsell error: {e}")
        return []

    # Get primary product info
    primary = primary_products[0]
    primary_brand = primary.get('brand')
    primary_category = primary.get('category')
    primary_price = primary.get('sale_price', 50)

    # Define price range
    min_price = primary_price * 0.5
    max_price = primary_price * 1.5

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Build query for upsells
    where_clauses = ["in_stock = 1"]
    params = []

    # Same brand (if available)
    if primary_brand:
        where_clauses.append("brand = ?")
        params.append(primary_brand)

    # Different category
    if primary_category:
        where_clauses.append("category != ?")
        params.append(primary_category)

    # Price range
    where_clauses.append("sale_price BETWEEN ? AND ?")
    params.extend([min_price, max_price])

    where_sql = " AND ".join(where_clauses)

    cursor.execute(f"""
        SELECT sku, product_name, brand, category,
               sale_price, in_stock, stock_status
        FROM products
        WHERE {where_sql}
        ORDER BY RANDOM()
        LIMIT ?;
    """, params + [num_suggestions])

    upsells = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return upsells


def generate_response(client, query_text, search_results, include_upsells=True):
    """
    Main response generation function.

    Steps:
        1. Format top 3 products for GPT
        2. Find upsell suggestions (if enabled)
        3. Create prompt with all data
        4. Get GPT response
        5. Format and return

    Args:
        client: OpenAI client
        query_text: Original search query
        search_results: Dict with 'results' and 'parsed_query'
        include_upsells: Whether to include upsell suggestions

    Returns:
        str: Conversational response with recommendations
    """
    products = search_results.get('results', [])

    if not products:
        return generate_no_results_response(client, query_text, search_results.get('parsed_query'))

    # Format top 3 products
    top_products = products[:3]
    products_text = format_products_for_gpt(top_products, include_descriptions=False)

    # Get upsells
    upsells_text = ""
    if include_upsells:
        db_path = config.DATABASE_PATH
        upsells = suggest_upsells(db_path, top_products, num_suggestions=2)
        if upsells:
            upsells_text = "\n\nComplementary Products (Upsells):\n" + format_upsells_for_gpt(upsells)

    # Create user prompt
    user_prompt = f"""
Customer Query: "{query_text}"

Found Products:
{products_text}
{upsells_text}

Please provide a helpful, conversational response recommending these products to the customer.
Highlight the best match, mention pricing, and suggest the upsells as "customers also purchased" items.
Keep it friendly and under 150 words.
"""

    # Call GPT API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,  # Slightly higher for more natural responses
            max_tokens=300
        )

        return response.choices[0].message.content

    except Exception as e:
        # Fallback to simple formatted response
        return generate_fallback_response(top_products, upsells if include_upsells else [])


def generate_no_results_response(client, query_text, parsed_query):
    """
    Generate helpful response when no products are found.

    Args:
        client: OpenAI client
        query_text: Original query
        parsed_query: Parsed query dict

    Returns:
        str: Helpful no-results response
    """
    user_prompt = f"""
Customer Query: "{query_text}"

No exact matches were found for this query.

Please provide a helpful response that:
1. Acknowledges we couldn't find exact matches
2. Suggests broadening the search (e.g., different brand, category)
3. Offers to help with more information
4. Remains friendly and professional

Keep it under 100 words.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": RESPONSE_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=200
        )

        return response.choices[0].message.content

    except Exception:
        return (
            "I couldn't find exact matches for your query. "
            "Could you provide more details like the brand, model number, or appliance type? "
            "I'm here to help you find the right part!"
        )


def generate_fallback_response(products, upsells=None):
    """
    Generate a simple formatted response without GPT (fallback).

    Args:
        products: List of product dicts
        upsells: List of upsell product dicts (optional)

    Returns:
        str: Formatted response
    """
    if not products:
        return "No products found matching your criteria. Please try a different search."

    lines = ["I found these products for you:\n"]

    for i, product in enumerate(products[:3], 1):
        name = product.get('product_name', 'Unknown')
        sku = product.get('sku', 'N/A')
        price = product.get('sale_price', 0)
        stock = "In Stock" if product.get('in_stock') else "Out of Stock"

        lines.append(f"{i}. **{name}** (SKU: {sku})")
        lines.append(f"   ${price:.2f} - {stock}")

    if upsells:
        lines.append("\n**Customers also purchased:**")
        for upsell in upsells[:2]:
            name = upsell.get('product_name', 'Unknown')
            price = upsell.get('sale_price', 0)
            lines.append(f"- {name} (${price:.2f})")

    return "\n".join(lines)


def main():
    """Demo response generation."""
    # Mock search results
    mock_results = {
        'query': 'water filter for Whirlpool',
        'parsed_query': {
            'intent': 'find_part',
            'part_type': 'water filter',
            'brand': 'Whirlpool'
        },
        'results': [
            {
                'sku': 'XWFE',
                'product_name': 'XWFE GE Refrigerator Water Filter',
                'brand': 'GE',
                'category': 'Refrigerator Parts',
                'regular_price': 64.02,
                'sale_price': 57.62,
                'discount_percent': 10.0,
                'in_stock': True,
                'stock_status': 'In Stock',
                'similarity_score': 0.89
            }
        ]
    }

    print("="*60)
    print("Response Generation Demo")
    print("="*60)

    # Load client
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key:
        print("\n[WARNING] No API key found, using fallback response")
        response = generate_fallback_response(mock_results['results'])
    else:
        client = OpenAI(api_key=api_key)
        response = generate_response(client, mock_results['query'], mock_results)

    print(f"\nQuery: {mock_results['query']}")
    print("\nResponse:")
    print("-"*60)
    print(response)


if __name__ == '__main__':
    main()
