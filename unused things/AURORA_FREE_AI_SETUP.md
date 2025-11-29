
# 🤗 Aurora Free AI Setup Guide

Aurora now supports **completely free** AI through Hugging Face! No credit card required.

## Quick Setup (2 minutes)

### 1. Get Your Free Hugging Face API Key

1. Go to https://huggingface.co/join (create free account)
2. Go to https://huggingface.co/settings/tokens
3. Click "New token" → Name it "Aurora" → Create token
4. Copy your token (starts with `hf_...`)

### 2. Add to Replit Secrets

1. In Replit, click the **Secrets** tool (🔒 icon in left sidebar)
2. Click "Add new secret"
3. Key: `HUGGINGFACE_API_KEY`
4. Value: Paste your `hf_...` token
5. Click "Add secret"

### 3. Restart Aurora

Click the **Stop** button, then **Run** again. You'll see:
```
[Aurora Chat] 🤗 Using free Hugging Face AI (Llama/Mistral models)
```

## What You Get (FREE Forever)

✅ **Meta Llama 3** - 8B parameter model (GPT-3.5 quality)
✅ **Unlimited requests** on free tier (with rate limits)
✅ **No credit card** required
✅ **Full conversational AI** capabilities
✅ **Automatic fallback** if Anthropic credits run out

## Alternative Free Models

Edit `server/aurora-chat.ts` line with the model URL to use different free models:

- **Mistral 7B**: `mistralai/Mistral-7B-Instruct-v0.2`
- **Falcon 7B**: `tiiuae/falcon-7b-instruct`
- **Zephyr**: `HuggingFaceH4/zephyr-7b-beta`

## Comparison

| Provider | Cost | Quality | Speed |
|----------|------|---------|-------|
| **Anthropic Claude** | $$ (needs credits) | ⭐⭐⭐⭐⭐ | ⚡⚡⚡ |
| **Hugging Face Llama** | 🆓 FREE | ⭐⭐⭐⭐ | ⚡⚡ |
| **Built-in Fallback** | 🆓 FREE | ⭐⭐ | ⚡⚡⚡ |

## Pro Tip

You can use **both**! Aurora will:
1. Try Anthropic Claude first (if you add credits)
2. Fall back to Hugging Face (free)
3. Use simple responses as last resort

This gives you the best of both worlds! 🎉
