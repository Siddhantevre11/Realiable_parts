"""
Pydantic models for request/response validation
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# Search Models
# ============================================================================

class SearchFilters(BaseModel):
    """Optional filters for search"""
    brand: Optional[str] = None
    category: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    in_stock: Optional[bool] = None


class SearchRequest(BaseModel):
    """Search request payload"""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    filters: Optional[SearchFilters] = Field(None, description="Optional filters")

    class Config:
        schema_extra = {
            "example": {
                "query": "water filter for Whirlpool fridge",
                "top_k": 5,
                "filters": {
                    "brand": "Whirlpool",
                    "category": "Refrigerator Parts",
                    "in_stock": True
                }
            }
        }


class ProductResult(BaseModel):
    """Product search result"""
    sku: str
    product_name: str
    brand: Optional[str]
    category: Optional[str]
    regular_price: Optional[float]
    sale_price: Optional[float]
    discount_percent: Optional[float]
    in_stock: Optional[bool]
    stock_status: Optional[str]
    description: Optional[str]
    compatible_models: Optional[str]
    main_image_url: Optional[str]
    product_url: Optional[str]
    similarity: Optional[float] = Field(None, description="Similarity score (0-1)")


class SearchResponse(BaseModel):
    """Search response"""
    success: bool = True
    query: str
    parsed_query: Optional[Dict[str, Any]] = None
    results: List[ProductResult]
    total_results: int
    response_time_ms: int


# ============================================================================
# Chat Models
# ============================================================================

class ChatMessage(BaseModel):
    """Single chat message"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str

    class Config:
        schema_extra = {
            "example": {
                "role": "user",
                "content": "I need a water filter"
            }
        }


class ChatRequest(BaseModel):
    """Chat request payload"""
    message: str = Field(..., min_length=1, description="User message")
    conversation_history: List[ChatMessage] = Field(
        default_factory=list,
        description="Previous conversation messages"
    )
    include_products: bool = Field(True, description="Include product recommendations")

    class Config:
        schema_extra = {
            "example": {
                "message": "I need a water filter for my Whirlpool fridge",
                "conversation_history": [],
                "include_products": True
            }
        }


class ChatProduct(BaseModel):
    """Simplified product for chat response"""
    sku: str
    product_name: str
    brand: Optional[str]
    sale_price: Optional[float]
    in_stock: Optional[bool]
    similarity: Optional[float]


class ChatResponse(BaseModel):
    """Chat response"""
    success: bool = True
    message: str
    products: Optional[List[ChatProduct]] = None
    conversation_history: List[ChatMessage]
    response_time_ms: int


# ============================================================================
# Product Models
# ============================================================================

class Product(BaseModel):
    """Full product model"""
    id: Optional[int]
    sku: str
    product_name: str
    brand: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    regular_price: Optional[float]
    sale_price: Optional[float]
    discount_percent: Optional[float]
    in_stock: Optional[bool]
    stock_status: Optional[str]
    description: Optional[str]
    compatible_models: Optional[str]
    specifications: Optional[str]
    main_image_url: Optional[str]
    all_image_urls: Optional[str]
    product_url: Optional[str]
    scraped_at: Optional[str]
    created_at: Optional[str]


class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int
    limit: int
    total_pages: int
    total_products: int


class ProductListResponse(BaseModel):
    """Product list response with pagination"""
    success: bool = True
    products: List[Product]
    pagination: PaginationMeta


class ProductDetailResponse(BaseModel):
    """Single product response"""
    success: bool = True
    product: Product


# ============================================================================
# Analytics Models
# ============================================================================

class CategoryDistribution(BaseModel):
    """Category distribution data"""
    category: str
    count: int


class PriceRange(BaseModel):
    """Price range stats"""
    min: float
    max: float


class AnalyticsOverview(BaseModel):
    """Analytics overview response"""
    success: bool = True
    total_products: int
    total_brands: int
    total_categories: int
    in_stock_count: int
    in_stock_percentage: float
    avg_price: float
    price_range: PriceRange
    category_distribution: List[CategoryDistribution]


class TopProduct(BaseModel):
    """Top product item"""
    sku: str
    product_name: str
    brand: Optional[str]
    category: Optional[str]
    sale_price: Optional[float]
    discount_percent: Optional[float]
    in_stock: Optional[bool]


class TopProductsResponse(BaseModel):
    """Top products response"""
    success: bool = True
    top_products: List[TopProduct]
    sort_by: str


# ============================================================================
# Metadata Models
# ============================================================================

class CategoriesResponse(BaseModel):
    """Categories list response"""
    success: bool = True
    categories: List[str]


class BrandsResponse(BaseModel):
    """Brands list response"""
    success: bool = True
    brands: List[str]


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    embeddings: str
    openai_api: str
    timestamp: str


# ============================================================================
# Error Models
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    path: Optional[str] = None
