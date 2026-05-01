"""Reaction response generator. Pure functions — no polling."""
import logging
import os
import re
from typing import Optional
import requests

logger = logging.getLogger(__name__)

def _load_env(key: str) -> Optional[str]:
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.getenv(key)

GIPHY_API_KEY = _load_env("GIPHY_API_KEY")
OPENROUTER_API_KEY = _load_env("OPENROUTER_API_KEY")

SUPPORTED_REACTIONS = ["👍", "🔥", "🤔", "❤️", "🤯", "😈", "🫡"]

def _search_gif(query: str) -> Optional[str]:
    if not GIPHY_API_KEY:
        return None
    try:
        resp = requests.get(
            "https://api.giphy.com/v1/gifs/search",
            params={"api_key": GIPHY_API_KEY, "q": query, "limit": 1, "rating": "pg-13"},
            timeout=10,
        )
        resp.raise_for_status()
        gifs = resp.json().get("data", [])
        if gifs:
            mp4 = gifs[0].get("images", {}).get("fixed_height", {}).get("mp4")
            return mp4 or gifs[0].get("images", {}).get("fixed_height", {}).get("url")
    except Exception as exc:
        logger.debug("GIF search failed: %s", exc)
    return None

def _call_llm(prompt: str, max_tokens: int = 200) -> str:
    """Generate text via OpenRouter (Kimi K2.6) and clean reasoning-model output.

    CRITICAL: Always run _clean_reasoning() on the output before returning.
    Never send raw reasoning chains to Telegram — they leak the prompt.
    """
    if not OPENROUTER_API_KEY:
        return "🤖"
    try:
        resp = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "moonshotai/kimi-k2.6",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": 0.8,
                "reasoning": {"enabled": False},
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("choices"):
            msg = data["choices"][0].get("message", {})
            content = msg.get("content")
            if content and content.strip():
                return _clean_reasoning(content.strip())
            reasoning = msg.get("reasoning", "")
            if reasoning:
                cleaned = re.sub(r"<think>.*?</think>", "", reasoning, flags=re.DOTALL).strip()
                return _clean_reasoning(cleaned) or "🤖"
            return "🤖"
    except Exception as exc:
        logger.debug("LLM call failed: %s", exc)
    return "🤖"


def _clean_reasoning(text: str) -> str:
    """Strip reasoning-model meta-commentary from K2.6 output."""
    if not text:
        return text

    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()

    lines = text.splitlines()
    result = []
    started = False

    META_PREFIXES = (
        "The user ", "I need ", "I should ", "I will ", "I must ",
        "I have ", "I want ", "Let me ", "Okay, ", "Alright, ",
        "The tone should be", "I need to", "The user wants",
        "Let me analyze", "Marked with", "I have to", "I want to",
        "Let me think", "Let me consider", "Let me craft", "Let me write",
        "First,", "Next,", "Finally,", "So,", "Now,",
        "Hmm,", "Well,", "Wait,", "Actually,",
        "I need to make sure", "I need to ensure",
        "The user reacted", "The user sent", "The user said",
        "React with", "Write a unique", "No meta-commentary",
        "Only the raw", "Output ONLY", "No punctuation",
        "No quotes", "No explanations",
    )

    META_SUBSTRINGS = (
        "wants me to", "I need to", "The user wants",
        "The tone should be", "Let me analyze", "Marked with",
        "I should write", "I will write", "I must write",
        "need to make sure", "need to ensure",
        "user wants me", "user reacted with", "user sent",
    )

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if not started:
            if stripped.startswith(META_PREFIXES):
                continue
            if any(sub in stripped for sub in META_SUBSTRINGS):
                continue
            if stripped.startswith("(") and stripped.endswith(")"):
                continue
            started = True
        if started:
            if stripped.startswith(META_PREFIXES) and len(stripped) < 80:
                continue
            for prefix in META_PREFIXES:
                if stripped.lower().startswith(prefix.lower()):
                    stripped = stripped[len(prefix):].strip()
                    stripped = stripped.lstrip(":-–— ").strip()
                    break
            result.append(stripped)

    cleaned = " ".join(result)

    inline_patterns = [
        r"(?i)the tone should be[^:]*:\s*",
        r"(?i)I need to[^:]*:\s*",
        r"(?i)the user wants[^:]*:\s*",
        r"(?i)let me analyze[^:]*:\s*",
        r"(?i)marked with[^:]*:\s*",
        r"(?i)so,\s*", r"(?i)now,\s*", r"(?i)okay,\s*", r"(?i)alright,\s*",
        r"(?i)here(?:'s| is)\s+(?:the\s+|my\s+|a\s+)?(response|answer|reaction)[^\w]*\s*",
    ]
    for pat in inline_patterns:
        cleaned = re.sub(pat, "", cleaned)

    cleaned = cleaned.strip()

    if not cleaned and text:
        sentences = re.split(r"(?<=[.!?])\s+", text)

        def _strip_sentence(s: str) -> str:
            s = s.strip()
            for prefix in META_PREFIXES:
                if s.lower().startswith(prefix.lower()):
                    s = s[len(prefix):].strip()
                    s = s.lstrip(":-–— ").strip()
                    break
            for pat in inline_patterns:
                s = re.sub(pat, "", s)
            return s.strip()

        for s in reversed(sentences):
            stripped = _strip_sentence(s)
            if stripped and len(stripped.split()) >= 1:
                if any(stripped.lower().startswith(p.lower()) for p in META_PREFIXES):
                    continue
                if any(sub in stripped for sub in META_SUBSTRINGS):
                    continue
                cleaned = stripped
                break

        if not cleaned and sentences:
            for s in reversed(sentences):
                stripped = _strip_sentence(s)
                if stripped and len(stripped.split()) >= 1:
                    cleaned = stripped
                    break

    return cleaned[:500] if cleaned else ""


