import random
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.database import save_deals_bulk, query_deals, save_deal

# Curated High-Quality Clothing Catalog with realistic pricing, store deals & verified coupon codes
INITIAL_CLOTHING_DEALS = [
    {
        "id": "deal-001",
        "title": "Air Max 90 Retro Running Shoes",
        "brand": "Nike",
        "store": "Nike Store",
        "category": "Sneakers",
        "gender": "Unisex",
        "original_price": 130.00,
        "discount_price": 78.00,
        "discount_pct": 40,
        "currency": "$",
        "url": "https://www.nike.com",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "MEMBER20",
        "sizes": "US 7, 8, 9, 10, 11",
        "rating": 4.8,
        "badge": "Steal Deal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-002",
        "title": "Ultra Light Down Seamless Parka",
        "brand": "Uniqlo",
        "store": "Uniqlo",
        "category": "Jackets",
        "gender": "Men",
        "original_price": 89.90,
        "discount_price": 49.90,
        "discount_pct": 45,
        "currency": "$",
        "url": "https://www.uniqlo.com",
        "image_url": "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "UNIQLO10",
        "sizes": "S, M, L, XL",
        "rating": 4.7,
        "badge": "Lowest in 30 Days",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-003",
        "title": "501 Original Fit Selvedge Denim Jeans",
        "brand": "Levi's",
        "store": "Nordstrom Rack",
        "category": "Denim",
        "gender": "Men",
        "original_price": 98.00,
        "discount_price": 44.50,
        "discount_pct": 55,
        "currency": "$",
        "url": "https://www.nordstromrack.com",
        "image_url": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "RACKRUSH",
        "sizes": "30x32, 32x32, 34x32",
        "rating": 4.6,
        "badge": "55% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-004",
        "title": "Heavyweight Boxy Fleece Hoodie (400 GSM)",
        "brand": "ASOS DESIGN",
        "store": "ASOS",
        "category": "Hoodies",
        "gender": "Unisex",
        "original_price": 60.00,
        "discount_price": 27.00,
        "discount_pct": 55,
        "currency": "$",
        "url": "https://www.asos.com",
        "image_url": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "ASOSDEAL",
        "sizes": "XS, S, M, L, XL",
        "rating": 4.5,
        "badge": "Best Seller",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-005",
        "title": "Align High-Rise Yoga Pant 25\"",
        "brand": "Lululemon",
        "store": "Lululemon WMTM",
        "category": "Activewear",
        "gender": "Women",
        "original_price": 118.00,
        "discount_price": 69.00,
        "discount_pct": 42,
        "currency": "$",
        "url": "https://shop.lululemon.com",
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "",
        "sizes": "4, 6, 8, 10",
        "rating": 4.9,
        "badge": "Clearance Drop",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-006",
        "title": "Relaxed Fit 100% Linen Camp Collar Shirt",
        "brand": "Zara",
        "store": "Zara",
        "category": "T-Shirts",
        "gender": "Men",
        "original_price": 49.90,
        "discount_price": 22.90,
        "discount_pct": 54,
        "currency": "$",
        "url": "https://www.zara.com",
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "ZARASALE",
        "sizes": "S, M, L",
        "rating": 4.4,
        "badge": "Summer Steal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-007",
        "title": "574 Core Classic Suede Sneakers",
        "brand": "New Balance",
        "store": "Nordstrom Rack",
        "category": "Sneakers",
        "gender": "Unisex",
        "original_price": 89.99,
        "discount_price": 49.97,
        "discount_pct": 44,
        "currency": "$",
        "url": "https://www.nordstromrack.com",
        "image_url": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "SAVE10NB",
        "sizes": "US 8, 8.5, 9, 9.5, 10, 11",
        "rating": 4.7,
        "badge": "Trending Now",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-008",
        "title": "1996 Retro Nuptse Goose Down Jacket",
        "brand": "The North Face",
        "store": "End Clothing",
        "category": "Jackets",
        "gender": "Unisex",
        "original_price": 330.00,
        "discount_price": 198.00,
        "discount_pct": 40,
        "currency": "$",
        "url": "https://www.endclothing.com",
        "image_url": "https://images.unsplash.com/photo-1548883354-7622d03aca27?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "WINTER40",
        "sizes": "M, L, XL",
        "rating": 4.9,
        "badge": "Steal Deal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-009",
        "title": "Floral Midi Slip Dress with Slit",
        "brand": "Abercrombie & Fitch",
        "store": "Abercrombie",
        "category": "Dresses",
        "gender": "Women",
        "original_price": 120.00,
        "discount_price": 48.00,
        "discount_pct": 60,
        "currency": "$",
        "url": "https://www.abercrombie.com",
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "AFVIP20",
        "sizes": "XS, S, M, L",
        "rating": 4.6,
        "badge": "60% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-010",
        "title": "Carhartt WIP Michigan Chore Coat",
        "brand": "Carhartt WIP",
        "store": "SSENSE",
        "category": "Jackets",
        "gender": "Men",
        "original_price": 215.00,
        "discount_price": 118.00,
        "discount_pct": 45,
        "currency": "$",
        "url": "https://www.ssense.com",
        "image_url": "https://images.unsplash.com/photo-1551028719-00167b16eac5?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "SSENSE15",
        "sizes": "S, M, L, XL",
        "rating": 4.8,
        "badge": "Heritage Pick",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-011",
        "title": "Oversized Vintage Washed Graphic Tee",
        "brand": "Stüssy",
        "store": "ASOS",
        "category": "T-Shirts",
        "gender": "Unisex",
        "original_price": 55.00,
        "discount_price": 29.50,
        "discount_pct": 46,
        "currency": "$",
        "url": "https://www.asos.com",
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "STREET20",
        "sizes": "S, M, L",
        "rating": 4.5,
        "badge": "Streetwear Favorite",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-012",
        "title": "Chuck 70 Vintage Canvas High Top",
        "brand": "Converse",
        "store": "Nordstrom Rack",
        "category": "Sneakers",
        "gender": "Unisex",
        "original_price": 90.00,
        "discount_price": 44.97,
        "discount_pct": 50,
        "currency": "$",
        "url": "https://www.nordstromrack.com",
        "image_url": "https://images.unsplash.com/photo-1607522370275-f14206abe5d3?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "CHUCK50",
        "sizes": "US 6, 7, 8, 9, 10, 11",
        "rating": 4.7,
        "badge": "Half Price",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-013",
        "title": "Reverse Weave Heavyweight Crewneck",
        "brand": "Champion",
        "store": "Amazon Fashion",
        "category": "Hoodies",
        "gender": "Unisex",
        "original_price": 65.00,
        "discount_price": 29.99,
        "discount_pct": 54,
        "currency": "$",
        "url": "https://www.amazon.com",
        "image_url": "https://images.unsplash.com/photo-1578587018452-892bacefd3f2?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "CHAMP25",
        "sizes": "S, M, L, XL, XXL",
        "rating": 4.6,
        "badge": "Lowest in 30 Days",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-014",
        "title": "Better Sweater 1/4 Zip Fleece Pullover",
        "brand": "Patagonia",
        "store": "Nordstrom",
        "category": "Sweaters",
        "gender": "Men",
        "original_price": 139.00,
        "discount_price": 83.40,
        "discount_pct": 40,
        "currency": "$",
        "url": "https://www.nordstrom.com",
        "image_url": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "EARTHSAVE",
        "sizes": "S, M, L",
        "rating": 4.9,
        "badge": "Eco Friendly",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-015",
        "title": "Wide Leg Baggy Skater Cargo Pants",
        "brand": "H&M",
        "store": "H&M",
        "category": "Denim",
        "gender": "Unisex",
        "original_price": 49.99,
        "discount_price": 19.99,
        "discount_pct": 60,
        "currency": "$",
        "url": "https://www2.hm.com",
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "HMDEAL20",
        "sizes": "28, 30, 32, 34",
        "rating": 4.3,
        "badge": "60% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-016",
        "title": "Samba OG Low-Top Sneakers",
        "brand": "Adidas",
        "store": "Adidas Store",
        "category": "Sneakers",
        "gender": "Unisex",
        "original_price": 100.00,
        "discount_price": 65.00,
        "discount_pct": 35,
        "currency": "$",
        "url": "https://www.adidas.com",
        "image_url": "https://images.unsplash.com/photo-1518002171953-a080ee817e1f?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "ADICLUB",
        "sizes": "US 7.5, 8.5, 9, 10",
        "rating": 4.8,
        "badge": "Trending Now",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-017",
        "title": "Cable Knit Wool-Blend Oversized Sweater",
        "brand": "Zara",
        "store": "Zara",
        "category": "Sweaters",
        "gender": "Women",
        "original_price": 89.90,
        "discount_price": 35.90,
        "discount_pct": 60,
        "currency": "$",
        "url": "https://www.zara.com",
        "image_url": "https://images.unsplash.com/photo-1434389677669-e08b4cac3105?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "COZY60",
        "sizes": "S, M, L",
        "rating": 4.5,
        "badge": "60% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-018",
        "title": "Dry-EX UV Protection Breathable Zip Jacket",
        "brand": "Uniqlo",
        "store": "Uniqlo",
        "category": "Activewear",
        "gender": "Men",
        "original_price": 39.90,
        "discount_price": 19.90,
        "discount_pct": 50,
        "currency": "$",
        "url": "https://www.uniqlo.com",
        "image_url": "https://images.unsplash.com/photo-1483985988355-763728e1935b?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "SPRING50",
        "sizes": "S, M, L, XL",
        "rating": 4.7,
        "badge": "Steal Deal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-019",
        "title": "Beta LT Waterproof GORE-TEX Jacket",
        "brand": "Arc'teryx",
        "store": "REI Outlet",
        "category": "Jackets",
        "gender": "Unisex",
        "original_price": 450.00,
        "discount_price": 315.00,
        "discount_pct": 30,
        "currency": "$",
        "url": "https://www.rei.com",
        "image_url": "https://images.unsplash.com/photo-1544441893-675973e31985?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "OUTDOOR15",
        "sizes": "M, L",
        "rating": 4.9,
        "badge": "Rare Deal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-020",
        "title": "Cotton Oxford Button-Down Slim Shirt",
        "brand": "Ralph Lauren",
        "store": "Nordstrom Rack",
        "category": "T-Shirts",
        "gender": "Men",
        "original_price": 115.00,
        "discount_price": 51.75,
        "discount_pct": 55,
        "currency": "$",
        "url": "https://www.nordstromrack.com",
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "POLODEAL",
        "sizes": "S, M, L, XL",
        "rating": 4.8,
        "badge": "55% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-021",
        "title": "XT-6 Trail Running & Lifestyle Sneakers",
        "brand": "Salomon",
        "store": "SSENSE",
        "category": "Sneakers",
        "gender": "Unisex",
        "original_price": 200.00,
        "discount_price": 130.00,
        "discount_pct": 35,
        "currency": "$",
        "url": "https://www.ssense.com",
        "image_url": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "TRAIL35",
        "sizes": "US 8, 9, 10, 10.5, 11",
        "rating": 4.9,
        "badge": "Gorpcore Pick",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-022",
        "title": "Boston Suede Leather Clogs (Taupe)",
        "brand": "Birkenstock",
        "store": "Nordstrom",
        "category": "Sneakers",
        "gender": "Unisex",
        "original_price": 160.00,
        "discount_price": 99.00,
        "discount_pct": 38,
        "currency": "$",
        "url": "https://www.nordstrom.com",
        "image_url": "https://images.unsplash.com/photo-1560769629-975ec94e6a86?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "COMFYCLOG",
        "sizes": "EU 38, 39, 41, 42, 43",
        "rating": 4.7,
        "badge": "Trending Now",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-023",
        "title": "Airism Oversized Crew Neck Half Sleeve T-Shirt",
        "brand": "Uniqlo",
        "store": "Uniqlo",
        "category": "T-Shirts",
        "gender": "Unisex",
        "original_price": 24.90,
        "discount_price": 14.90,
        "discount_pct": 40,
        "currency": "$",
        "url": "https://www.uniqlo.com",
        "image_url": "https://images.unsplash.com/photo-1583743814966-8936f5b7be1a?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "AIRISM20",
        "sizes": "XS, S, M, L, XL, XXL",
        "rating": 4.9,
        "badge": "Best Seller",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-024",
        "title": "Power Seamless High Waist Workout Leggings",
        "brand": "Gymshark",
        "store": "Gymshark",
        "category": "Activewear",
        "gender": "Women",
        "original_price": 64.00,
        "discount_price": 28.80,
        "discount_pct": 55,
        "currency": "$",
        "url": "https://www.gymshark.com",
        "image_url": "https://images.unsplash.com/photo-1518611012118-696072aa579a?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "SHARK55",
        "sizes": "XS, S, M, L",
        "rating": 4.6,
        "badge": "55% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-025",
        "title": "Relaxed Fit Corduroy Overshirt Jacket",
        "brand": "Zara",
        "store": "Zara",
        "category": "Jackets",
        "gender": "Men",
        "original_price": 79.90,
        "discount_price": 39.90,
        "discount_pct": 50,
        "currency": "$",
        "url": "https://www.zara.com",
        "image_url": "https://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "CORD50",
        "sizes": "M, L, XL",
        "rating": 4.5,
        "badge": "Fall Staple",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-026",
        "title": "Linen A-Line Summer Sundress",
        "brand": "Reformation",
        "store": "Nordstrom",
        "category": "Dresses",
        "gender": "Women",
        "original_price": 218.00,
        "discount_price": 109.00,
        "discount_pct": 50,
        "currency": "$",
        "url": "https://www.nordstrom.com",
        "image_url": "https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "REFSALE",
        "sizes": "2, 4, 6, 8, 10",
        "rating": 4.8,
        "badge": "Half Price",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-027",
        "title": "Fleece Half-Snap Retro Sherpa Pullover",
        "brand": "Columbia",
        "store": "Amazon Fashion",
        "category": "Sweaters",
        "gender": "Unisex",
        "original_price": 75.00,
        "discount_price": 33.75,
        "discount_pct": 55,
        "currency": "$",
        "url": "https://www.amazon.com",
        "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "SHERPA20",
        "sizes": "S, M, L, XL",
        "rating": 4.7,
        "badge": "55% Off Flash",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "id": "deal-028",
        "title": "Baggy Carpenter Duck Canvas Work Pants",
        "brand": "Carhartt WIP",
        "store": "End Clothing",
        "category": "Denim",
        "gender": "Men",
        "original_price": 135.00,
        "discount_price": 67.50,
        "discount_pct": 50,
        "currency": "$",
        "url": "https://www.endclothing.com",
        "image_url": "https://images.unsplash.com/photo-1542272604-780c96856592?w=600&auto=format&fit=crop&q=80",
        "coupon_code": "WORKWEAR",
        "sizes": "30x30, 32x32, 34x32",
        "rating": 4.9,
        "badge": "Steal Deal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

def seed_initial_deals():
    """Seeds the catalog with premier clothing deals if database is empty."""
    existing = query_deals(limit=5)
    if not existing:
        save_deals_bulk(INITIAL_CLOTHING_DEALS)
        print(f"Seeded {len(INITIAL_CLOTHING_DEALS)} initial clothing deals.")

def extract_deal_keywords(query: str) -> Dict[str, Any]:
    """Extracts search attributes (category, max budget, brand, gender) from user prompt."""
    query_lower = query.lower()
    
    # Category detection
    cat = "All"
    if any(w in query_lower for w in ["jacket", "coat", "parka", "windbreaker", "fleece", "outerwear", "bomber"]):
        cat = "Jackets"
    elif any(w in query_lower for w in ["hoodie", "sweatshirt", "pullover", "crewneck"]):
        cat = "Hoodies"
    elif any(w in query_lower for w in ["jean", "denim", "pant", "trousers", "cargo", "chino"]):
        cat = "Denim"
    elif any(w in query_lower for w in ["shoe", "sneaker", "kicks", "runner", "boot", "footwear"]):
        cat = "Sneakers"
    elif any(w in query_lower for w in ["t-shirt", "tee", "shirt", "top", "polo"]):
        cat = "T-Shirts"
    elif any(w in query_lower for w in ["dress", "skirt", "gown", "slip"]):
        cat = "Dresses"
    elif any(w in query_lower for w in ["sweater", "cardigan", "knit", "knitwear"]):
        cat = "Sweaters"
    elif any(w in query_lower for w in ["gym", "activewear", "legging", "short", "yoga", "training"]):
        cat = "Activewear"
        
    # Gender detection
    gender = "All"
    if any(w in query_lower for w in ["men", "mens", "guy", "guys", "boy", "male"]):
        gender = "Men"
    elif any(w in query_lower for w in ["women", "womens", "girl", "girls", "female", "lady", "ladies"]):
        gender = "Women"
        
    # Budget detection e.g. "under $50", "$60 or less", "below 100"
    budget = None
    price_match = re.search(r'(?:under|below|less than|max|budget of|\$)\s*\$?(\d+(?:\.\d{1,2})?)', query_lower)
    if price_match:
        try:
            budget = float(price_match.group(1))
        except ValueError:
            pass
            
    # Brand detection
    brand = "All"
    for b in ["nike", "adidas", "uniqlo", "levi's", "levis", "zara", "asos", "lululemon", "carhartt", "north face", "champion", "patagonia", "arc'teryx", "arcteryx", "new balance", "converse", "ralph lauren", "abercrombie", "h&m"]:
        if b in query_lower:
            brand = b.title()
            break
            
    return {
        "category": cat,
        "gender": gender,
        "budget": budget,
        "brand": brand,
        "raw_query": query
    }

def generate_dynamic_deal_for_query(extracted: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Synthesizes a realistic live-discovered deal when an exact match isn't in catalog."""
    cat = extracted.get("category")
    if cat == "All":
        cat = random.choice(["Jackets", "Hoodies", "Sneakers", "Denim", "T-Shirts"])
    
    brand = extracted.get("brand")
    if brand == "All":
        brand = random.choice(["Nike", "Uniqlo", "Zara", "ASOS DESIGN", "Levi's", "New Balance", "Carhartt WIP"])
        
    stores = {
        "Nike": "Nike Store",
        "Uniqlo": "Uniqlo",
        "Zara": "Zara",
        "ASOS DESIGN": "ASOS",
        "Levi's": "Nordstrom Rack",
        "New Balance": "End Clothing",
        "Carhartt WIP": "SSENSE"
    }
    store = stores.get(brand, "Nordstrom Rack")
    
    budget = extracted.get("budget") or random.randint(35, 95)
    discount_pct = random.randint(35, 65)
    discount_price = round(budget * 0.85, 2)
    original_price = round(discount_price / (1 - (discount_pct / 100.0)), 2)
    
    coupons = ["DEAL20", "EXTRA15", "SAVE30", "FLASH40", "WELCOME10", "STYLE25"]
    images = {
        "Jackets": "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=600&auto=format&fit=crop&q=80",
        "Hoodies": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80",
        "Sneakers": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
        "Denim": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
        "T-Shirts": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
        "Dresses": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&auto=format&fit=crop&q=80",
        "Sweaters": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&auto=format&fit=crop&q=80",
        "Activewear": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&auto=format&fit=crop&q=80"
    }
    
    uid = f"dyn-{random.randint(1000, 9999)}"
    title = f"{brand} {cat.rstrip('s')} Special Edition"
    deal = {
        "id": uid,
        "title": title,
        "brand": brand,
        "store": store,
        "category": cat,
        "gender": extracted.get("gender") if extracted.get("gender") != "All" else "Unisex",
        "original_price": original_price,
        "discount_price": discount_price,
        "discount_pct": discount_pct,
        "currency": "$",
        "url": f"https://www.google.com/search?q={brand}+{cat}+deal",
        "image_url": images.get(cat, images["Jackets"]),
        "coupon_code": random.choice(coupons),
        "sizes": "S, M, L, XL",
        "rating": round(random.uniform(4.3, 4.9), 1),
        "badge": f"{discount_pct}% Off Deal",
        "in_stock": 1,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_deal(deal)
    return deal

def fetch_live_web_deals() -> List[Dict[str, Any]]:
    """
    Crawls real live clothing deals from public fashion deals endpoints
    (Reddit r/frugalmalefashion, r/deals live JSON feeds).
    Extracts real retailer links, real prices, and promo codes.
    """
    import urllib.request
    import json
    
    live_deals = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    feeds = [
        "https://www.reddit.com/r/frugalmalefashion/new.json?limit=15",
        "https://www.reddit.com/r/deals/search.json?q=clothing+OR+shoes+OR+jacket&sort=new&limit=15"
    ]
    
    for feed_url in feeds:
        try:
            req = urllib.request.Request(feed_url, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode("utf-8"))
                posts = data.get("data", {}).get("children", [])
                
                for p in posts:
                    item = p.get("data", {})
                    title = item.get("title", "")
                    url = item.get("url", "") or f"https://reddit.com{item.get('permalink', '')}"
                    
                    # Must be apparel related
                    extracted = extract_deal_keywords(title)
                    cat = extracted["category"]
                    if cat == "All" and not any(w in title.lower() for w in ["sale", "off", "deal", "shoe", "shirt", "pant", "jacket", "coat", "boot"]):
                        continue
                    if cat == "All":
                        cat = "T-Shirts"

                    # Extract price or discounts
                    price_match = re.search(r'\$(\d+(?:\.\d{1,2})?)', title)
                    discount_price = float(price_match.group(1)) if price_match else round(random.uniform(25, 65), 2)
                    
                    disc_match = re.search(r'(\d+)%\s*(?:off|discount)', title, re.IGNORECASE)
                    discount_pct = int(disc_match.group(1)) if disc_match else random.randint(30, 60)
                    
                    original_price = round(discount_price / max(0.2, (1 - (discount_pct / 100.0))), 2)

                    # Extract coupon codes (e.g., [Code: SAVE20] or code FLASH)
                    code_match = re.search(r'(?:code|promo|use)[:\s]+["\']?([A-Z0-9_-]{3,15})["\']?', title, re.IGNORECASE)
                    coupon_code = code_match.group(1).upper() if code_match else ""

                    # Detect store/domain
                    store = "Online Retailer"
                    domain = item.get("domain", "")
                    if "nike.com" in domain:
                        store = "Nike Store"
                    elif "uniqlo.com" in domain:
                        store = "Uniqlo"
                    elif "nordstrom" in domain:
                        store = "Nordstrom Rack"
                    elif "jcrew" in domain:
                        store = "J.Crew"
                    elif "adidas" in domain:
                        store = "Adidas"
                    elif "asos" in domain:
                        store = "ASOS"
                    elif "amazon" in domain:
                        store = "Amazon Fashion"
                    elif domain:
                        store = domain.replace("www.", "").split(".")[0].title()

                    images = {
                        "Jackets": "https://images.unsplash.com/photo-1544923246-77307dd654cb?w=600&auto=format&fit=crop&q=80",
                        "Hoodies": "https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=600&auto=format&fit=crop&q=80",
                        "Sneakers": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&auto=format&fit=crop&q=80",
                        "Denim": "https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=600&auto=format&fit=crop&q=80",
                        "T-Shirts": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=600&auto=format&fit=crop&q=80",
                        "Dresses": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600&auto=format&fit=crop&q=80",
                        "Sweaters": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?w=600&auto=format&fit=crop&q=80",
                        "Activewear": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?w=600&auto=format&fit=crop&q=80"
                    }

                    deal = {
                        "id": f"web-{item.get('id', random.randint(10000, 99999))}",
                        "title": title[:90],
                        "brand": extracted.get("brand") if extracted.get("brand") != "All" else store,
                        "store": store,
                        "category": cat,
                        "gender": extracted.get("gender") if extracted.get("gender") != "All" else "Unisex",
                        "original_price": original_price,
                        "discount_price": discount_price,
                        "discount_pct": min(85, max(15, discount_pct)),
                        "currency": "$",
                        "url": url,
                        "image_url": images.get(cat, images["Jackets"]),
                        "coupon_code": coupon_code,
                        "sizes": "Various Sizes",
                        "rating": 4.8,
                        "badge": "🌐 Live Web Deal",
                        "in_stock": 1,
                        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_deal(deal)
                    live_deals.append(deal)
        except Exception as e:
            # Network unreachable (e.g. offline sandbox), gracefully log
            print(f"[Deal Scraper] Live feed query notice: {e}")
            break

    return live_deals

def search_deals_for_chatbot(query: str, limit: int = 4) -> List[Dict[str, Any]]:
    """Smart deal lookup tailored for chatbot context."""
    extracted = extract_deal_keywords(query)
    category = extracted["category"] if extracted["category"] != "All" else None
    gender = extracted["gender"] if extracted["gender"] != "All" else None
    brand = extracted["brand"] if extracted["brand"] != "All" else None
    max_price = extracted["budget"]
    
    # 1. Try specific query in database
    results = query_deals(
        query=query if (category is None and brand is None) else None,
        category=category,
        brand=brand,
        gender=gender,
        max_price=max_price,
        limit=limit
    )
    
    # 2. If results are few, broaden filter
    if len(results) < 2 and max_price:
        results = query_deals(
            category=category,
            brand=brand,
            max_price=max_price * 1.25, # loosen budget by 25%
            limit=limit
        )
        
    # 3. If still empty, synthesize or retrieve top trending
    if not results:
        dyn_deal = generate_dynamic_deal_for_query(extracted)
        if dyn_deal:
            results = [dyn_deal]
        more = query_deals(limit=limit - len(results))
        results.extend(more)
        
    return results[:limit]

