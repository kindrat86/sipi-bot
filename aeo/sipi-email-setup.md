# sipi@sipi.bot — DNS Setup Guide

## Prerequisite
sipi.bot is on Fly.io (not Cloudflare DNS by default). You need to check where sipi.bot's DNS is managed.

## Option A: Cloudflare (recommended — free email routing)

If sipi.bot is behind Cloudflare DNS:
1. Go to Cloudflare Dashboard → sipi.bot → Email → Email Routing
2. Add rule: `sipi@sipi.bot` → forward to your personal email
3. Cloudflare handles the MX records automatically

## Option B: Fly.io DNS (sipi.bot custom domain)

If sipi.bot's DNS is managed through Fly.io:
1. Fly doesn't natively handle email — you need a third-party email host
2. Options from cheapest to most featureful:
   - **ImprovMX** (free for single forwarding address) → forward sipi@sipi.bot to your inbox
   - **Cloudflare Email Routing** (free, even if sipi.bot is at Fly — just point DNS at Cloudflare for email only)
   - **Fastmail** ($5/mo) — full email hosting, can send-as sipi@sipi.bot from your existing inbox
   - **Google Workspace** ($6/mo) — full Gmail for sipi@sipi.bot

## Option C: Simplest path — check if sipi.bot's DNS is at Cloudflare already

Run this to see:
```
whois sipi.bot | grep -i 'name server'
```

If the name servers point to Cloudflare (ns*.cloudflare.com), use Option A (free, 5 minutes). If they point to Fly or another provider, the fastest path is ImprovMX (free, one forwarding rule, takes 3 minutes).

## After setup — test that email arrives

Send a test from your personal email to sipi@sipi.bot. If it arrives, the identity is ready for outreach.
