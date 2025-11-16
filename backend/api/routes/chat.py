"""
Chat endpoints - GPT-powered conversational interface
"""

from fastapi import APIRouter, HTTPException
from api.models.schemas import ChatRequest, ChatResponse, ChatMessage, ChatProduct
from intelligent_search import IntelligentSearchSystem
import time
import logging
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)

router = APIRouter()

DB_PATH = "database/products.db"

# Initialize search system (singleton)
_search_system = None


def get_search_system():
    """
    Get or create IntelligentSearchSystem instance (singleton).

    Returns:
        IntelligentSearchSystem: Initialized search system
    """
    global _search_system
    if _search_system is None:
        try:
            logger.info("Initializing IntelligentSearchSystem...")
            _search_system = IntelligentSearchSystem(DB_PATH)
            logger.info("IntelligentSearchSystem initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize search system: {e}")
            raise
    return _search_system


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    GPT-powered chatbot for product assistance.

    This endpoint provides conversational AI that:
    - Understands natural language queries
    - Finds relevant products using semantic search
    - Generates helpful, conversational responses
    - Suggests complementary products (upsells)
    - Maintains conversation history

    Perfect for sales agents helping customers find parts.
    """
    start_time = time.time()

    try:
        logger.info(f"Chat request: message='{request.message[:50]}...', "
                   f"history_length={len(request.conversation_history)}")

        # Get search system
        system = get_search_system()

        # Get response with products
        result = system.search(
            query_text=request.message,
            top_k=3,
            return_raw=True
        )

        # Build conversation history
        history = request.conversation_history.copy()
        history.append(ChatMessage(role="user", content=request.message))
        history.append(ChatMessage(role="assistant", content=result['response']))

        # Format products for chat response
        chat_products = None
        if request.include_products and result.get('products'):
            chat_products = []
            for product in result['products'][:5]:  # Top 5 products
                chat_products.append(ChatProduct(
                    sku=product.get('sku', ''),
                    product_name=product.get('product_name', ''),
                    brand=product.get('brand'),
                    sale_price=product.get('sale_price'),
                    in_stock=product.get('in_stock'),
                    similarity=product.get('similarity') or product.get('similarity_score')
                ))

        response_time = int((time.time() - start_time) * 1000)

        logger.info(f"Chat completed: {len(chat_products or [])} products in {response_time}ms")

        return ChatResponse(
            success=True,
            message=result['response'],
            products=chat_products,
            conversation_history=history,
            response_time_ms=response_time
        )

    except ValueError as e:
        # API key or configuration errors
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="Chat service unavailable. Please check API configuration."
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Chat request failed: {str(e)}"
        )


@router.get("/chat/health")
async def chat_health():
    """
    Check if chat system is ready.

    Returns:
        dict: Health status of chat system
    """
    try:
        system = get_search_system()
        return {
            "status": "healthy",
            "message": "Chat system is ready",
            "model_loaded": system.embedding_model is not None,
            "client_connected": system.client is not None
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": str(e)
        }
