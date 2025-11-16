"""
Semantic search using OpenAI embeddings
NO sentence-transformers - pure OpenAI API
"""

import sqlite3
import pickle
import os
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from dotenv import load_dotenv

load_dotenv()

def load_product_embeddings(db_path):
    """Load all product embeddings from database"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT sku, product_name, brand, category, sale_price, embedding FROM products WHERE embedding IS NOT NULL")
    
    products = []
    embeddings = []
    
    for row in cursor.fetchall():
        product = dict(row)
        if product['embedding']:
            try:
                embedding = pickle.loads(product['embedding'])
                embeddings.append(embedding)
                products.append(product)
            except Exception as e:
                print(f"Error loading embedding for {product.get('sku')}: {e}")
                continue
    
    conn.close()
    
    return products, np.array(embeddings) if embeddings else np.array([])

def embed_search_query(query_text):
    """Generate embedding for search query using OpenAI API"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found")
    
    client = OpenAI(api_key=api_key)
    
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query_text
    )
    
    return np.array(response.data[0].embedding)

def search_products(db_path, query_text, top_k=5):
    """Main search function using OpenAI embeddings"""
    try:
        products, embeddings = load_product_embeddings(db_path)
        
        if len(products) == 0:
            print("No products found")
            return []
        
        print(f"Loaded {len(products)} products with embeddings")
        print(f"Product embeddings shape: {embeddings.shape}")
        
        # Embed query using OpenAI
        query_embedding = embed_search_query(query_text)
        print(f"Query embedding shape: {query_embedding.shape}")
        
        # Calculate similarities
        query_embedding = query_embedding.reshape(1, -1)
        similarities = cosine_similarity(query_embedding, embeddings)[0]
        
        print(f"Similarities calculated: min={similarities.min():.3f}, max={similarities.max():.3f}")
        
        # Get top K
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        # Build results
        results = []
        for idx in top_indices:
            product = dict(products[idx])
            product['similarity'] = float(similarities[idx])
            results.append(product)
        
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        import traceback
        traceback.print_exc()
        return []

def hybrid_search(db_path, query_text, parsed_query=None, top_k=5):
    """Hybrid search"""
    return search_products(db_path, query_text, top_k)

def load_search_model():
    """Dummy function - no model needed with OpenAI API"""
    return None