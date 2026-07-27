# Google Search Console — verification + sitemap submission

**Status:** verification files already deployed and serving HTTP 200. Only the two console clicks below remain. This is the single highest-impact unblocked traffic action.

## What's already done (verified 2026-07-27)

Both Google verification files are live and return the correct content:

| URL | HTTP | Body |
|---|---|---|
| `https://sipi.bot/google57979683042f3b0e.html` | 200 | `google-site-verification: google57979683042f3b0e.html` |
| `https://sipi.bot/googlea30bb998b91eb6ac.html` | 200 | `google-site-verification: googlea30bb998b91eb6ac.html` |

Bing Webmaster is already verified (`msvalidate.01` is in the homepage `<head>`).

## What you need to do (~3 minutes)

### 1. Verify ownership (one of two ways)

Go to **[search.google.com/search-console](https://search.google.com/search-console)** → **Add property** → `sipi.bot` (URL-prefix or Domain).

- **Domain property (recommended):** Google will give you a `TXT` record to add at your DNS provider (Cloudflare/wherever `sipi.bot` lives). This verifies all subdomains at once and is the most robust.
- **URL-prefix property (faster):** Add `https://sipi.bot`, choose "HTML file" verification, and Google will confirm the file above is already reachable — instant verify.

If you used the Domain property, pick whichever verification token Google shows; the HTML files above cover the URL-prefix path.

### 2. Submit the sitemap

Once verified, in Search Console go to **Sitemaps** → submit:

```
https://sipi.bot/sitemap.xml
```

Expected: ~237 URLs discovered (230 content + 7 new hub pages from this deploy). If Google reports fewer, run "URL inspection" on a sample page from each cluster.

### 3. Request indexing for the highest-value pages (optional, speeds first indexing)

In **URL inspection**, paste and "Request indexing" for:

- `https://sipi.bot/` (homepage)
- `https://sipi.bot/learn/spend-firewall-guide` (pillar)
- `https://sipi.bot/templates/agent-spend-policy-template/` (link-asset)
- `https://sipi.bot/alternatives/`, `/compare/`, `/templates/`, `/limits/`, `/policies/`, `/tutorials/` (the 7 new hub pages)

### 4. Check back in 3–7 days

- **Pages** report → look for the 6 previously-soft-404 hub URLs now showing as indexed (they were `{"error":"not_found"}` 404s before this deploy).
- **Coverage** → confirm "Excluded by 'noindex' tag" is zero (we don't noindex anything that should rank).
- **Crawl stats** → confirm Googlebot is hitting the site daily.

## Why this is win #1

Without GSC you have no visibility into which of the 237 URLs Google has actually indexed, no CTR/position data, and no way to detect crawl errors. The verification plumbing is already deployed; the console click is the last 5%.
