import time
import requests
import json
from typing import List, Dict, Any, Optional, Tuple
from app.config import config
from app.database import log_model_switch, log_search

SYSTEM_PROMPT = """You are "ThreadHunter AI" — a smart, stylish, and deal-obsessed personal shopping assistant.
Your goal is to help users find the best clothing deals, sales, discounts, and outfit combinations.
Guidelines:
1. Be enthusiastic, fashion-savvy, and transparent about prices and savings.
2. Highlight specific discounts, price drops, and promo codes from the provided deal catalog.
3. Offer quick styling or fit advice (e.g., boxy fit, breathable fabric, layering tips).
4. Keep answers concise, visually clean with markdown bullet points, bolded prices, and deal highlights.
5. If deals are provided in context, reference them naturally with store names, original vs sale prices, and savings.
"""

class GeminiAIService:
    def __init__(self):
        self.fallback_chain = list(config.MODEL_FALLBACK_CHAIN)
        self.current_model_index = 0
        self.current_key_index = 0
        self.total_switches_session = 0

    @property
    def current_model(self) -> str:
        if 0 <= self.current_model_index < len(self.fallback_chain):
            return self.fallback_chain[self.current_model_index]
        return self.fallback_chain[0]

    def set_active_model(self, model_name: str) -> bool:
        if model_name in self.fallback_chain:
            prev = self.current_model
            self.current_model_index = self.fallback_chain.index(model_name)
            log_model_switch(prev, model_name, "Manual user override in dashboard", success=True)
            return True
        return False

    def get_api_key(self) -> Optional[str]:
        keys = config.get_api_keys()
        if not keys:
            return None
        self.current_key_index = self.current_key_index % len(keys)
        return keys[self.current_key_index]

    def _rotate_key_or_model(self, reason: str) -> Tuple[str, str, bool]:
        """
        Advances to next API key or next model in fallback hierarchy.
        Returns (previous_model, new_model, switched_model_bool)
        """
        keys = config.get_api_keys()
        prev_model = self.current_model
        
        # If multiple keys exist, try rotating key first
        if len(keys) > 1 and self.current_key_index + 1 < len(keys):
            self.current_key_index += 1
            masked_key = f"...{keys[self.current_key_index][-4:]}" if len(keys[self.current_key_index]) > 4 else "key"
            log_model_switch(prev_model, prev_model, f"{reason} -> Rotated to next API key ({masked_key})", success=True)
            self.total_switches_session += 1
            return prev_model, prev_model, False

        # Otherwise advance to next model in fallback chain
        self.current_key_index = 0
        self.current_model_index = (self.current_model_index + 1) % len(self.fallback_chain)
        new_model = self.current_model
        
        masked_key = ""
        active_key = self.get_api_key()
        if active_key and len(active_key) > 4:
            masked_key = f"...{active_key[-4:]}"
            
        log_model_switch(prev_model, new_model, reason, api_key_masked=masked_key, success=True)
        self.total_switches_session += 1
        return prev_model, new_model, True

    def simulate_rate_limit_switch(self) -> Dict[str, Any]:
        """Manually trigger a simulated 429 rate-limit fallback for demo & testing."""
        prev, new_model, is_new = self._rotate_key_or_model("Simulated HTTP 429 Rate Limit (Free Tier Quota Exceeded)")
        return {
            "status": "success",
            "from_model": prev,
            "to_model": new_model,
            "reason": "Simulated HTTP 429 Rate Limit",
            "message": f"Successfully triggered fallback switch from '{prev}' to '{new_model}'"
        }

    def generate_chat_response(
        self,
        user_message: str,
        matching_deals: List[Dict[str, Any]],
        preferred_model: Optional[str] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        
        if preferred_model and preferred_model in self.fallback_chain:
            self.current_model_index = self.fallback_chain.index(preferred_model)
            
        keys = config.get_api_keys()
        
        # Format deal catalog context for the AI
        deals_context = "CURRENT LIVE CLOTHING DEALS FOUND:\n"
        for i, d in enumerate(matching_deals, 1):
            deals_context += (
                f"{i}. [{d['brand']}] {d['title']} | Store: {d['store']} | "
                f"Now: {d['currency']}{d['discount_price']} (Was {d['currency']}{d['original_price']}, -{d['discount_pct']}%) | "
                f"Coupon: {d.get('coupon_code') or 'None'} | Rating: {d.get('rating', 4.5)}/5 | "
                f"Badge: {d.get('badge', '')}\n"
            )

        full_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"{deals_context}\n"
            f"USER QUERY: {user_message}\n\n"
            f"Provide a helpful, stylish recommendation referencing these deals, coupons, and tips:"
        )

        # If no API key configured, use intelligent local heuristic response
        if not keys:
            latency_ms = int((time.time() - start_time) * 1000)
            reply = self._build_heuristic_response(user_message, matching_deals, has_key=False)
            log_search(user_message, "Local Heuristic Engine", latency_ms, len(matching_deals))
            return {
                "reply": reply,
                "deals": matching_deals,
                "model_used": "Local Stylist Heuristic (Add Gemini API key in Settings)",
                "fallback_triggered": False,
                "fallback_details": None,
                "latency_ms": latency_ms
            }

        # Attempt API calls with fallback loop across models
        attempts = 0
        max_attempts = len(self.fallback_chain)
        fallback_details = []
        fallback_triggered = False

        while attempts < max_attempts:
            active_model = self.current_model
            api_key = self.get_api_key()
            endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{active_model}:generateContent?key={api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": full_prompt}
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 900
                }
            }

            try:
                resp = requests.post(
                    endpoint,
                    headers={"Content-Type": "application/json"},
                    json=payload,
                    timeout=12
                )
                
                # Check for Rate Limit (429) or Overloaded (503)
                if resp.status_code in (429, 503):
                    fallback_triggered = True
                    error_msg = f"HTTP {resp.status_code} ({resp.json().get('error', {}).get('message', 'Rate Limit Exceeded')[:60]})"
                    prev_m, next_m, _ = self._rotate_key_or_model(f"Rate Limit: {error_msg}")
                    fallback_details.append(f"Model '{prev_m}' hit rate limit -> switched to '{next_m}'")
                    attempts += 1
                    continue
                
                # If invalid key or other 400 client error
                if resp.status_code == 400:
                    err_text = resp.text
                    if "API_KEY_INVALID" in err_text or "not found" in err_text:
                        # Fallback to local heuristic
                        latency_ms = int((time.time() - start_time) * 1000)
                        reply = self._build_heuristic_response(user_message, matching_deals, has_key=True, error="API Key Invalid or Model Unavailable")
                        return {
                            "reply": reply,
                            "deals": matching_deals,
                            "model_used": f"{active_model} (Fallback)",
                            "fallback_triggered": True,
                            "fallback_details": "API Key returned 400 error. Switched to Heuristic Engine.",
                            "latency_ms": latency_ms
                        }

                resp.raise_for_status()
                data = resp.json()
                
                # Extract response text
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    reply_text = "".join([p.get("text", "") for p in parts]).strip()
                    latency_ms = int((time.time() - start_time) * 1000)
                    log_search(user_message, active_model, latency_ms, len(matching_deals))
                    return {
                        "reply": reply_text,
                        "deals": matching_deals,
                        "model_used": active_model,
                        "fallback_triggered": fallback_triggered,
                        "fallback_details": " | ".join(fallback_details) if fallback_details else None,
                        "latency_ms": latency_ms
                    }
                else:
                    raise Exception("No content returned in candidates")

            except (requests.exceptions.RequestException, Exception) as exc:
                fallback_triggered = True
                prev_m, next_m, _ = self._rotate_key_or_model(f"Network / API Error: {str(exc)[:60]}")
                fallback_details.append(f"Switched from '{prev_m}' to '{next_m}' due to connection issue")
                attempts += 1

        # If all API attempts fail or are rate-limited, fallback gracefully to Local Heuristic Engine
        latency_ms = int((time.time() - start_time) * 1000)
        reply = self._build_heuristic_response(user_message, matching_deals, has_key=True, rate_limited=True)
        return {
            "reply": reply,
            "deals": matching_deals,
            "model_used": "Local Stylist Heuristic (All Gemini models rate-limited)",
            "fallback_triggered": True,
            "fallback_details": "All Gemini models hit free rate limits. Gracefully fell back to local fashion engine.",
            "latency_ms": latency_ms
        }

    def _build_heuristic_response(
        self,
        query: str,
        deals: List[Dict[str, Any]],
        has_key: bool = True,
        rate_limited: bool = False,
        error: Optional[str] = None
    ) -> str:
        """High quality, responsive offline/fallback generator."""
        intro = "Hey there! I scoured the web and our live deal catalog for you. Here are the hottest clothing bargains that match your vibe:"
        if rate_limited:
            intro = "⚠️ **Rate Limit Handled!** All Gemini free-tier endpoints hit requests-per-minute quotas. I automatically switched into **High-Speed Stylist Mode** so your deal hunt isn't interrupted!"
        elif not has_key:
            intro = "👋 Welcome to **ThreadHunter**! I've loaded the best live clothing deals below. *(Tip: Add your free Gemini API key in the Settings tab to unlock full conversational AI styling!)*"

        lines = [intro, ""]
        if deals:
            best = deals[0]
            lines.append(f"### 🏆 Top Pick: **{best['title']}** ({best['brand']})")
            lines.append(f"- **Sale Price:** **${best['discount_price']}** ~~(Original: ${best['original_price']})~~ **[{best['discount_pct']}% OFF]**")
            lines.append(f"- **Store:** {best['store']}")
            if best.get("coupon_code"):
                lines.append(f"- **Promo Code:** Use `{best['coupon_code']}` at checkout for extra savings!")
            if best.get("badge"):
                lines.append(f"- **Deal Status:** 🔥 {best['badge']}")
            lines.append("")

            if len(deals) > 1:
                lines.append("### ✨ More Great Steals:")
                for d in deals[1:]:
                    code_str = f" | Code: `{d['coupon_code']}`" if d.get("coupon_code") else ""
                    lines.append(f"- **{d['title']}** ({d['brand']}) — **${d['discount_price']}** (-{d['discount_pct']}%){code_str} at *{d['store']}*")
                lines.append("")

            lines.append("💡 **Stylist Tip:** Always check your size in the deal cards below and click **'Track Deal'** to monitor further price cuts in your dashboard!")
        else:
            lines.append("I couldn't find an exact match under those exact filters, but check out the trending deals in the explorer tab or adjust your budget range!")

        return "\n".join(lines)

ai_service = GeminiAIService()
