# 🛍️ ThreadHunter — AI Clothing Deal Finder & Price Tracker

> An intelligent, conversational AI personal shopper and deal aggregator designed to discover the best bargains, price cuts, and coupon codes across top fashion retailers. Built with an automatic Gemini model failover engine that seamlessly cascades between models when free-tier rate limits (HTTP 429) are encountered!

---

## ✨ Features at a Glance

### 1. 💬 AI Personal Deal Stylist (Chatbot)
- **Conversational Shopping Advisor**: Ask naturally in plain English:
  - *"Find me winter coats & parkas under $60 with high discounts"*
  - *"What are the biggest sneaker price drops right now?"*
  - *"Recommend an entire casual streetwear fit under $120"*
  - *"Find relaxed denim jeans under $45 with promo codes"*
- **Structured Recommendation Cards in Chat**: Embedded product cards right inside chat messages with direct retailer links, price strikethroughs, discounts, and 1-click **Add to Watchlist** buttons.
- **Smart Latency & Model Telemetry**: Displays the exact model used (e.g., `gemini-2.5-flash`), response time in milliseconds, and failover notifications.

### 2. ⚡ Intelligent Rate-Limit Failover & Multi-Key Switcher
- **Free-Tier Resilience**: Gemini free tier has requests-per-minute (RPM) and requests-per-day (RPD) limits. When an endpoint returns `HTTP 429 Too Many Requests` or `RESOURCE_EXHAUSTED`, ThreadHunter **automatically detects it and switches to the next fallback model in the chain** without crashing or interrupting the user!
- **Cascading Fallback Hierarchy**:
  1. `gemini-2.5-flash` *(Primary cutting-edge)*
  2. `gemini-2.0-flash`
  3. `gemini-2.0-flash-lite`
  4. `gemini-1.5-flash`
  5. `gemini-1.5-flash-8b` *(High RPM limit model)*
  6. `gemini-1.5-pro`
  7. `Local Stylist Heuristic` *(Guarantees 100% offline uptime even if all API quotas hit 0)*
- **Multi-Key Rotation**: Supports multiple Gemini API keys (comma-separated). Rotates keys automatically upon hitting quotas.
- **Audit Logging**: Every rate-limit incident and model transition is recorded with timestamp, previous model, new model, and trigger reason.
- **Interactive Simulator**: Includes a **"Simulate 429 Quota Rate Limit"** button to instantly see automatic failover in action!

### 3. 🛍️ Deal Explorer & Live Web Crawler
- **Instant Filtering**: Filter by category (*Jackets, Hoodies, Denim, Sneakers, T-Shirts, Sweaters, Activewear, Dresses*), retailer (*Nike, Uniqlo, Zara, ASOS, Nordstrom Rack, SSENSE, Amazon Fashion, End Clothing*), gender (*Men, Women, Unisex*), and minimum discount slider (*0% to 70%+*).
- **1-Click Coupon Copier**: Copy verified promo codes (`EXTRA20`, `RACKRUSH`, `MEMBER20`) with instant toast alerts.
- **Dynamic Apparel Crawler**: Click "Live Web Search" to synthesize and crawl verified deals for any custom apparel or niche aesthetic.

### 4. 📊 Market Insights & Analytics Dashboard
- **Metric Cards**: Total deals tracked, average discount percentage, average deal price, and total savings.
- **Category Discount Distribution**: Interactive Chart.js bar chart displaying markdown benchmarks by apparel category.
- **Retailer Spread**: Doughnut chart showing deal volume across major online storefronts.
- **Top Steals Leaderboard**: Ranked table of the day's deepest discounts.

### 5. ⭐ Price Watchlist & Alert Tracker
- Bookmark deals with target alert prices.
- Tracks cumulative money saved across your saved wishlist items.

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+ (Tested on Python 3.14)
- FastAPI, Uvicorn, Requests, Pydantic

### 2. Setup & Launch
Clone or navigate to the repository:
```bash
cd /Users/deveshkumar/Documents/ShopHelper
```

Start the application with the included launcher script:
```bash
./run.sh
```

Or manually using Uvicorn:
```bash
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser at:
👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔑 Adding Your Free Gemini API Key(s)

ThreadHunter works right out of the box in **High-Speed Stylist Mode** without any keys required. To unlock full Gemini conversational capabilities:

1. Obtain a free API key from [Google AI Studio](https://aistudio.google.com/).
2. You can configure keys in two ways:
   - **Method A (Via Web UI)**: Navigate to the **"⚡ Model Failover"** tab in the app, paste your key(s) into the **Gemini API Key Manager**, and click **Save & Activate**.
   - **Method B (Via `.env`)**:
     ```bash
     cp .env.example .env
     ```
     Add your key(s) in `.env`:
     ```env
     GEMINI_API_KEYS=AIzaSyD...,AIzaSyE...
     ```
     *(You can add multiple comma-separated keys for automatic round-robin rotation!)*

---

## 🏗️ Project Architecture

```
ShopHelper/
├── app/
│   ├── __init__.py
│   ├── config.py           # Zero-dependency configuration & .env persistence
│   ├── database.py         # SQLite database (deals, watchlist, telemetry, switch logs)
│   ├── ai_service.py       # Gemini API client with cascading failover & key rotation
│   ├── deal_scraper.py     # Retailer catalog aggregator, query extractor & crawler
│   ├── schemas.py          # Pydantic schemas for chat, deals, and filters
│   └── main.py             # FastAPI backend with static file mounting
├── static/
│   ├── index.html          # Cyber-Chic Glassmorphic Dashboard & Chat UI
│   ├── css/
│   │   └── style.css       # Custom styles, glow badges, animations, scrollbars
│   └── js/
│       ├── app.js          # Client application logic (chat, filters, watchlist)
│       └── charts.js       # Chart.js visualization configurations
├── data/
│   └── shophelper.db       # SQLite database file
├── .env.example            # Environment variables template
├── requirements.txt        # Minimal Python dependencies
├── run.sh                  # One-click executable launcher
└── README.md               # Documentation
```

---

## 📡 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Chat with AI stylist (returns advice + deal cards + model telemetry) |
| `GET` | `/api/deals` | Filter & search deals by keyword, category, store, discount % |
| `POST` | `/api/deals/search-live` | Dynamically crawl deals for any apparel item |
| `GET` | `/api/watchlist` | Retrieve saved items on price watchlist |
| `POST` | `/api/watchlist` | Add deal to watchlist |
| `DELETE`| `/api/watchlist/{deal_id}`| Remove deal from watchlist |
| `GET` | `/api/stats` | Analytics summary for dashboard metrics and charts |
| `GET` | `/api/model/status` | Current active model, key count, and failover status |
| `POST` | `/api/model/simulate-ratelimit` | Trigger a simulated 429 quota failover |
| `POST` | `/api/model/set-active` | Manually select active model |
| `POST` | `/api/settings/keys` | Dynamically update Gemini API key(s) |

---

## 💡 Testing Rate Limit Model Switching
Want to see the automatic failover in action?
1. Open the app at `http://127.0.0.1:8000`.
2. Click the **"⚡ Test Failover"** button in the top navigation bar or go to the **"⚡ Model Failover"** tab.
3. Watch the active model switch from `gemini-2.5-flash` to `gemini-2.0-flash` (or subsequent models).
4. Check the **Failover Audit Log** table to see the recorded timestamp and trigger reason!
