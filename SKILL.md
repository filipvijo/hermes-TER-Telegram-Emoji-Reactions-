# Telegram Emoji Reactions (TER) — Hermes Skill

Adds emoji reaction auto-responses to the Hermes Telegram gateway.

## What It Does

When a user reacts to a Hermes message with an emoji, the bot responds automatically:

- 👍 🔥 → Context-relevant GIF from Giphy (Kimi K2.6 generates the search query)
- 🤔 ❤️ 🤯 😈 🫡 → Personality-driven text response via Kimi K2.6

## Implementation

- Hooks into existing polling loop — no competing pollers, avoids 409 conflicts
- Async via asyncio.to_thread() — non-blocking gateway event loop
- Kimi K2.6 reasoning chain cleanup to prevent prompt leaks
- Feature-toggled via TELEGRAM_REACTIONS=true in ~/.hermes/.env
- Reactions only trigger on Hermes' own messages (in-memory cache)

## Setup

Add to ~/.hermes/.env:
TELEGRAM_REACTIONS=true
GIPHY_API_KEY=your_key
OPENROUTER_API_KEY=your_key

## Files Modified
- gateway/platforms/telegram.py — reaction handler integrated
- tools/telegram_reaction_tool.py — Kimi K2.6 response generator
