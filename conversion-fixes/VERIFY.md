# Post-deploy verification (run these after `flyctl deploy`)

## 1. Pricing schema is live + valid
```bash
# Should print 1 (one JSON-LD block on /pricing)
curl -s https://sipi.bot/pricing | grep -c 'application/ld+json'

# Should be valid JSON with Product + FAQPage, no aggregateRating
curl -s https://sipi.bot/pricing | python3 -c "
import sys,re,json
h=sys.stdin.read()
for b in re.findall(r'<script type=\"application/ld\+json\">(.*?)</script>',h,re.S):
    d=json.loads(d if False else b)
    for n in d.get('@graph',[]):
        print(n.get('@type'), '| rating=' , 'aggregateRating' in n)
"
# Expected:
#   Product | rating= False      ← honesty gate OK
#   FAQPage | rating= False
```
Then paste the JSON-LD into https://search.google.com/test/rich-results
(expect: Product + FAQ eligible; no warnings about ratings).

## 2. Hub 404s now 301-redirect
```bash
for u in /compare /compare/ /calculator /calculator/; do
  printf "%-14s -> " "$u"
  curl -s -o /dev/null -w "HTTP %{http_code} Location: %{redirect_url}\n" "https://sipi.bot$u"
done
# Expected:
#   /compare       -> HTTP 301 Location: https://sipi.bot/vs/
#   /compare/      -> HTTP 301 Location: https://sipi.bot/vs/
#   /calculator    -> HTTP 301 Location: https://sipi.bot/tools/risk-calculator/
#   /calculator/   -> HTTP 301 Location: https://sipi.bot/tools/risk-calculator/
```

## 3. No regressions (security headers + checkout + key routes)
```bash
# Security headers survive the redirect
curl -sI https://sipi.bot/compare | grep -i 'strict-transport\|x-frame\|cross-origin'

# Checkout still 302s to live Stripe (view-only, never complete)
curl -s -o /dev/null -w "/checkout/team -> HTTP %{http_code}\n" https://sipi.bot/checkout/team

# Key routes still 200
for u in / /pricing /dashboard /playground/ /vs/ /tools/risk-calculator/; do
  curl -s -o /dev/null -w "%{http_code} $u\n" "https://sipi.bot$u"
done
```

## 4. fly.toml + secrets untouched
```bash
git diff main -- fly.toml | wc -l   # must be 0
```
