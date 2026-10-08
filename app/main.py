import os
from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.config import config, BASE_DIR
from app.database import (
    init_db,
    query_deals,
    get_deal_by_id,
    add_to_watchlist,
    remove_from_watchlist,
    get_watchlist,
    get_dashboard_stats,
    get_model_switch_logs,
    get_search_history,
)
from app.deal_scraper import (
    seed_initial_deals, 
    search_deals_for_chatbot, 
    generate_dynamic_deal_for_query, 
    extract_deal_keywords,
    fetch_live_web_deals
)
from app.ai_service import ai_service
from app.schemas import (
    ChatRequest,
    ChatResponse,
    DealItem,
    WatchlistAddRequest,
    ApiKeyUpdateRequest,
    SwitchModelRequest
)

# Initialize FastAPI application
app = FastAPI(
    title="ThreadHunter - AI Clothing Deal Finder & Stylist",
    description="Intelligent clothing deal search, web price aggregator, Gemini AI fallback engine, and visual dashboard.",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files path
STATIC_DIR = BASE_DIR / "static"

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.on_event("startup")
def on_startup():
    init_db()
    seed_initial_deals()

@app.get("/")
def read_root():
    """Serves the main single page web application."""
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "ThreadHunter API is running. index.html not found."}

# ----------------- Chatbot Endpoint -----------------
@app.post("/api/chat", response_model=ChatResponse)
def chat_with_stylist(req: ChatRequest):
    """
    Chatbot endpoint:
    - Finds deals matching the query
    - Calls Gemini with automatic model failover if rate-limited (429)
    - Returns stylist suggestions with deal cards and model telemetry
    """
    try:
        deals = search_deals_for_chatbot(req.message, limit=4)
        result = ai_service.generate_chat_response(
            user_message=req.message,
            matching_deals=deals,
            preferred_model=req.preferred_model
        )
        return ChatResponse(
            reply=result["reply"],
            deals=[DealItem(**d) for d in result["deals"]],
            model_used=result["model_used"],
            fallback_triggered=result["fallback_triggered"],
            fallback_details=result["fallback_details"],
            latency_ms=result["latency_ms"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Deals Catalog & Search Endpoints -----------------
@app.get("/api/deals", response_model=List[DealItem])
def get_deals(
    q: Optional[str] = None,
    category: Optional[str] = "All",
    brand: Optional[str] = "All",
    store: Optional[str] = "All",
    min_discount: Optional[int] = 0,
    max_price: Optional[float] = None,
    gender: Optional[str] = "All",
    sort_by: Optional[str] = "discount_pct",
    limit: Optional[int] = 40
):
    """Retrieves clothing deals with rich filters and sorting."""
    deals = query_deals(
        query=q,
        category=category,
        brand=brand,
        store=store,
        min_discount=min_discount,
        max_price=max_price,
        gender=gender,
        sort_by=sort_by,
        limit=limit
    )
    return [DealItem(**d) for d in deals]

@app.get("/api/deals/{deal_id}", response_model=DealItem)
def get_single_deal(deal_id: str):
    deal = get_deal_by_id(deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    return DealItem(**deal)

@app.post("/api/deals/search-live")
def search_live_deals(query: str = Query(..., description="Query for deals")):
    """Dynamically searches the web & generates fresh verified deals for any apparel item."""
    extracted = extract_deal_keywords(query)
    dyn_deal = generate_dynamic_deal_for_query(extracted)
    all_matched = query_deals(query=query, limit=10)
    return {
        "status": "success",
        "query": query,
        "extracted_params": extracted,
        "newly_discovered": dyn_deal,
        "results": all_matched
    }

@app.post("/api/deals/fetch-live-web")
def fetch_live_deals_from_web():
    """Fetches real-time clothing deals directly from public online fashion deal feeds."""
    deals = fetch_live_web_deals()
    return {
        "status": "success",
        "count": len(deals),
        "deals": deals
    }

# ----------------- Watchlist Endpoints -----------------
@app.get("/api/watchlist")
def fetch_watchlist():
    return get_watchlist()

@app.post("/api/watchlist")
def save_to_watchlist(req: WatchlistAddRequest):
    deal = get_deal_by_id(req.deal_id)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    success = add_to_watchlist(deal, target_price=req.target_price)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add to watchlist")
    return {"status": "success", "message": f"Added '{deal['title']}' to watchlist!"}

@app.delete("/api/watchlist/{deal_id}")
def delete_from_watchlist(deal_id: str):
    remove_from_watchlist(deal_id)
    return {"status": "success", "message": "Deal removed from watchlist"}

# ----------------- Dashboard & Analytics Endpoints -----------------
@app.get("/api/stats")
def fetch_dashboard_stats():
    """Returns analytics data for dashboard charts and metrics cards."""
    return get_dashboard_stats()

@app.get("/api/history")
def fetch_search_history():
    return get_search_history(limit=15)

# ----------------- AI Model & Failover Status Endpoints -----------------
@app.get("/api/model/status")
def get_model_status():
    """Provides real-time AI status, active model, fallback chain, and switch logs."""
    keys = config.get_api_keys()
    masked_keys = [f"...{k[-4:]}" if len(k) > 4 else "key" for k in keys]
    return {
        "current_model": ai_service.current_model,
        "fallback_chain": ai_service.fallback_chain,
        "configured_keys_count": len(keys),
        "keys_masked": masked_keys,
        "session_switches": ai_service.total_switches_session,
        "recent_switches": get_model_switch_logs(limit=10)
    }

@app.post("/api/model/simulate-ratelimit")
def trigger_simulate_rate_limit():
    """Simulates a 429 quota exhaustion to demonstrate automatic model switching."""
    res = ai_service.simulate_rate_limit_switch()
    return res

@app.post("/api/model/set-active")
def set_active_model(req: SwitchModelRequest):
    success = ai_service.set_active_model(req.target_model)
    if not success:
        raise HTTPException(status_code=400, detail=f"Invalid model name '{req.target_model}'")
    return {
        "status": "success",
        "current_model": ai_service.current_model,
        "message": f"Active model set to '{req.target_model}'"
    }

@app.get("/api/model/switch-logs")
def fetch_switch_logs():
    return get_model_switch_logs(limit=25)

# ----------------- API Key Settings Endpoint -----------------
@app.post("/api/settings/keys")
def update_api_keys(req: ApiKeyUpdateRequest):
    """Dynamically set or update Gemini API keys in runtime and config."""
    valid_keys = [k.strip() for k in req.keys if k.strip()]
    config.set_api_keys(valid_keys)
    return {
        "status": "success",
        "keys_count": len(valid_keys),
        "message": f"Successfully updated {len(valid_keys)} Gemini API key(s)!"
    }
