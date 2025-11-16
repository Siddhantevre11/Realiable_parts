"""
Main intelligent search system
Combines all components into simple interface
"""

from openai import OpenAI
import os
from dotenv import load_dotenv
import sqlite3

import config
from gpt_query_processor import extract_query_intent
from semantic_search import hybrid_search, load_search_model
from gpt_response_generator import generate_response, suggest_upsells


class IntelligentSearchSystem:
    """
    Complete AI-powered search system.

    Combines GPT query understanding, semantic search,
    and intelligent response generation.
    """

    def __init__(self, db_path=None, openai_api_key=None):
        """
        Initialize search system.

        Args:
            db_path: Path to database (default from config)
            openai_api_key: OpenAI API key (default from env)
        """
        # Database path
        self.db_path = db_path or config.DATABASE_PATH

        # Load environment variables
        load_dotenv()

        # Initialize OpenAI client
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. "
                "Set OPENAI_API_KEY environment variable or pass openai_api_key parameter."
            )

        self.client = OpenAI(api_key=api_key)

        # Load embedding model (reuse across searches)
        print("Loading embedding model...")
        self.embedding_model = load_search_model()
        print("[OK] Intelligent search system ready")

    def search(self, query_text, top_k=5, include_upsells=True, return_raw=False):
        """
        Main search function.

        Args:
            query_text: Natural language query from agent
            top_k: Number of results to return
            include_upsells: Whether to include upsell suggestions
            return_raw: Return raw data instead of formatted response

        Returns:
            If return_raw=False: Natural language response string
            If return_raw=True: Dict with parsed_query, products, response
        """
        # Step 1: Parse query with GPT
        parsed_query = extract_query_intent(query_text, self.client)

        # Step 2: Run hybrid semantic search
       	search_results = hybrid_search(
    	self.db_path, 
    	query_text, 
    	top_k=top_k
	)
        # Prepare results dict
        results_dict = {
            'query': query_text,
            'parsed_query': parsed_query,
            'results': search_results
        }

        # Step 3: Generate conversational response
        response_text = generate_response(
            self.client,
            query_text,
            results_dict,
            include_upsells
        )

        if return_raw:
            return {
                'query': query_text,
                'parsed_query': parsed_query,
                'products': search_results,
                'response': response_text
            }
        else:
            return response_text

    def get_product_details(self, sku):
        """
        Get detailed information about a specific product.

        Args:
            sku: Product SKU

        Returns:
            dict: Product details or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM products
            WHERE sku = ?
            LIMIT 1;
        """, (sku.upper(),))

        row = cursor.fetchone()
        conn.close()

        return dict(row) if row else None

    def compare_products(self, sku_list):
        """
        Compare multiple products side-by-side.

        Args:
            sku_list: List of product SKUs

        Returns:
            str: Formatted comparison
        """
        products = []
        for sku in sku_list:
            product = self.get_product_details(sku)
            if product:
                products.append(product)

        if not products:
            return "No products found for comparison."

        # Generate comparison using GPT
        comparison_prompt = f"""
Compare these {len(products)} products and highlight:
1. Price differences
2. Key features
3. Best value option
4. Recommendations for different use cases

Products:
"""

        for product in products:
            comparison_prompt += f"\n- {product['product_name']} (${product.get('sale_price', 0):.2f})"
            comparison_prompt += f"\n  Brand: {product.get('brand', 'N/A')}"
            comparison_prompt += f"\n  Stock: {product.get('stock_status', 'Unknown')}\n"

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful product comparison assistant."},
                    {"role": "user", "content": comparison_prompt}
                ],
                temperature=0.7,
                max_tokens=400
            )

            return response.choices[0].message.content

        except Exception as e:
            return f"Error generating comparison: {e}"


def demo_search_system(db_path=None):
    """
    Demo function showing example usage.

    Args:
        db_path: Path to database (optional)
    """
    print("\n" + "="*60)
    print("Intelligent Search System Demo")
    print("="*60)

    try:
        # Initialize system
        system = IntelligentSearchSystem(db_path)

        # Test queries
        test_queries = [
            "I need a water filter for a Whirlpool fridge",
            "ice maker for GE refrigerator",
            "cheap dishwasher replacement parts",
            "Samsung dryer door gasket",
            "what's the best water filter under $50?"
        ]

        for query in test_queries:
            print(f"\n{'='*60}")
            print(f"Query: {query}")
            print(f"{'='*60}\n")

            # Search (with raw data for debugging)
            result = system.search(query, top_k=3, return_raw=True)

            # Show parsed query
            print("Parsed Query:")
            print(f"  Intent: {result['parsed_query'].get('intent')}")
            print(f"  Part: {result['parsed_query'].get('part_type')}")
            print(f"  Brand: {result['parsed_query'].get('brand')}")
            print(f"  Category: {result['parsed_query'].get('category')}\n")

            # Show top matches
            print(f"Top {len(result['products'])} Matches:")
            for i, product in enumerate(result['products'][:3], 1):
                print(f"  {i}. {product['product_name']}")
                print(f"     Score: {product.get('similarity_score', 0):.3f}")
                print(f"     Price: ${product.get('sale_price', 0):.2f}")

            # Show response
            print("\nResponse:")
            print("-"*60)
            print(result['response'])

        print("\n" + "="*60)
        print("Demo Complete!")
        print("="*60)

    except ValueError as e:
        print(f"\n[ERROR] {e}")
        print("\nPlease set up your OpenAI API key:")
        print("  export OPENAI_API_KEY='sk-your-key-here'")
        print("  or create a .env file with OPENAI_API_KEY=sk-...")

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


def interactive_search(db_path=None):
    """
    Interactive search mode - ask questions in a loop.

    Args:
        db_path: Path to database (optional)
    """
    print("\n" + "="*60)
    print("Interactive Intelligent Search")
    print("="*60)
    print("Type your queries below. Type 'quit' or 'exit' to stop.\n")

    try:
        system = IntelligentSearchSystem(db_path)

        while True:
            query = input("\nYour query: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break

            if not query:
                continue

            print("\nSearching...")
            response = system.search(query, top_k=5)

            print("\n" + "-"*60)
            print(response)
            print("-"*60)

    except ValueError as e:
        print(f"\n[ERROR] {e}")
        print("\nPlease set up your OpenAI API key:")
        print("  export OPENAI_API_KEY='sk-your-key-here'")

    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Intelligent Search System for Appliance Parts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python intelligent_search.py --demo              # Run demo with sample queries
  python intelligent_search.py --interactive       # Interactive search mode
  python intelligent_search.py "water filter"      # Single query
        """
    )

    parser.add_argument('query', nargs='?', help='Search query')
    parser.add_argument('--db', default=config.DATABASE_PATH, help='Database path')
    parser.add_argument('--demo', action='store_true', help='Run demo mode')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results')
    parser.add_argument('--raw', action='store_true', help='Return raw data')

    args = parser.parse_args()

    if args.demo:
        demo_search_system(args.db)
    elif args.interactive:
        interactive_search(args.db)
    elif args.query:
        try:
            system = IntelligentSearchSystem(args.db)
            result = system.search(args.query, args.top_k, return_raw=args.raw)

            if args.raw:
                import json
                print(json.dumps(result, indent=2, default=str))
            else:
                print("\n" + result)

        except Exception as e:
            print(f"[ERROR] {e}")
            import sys
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
