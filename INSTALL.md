# Installation Guide

## Prerequisites
- [Hermes Agent](https://github.com/nousresearch/hermes-agent) installed
- Python 3.10+
- Telegram bot token
- Giphy API key
- OpenRouter API key

## Steps

### 1. Copy the reaction tool
```bash
cp telegram_reaction_tool.py ~/.hermes/hermes-agent/tools/
```

### 2. Apply the gateway patch
```bash
cd ~/.hermes/hermes-agent
git apply gateway_reaction_handler.patch
```

### 3. Set environment variables
Add to `~/.hermes/.env`:
```
TELEGRAM_REACTIONS=true
GIPHY_API_KEY=your_giphy_key
OPENROUTER_API_KEY=your_openrouter_key
```

### 4. Restart the gateway
```bash
systemctl --user restart hermes-gateway.service
```

### 5. Test it
Send a message via Telegram to your Hermes bot, then react with ❤️ or 👍

## Supported Emojis
- 👍 → Celebratory GIF (Giphy)
- 🔥 → Hype GIF (Giphy)
- 🤔 → Thoughtful text (max 300 chars)
- ❤️ → Poetic text (max 150 chars)
- 🤯 → Mind-blown text (max 200 chars)
- 😈 → Witty text (max 100 chars)
- 🫡 → Formal text (max 150 chars)

Unlisted emojis → brief acknowledgment text
