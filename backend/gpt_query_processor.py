"""
Use GPT-3.5-turbo to parse natural language queries
Extracts intent, entities, and search parameters
"""

from openai import OpenAI
import json
import os
from dotenv import load_dotenv


# GPT System Prompt for Query Understanding
GPT_SYSTEM_PROMPT = """
You are an expert assistant for an appliance parts distributor. Your job is to parse customer queries and extract structured information.

Extract the following from the query:
- intent: "find_part" | "check_price" | "check_compatibility" | "general_question"
- part_type: The type of part (e.g., "water filter", "ice maker", "door gasket", "drum", "motor")
- brand: Brand name if mentioned (e.g., "Whirlpool", "GE", "Samsung", "LG", "Frigidaire", "Bosch")
- model_number: Appliance model number if mentioned
- category: Appliance category ("refrigerator" | "dishwasher" | "washer" | "dryer" | "oven" | null)
- keywords: Key search terms as a list
- price_sensitivity: "budget" | "premium" | null (infer from words like "cheap", "best", "high-quality")
- urgency: "urgent" | "normal" | null (infer from words like "asap", "urgent", "quick")

Return ONLY a valid JSON object, no other text.

Examples:

Query: "I need a water filter for a Whirlpool fridge"
{
  "intent": "find_part",
  "part_type": "water filter",
  "brand": "Whirlpool",
  "model_number": null,
  "category": "refrigerator",
  "keywords": ["water", "filter", "whirlpool"],
  "price_sensitivity": null,
  "urgency": "normal"
}

Query: "cheap ice maker for GE model GSS25GSHSS"
{
  "intent": "find_part",
  "part_type": "ice maker",
  "brand": "GE",
  "model_number": "GSS25GSHSS",
  "category": "refrigerator",
  "keywords": ["ice", "maker", "ge"],
  "price_sensitivity": "budget",
  "urgency": "normal"
}

Query: "do you have replacement door seals for Samsung dishwashers?"
{
  "intent": "find_part",
  "part_type": "door seal",
  "brand": "Samsung",
  "model_number": null,
  "category": "dishwasher",
  "keywords": ["door", "seal", "gasket", "samsung"],
  "price_sensitivity": null,
  "urgency": "normal"
}

Query: "urgent need Whirlpool washer drum WFW9151YW00"
{
  "intent": "find_part",
  "part_type": "drum",
  "brand": "Whirlpool",
  "model_number": "WFW9151YW00",
  "category": "washer",
  "keywords": ["drum", "whirlpool", "washer"],
  "price_sensitivity": null,
  "urgency": "urgent"
}

Query: "best quality water filter under $50"
{
  "intent": "find_part",
  "part_type": "water filter",
  "brand": null,
  "model_number": null,
  "category": "refrigerator",
  "keywords": ["water", "filter", "quality"],
  "price_sensitivity": "budget",
  "urgency": "normal"
}
"""


def call_gpt_api(client, system_prompt, user_message, temperature=0.1, max_tokens=300):
    """
    Make API call to GPT-3.5-turbo.

    Args:
        client: OpenAI client instance
        system_prompt: System prompt for GPT
        user_message: User query
        temperature: Temperature for generation (0.1 for consistency)
        max_tokens: Maximum tokens in response

    Returns:
        str: GPT response content
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )

        return response.choices[0].message.content

    except Exception as e:
        raise Exception(f"GPT API call failed: {e}")


def parse_query_with_gpt(query_text, client=None):
    """
    Send query to GPT to extract structured information.

    Args:
        query_text: Natural language query from user
        client: OpenAI client (optional, will create if not provided)

    Returns:
        dict: Structured query data

    Example:
        Input: "I need a water filter for Whirlpool WRF535SMBM00"

        Output: {
            "intent": "find_part",
            "part_type": "water filter",
            "brand": "Whirlpool",
            "model_number": "WRF535SMBM00",
            "category": "refrigerator",
            "keywords": ["water", "filter", "whirlpool"],
            "price_sensitivity": null,
            "urgency": "normal"
        }
    """
    # Create client if not provided
    if client is None:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
        client = OpenAI(api_key=api_key)

    # Call GPT API
    try:
        response_text = call_gpt_api(
            client,
            GPT_SYSTEM_PROMPT,
            query_text,
            temperature=0.1,
            max_tokens=300
        )

        # Parse JSON response
        parsed_query = json.loads(response_text)

        # Validate required fields
        required_fields = ['intent', 'part_type', 'brand', 'category', 'keywords']
        for field in required_fields:
            if field not in parsed_query:
                parsed_query[field] = None

        return parsed_query

    except json.JSONDecodeError as e:
        # If GPT doesn't return valid JSON, create fallback structure
        print(f"[WARNING] Failed to parse GPT response as JSON: {e}")
        return create_fallback_parse(query_text)

    except Exception as e:
        print(f"[ERROR] Query parsing failed: {e}")
        return create_fallback_parse(query_text)


def create_fallback_parse(query_text):
    """
    Create a basic parsed query structure from text (fallback).

    Args:
        query_text: Original query text

    Returns:
        dict: Basic parsed structure
    """
    # Simple keyword extraction
    words = query_text.lower().split()

    # Try to detect common brands
    brands = ['whirlpool', 'ge', 'samsung', 'lg', 'frigidaire', 'bosch', 'kitchenaid', 'maytag']
    detected_brand = None
    for brand in brands:
        if brand in query_text.lower():
            detected_brand = brand.title()
            break

    # Try to detect categories
    categories = {
        'refrigerator': ['fridge', 'refrigerator', 'freezer'],
        'dishwasher': ['dishwasher'],
        'washer': ['washer', 'washing machine'],
        'dryer': ['dryer'],
    }

    detected_category = None
    for category, keywords in categories.items():
        if any(keyword in query_text.lower() for keyword in keywords):
            detected_category = category
            break

    return {
        'intent': 'find_part',
        'part_type': None,
        'brand': detected_brand,
        'model_number': None,
        'category': detected_category,
        'keywords': words[:10],  # First 10 words
        'price_sensitivity': None,
        'urgency': 'normal',
        'fallback': True
    }


def extract_query_intent(query_text, client=None):
    """
    Main function: Parse query and return structured data.

    Args:
        query_text: Natural language query
        client: OpenAI client (optional)

    Returns:
        dict: Parsed query structure
    """
    return parse_query_with_gpt(query_text, client)


def test_query_parsing():
    """
    Test query parsing with sample queries.
    """
    test_queries = [
        "I need a water filter for a Whirlpool fridge",
        "ice maker for GE refrigerator model GSS25GSHSS",
        "cheap dishwasher replacement parts",
        "Samsung dryer door gasket urgent",
        "what's the best water filter under $50?",
        "do you have drain pumps for Bosch dishwashers?"
    ]

    print("="*60)
    print("Testing GPT Query Parsing")
    print("="*60)

    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-"*60)

        try:
            parsed = extract_query_intent(query)
            print(json.dumps(parsed, indent=2))

        except Exception as e:
            print(f"ERROR: {e}")


if __name__ == '__main__':
    test_query_parsing()