def _generate_response(original_text: str, emoji: str) -> dict:
    """Generate a contextual response. NEVER send the prompt to Telegram."""
    emoji_config = {
        "👍": {"mode": "gif", "personality": "celebratory, approving, positive, uplifting"},
        "🔥": {"mode": "gif", "personality": "hype, epic, exciting, energetic, intense"},
        "🤔": {"mode": "text", "personality": "thoughtful, analytical, deep-thinking, philosophical", "max_chars": 300},
        "❤️": {"mode": "text", "personality": "poetic, emotional, warm, heartfelt, genuine", "max_chars": 150},
        "🤯": {"mode": "text", "personality": "mind-blown, surprising, paradigm-shifting, revelatory", "max_chars": 200},
        "😈": {"mode": "text", "personality": "mischievous, dark humor, witty, slightly evil but not offensive", "max_chars": 100},
        "🫡": {"mode": "text", "personality": "respectful, military-style, disciplined, formal acknowledgment, precise", "max_chars": 150},
    }

    config = emoji_config.get(emoji)
    if not config:
        config = {"mode": "text", "personality": "acknowledging, responsive, brief", "max_chars": 100}

    mode = config["mode"]
    personality = config["personality"]
    max_chars = config.get("max_chars", 200)

    if mode == "gif":
        query_prompt = (
            f"Write a 3-5 word Giphy search query for a {personality} "
            f"reaction ({emoji}) to this message: '{original_text[:300]}'. "
            f"Output ONLY the raw query words. No punctuation, no quotes, no explanations."
        )
        raw = _call_llm(query_prompt, max_tokens=30)
        query = _clean_reasoning(raw)
        query = "".join(c for c in query if c.isalnum() or c in " -_").strip()
        if not query:
            query = f"{emoji} reaction"
        gif_url = _search_gif(query)
        return {"type": "animation", "url": gif_url, "text": None}
    else:
        text_prompt = (
            f"React with {emoji} ({personality}). "
            f"Write a unique response (max {max_chars} chars) to: '{original_text[:500]}'. "
            f"No meta-commentary. Only the raw response text."
        )
        raw = _call_llm(text_prompt, max_tokens=max_chars)
        text = _clean_reasoning(raw)
        return {"type": "text", "url": None, "text": text}
