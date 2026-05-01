# Telegram Emoji Reactions (TER)
### A Hermes Agent Hackathon Submission

![Hermes Agent](https://img.shields.io/badge/Hermes-Agent-blue)
![Kimi K2.6](https://img.shields.io/badge/Kimi-K2.6-orange)
![License](https://img.shields.io/badge/license-MIT-green)

Adds emoji reaction auto-responses to the Hermes Telegram gateway.
Built for the NousResearch x Kimi Creative Hackathon 2025.

## Demo
[Watch the demo →]https://x.com/TeslianHumanoid/status/2049766087458164919?s=20

## What It Does

React to any Hermes message with an emoji → get a contextual AI response:

| Emoji | Type | Behavior |
|-------|------|----------|
| 👍 | GIF | Celebratory, approving GIF via Giphy |
| 🔥 | GIF | High-energy, intense GIF via Giphy |
| 🤔 | Text | Analytical, philosophical reply (max 300 chars) |
| ❤️ | Text | Poetic, emotional reply (max 150 chars) |
| 🤯 | Text | Mind-blowing, revelatory reply (max 200 chars) |
| 😈 | Text | Witty, mischievous reply (max 100 chars) |
| 🫡 | Text | Formal, respectful reply (max 150 chars) |

GIF triggers: Kimi K2.6 generates a 3-5 word Giphy search query based on the original message + emoji personality.

## Technical Highlights

- Hooks into existing polling loop — no competing pollers, avoids 409 conflicts
- Async via asyncio.to_thread() — non-blocking gateway event loop
- Kimi K2.6 reasoning chain cleanup to prevent prompt leaks
- Feature-toggled via TELEGRAM_REACTIONS=true
- Reactions only trigger on Hermes' own messages (in-memory cache)

## Setup

Add to ~/.hermes/.env:

TELEGRAM_REACTIONS=true
GIPHY_API_KEY=your_key
OPENROUTER_API_KEY=your_key

See SKILL.md for full implementation guide.

## Built With

- [Hermes Agent](https://github.com/nousresearch/hermes-agent) — NousResearch
- [Kimi K2.6](https://platform.moonshot.ai) — via OpenRouter
- [Giphy API](https://developers.giphy.com)

## License
MIT
