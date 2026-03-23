# FAQ

## What API keys do I need?
You need an **Anthropic API key** (for the chat) and an **OpenRouter API key** (for document extraction). Both have free tiers or low cost.

## How much does it cost to run?
The app itself is free. API costs depend on usage:
- Extraction: ~$0.01 per document (Gemini Flash via OpenRouter)
- Chat: ~$0.02 per conversation turn (Claude Sonnet 4)
- A typical month with 5 documents and 20 chat messages: ~$0.50

## Can I use it without AI?
You can add vehicles and records manually, but the AI extraction and chat are the core features. Without API keys, uploads and chat wont work.

## Is my data safe?
Yes. Car Carer is self-hosted — your data stays on your machine. No data is sent anywhere except to the AI APIs for extraction and chat. Documents are stored locally.

## Can I share a vehicle with my mechanic?
Yes! Use the Sharing tab to invite anyone by email. You can assign roles: owner, editor (can add/edit), or viewer (read-only).

## What document formats are supported?
PDF, PNG, JPEG, and WebP. Both digital PDFs and photos of paper documents work.

## Can I import from LubeLogger?
Not yet, but it is on the roadmap (see issue #5).
