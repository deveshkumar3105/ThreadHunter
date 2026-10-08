from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class DealItem(BaseModel):
    id: str
    title: str
    brand: str
    store: str
    category: str
    gender: Optional[str] = "Unisex"
    original_price: float
    discount_price: float
    discount_pct: int
    currency: Optional[str] = "$"
    url: str
    image_url: Optional[str] = None
    coupon_code: Optional[str] = None
    sizes: Optional[str] = "S, M, L, XL"
    rating: Optional[float] = 4.5
    badge: Optional[str] = None
    in_stock: Optional[int] = 1
    created_at: Optional[str] = None

class ChatRequest(BaseModel):
    message: str
    category: Optional[str] = None
    budget: Optional[float] = None
    gender: Optional[str] = None
    preferred_model: Optional[str] = None

class ChatResponse(BaseModel):
    reply: str
    deals: List[DealItem]
    model_used: str
    fallback_triggered: bool = False
    fallback_details: Optional[str] = None
    latency_ms: int = 0

class DealFilterRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = "All"
    brand: Optional[str] = "All"
    store: Optional[str] = "All"
    min_discount: Optional[int] = 0
    max_price: Optional[float] = None
    gender: Optional[str] = "All"
    sort_by: Optional[str] = "discount_pct"
    limit: Optional[int] = 50

class WatchlistAddRequest(BaseModel):
    deal_id: str
    target_price: Optional[float] = None

class ApiKeyUpdateRequest(BaseModel):
    keys: List[str]

class SwitchModelRequest(BaseModel):
    target_model: str
