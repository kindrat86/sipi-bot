"""templates.py — landing page (Brunson H/S/O + Isenberg teardown) + dashboard.

Dark, code-forward, mobile-first. Stdlib string templates (no jinja).
"""
from __future__ import annotations

import os

CSS = """
:root{--bg:#0a0a0a;--panel:#121316;--panel2:#17181c;--line:#23242a;
--txt:#e8e8ea;--mut:#8a8d96;--accent:#00d4aa;--red:#ff5470;--amber:#ffb020;--green:#00d4aa;}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--txt);font:16px/1.6 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid rgba(0,212,170,.5);outline-offset:3px}
html{scroll-behavior:smooth}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.mono{font-family:'SF Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
nav{position:sticky;top:0;z-index:20;background:rgba(10,10,10,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px;flex-wrap:wrap}
.brand{font-weight:700;font-size:19px;letter-spacing:-.02em}
.brand .dot{color:var(--accent)}
.nav-links{display:flex;gap:22px;align-items:center;font-size:14px;flex-wrap:wrap}
.nav-links a{color:var(--mut);min-height:44px;display:inline-flex;align-items:center}.nav-links a:hover{color:var(--txt)}.nav-links a.btn,.nav-links a.btn:hover,.nav-links a.btn:visited{color:#04120e}.nav-toggle{display:none;background:transparent;border:1px solid var(--line);border-radius:8px;color:var(--txt);width:44px;height:44px;align-items:center;justify-content:center;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:border-color .15s}.nav-toggle:hover{border-color:var(--accent)}.nav-toggle svg{width:24px;height:24px;flex:0 0 auto;display:block}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:var(--accent);color:#04120e;font-weight:700;padding:12px 22px;border-radius:10px;border:none;cursor:pointer;font-size:15px;transition:transform .18s ease,background .18s ease,border-color .18s ease}
.btn:hover{transform:translateY(-1px)}
.btn:active{transform:translateY(1px) scale(.99)}
.btn.ghost{background:transparent;color:var(--txt);border:1px solid var(--line)}
section{padding:72px 0;border-bottom:1px solid var(--line)}
.hero{padding:90px 0 80px;text-align:center;background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(0,212,170,.10),transparent)}
.hero-actions{display:flex;align-items:center;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:26px}
.hero-proof{display:flex;align-items:center;justify-content:center;gap:10px 18px;flex-wrap:wrap;margin-top:18px;color:var(--mut);font-size:13px}
.hero-proof a{text-decoration:underline;text-underline-offset:3px}
.tag{display:inline-block;font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--accent);border:1px solid rgba(0,212,170,.3);border-radius:100px;padding:6px 14px;margin-bottom:24px}
h1{font-size:clamp(32px,6vw,56px);line-height:1.05;letter-spacing:-.03em;font-weight:800;margin-bottom:20px}
h1 .hl{color:var(--red)}
.sub{font-size:clamp(17px,2.4vw,21px);color:var(--mut);max-width:680px;margin:0 auto 34px}
h2{font-size:clamp(26px,4vw,38px);letter-spacing:-.02em;margin-bottom:14px;font-weight:800}
.lead{color:var(--mut);font-size:18px;max-width:640px;margin-bottom:40px}
.center{text-align:center;margin:0 auto}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:24px}
.card h3{font-size:18px;margin-bottom:10px}
.tl{list-style:none;display:flex;flex-direction:column;gap:12px}
.tl li{display:flex;gap:14px;align-items:flex-start;background:var(--panel2);border:1px solid var(--line);border-radius:12px;padding:14px 16px}
.tl .t{color:var(--mut);font-size:13px;min-width:52px;padding-top:2px}
.badge{font-size:12px;font-weight:700;padding:3px 9px;border-radius:6px;white-space:nowrap}
.b-red{background:rgba(255,84,112,.14);color:var(--red)}
.b-green{background:rgba(0,212,170,.14);color:var(--green)}
.b-amber{background:rgba(255,176,32,.14);color:var(--amber)}
.contrast{display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid var(--line);border-radius:16px;overflow:hidden}
.contrast>div{padding:26px}
.contrast .old{background:rgba(255,84,112,.05)}
.contrast .new{background:rgba(0,212,170,.05)}
.contrast h3{font-size:15px;text-transform:uppercase;letter-spacing:.08em;margin-bottom:16px}
.contrast ul{list-style:none;display:flex;flex-direction:column;gap:12px;font-size:15px}
.contrast li{display:flex;gap:10px}
.price{max-width:440px;margin:0 auto;background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid rgba(0,212,170,.3);border-radius:20px;padding:36px;text-align:center}
.price .amt{font-size:52px;font-weight:800;letter-spacing:-.03em}
.price .amt span{font-size:18px;color:var(--mut);font-weight:500}
.price ul{list-style:none;text-align:left;margin:24px 0;display:flex;flex-direction:column;gap:12px}
.price li{display:flex;gap:10px;color:var(--txt)}
.price li .c{color:var(--accent)}
.grid2>.price{display:flex;flex-direction:column}
.grid2>.price>.btn{margin-top:auto}
.strike{color:var(--mut);text-decoration:line-through;font-size:15px}
.codebox{background:#000;border:1px solid var(--line);border-radius:12px;padding:18px;overflow-x:auto;font-size:13.5px;color:#cfd2d8;text-align:left}
.codebox .k{color:var(--accent)}.codebox .s{color:var(--amber)}.codebox .c{color:var(--mut)}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:8px}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px;text-align:center}
.kpi .n{font-size:30px;font-weight:800;color:var(--accent)}
.kpi .l{font-size:13px;color:var(--mut);margin-top:4px}
footer{padding:40px 0;text-align:center;color:var(--mut);font-size:14px}
.form{display:flex;gap:10px;max-width:440px;margin:18px auto 0}
.form input{flex:1;background:var(--panel2);border:1px solid var(--line);color:var(--txt);padding:13px 15px;border-radius:10px;font-size:15px}
.mt40{margin-top:40px}.mt24{margin-top:24px}
.faq{max-width:760px;margin:0 auto;display:flex;flex-direction:column;gap:12px;text-align:left}
.faq details{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px}
.faq summary{font-weight:700;cursor:pointer;font-size:16px;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::before{content:"+ ";color:var(--accent);font-weight:800}
.faq details[open] summary::before{content:"– "}
.faq details p{color:var(--mut);margin-top:12px;font-size:15px}
.doc{max-width:760px;margin:0 auto;text-align:left}
.doc h1{font-size:clamp(28px,5vw,40px);margin-bottom:8px}
.doc p,.doc li{color:var(--mut);font-size:16px;margin-bottom:12px}
.doc h2{font-size:22px;margin:28px 0 10px}
.doc .lead{color:var(--txt);font-size:18px}
.deflist{max-width:760px;margin:8px auto 0;text-align:left}
.deflist dt{font-weight:700;color:var(--accent);margin-top:16px;font-size:17px}
.deflist dd{margin:6px 0 0;color:var(--mut);font-size:15px}
.deflist code{background:var(--panel2);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-family:'SF Mono',monospace;font-size:13px;color:var(--txt)}
.cmp{width:100%;border-collapse:collapse;margin-top:20px;font-size:14.5px}
.cmp th,.cmp td{border:1px solid var(--line);padding:12px 14px;text-align:left}
.cmp thead th{background:var(--panel2);color:var(--txt);font-weight:700}
.cmp tbody tr:nth-child(even){background:rgba(255,255,255,.02)}
.cmp tbody tr:last-child{background:rgba(0,212,170,.06)}
.sec-table{width:100%;border-collapse:collapse;margin:20px 0;font-size:14.5px;display:block;overflow-x:auto;-webkit-overflow-scrolling:touch}
.sec-table th,.sec-table td{border:1px solid var(--line);padding:12px 14px;text-align:left;vertical-align:top}
.sec-table thead th{background:var(--panel2);color:var(--txt);font-weight:700}
.sec-table code{background:var(--panel2);border:1px solid var(--line);border-radius:5px;padding:1px 6px;font-family:'SF Mono',monospace;font-size:12.5px;color:var(--accent)}
.doc ul{max-width:760px;margin:12px auto;text-align:left;color:var(--txt)}
.doc ul li{margin:8px 0;line-height:1.6}
.doc pre{background:var(--panel2);border:1px solid var(--line);border-radius:8px;padding:16px;overflow-x:auto;max-width:760px;margin:16px auto;text-align:left}
.doc pre code{background:none;border:0;padding:0;color:var(--accent);font-family:'SF Mono',monospace;font-size:13px}
.doc .quiet{color:var(--mut);font-size:14px;max-width:760px;margin:24px auto 0}
@media(max-width:760px){.grid2,.contrast,.kpis{grid-template-columns:1fr}.decision3{grid-template-columns:1fr!important}.nav-toggle{display:inline-flex}#mainnav{position:absolute;top:60px;left:0;right:0;flex-direction:column;align-items:stretch;justify-content:flex-start;width:100%;background:rgba(10,10,10,.98);backdrop-filter:blur(10px);border-bottom:1px solid var(--line);padding:8px 20px 18px;gap:2px;display:none;z-index:30;max-height:calc(100dvh - 60px);overflow-y:auto}nav.menu-open #mainnav{display:flex}#mainnav a{width:100%;padding:10px 0;justify-content:flex-start}#mainnav a.btn{justify-content:center;margin-top:10px}#mainnav a:not(.btn){font-size:15px}section{padding:52px 0}.hero{padding:48px 0 56px}.hero .tag{margin-bottom:18px}.hero h1{margin-bottom:16px}.hero .sub{margin-bottom:0;font-size:17px}.hero-actions{align-items:stretch;margin-top:22px}.hero-actions .btn{width:100%}.hero-actions .text-link{min-height:44px;display:inline-flex;align-items:center;justify-content:center}.hero-proof{margin-top:14px;gap:6px 12px}.cmp{font-size:12.5px;display:block;overflow-x:auto;-webkit-overflow-scrolling:touch}.cmp th,.cmp td{padding:8px}}/* the comparison table is 371px inside a 335px column, so it pushed the whole document to 391px on a 375px phone; scroll it inside its own box instead */
"""

# ─── Analytics ───
# PostHog — product analytics. Public client-side token (safe to ship). Overridable via env.
POSTHOG_KEY = os.environ.get("POSTHOG_KEY", "phc_lyZCgvTpicjLzAO3rY2GhxuX5WUc5jQjP8ZVwwJqauX")
POSTHOG_HOST = os.environ.get("POSTHOG_HOST", "https://eu.i.posthog.com")

# Google Analytics stays disabled until it is wired through the consent loader.
GA4_ID = os.environ.get("GA4_MEASUREMENT_ID", "")
GA4_SNIPPET = ""
POSTHOG_SNIPPET = ""


def landing_page_html() -> str:
    s = """<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){try{window.trustedTypes.createPolicy("default",{createHTML:function(s){return s},createScript:function(s){return s},createScriptURL:function(s){return s}})}catch(e){}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>sipi.bot — The Pre-Spend Firewall for Autonomous AI Agents</title>
<meta name="description" content="sipi.bot is a pre-spend firewall for AI agents: one API call approves, blocks, or flags every transaction against per-tx caps, velocity limits, and merchant rules.">
<link rel="canonical" href="https://sipi.bot/">
<link rel="alternate" hreflang="en" href="https://sipi.bot/">
<link rel="alternate" hreflang="en-US" href="https://sipi.bot/">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot/">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="msvalidate.01" content="FA4E122745948F0CAD16959F59DDCB85">
<meta property="og:title" content="sipi.bot — The Pre-Spend Firewall for Autonomous AI Agents">
<meta property="og:description" content="sipi.bot is a pre-spend firewall (payment-control API) for autonomous AI agents: approve, block, or flag every agent transaction before a dollar moves.">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot/">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="sipi.bot — The pre-spend firewall for autonomous AI agents"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="sipi.bot — The Pre-Spend Firewall for Autonomous AI Agents">
<meta name="twitter:description" content="Pre-spend firewall for autonomous AI agents: approve, block, or flag every agent transaction before a dollar moves.">
<meta name="twitter:image" content="https://sipi.bot/og.png">
<meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","@id":"https://sipi.bot/#org","name":"sipi.bot","alternateName":["sipibot","sipi bot","sipi.bot spend firewall"],"url":"https://sipi.bot/","description":"sipi.bot is a spend firewall for autonomous AI agents — a real-time API that returns APPROVED, BLOCKED, or FLAGGED for every payment an agent attempts, enforcing per-transaction caps, daily totals, velocity limits, and merchant rules so a runaway agent can't drain your funds.","disambiguatingDescription":"sipi.bot is a payment-control spend firewall API for autonomous AI agents (x402 / AP2 / AgentKit) — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.","sameAs":["https://github.com/kindrat86/sipi-bot","https://pypi.org/project/sipi-bot/","https://x.com/sipiteno","https://www.linkedin.com/in/maryan-k/"],"knowsAbout":["AI Agent Spend Control","Autonomous Agent Payment Firewall","API Spend Governance","x402 Payment Protocol","Agent Transaction Monitoring","Runaway AI Cost Prevention","Agent Budget Management","Multi-Agent Spend Orchestration"]},{"@type":"WebSite","@id":"https://sipi.bot/#website","url":"https://sipi.bot/","name":"sipi.bot","publisher":{"@id":"https://sipi.bot/#org"}},{"@type":"WebPage","@id":"https://sipi.bot/#page","url":"https://sipi.bot/","name":"sipi.bot — The Pre-Spend Firewall for Autonomous AI Agents","isPartOf":{"@id":"https://sipi.bot/#website"},"datePublished":"2026-07-08","dateModified":"2026-07-17","author":{"@id":"https://sipi.bot/#person"}},{"@type":"BreadcrumbList","@id":"https://sipi.bot/#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://sipi.bot/"}]},{"@type":"SiteNavigationElement","name":["Home","Dashboard","Pricing","About"],"url":["https://sipi.bot/","https://sipi.bot/dashboard","https://sipi.bot/pricing","https://sipi.bot/about"]},{"@type":"SoftwareApplication","@id":"https://sipi.bot/#app","name":"sipi.bot","alternateName":["sipibot","sipi bot"],"applicationCategory":"BusinessApplication","operatingSystem":"Any (HTTP API, MCP, CLI)","description":"Spend firewall that evaluates every autonomous-agent transaction against your rules and returns approve, block, or flag with a deterministic rules check.","disambiguatingDescription":"A payment-control spend firewall API for autonomous AI agents — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.","offers":[{"@type":"Offer","name":"Team","price":"99","priceCurrency":"USD","description":"Team plan — $99/month, unlimited transaction evaluations."},{"@type":"Offer","name":"Business","price":"499","priceCurrency":"USD","description":"Business plan — $499/month, unlimited transaction evaluations with priority support."}],"featureList":["Per-transaction, daily, velocity, merchant, category and time rules","Human-in-the-loop approval queue","Queryable audit log","MCP tool + HTTP API + CLI"]},{"@type":"FAQPage","@id":"https://sipi.bot/#faq","mainEntity":[{"@type":"Question","name":"What is a spend firewall for AI agents?","acceptedAnswer":{"@type":"Answer","text":"A spend firewall sits in front of every transaction an autonomous AI agent attempts and evaluates it against your rules — approving, blocking, or flagging it before any money moves. sipi.bot returns a decision with a deterministic rules check over HTTP, MCP, or CLI."}},{"@type":"Question","name":"How does sipi.bot stop an agent from overspending?","acceptedAnswer":{"@type":"Answer","text":"Your agent calls sipi.bot before it spends. sipi.bot checks the transaction against per-transaction, daily, velocity, merchant, category, and time rules and returns approve, block, or flag. Velocity limits kill runaway retry loops instantly, and unknown merchants are blocked unless allowlisted."}},{"@type":"Question","name":"How much does sipi.bot cost?","acceptedAnswer":{"@type":"Answer","text":"Hosted plans are flat-rate: Team is $99/month and Business is $499/month, both with unlimited transaction evaluations — no per-call fees, no metering, no overage tiers. The open-source core is MIT-licensed and free to self-host forever."}},{"@type":"Question","name":"Does sipi.bot work with MCP and Claude Code?","acceptedAnswer":{"@type":"Answer","text":"Yes. sipi.bot is a native MCP tool, so Claude Code, Cursor, and Hermes call it directly, and it also exposes a plain HTTP API and a CLI so any agent runtime can use it. Client wrappers for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK take a few lines each."}},{"@type":"Question","name":"Is sipi.bot a SIP, voice, or telephony product?","acceptedAnswer":{"@type":"Answer","text":"No. Despite the name, sipi.bot has nothing to do with SIP, VoIP, or voice, and it is not a bot-management or 'block AI bots' tool. sipi.bot is a spend firewall that governs how much money autonomous AI agents can spend."}},{"@type":"Question","name":"How does sipi.bot protect against runaway AI spending?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot evaluates every transaction request with a deterministic rules check before money moves. It enforces per-transaction caps, daily totals, velocity limits, and merchant allowlists. If a rule is violated, the transaction is BLOCKED instantly — you wake up to a clean log, not a drained account."}},{"@type":"Question","name":"Which payment protocols does sipi.bot support?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot works with any HTTP-based payment pipeline: x402, AP2, AgentKit (Coinbase), Stripe agent tooling, LangChain, CrewAI, and the Model Context Protocol (MCP). It's protocol-agnostic — if your agent speaks HTTP, sipi.bot can gate it."}},{"@type":"Question","name":"Can I try sipi.bot for free?","acceptedAnswer":{"@type":"Answer","text":"Yes — you can call the evaluate API right now, free, with no signup and no credit card. Send a POST to /v1/transactions/evaluate and get a decision with a deterministic rules check — 100 calls per minute per IP with no account required. Hosted plans add a private workspace and managed infrastructure."}},{"@type":"Question","name":"How fast is the API?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot decisions return with a deterministic rules check. Measure end-to-end latency from your deployment region before using it on a critical payment path."}}]},{"@type":"SpeakableSpecification","cssSelector":["h1","h2","p"]},{"@type":"Person","@id":"https://sipi.bot/#person","name":"Maryan","givenName":"Maryan","description":"Solo founder and AI infrastructure engineer. Building in the agent-economy stack since 2024 — spend controls, payment protocols (x402, AP2), MCP tooling, and compliance infrastructure.","knowsAbout":["AI Agent Spend Control","Autonomous Agent Payment Firewall","x402 Payment Protocol","MCP Tooling","Agent Infrastructure"],"sameAs":["https://github.com/kindrat86","https://x.com/sipiteno","https://pypi.org/user/kindrat86/"],"jobTitle":"Founder","worksFor":{"@id":"https://sipi.bot/#org"},"nationality":{"@type":"Country","name":"Greece"}}]}</script><style>{CSS}</style>{POSTHOG}{GA4_SNIPPET}<!-- /ux.css + /ux.js removed 2026-07-26. They loaded AFTER this page's own <style>{CSS}</style>, and ux.css is light by default (--ux-text:#0f172a, --ux-surface:#fff, dark only inside a prefers-color-scheme query). So for every light-mode visitor body text became #0f172a while .card kept this page's own --panel #121316 — measured 1.04:1, i.e. the "Who uses a spend firewall" cards were invisible in production. This page uses no .ux-* class, no var(--ux-*) and no ux.js hook, so the pair contributed nothing but the bug (and two render-blocking requests). --></head><body>
<nav><div class="wrap">
  <div class="brand">sipi<span class="dot">.bot</span></div>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mainnav" aria-label="Open menu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  <div class="nav-links" id="mainnav">
    <a href="#how">How it works</a>
    <a href="#faq">FAQ</a>
    <a href="#pricing">Pricing</a>
    <a href="/learn/how-to-control-ai-agent-spending">Compare approaches</a>
    <a href="/pricing" class="btn">See plans</a>
  </div>
</div></nav>
<script>(function(){var t=document.querySelector('.nav-toggle');if(!t)return;var n=t.closest('nav');function set(o){n.classList.toggle('menu-open',o);t.setAttribute('aria-expanded',o);t.setAttribute('aria-label',o?'Close menu':'Open menu');}t.addEventListener('click',function(){set(!n.classList.contains('menu-open'));});n.querySelectorAll('.nav-links a').forEach(function(a){a.addEventListener('click',function(){set(false);});});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&n.classList.contains('menu-open')){set(false);t.focus();}});})();</script>

<header class="hero"><div class="wrap">
  <span class="tag">Spend controls for the agent economy</span>
  <h1>Your AI agent just spent<br><span class="hl">$12,400 while you slept.</span></h1>
  <p class="sub"><strong>sipi.bot is the pre-spend firewall for autonomous AI agents.</strong>
  One HTTP call checks every proposed payment against your caps, velocity limits,
  and merchant rules—then returns APPROVED, BLOCKED, or FLAGGED with a deterministic rules check,
  before money moves.</p>
  <div class="hero-actions">
    <a href="/pricing" class="btn">Protect my agent — see plans</a>
    <a href="/playground/" class="btn ghost">Run a free live check</a>
  </div>
  <div class="hero-proof" aria-label="Product proof">
    <a href="/eval-report/">53/53 public evals</a>
    <span aria-hidden="true">·</span>
    <a href="https://github.com/kindrat86/sipi-bot" rel="noopener">MIT-licensed core</a>
    <span aria-hidden="true">·</span>
    <a href="/about">Founder story</a>
  </div>
  <!-- TRY IT NOW -->
  <div class="codebox mono" style="max-width:620px;margin:24px auto 0;text-align:left">
<p style="color:var(--accent);font-weight:700;margin-bottom:8px;font-size:14px">✨ Try it right now — no signup, no key. Copy, paste, run.</p>
curl -X POST https://sipi.bot/v1/transactions/evaluate \\<br>
&nbsp;&nbsp;-H <span class="s">"Content-Type: application/json"</span> \\<br>
&nbsp;&nbsp;-d <span class="s">'{"amount": 12400, "currency": "USD", "merchant": "example-vendor"}'</span><br><br>
<span class="c"># Returns a deterministic decision:</span><br>
{ <span class="k">"decision"</span>: <span class="s">"BLOCKED"</span>, <span class="k">"reason"</span>: <span class="s">"Block any single transaction over $500"</span>, <span class="k">"rule_id"</span>: <span class="s">"rul_d8edb12ffa"</span>, <span class="k">"transaction_id"</span>: <span class="s">"txn_e340f0e12489"</span>, <span class="k">"amount"</span>: <span class="k">12400.0</span>, <span class="k">"merchant"</span>: <span class="s">"example-vendor"</span> }
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:16px">
      <button type="button" class="btn" id="hero-run-check">Run this live check</button>
      <button type="button" class="btn ghost" id="hero-copy-check">Copy curl command</button>
    </div>
    <div id="hero-live-result" aria-live="polite" style="display:none;margin-top:14px;padding:12px;border:1px solid var(--line);border-radius:9px;white-space:pre-wrap"></div>
    <div id="hero-live-next" style="display:none;margin-top:12px">
      <a href="/pricing?from=homepage-live-proof" class="btn">Use this protection in production →</a>
    </div>
  </div>
  <div class="kpis mt40">
    <div class="kpi"><div class="n">Deterministic</div><div class="l">rules engine</div></div>
    <div class="kpi"><div class="n">3</div><div class="l">outcomes: approve / block / flag</div></div>
    <div class="kpi"><div class="n">53/53</div><div class="l">sipi.bot Eval Gym scenarios</div></div>
    <div class="kpi"><div class="n">6</div><div class="l">rule types enforced</div></div>
  </div>
  <!-- DREAM 100 / AUTHORITY BAR (Brunson Traffic Secrets Secret #2: surface the congregation) -->
  <div style="margin-top:36px;padding:18px 16px;border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06);background:rgba(0,212,170,.03)">
    <div style="max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px 28px;font-size:14px;color:#8a8d96">
      <span style="color:var(--accent);font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:11px">Works with</span>
      <a href="/for/">◆ x402-compatible HTTP flows</a>
      <a href="/for/openai-agents/">◆ OpenAI Agents SDK</a>
      <a href="/for/langchain/">◆ LangChain</a>
      <a href="/integrations/crewai/">◆ CrewAI</a>
      <a href="/.well-known/mcp.json">◆ Model Context Protocol</a>
    </div>
    <p style="text-align:center;margin:10px 0 0;font-size:12.5px;color:#6b6f78">sipi.bot is the spend layer for the same agent protocols that move money autonomously. We plug in before the transaction, not after the incident.</p>
  </div>
</div></header>

<section id="how"><div class="wrap">
  <h2>Would you give an intern your credit card with no limit?</h2>
  <p class="lead">That's what happens the moment you deploy an autonomous agent. Here's the difference one API call makes.</p>
  <div class="grid2">
    <div class="card">
      <h3 style="color:var(--red)">❌ The old way — hope</h3>
      <ul class="tl">
        <li><span class="t mono">2:14a</span><div>Agent hits a rate-limit, retries the purchase 40× <span class="badge b-red">$4,000</span></div></li>
        <li><span class="t mono">2:15a</span><div>Buys compute from an unknown vendor <span class="badge b-red">$6,200</span></div></li>
        <li><span class="t mono">2:31a</span><div>Tips an API into an overage tier <span class="badge b-red">$2,200</span></div></li>
        <li><span class="t mono">9:03a</span><div>You wake up. You find out from Stripe. <span class="badge b-red">$12,400</span></div></li>
      </ul>
    </div>
    <div class="card">
      <h3 style="color:var(--green)">✅ The sipi.bot way — control</h3>
      <ul class="tl">
        <li><span class="t mono">2:14a</span><div>Retry #11 exceeds velocity rule <span class="badge b-green">BLOCKED</span></div></li>
        <li><span class="t mono">2:15a</span><div>Unknown vendor not on allowlist <span class="badge b-green">BLOCKED</span></div></li>
        <li><span class="t mono">2:31a</span><div>$2,200 &gt; approval threshold <span class="badge b-amber">FLAGGED</span></div></li>
        <li><span class="t mono">9:03a</span><div>You wake up to a clean log and one thing to approve. <span class="badge b-green">$0 lost</span></div></li>
      </ul>
    </div>
  </div>

  <h2 class="mt40" style="margin-top:56px">One call. Before the money moves.</h2>
  <p class="lead">Your agent asks permission first. It's HTTP, so any agent can call it — and an MCP tool, so Claude Code / Cursor / Hermes call it natively.</p>
  <div class="codebox mono">
<span class="c"># Your agent asks before it spends</span><br>
curl -X POST https://sipi.bot/v1/transactions/evaluate \\<br>
&nbsp;&nbsp;-H <span class="s">"Authorization: Bearer ***"</span> \\<br>
&nbsp;&nbsp;-d <span class="s">'{"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"}'</span><br><br>
<span class="c"># sipi.bot answers without a model call</span><br>
{ <span class="k">"decision"</span>: <span class="s">"BLOCKED"</span>, <span class="k">"reason"</span>: <span class="s">"Merchant not on allowlist"</span> }
  </div>

  <h2 class="mt40" style="margin-top:56px">The three decisions, defined</h2>

  <!-- ===== BRUNSON: NAMED FRAMEWORK (Ch16) — The 3-Decision Spend Firewall™ ===== -->
  <section id="framework" style="margin-top:40px;padding:36px 28px;background:var(--panel);border:1px solid var(--line);border-radius:16px">
    <div style="text-align:center;max-width:720px;margin:0 auto 28px">
      <span class="tag">The Framework</span>
      <h2 style="margin:14px 0 8px">Every agent transaction gets <span style="color:var(--accent)">one of three answers</span>.</h2>
      <p style="color:var(--mut);font-size:1.02rem;line-height:1.6;margin:0">
        Not a suggestion. Not a soft preference. A deterministic firewall. We call it
        <strong style="color:var(--txt)">The 3-Decision Spend Firewall&trade;</strong>. Your agent calls it before every spend, it answers in under 5&nbsp;ms, and the answer is final.
      </p>
    </div>

    <div class="decision3" style="display:grid;grid-template-columns:repeat(3,1fr);gap:16px">
      <!-- DECISION 1: APPROVED -->
      <div style="background:var(--panel2);border:1px solid var(--line);border-radius:14px;padding:26px 22px;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:var(--green)"></div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
          <span style="display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:rgba(0,212,170,.12);border:1px solid rgba(0,212,170,.24);color:var(--accent);font-weight:800;font-size:.85rem">01</span>
          <span style="font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);font-weight:700">Decision One</span>
        </div>
        <h3 style="color:var(--green);font-size:1.25rem;margin:0 0 8px;font-weight:800;letter-spacing:.04em">APPROVED</h3>
        <p style="color:var(--mut);font-size:.92rem;line-height:1.55;margin:0">
          Transaction is within your <strong style="color:var(--txt)">caps</strong>, <strong style="color:var(--txt)">velocity rules</strong>, and <strong style="color:var(--txt)">merchant whitelist</strong>. The agent proceeds.
        </p>
      </div>
      <!-- DECISION 2: BLOCKED -->
      <div style="background:var(--panel2);border:1px solid var(--line);border-radius:14px;padding:26px 22px;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:var(--red)"></div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
          <span style="display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:rgba(255,84,112,.12);border:1px solid rgba(255,84,112,.24);color:var(--red);font-weight:800;font-size:.85rem">02</span>
          <span style="font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);font-weight:700">Decision Two</span>
        </div>
        <h3 style="color:var(--red);font-size:1.25rem;margin:0 0 8px;font-weight:800;letter-spacing:.04em">BLOCKED</h3>
        <p style="color:var(--mut);font-size:.92rem;line-height:1.55;margin:0">
          Transaction exceeds a <strong style="color:var(--txt)">hard limit</strong>, hits a <strong style="color:var(--txt)">banned merchant category</strong>, or breaks a rule you set. The agent stops. <strong style="color:var(--red)">No override.</strong>
        </p>
      </div>
      <!-- DECISION 3: FLAGGED -->
      <div style="background:var(--panel2);border:1px solid var(--line);border-radius:14px;padding:26px 22px;position:relative;overflow:hidden">
        <div style="position:absolute;top:0;left:0;right:0;height:3px;background:var(--amber)"></div>
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px">
          <span style="display:grid;place-items:center;width:38px;height:38px;border-radius:10px;background:rgba(255,176,32,.12);border:1px solid rgba(255,176,32,.24);color:var(--amber);font-weight:800;font-size:.85rem">03</span>
          <span style="font-size:.7rem;letter-spacing:.16em;text-transform:uppercase;color:var(--mut);font-weight:700">Decision Three</span>
        </div>
        <h3 style="color:var(--amber);font-size:1.25rem;margin:0 0 8px;font-weight:800;letter-spacing:.04em">FLAGGED</h3>
        <p style="color:var(--mut);font-size:.92rem;line-height:1.55;margin:0">
          Edge case. Unusual pattern. New merchant. <strong style="color:var(--txt)">Held for human review</strong> before a single dollar moves.
        </p>
      </div>
    </div>

    <div style="margin-top:22px;text-align:center;padding:18px;background:rgba(0,212,170,.04);border:1px dashed rgba(0,212,170,.3);border-radius:12px">
      <p style="color:var(--mut);font-size:.9rem;margin:0;line-height:1.6">
        <span style="color:var(--accent);font-weight:800;letter-spacing:.06em">APPROVED &nbsp;&bull;&nbsp; BLOCKED &nbsp;&bull;&nbsp; FLAGGED.</span>
        Three answers. Five milliseconds. Every transaction. That is the firewall.
      </p>
    </div>
  </section>
  <!-- ===== /BRUNSON FRAMEWORK ===== -->

  <dl class="deflist">
    <dt>Approve</dt><dd>The transaction passes every active rule. sipi.bot returns <code>APPROVED</code> and your agent proceeds — logged for the audit trail.</dd>
    <dt>Block</dt><dd>The transaction violates a hard rule (over a cap, unknown merchant, velocity breach). sipi.bot returns <code>BLOCKED</code> and no money moves.</dd>
    <dt>Flag</dt><dd>The transaction is allowed but crosses an approval threshold. sipi.bot returns <code>FLAGGED</code> and routes it to your human-in-the-loop approval queue.</dd>
  </dl>

  <h2 class="mt40" style="margin-top:56px">How sipi.bot compares</h2>
  <table class="cmp">
    <thead><tr><th>Approach</th><th>Stops runaway spend</th><th>Latency</th><th>Audit log</th><th>Cost</th></tr></thead>
    <tbody>
      <tr><td>Trust the prompt</td><td>❌ No</td><td>—</td><td>❌ No</td><td>$0 (until it isn't)</td></tr>
      <tr><td>Provider spend cap</td><td>⚠️ Per-provider only</td><td>—</td><td>⚠️ Partial</td><td>Varies</td></tr>
      <tr><td>Manual review</td><td>✅ Yes</td><td>Minutes+</td><td>⚠️ Separate notes</td><td>Variable</td></tr>
      <tr><td><strong>sipi.bot</strong></td><td>✅ Yes</td><td><strong>No model call</strong></td><td>✅ Queryable</td><td><strong>$99/mo</strong></td></tr>
    </tbody>
  </table>

  <h2 class="mt40" style="margin-top:56px">The six rules a spend firewall enforces</h2>
  <p class="lead">Every transaction an agent attempts is checked against these before any money moves. Turn on the ones that matter for your workload.</p>
  <dl class="deflist">
    <dt>Per-transaction cap</dt><dd>A hard ceiling on any single spend — for example, block anything over $200 outright.</dd>
    <dt>Daily / period total</dt><dd>A rolling budget across all transactions, so many small buys can't quietly add up to a runaway day.</dd>
    <dt>Velocity limit</dt><dd>A cap on how many transactions are allowed in a window. This is what kills a retry loop hammering a failed purchase 40 times at 2am.</dd>
    <dt>Merchant allowlist</dt><dd>Only approved vendors go through; an unknown merchant like <code>unknown-gpu.ru</code> is blocked unless you've allowlisted it.</dd>
    <dt>Category rule</dt><dd>Allow, cap, or flag by spend category — compute, SaaS, ads, data — so an agent can buy API credits but never wire money.</dd>
    <dt>Time-of-day rule</dt><dd>Restrict or flag spend outside expected hours, so unattended overnight activity has to pass a human first.</dd>
  </dl>

  <h2 class="mt40" style="margin-top:56px">Who uses a spend firewall</h2>
  <p class="lead">Any time an autonomous agent holds a payment method, it needs a spending policy it can't override. Common deployments:</p>
  <div class="grid2">
    <div class="card"><h3>Autonomous purchasing agents</h3><p>Agents that buy compute, API credits, ads, or SaaS on their own. sipi.bot enforces the budget the prompt can't be trusted to hold.</p></div>
    <div class="card"><h3>Multi-agent systems</h3><p>Swarms where dozens of agents spend in parallel. A shared daily cap and velocity limit stop the fleet from compounding one mistake. See <a href="/integrations/crewai/">CrewAI</a> and <a href="/for/langchain/">LangChain</a>.</p></div>
    <div class="card"><h3>Agentic payments (x402 / AP2 / AgentKit)</h3><p>Agents transacting over machine-payment rails. sipi.bot is the approval layer in front of the wallet — see the <a href="/alternatives/x402/">x402 approach</a>.</p></div>
    <div class="card"><h3>CI, research &amp; ops agents</h3><p>Background agents that provision infrastructure or pull paid data. The queryable audit log shows exactly what was bought and why.</p></div>
  </div>

  <h2 class="mt40" style="margin-top:56px">What sipi.bot is <em>not</em></h2>
  <p class="lead">Because the name gets misread: <strong>sipi.bot is a payment-control spend firewall for autonomous AI agents.</strong> It is <em>not</em> a SIP/VoIP telephony bot, and it is <em>not</em> an AI-bot-blocking tool or web-application firewall (WAF). It never holds your money — it's a decision API that returns approve, block, or flag with a deterministic rules check, and your existing payment rail is what actually moves (or doesn't move) the funds.</p>
</div></section>

<!-- ═══ EXPERT SECRETS: Origin Story + Epiphany Bridge (Ch 1,4,5,6) ═══ -->
<section id="origin" style="border-bottom:1px solid var(--line)"><div class="wrap">
  <h2>The Night I Almost Shipped a Bankrupt Agent</h2>
  <p class="lead">Every product starts with a wound. This one started at 2:14 AM with a $12,400 log entry I couldn't believe was real.</p>
  
  <div style="max-width:760px;margin:32px auto 0;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:28px">
    <div style="color:var(--mut);font-size:14px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px">The Backstory</div>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:18px">
      I deployed my first autonomous purchasing agent on a Tuesday. It was beautiful — four lines of orchestration, an x402 payment rail, and a prompt that said "buy GPU compute when under 70% utilization." I went to sleep feeling like I'd shipped the future.
    </p>
    
    <div style="color:var(--mut);font-size:14px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px">The Wall</div>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:18px">
      I woke up to Stripe notifications. The agent had hit a rate-limit at 2:14 AM and retried 40 times. It bought compute from a vendor I'd never heard of — <code style="background:rgba(255,84,112,.12);color:var(--red);padding:2px 6px;border-radius:4px;font-size:14px">unknown-gpu.ru</code>. It tipped an API into overage. Total damage: <strong style="color:var(--red)">$12,400</strong>. In seven hours. While I was sleeping.
    </p>

    <div style="color:var(--mut);font-size:14px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px">The Epiphany</div>
    <div style="border-left:3px solid var(--accent);padding:4px 0 4px 18px;margin-bottom:18px">
      <p style="font-size:17px;line-height:1.7;color:var(--txt);font-style:italic">
        "The agent didn't do anything wrong. It followed the prompt. It bought compute when utilization dipped. It retried on failure — exactly what we train agents to do. The problem wasn't the agent. The problem was that <strong>nobody was checking</strong>. The payment rails move money. They don't ask if the merchant is sketchy, if the amount is suspicious, or if forty retries in three minutes is a bug or a feature. There was no firewall."
      </p>
      <p style="font-size:15px;color:var(--accent);margin-top:8px">— Maryan, founder</p>
    </div>

    <div style="color:var(--mut);font-size:14px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px">The Internal Shift</div>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:18px">
      I spent the next week reading every provider's spend-control docs. OpenAI has usage limits — per-provider. Anthropic has rate limits — per-model. Stripe has Radar — for fraud, not agent velocity. Every solution was partial and reactive. You find out <em>after</em>. Nobody was building the thing that says "no" <em>before</em> the money moves.
    </p>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:18px">
      So I stopped looking. I built the missing layer: a spend firewall that sits in front of every transaction, checks it against your rules, and returns approve, block, or flag — with a deterministic rules check. Not a dashboard. Not a report. A decision. Before the money moves.
    </p>

    <div style="color:var(--mut);font-size:14px;text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px">The New Opportunity</div>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:8px">
      The payment rails — x402, AP2, AgentKit — are letting agents spend autonomously. Every week more agents get deployed. Every week the total at-risk spend grows. And <strong>not one of those rails screens transactions before they settle</strong>. That gap — between an agent's ability to spend and your ability to control it — is exactly where sipi.bot lives.
    </p>
    <p style="font-size:17px;line-height:1.7;color:var(--txt)">
      <strong style="color:var(--accent)">This isn't a spending cap. It's a spending policy.</strong> One curl call. One decision. Before a single dollar moves. That's the thing I needed at 2:14 AM. Now it's yours.
    </p>
  </div>

  <div class="kpis mt40" style="max-width:600px;margin-left:auto;margin-right:auto">
    <div class="kpi"><div class="n">$12,400</div><div class="l">loss that inspired sipi.bot</div></div>
    <div class="kpi"><div class="n">1</div><div class="l">founder, shipping in the open</div></div>
    <div class="kpi"><div class="n">MIT</div><div class="l">licensed — self-host forever</div></div>
  </div>
</div></section>

<!-- ═══ The 3 False Beliefs That Keep Your Agent Unguarded (Ch 7) ═══ -->
<section id="false-beliefs"><div class="wrap">
  <h2 class="center">The 3 false beliefs that let agents run wild</h2>
  <p class="lead center">If you're deploying an autonomous agent right now, you probably hold at least one of these. Here's why each one is wrong — and the epiphany that changes everything.</p>
  
  <div style="max-width:760px;margin:36px auto 0;display:flex;flex-direction:column;gap:24px">
    <div class="card">
      <div class="badge b-red" style="margin-bottom:10px">FALSE BELIEF #1 — The Vehicle</div>
      <h3 style="font-size:20px;margin-bottom:8px">"My prompt handles spending — I told it to be careful."</h3>
      <p style="color:var(--mut);margin-bottom:10px"><strong>The False Belief:</strong> A well-written prompt is a spending control. If I just add "don't overspend" to the system prompt, the agent will enforce its own budget.</p>
      <p style="color:var(--accent)"><strong>The Epiphany:</strong> Prompts are suggestions, not controls. An agent in a retry loop, a hallucination, or a prompt injection doesn't "decide" to overspend — it executes what it was instructed to do. Your prompt is a wish. A spend firewall is a rule. Wishes don't survive 2 AM.</p>
    </div>

    <div class="card">
      <div class="badge b-amber" style="margin-bottom:10px">FALSE BELIEF #2 — Internal Belief</div>
      <h3 style="font-size:20px;margin-bottom:8px">"I'll catch it. I check my dashboard every morning."</h3>
      <p style="color:var(--mut);margin-bottom:10px"><strong>The False Belief:</strong> Human review is a spending control. I monitor my agent. If something goes wrong, I'll see it and stop it.</p>
      <p style="color:var(--accent)"><strong>The Epiphany:</strong> By the time you see it, the money is gone. At 2:14 AM, the agent retried 40 times in under three minutes. You woke up at 9:03 AM to $12,400 in Stripe notifications. Human review is not a control — it's a post-mortem. The firewall has to fire in milliseconds, not morning coffee.</p>
    </div>

    <div class="card">
      <div class="badge b-green" style="margin-bottom:10px">FALSE BELIEF #3 — External Belief</div>
      <h3 style="font-size:20px;margin-bottom:8px">"My payment provider handles this — they have fraud detection."</h3>
      <p style="color:var(--mut);margin-bottom:10px"><strong>The False Belief:</strong> Stripe, Coinbase, or my bank will catch suspicious agent spending the same way they catch credit card fraud.</p>
      <p style="color:var(--accent)"><strong>The Epiphany:</strong> Payment providers flag fraud — stolen cards, chargebacks, identity theft. They don't flag "your agent bought compute from a weird vendor 40 times in 3 minutes." To Stripe, that looks like legitimate API usage. The agent is authorized. The spending is the problem. And no payment rail screens for that. sipi.bot is the layer that does.</p>
    </div>
  </div>

  <p class="center mt40" style="font-size:18px;color:var(--txt)">
    Kill all three false beliefs and only one question remains:<br>
    <strong style="color:var(--accent);font-size:20px">which rules does your agent need before it spends its first dollar?</strong>
  </p>
  <p class="center mt24"><a href="/pricing" class="btn">Set my rules →</a></p>
</div></section>

<!-- ═══ The Cause / Movement (Ch 2) ═══ -->
<section id="cause"><div class="wrap">
  <h2 class="center">We are the builders who stopped trusting the prompt.</h2>
  <p class="lead center">A quiet movement of engineers who deploy autonomous agents — and refuse to hope the spending works out.</p>
  <div style="max-width:680px;margin:32px auto 0;background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:24px">
    <p style="font-size:16px;line-height:1.7;color:var(--txt);margin-bottom:14px">
      We shipped agents that buy compute at 3 AM without asking. We woke up to Stripe notifications we couldn't explain. We learned — the hard way — that <strong>prompts are not controls</strong> and payment rails don't screen.
    </p>
    <p style="font-size:16px;line-height:1.7;color:var(--txt);margin-bottom:14px">
      We stopped pretending "be careful" was a spending policy. We built a firewall that says <span style="color:var(--accent)">approve</span>, <span style="color:var(--red)">block</span>, or <span style="color:var(--amber)">flag</span> before a single dollar moves.
    </p>
    <p style="font-size:16px;line-height:1.7;color:var(--txt)">
      <strong>We don't measure in signups. We measure in dollars not spent.</strong> Every blocked transaction is a $12,400 morning that didn't happen. This is not a self-improvement group. This is a shipping movement.
    </p>
  </div>
  <div class="kpis mt40" style="max-width:600px;margin-left:auto;margin-right:auto">
    <div class="kpi"><div class="n">No ML</div><div class="l">in the decision path</div></div>
    <div class="kpi"><div class="n">53/53</div><div class="l">eval scenarios passed</div></div>
    <div class="kpi"><div class="n">$0</div><div class="l">lost to runaway agents</div></div>
  </div>
</div></section>

<section><div class="wrap">
  <h2 class="center">Hope is not a spending policy.</h2>
  <div class="contrast mt24">
    <div class="old">
      <h3 style="color:var(--red)">Without sipi.bot</h3>
      <ul>
        <li>🔴 Agent spends first, you find out later</li>
        <li>🔴 One infinite loop drains the card at 3am</li>
        <li>🔴 No record of why anything was bought</li>
        <li>🔴 "Trust the prompt" is your only control</li>
      </ul>
    </div>
    <div class="new">
      <h3 style="color:var(--green)">With sipi.bot</h3>
      <ul>
        <li>🟢 Every spend checked against your rules first</li>
        <li>🟢 Velocity limits kill runaway loops instantly</li>
        <li>🟢 Queryable audit log of every decision</li>
        <li>🟢 Human-in-the-loop on the transactions that matter</li>
      </ul>
    </div>
  </div>
</div></section>

<section id="pricing"><div class="wrap">
  <h2 class="center">Your agent's spending department.</h2>
  <p class="lead center">Not $0.05 per call. A flat firewall you never think about.</p>

  <!-- VALUE STACK (Brunson DotCom Secrets Secret 18: The Stack) -->
  <div class="valuestack" style="max-width:560px;margin:32px auto 0;padding:28px 24px;border:1px solid var(--line);border-radius:16px;background:var(--panel2)">
    <div style="text-align:center;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:600;margin-bottom:16px">What you actually get</div>
    <ul style="list-style:none;padding:0;margin:0 0 18px;font-size:15px;line-height:2">
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Spend firewall engine (6 rule types, No model call)</span><strong style="color:var(--mut);text-decoration:line-through">$1,200/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Live control-room dashboard + SSE</span><strong style="color:var(--mut);text-decoration:line-through">$400/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Human-in-the-loop approval queue</span><strong style="color:var(--mut);text-decoration:line-through">$300/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Queryable audit log (compliance-grade)</span><strong style="color:var(--mut);text-decoration:line-through">$250/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>MCP tool + HTTP API + CLI (all runtimes)</span><strong style="color:var(--mut);text-decoration:line-through">$150/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>MIT self-host core + onboarding call</span><strong style="color:var(--mut);text-decoration:line-through">$200/mo</strong></li>
    </ul>
    <div style="border-top:1px dashed var(--line);padding-top:14px;display:flex;justify-content:space-between;align-items:baseline">
      <span style="font-size:14px;color:var(--mut)">Total value</span>
      <!-- 2026-07-24: was $1,295/mo — copy-pasted from a different value
      stack elsewhere on this page. This stack's own 6 line items
      (1,200+400+300+250+150+200) sum to $2,500/mo. -->
      <strong style="color:var(--mut);text-decoration:line-through;font-size:18px">$2,500/mo</strong>
    </div>
    <div style="display:flex;justify-content:space-between;align-items:baseline;margin-top:6px">
      <span style="font-size:18px;color:var(--txt);font-weight:600">Your price</span>
      <strong style="color:var(--accent);font-size:32px">$99/mo</strong>
    </div>
    <p style="text-align:center;font-size:12.5px;color:var(--mut);margin:10px 0 0">Same price whether your agent makes 10 or 10,000 decisions. No per-call fees. No overage tier.</p>
  </div>

  <div class="price mt24">
    <div class="amt">$99<span> / month</span></div>
    <div class="strike">Hiring a human to babysit spend: $4,500/mo</div>
    <ul>
      <li><span class="c">✓</span> Unlimited transaction evaluations</li>
      <li><span class="c">✓</span> Per-tx, daily, velocity, merchant, category & time rules</li>
      <li><span class="c">✓</span> Human-in-the-loop approval queue</li>
      <li><span class="c">✓</span> Live dashboard + queryable audit log</li>
      <li><span class="c">✓</span> MCP tool + HTTP API + CLI</li>
      <li><span class="c">✓</span> <strong>Guarantee:</strong> if we green-light a spend that breaks your rule, that month is free</li>
    </ul>
    <a href="/checkout/team?source=homepage_pricing" rel="nofollow" onclick="window.sipiTrack&&window.sipiTrack('cta_clicked',{cta_id:'homepage_team_checkout',destination:'/checkout/team',placement:'homepage_pricing',plan:'team'})" class="btn" style="width:100%">Start Team — $99/mo</a>
    <a href="/playground/" class="btn ghost" style="width:100%;margin-top:10px">Try the live firewall first</a>
    <p style="color:var(--accent);font-size:12px;margin-top:10px;text-align:center">🛡️ Guarantee: green-light a rule violation, month is free</p>
    <p class="mono" style="color:var(--mut);font-size:13px;margin-top:10px">Free self-host core &nbsp;•&nbsp; open on GitHub</p>
  </div>
</div></section>

<!-- TRAFFIC YOU OWN: standalone lead-magnet capture (Brunson Traffic Secrets Secret 5) -->
<section id="get-the-playbook" style="background:linear-gradient(135deg,rgba(0,212,170,.06),rgba(0,212,170,.02));border-top:1px solid rgba(0,212,170,.15);border-bottom:1px solid rgba(0,212,170,.15);padding:48px 0">
  <div class="wrap" style="max-width:680px;text-align:center">
    <span style="display:inline-block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:600;padding:4px 12px;border:1px solid rgba(0,212,170,.3);border-radius:999px;margin-bottom:14px">Free · 5-day email playbook</span>
    <h2 style="margin:0 0 8px">The Spend Firewall Playbook</h2>
    <p style="color:var(--mut);font-size:16px;line-height:1.6;margin:0 0 20px">One email a day for five days. Day 1: the night my agent spent $12,400. Day 2: the six rules that stop it. Day 3: wiring it into your agent. Day 4: the eval suite. Day 5: the deployment checklist. No sales pressure — if the playbook isn't useful, unsubscribe anytime.</p>
    <form class="form" style="max-width:460px;margin:0 auto" onsubmit="return sub(event)">
      <div style="display:flex;gap:8px">
        <label for="pb-em" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden">Email address</label><input type="email" id="pb-em" placeholder="you@company.com" required style="flex:1">
        <button class="btn" type="submit">Send me Day 1 →</button>
      </div>
      <!-- 2026-07-24: removed the "$7 order bump" checkbox here — it posted
      order_bump:true to /subscribe, but the backend never read that field:
      no charge was ever collected and no bump-specific deliverable was ever
      sent. Checked-by-default + silently-dropped is the single worst
      trust/honesty defect on this page. Re-add only once a real $7 Stripe
      price + fulfillment path exists. See conversion-audit-scored-2026-07-24. -->
      <p class="msg-inline" aria-live="polite" style="color:var(--accent);font-size:14px;margin:10px 0 0;text-align:center"></p>
    </form>
    <p style="font-size:12.5px;color:var(--mut);margin:12px 0 0">Joining the list does not sign you up for anything paid. The hosted plan is a separate checkout.</p>
  </div>
</section>

<section id="faq"><div class="wrap">
  <h2 class="center">Frequently asked questions</h2>
  <p class="lead center"><strong>TL;DR:</strong> sipi.bot is a spend firewall for autonomous AI agents. Your agent asks permission before it spends; sipi.bot returns approve, block, or flag with a deterministic rules check based on your rules — over HTTP, MCP, or CLI, for a flat $99/month.</p>
  <div class="faq mt24">
    <details open><summary>What is a spend firewall for AI agents?</summary>
      <p>A <strong>spend firewall</strong> sits in front of every transaction an autonomous AI agent attempts and evaluates it against your rules — approving, blocking, or flagging it before any money moves. sipi.bot returns a decision with a deterministic rules check over HTTP, MCP, or CLI.</p></details>
    <details><summary>How does sipi.bot stop an agent from overspending?</summary>
      <p>Your agent calls sipi.bot before it spends. sipi.bot checks the transaction against per-transaction, daily, velocity, merchant, category, and time rules and returns approve, block, or flag. Velocity limits kill runaway retry loops instantly, and unknown merchants are blocked unless allowlisted.</p></details>
    <details><summary>How much does sipi.bot cost?</summary>
      <p>Hosted plans are flat-rate: Team is <strong>$99/month</strong> and Business is $499/month, both with unlimited transaction evaluations — no per-call fees, no metering, no overage tiers. The open-source core is MIT-licensed and free to self-host forever, and the full plan comparison is on the <a href="/pricing">pricing page</a>.</p></details>
    <details><summary>Does sipi.bot work with MCP and Claude Code?</summary>
      <p>Yes. sipi.bot is a native MCP tool, so Claude Code, Cursor, and Hermes call it directly, and it also exposes a plain HTTP API and a CLI so any agent runtime can use it. Client wrappers for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK take a few lines each.</p></details>
    <details><summary>What happens if sipi.bot wrongly approves a spend?</summary>
      <p>If sipi.bot green-lights a spend that breaks one of your active rules, that month's subscription is free. Every decision is written to a queryable audit log recording the rule that fired, the amount, and the reason, so you can review exactly why anything was approved, blocked, or flagged.</p></details>
    <details><summary>Does sipi.bot support x402, AP2, and Coinbase AgentKit?</summary>
      <p>Yes. sipi.bot sits in front of agentic-payment rails including x402, Google's AP2, and Coinbase AgentKit as the approval layer — your agent asks sipi.bot for a decision before it settles a payment on any of them. It's rail-agnostic because it evaluates the transaction (amount, merchant, category), not the plumbing.</p></details>
    <details><summary>Does sipi.bot hold or move my money?</summary>
      <p>No. sipi.bot is a decision API, not a wallet or a processor. It returns approve, block, or flag; your existing payment rail is what actually moves the funds. That means there's no float, no custody, and nothing new to reconcile — you're only adding a control check in front of what you already use.</p></details>
    <details><summary>Can I self-host sipi.bot?</summary>
      <p>Yes. The core is MIT-licensed and open on <a href="https://github.com/kindrat86/sipi-bot">GitHub</a>, free to self-host forever. The hosted plans add the live dashboard, managed approval queue, and timestamped audit log storage. See the <a href="/self-hosted/">self-hosted guide</a>.</p></details>
    <details><summary>How is this different from my provider's spending cap?</summary>
      <p>A provider cap (OpenAI, Anthropic, a cloud bill) only limits spend <em>on that provider</em>, and usually only tells you after the fact. sipi.bot sits in front of <em>every</em> transaction across every merchant, decides in real time before money moves, and keeps one audit log for all of it — see <a href="/vs/stripe-radar/">how it compares to Stripe Radar</a>.</p></details>
  </div>
</div></section>

<footer class="sipi-resources"><div class="wrap">
  <div style="margin-bottom:16px">
    <strong style="color:var(--txt)">Framework integrations:</strong>
    <a href="/for/langchain/">LangChain</a> · <a href="/integrations/crewai/">CrewAI</a> ·
    <a href="/for/openai-agents/">OpenAI Agents SDK</a> · <a href="/for/vercel-ai-sdk/">Vercel AI SDK</a> ·
    <a href="/for/">all integrations →</a>
  </div>
  <div style="margin-bottom:16px;font-size:13px;line-height:2">
    <strong style="color:var(--txt)">Compare & alternatives:</strong>
    <a href="/vs/hardcoded-check/">vs hardcoded budget check</a> ·
    <a href="/vs/stripe-radar/">vs Stripe Radar</a> ·
    <a href="/alternatives/x402/">x402 alternative</a> ·
    <a href="/self-hosted/">self-hosted / open source</a> ·
    <a href="/benchmarks/">spend benchmarks</a> ·
    <a href="/learn/how-to-control-ai-agent-spending">5 approaches compared</a> ·
    <a href="/best/">best-of comparisons</a>
  </div>
  <div style="margin-bottom:16px;font-size:13px;line-height:2">
    <strong style="color:var(--txt)">Learn & resources:</strong>
    <a href="/learn/spend-firewall-guide">complete guide</a> ·
    <a href="/glossary/">glossary</a> ·
    <a href="/faq/">FAQ</a> ·
    <a href="/answers/">answers hub</a> ·
    <a href="/how-to/">how-to</a> ·
    <a href="/use-cases/">use cases</a> ·
    <a href="/guides/">deep guides</a> ·
    <a href="/checklists/">checklists</a> ·
    <a href="/templates/agent-spend-policy-template">policy template</a>
  </div>
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/eval-report/">Eval report</a> · <a href="/.well-known/agent-card.json">Agent card</a> · <a href="/blog/">Blog</a> · <a href="/about">About</a> · <a href="/security">Security</a> · <a href="/status">Status</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
  <div style="margin-top:14px;color:var(--mut);font-size:13px">Find us where builders are:
    <a href="https://github.com/kindrat86/sipi-bot" rel="me noopener">GitHub</a> ·
    <a href="https://pypi.org/project/sipi-bot/" rel="me noopener">PyPI</a> ·
    <a href="https://x.com/sipiteno" rel="me noopener">X / Twitter</a> ·
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
  </div>
</div></footer>
<script>
function sub(e){e.preventDefault();
var form=e.target;var input=form.querySelector('input[type=email]');var email=input?input.value:'';
var msgEl=form.querySelector('.msg-inline')||document.getElementById('msg');
var ref=document.getElementById('ref')?document.getElementById('ref').value:'';
if(!email){return false;}
var btn=form.querySelector('button[type=submit]');if(btn){btn.disabled=true;var orig=btn.textContent;btn.textContent='Sending...';}
window.sipiTrack&&window.sipiTrack('lead_form_submitted',{asset:'spend_firewall_playbook',placement:'homepage'});
fetch('/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({email:email,ref:ref})})
.then(r=>r.json().then(d=>({ok:r.ok,data:d}))).then(x=>{if(!x.ok)throw new Error(x.data.message||'subscribe_failed');window.sipiTrack&&window.sipiTrack('lead_subscribed',{asset:'spend_firewall_playbook',placement:'homepage'});if(msgEl){msgEl.textContent=x.data.message||'You are on the list.';}if(input){input.value='';}if(btn){btn.disabled=false;btn.textContent=orig;}})
.catch((err)=>{window.sipiTrack&&window.sipiTrack('lead_subscription_failed',{asset:'spend_firewall_playbook',failure_type:'request'});if(msgEl){msgEl.textContent=err.message==='subscribe_failed'?'Something went wrong — please try again.':err.message;}if(btn){btn.disabled=false;btn.textContent=orig;}});
return false;}
(function(){
var run=document.getElementById('hero-run-check'),copy=document.getElementById('hero-copy-check');
var result=document.getElementById('hero-live-result'),next=document.getElementById('hero-live-next');
var command="curl -X POST https://sipi.bot/v1/transactions/evaluate -H 'Content-Type: application/json' -d '{\\"amount\\":12400,\\"currency\\":\\"USD\\",\\"merchant\\":\\"example-vendor\\"}'";
if(copy)copy.addEventListener('click',function(){navigator.clipboard.writeText(command).then(function(){copy.textContent='Copied';window.sipiTrack&&window.sipiTrack('cta_clicked',{cta_id:'homepage_curl_copy',destination:'clipboard',placement:'live_proof'});});});
if(run)run.addEventListener('click',function(){run.disabled=true;run.textContent='Checking…';result.style.display='block';result.textContent='Evaluating against the live firewall…';next.style.display='none';fetch('/v1/transactions/evaluate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:12400,currency:'USD',merchant:'example-vendor'})}).then(function(r){return r.json().then(function(d){return{ok:r.ok,data:d};});}).then(function(x){if(!x.ok)throw new Error('evaluation_failed');result.textContent=(x.data.decision||'UNKNOWN')+' — '+(x.data.reason||'No reason returned');next.style.display='block';window.sipiTrack&&window.sipiTrack('homepage_live_evaluation_completed',{decision:(x.data.decision||'unknown').toLowerCase(),amount_bucket:'2000_plus'});}).catch(function(){result.textContent='The live check could not run. Please try the playground.';window.sipiTrack&&window.sipiTrack('homepage_live_evaluation_failed',{failure_type:'request'});}).finally(function(){run.disabled=false;run.textContent='Run this live check';});});
})();
</script>
<!-- BY THE NUMBERS — honest product facts (audit 2026-07-27). No synthetic
     testimonials: the prior quotes were removed 2026-07-21 for lacking real
     attribution. This block states only verifiable facts from the repo and
     the public eval. Restore named-customer proof only with real attribution. -->
<section class="by-numbers" aria-label="sipi.bot by the numbers">
  <div class="wrap">
    <h2 class="center">By the numbers</h2>
    <p class="center quiet" style="max-width:640px;margin:0 auto 28px">No vanity metrics, no inflated claims, no fabricated testimonials. These are facts you can verify yourself.</p>
    <div class="numbers-grid">
      <div class="number-card">
        <div class="number">53/53</div>
        <div class="number-label">public eval scenarios passing <a href="/eval-report/">→ verify</a></div>
      </div>
      <div class="number-card">
        <div class="number">MIT</div>
        <div class="number-label">open-source core, free to self-host <a href="https://github.com/kindrat86/sipi-bot">→ source</a></div>
      </div>
      <div class="number-card">
        <div class="number">230+</div>
        <div class="number-label">docs, integration & benchmark pages</div>
      </div>
      <div class="number-card">
        <div class="number">3</div>
        <div class="number-label">ways to call it: HTTP API, MCP tool, CLI</div>
      </div>
    </div>
    <p class="center quiet" style="margin-top:24px;font-size:0.875rem">A deterministic rules engine — no model in the decision path. <a href="/security">How sipi.bot handles security →</a></p>
  </div>
</section>
<style>
.by-numbers { padding: 56px 0 48px; border-top: 1px solid var(--line); }
.by-numbers h2 { font-size: 2rem; margin-bottom: 8px; }
.numbers-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  max-width: 960px;
  margin: 0 auto;
}
.number-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 24px 16px;
  text-align: center;
}
.number {
  font-size: 2.25rem;
  font-weight: 800;
  color: var(--accent);
  line-height: 1.1;
  margin-bottom: 8px;
}
.number-label {
  font-size: 0.875rem;
  color: var(--txt);
  opacity: 0.8;
  line-height: 1.4;
}
.number-label a { color: var(--accent); }
@media (max-width: 760px) {
  .numbers-grid { grid-template-columns: repeat(2, 1fr); }
  .number { font-size: 1.75rem; }
}
</style>
</body></html>"""
    s = s.replace("{CSS}", CSS)
    s = s.replace("{POSTHOG}", POSTHOG_SNIPPET)
    s = s.replace("{GA4_SNIPPET}", GA4_SNIPPET)
    # Keep the source history available for editorial review while shipping a
    # focused conversion page. These sections repeated the same founder story
    # and unsupported persuasion framing already established above.
    origin_start = s.find("<!-- ═══ EXPERT SECRETS: Origin Story")
    hope_start = s.find('<section><div class="wrap">\n  <h2 class="center">Hope is not')
    if origin_start >= 0 and hope_start > origin_start:
        s = s[:origin_start] + s[hope_start:]
    value_start = s.find("<!-- VALUE STACK")
    price_start = s.find('<div class="price mt24">', value_start)
    if value_start >= 0 and price_start > value_start:
        s = s[:value_start] + s[price_start:]
    s = s.replace(
        '<div class="strike">Hiring a human to babysit spend: $4,500/mo</div>',
        "",
    )
    return s


def doc_page_html(title: str, canonical_path: str, description: str, body_html: str) -> str:
    """Reusable EEAT/content page (about, privacy, terms, contact)."""
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>{title} — sipi.bot</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://sipi.bot{canonical_path}">
<link rel="alternate" hreflang="en" href="https://sipi.bot{canonical_path}">
<link rel="alternate" hreflang="en-US" href="https://sipi.bot{canonical_path}">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot{canonical_path}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title} — sipi.bot">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot{canonical_path}">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="sipi.bot — The pre-spend firewall for autonomous AI agents"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title} — sipi.bot">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="https://sipi.bot/og.png">
<meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{title}","url":"https://sipi.bot{canonical_path}","description":"{description}","isPartOf":{{"@type":"WebSite","name":"sipi.bot","url":"https://sipi.bot/"}},"publisher":{{"@type":"Organization","name":"sipi.bot","url":"https://sipi.bot/"}}}}</script>
<style>{CSS}</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap">
  <div class="brand"><a href="/" style="color:var(--txt)">sipi<span class="dot">.bot</span></a></div>
  <div class="nav-links">
    <a href="/#how">How it works</a>
    <a href="/#faq">FAQ</a>
    <a href="/pricing">Pricing</a>
    <a href="/learn/how-to-control-ai-agent-spending">Compare approaches</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>
<section><div class="wrap"><article class="doc">
{body_html}
<p style="margin-top:40px"><a href="/">← Back to sipi.bot</a></p>
</article></div></section>
<footer class="sipi-resources"><div class="wrap">
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/eval-report/">Eval report</a> · <a href="/.well-known/agent-card.json">Agent card</a> · <a href="/blog/">Blog</a> · <a href="/about">About</a> · <a href="/security">Security</a> · <a href="/status">Status</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
  <div style="margin-top:14px;color:var(--mut);font-size:13px">
    <a href="/benchmarks/">Benchmarks</a> ·
    <a href="/best/">Best-of comparisons</a> ·
    Find us where builders are:
    <a href="https://github.com/kindrat86/sipi-bot" rel="me noopener">GitHub</a> ·
    <a href="https://pypi.org/project/sipi-bot/" rel="me noopener">PyPI</a> ·
    <a href="https://x.com/sipiteno" rel="me noopener">X / Twitter</a> ·
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
  </div>
</div></footer>
</body></html>"""


ABOUT_BODY = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"Person","@id":"https://sipi.bot/about/#person","name":"Maryan","url":"https://sipi.bot/about","description":"Founder and builder of sipi.bot — the spend firewall for autonomous AI agents. AI infrastructure engineer based in Kifisia, Greece, building agent-economy tools since 2024.","jobTitle":"Founder","worksFor":{"@type":"Organization","name":"sipi.bot","url":"https://sipi.bot/"},"knowsAbout":["AI Agent Spend Control","Autonomous Agent Payment Firewall","x402 Payment Protocol","Model Context Protocol","Agent Transaction Monitoring","API Spend Governance"],"sameAs":["https://github.com/kindrat86","https://x.com/sipiteno","https://pypi.org/user/kindrat86/"]}</script>
<h1>About sipi.bot</h1>
<p class="lead">sipi.bot is the spend firewall for autonomous AI agents — the control layer that evaluates every transaction an agent attempts and returns approve, block, or flag before any money moves. Built for the agent economy, open-source (MIT), and free to self-host.</p>

<h2>Why we built it</h2>
<p>The agent economy handed autonomous software real spending power — API credits, compute, SaaS, payments — usually backed by a human's credit card and no hard limit. Runaway retry loops and unattended purchase chains are failure modes worth testing before an agent receives live payment access. We built sipi.bot because every autonomous agent deserves a guardrail, and every operator deserves to sleep without checking their bank balance.</p>

<h2>What sipi.bot does</h2>
<p>sipi.bot sits in front of every transaction an autonomous AI agent attempts. One HTTP call — <code>POST /v1/transactions/evaluate</code> — evaluates the proposed spend against your rules and returns APPROVED, BLOCKED, or FLAGGED with a deterministic rules check. Six rule types are enforced: per-transaction caps, daily totals, velocity limits (runaway-loop protection), merchant allow/block lists, category limits, and time-window constraints. Every decision is written to a queryable audit log, and transactions that need human judgment are routed to an approval queue — not auto-approved and not silently blocked.</p>

<h2>How it works</h2>
<p>You define rules: "Max $500 per transaction," "Max $2,000 per day," "Block any merchant matching *.ru," "Require human approval above $1,000." Your agent calls sipi.bot before it spends money. sipi.bot evaluates every active rule in priority order. The first BLOCK rule that matches stops the transaction instantly — no money moves. FLAGGED transactions enter the human-in-the-loop queue. APPROVED transactions proceed. The entire decision path is logged, timestamped, and auditable.</p>

<h2>Surfaces</h2>
<ul>
  <li><strong>HTTP API</strong> — <code>POST /v1/transactions/evaluate</code> with JSON body, returns JSON decision. Works with any agent runtime.</li>
  <li><strong>MCP Server</strong> — Native Model Context Protocol tool. Claude Code, Cursor, and Hermes call <code>evaluate_transaction</code> directly.</li>
  <li><strong>CLI</strong> — <code>pip install sipi-bot && sipi-guard</code> for shell scripts, CI pipelines, and cron jobs.</li>
  <li><strong>Agent Card</strong> — <code>/.well-known/agent-card.json</code> for A2A (Agent-to-Agent) discovery.</li>
</ul>

<h2>Pricing</h2>
<p>Flat-rate, no per-call fees. Team: $99/month. Business: $499/month. Both include unlimited transaction evaluations. The open-source core is MIT-licensed and free to self-host forever — same rule engine, same latency, no limits.</p>

<h2>Who's behind it</h2>
<p>sipi.bot was built by <strong>Maryan</strong>, a solo founder and AI infrastructure engineer based in Kifisia, Greece. Maryan has been building in the agent-economy stack since 2024 — spend controls, payment protocols (x402, AP2), MCP tooling, and compliance infrastructure. Previously built sanctions screening tools for AI agent payments (sanctionsai.dev) and churn analytics (churnlens.site).</p>

<h2>Open source</h2>
<p>The sipi.bot core is open-source under the MIT license. The rule engine, MCP server, CLI, and evaluation logic are all public at <a href="https://github.com/kindrat86/sipi-bot">github.com/kindrat86/sipi-bot</a>. The hosted version layers billing, dashboard, and approval-queue persistence on top of the same engine.</p>
"""


DREAM100_BODY = """<h1>Dream 100 — Where Agent-Builders Already Gather</h1>
<p class="lead">Russell Brunson says: <em>"Identify your Dream 100, serve them before you ask."</em> Our dream customers — developers deploying autonomous agents that can spend money — already congregate in these communities, protocols, and platforms. We show up, contribute, and serve first.</p>

<h2>Tier 1 — Agent Payment Infrastructure (20)</h2>
<p>The protocols and SDKs our customers already build on. We contribute, document, and build alongside them.</p>
<ul>
  <li><strong>x402 Working Group</strong> — the payment protocol for AI agents</li>
  <li><strong>Coinbase AgentKit</strong> — agent wallet & payment SDK</li>
  <li><strong>Anthropic Agent SDK</strong> — Claude agent framework</li>
  <li><strong>OpenAI Agents SDK</strong> — GPT agent orchestration</li>
  <li><strong>Google AP2</strong> — agent-to-agent payment protocol</li>
  <li><strong>LangChain / LangGraph</strong> — agent orchestration framework</li>
  <li><strong>CrewAI</strong> — multi-agent framework</li>
  <li><strong>Model Context Protocol (MCP)</strong> — agent tooling standard</li>
  <li><strong>Stripe Agent Toolkit</strong> — payment tooling for agents</li>
  <li><strong>Vercel AI SDK</strong> — agent streaming & tool calls</li>
</ul>

<h2>Tier 2 — Developer Communities (30)</h2>
<p>Where agent developers congregate, ask questions, and share builds. We answer questions, ship tools, and earn trust.</p>
<ul>
  <li><strong>r/LocalLLaMA</strong> (500K+) — local agent deployments</li>
  <li><strong>r/AI_Agents</strong> (200K+) — agent building community</li>
  <li><strong>r/LangChain</strong> (150K+) — LangChain users</li>
  <li><strong>Hacker News</strong> — dev news & Show HN launches</li>
  <li><strong>Indie Hackers</strong> — founder/developer community</li>
  <li><strong>r/MachineLearning</strong> (3M+) — ML practitioners</li>
  <li><strong>r/OpenAI</strong> (300K+) — OpenAI developer community</li>
  <li><strong>r/singularity</strong> (500K+) — AI acceleration</li>
  <li><strong>GitHub Trending (Python/TypeScript)</strong> — repo discovery</li>
  <li><strong>PyPI</strong> — Python package distribution</li>
</ul>

<h2>Tier 3 — Newsletters, Podcasts & Publications (15)</h2>
<p>The voices agent developers trust. We pitch, contribute, and share research.</p>
<ul>
  <li><strong>Latent Space</strong> — AI engineering podcast & newsletter</li>
  <li><strong>The Sequence</strong> — AI research newsletter</li>
  <li><strong>TLDR AI</strong> — daily AI newsletter (500K+ subs)</li>
  <li><strong>BensBites</strong> — AI product newsletter</li>
  <li><strong>AlphaSignal</strong> — ML practitioner newsletter</li>
  <li><strong>Practical AI</strong> — podcast for ML engineers</li>
  <li><strong>AI Engineer Summit</strong> — conference & community</li>
</ul>

<h2>How We Serve the Dream 100</h2>
<div class="how-grid">
  <div class="how-card"><h3>1. Build in Public</h3><p>We open-source our eval harness, MCP server, and x402 integration examples. Contribution first, promotion never.</p></div>
  <div class="how-card"><h3>2. Contribute First</h3><p>Documentation, bug reports, and compatibility patches flow upstream to the frameworks our customers use.</p></div>
  <div class="how-card"><h3>3. Feature Them</h3><p>Our Dream 100 members are referenced in our docs, examples, and case studies — not as name-drops, but as the foundation our product sits on.</p></div>
</div>

<div class="cta-box">
  <h2>Think you belong on this list?</h2>
  <p>If you build agent infrastructure, tooling, or community and want to integrate spend controls, reach out.</p>
  <a href="mailto:dom@carshake.online" class="btn">Get in touch →</a>
</div>

<style>
.how-grid{display:grid;gap:16px;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));margin:20px 0}
.how-card{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px}
.how-card h3{margin:0 0 8px;font-size:1rem;color:#e2e8f0}
.how-card p{margin:0;font-size:.88rem;color:#64748b;line-height:1.6}
.cta-box{background:linear-gradient(135deg,rgba(99,102,241,.08),rgba(99,102,241,.02));border:1px solid rgba(99,102,241,.15);border-radius:16px;padding:32px;text-align:center;margin:40px 0}
.lead{font-size:1.05em;color:#94a3b8;margin:0 0 32px;line-height:1.6}
</style>
"""

CALENDAR_BODY = """<h1>Content Calendar — sipi.bot Publishing Schedule</h1>
<p class="lead">What we ship, when we ship it — across the agent-spending frontier. Every piece of content is designed to surface on one of the three channels our Dream 100 customers already use: developer communities, protocol documentation, and agent-builder newsletters.</p>

<div class="stats-grid">
  <div class="stat"><div class="stat-num">Weekly</div><div class="stat-label">Eval report refresh</div></div>
  <div class="stat"><div class="stat-num">Monthly</div><div class="stat-label">x402 integration tests</div></div>
  <div class="stat"><div class="stat-num">Quarterly</div><div class="stat-label">Agent-spend benchmark</div></div>
  <div class="stat"><div class="stat-num">No ML</div><div class="stat-label">Deterministic decision path</div></div>
</div>

<h2>Weekly Publishing</h2>
<div class="cal-box">
  <div class="cal-grid">
    <div class="cal-row"><span class="cal-day">Monday</span><span class="cal-topic">Eval harness refresh<div class="cal-desc">The open-source eval suite runs against the latest model releases. Results published at /eval-report.</div></span></div>
    <div class="cal-row"><span class="cal-day">Wednesday</span><span class="cal-topic">MCP server compatibility test<div class="cal-desc">Test sipi.bot's MCP tool against the latest Claude Desktop, Cursor, and Hermes releases.</div></span></div>
    <div class="cal-row"><span class="cal-day">Friday</span><span class="cal-topic">GitHub release notes<div class="cal-desc">Open-source changelog: new rules, performance improvements, integration fixes.</div></span></div>
  </div>
</div>

<h2>Monthly Publishing</h2>
<div class="cal-box">
  <div class="cal-grid">
    <div class="cal-row"><span class="cal-day">Week 1</span><span class="cal-topic">x402 integration examples<div class="cal-desc">New payment-rail integration patterns: Stripe Agent Toolkit, Coinbase AgentKit, Google AP2.</div></span></div>
    <div class="cal-row"><span class="cal-day">Week 2</span><span class="cal-topic">Agent-framework guides<div class="cal-desc">How to wire sipi.bot into CrewAI, LangGraph, AutoGen, and custom agent loops.</div></span></div>
    <div class="cal-row"><span class="cal-day">Week 3</span><span class="cal-topic">Spend-control deep dives<div class="cal-desc">Per-rule deep dives: velocity limits, merchant allowlisting, category rules, time-of-day gates.</div></span></div>
    <div class="cal-row"><span class="cal-day">Week 4</span><span class="cal-topic">Community showcase<div class="cal-desc">Self-hosted deployments, unusual use cases, and agent-spend horror stories from the community.</div></span></div>
  </div>
</div>

<h2>Quarterly Publishing</h2>
<div class="cal-box">
  <div class="cal-grid">
    <div class="cal-row"><span class="cal-day">Q1/Q2/Q3/Q4</span><span class="cal-topic">Agent-Spend Frontier Benchmark<div class="cal-desc">Aggregate, anonymized data from the hosted service: average transaction sizes, block rates, rule-trigger patterns, and emerging merchant categories.</div></span></div>
    <div class="cal-row"><span class="cal-day">Quarterly</span><span class="cal-topic">Open-source release<div class="cal-desc">New stable release with all accumulated fixes and features from the hosted service.</div></span></div>
  </div>
</div>

<h2>Distribution Channels</h2>
<div class="cal-box">
  <div class="cal-grid">
    <div class="cal-row"><span class="cal-day">Per release</span><span class="cal-topic"><span class="tag">GitHub</span> <span class="tag">PyPI</span><div class="cal-desc">MIT-licensed core at github.com/kindrat86/sipi-bot, pip-installable via PyPI.</div></span></div>
    <div class="cal-row"><span class="cal-day">Ongoing</span><span class="cal-topic"><span class="tag">MCP</span> <span class="tag">A2A</span> <span class="tag">NLWeb</span><div class="cal-desc">Agent-native distribution: MCP server, A2A endpoint, NLWeb endpoint — free in perpetuity.</div></span></div>
    <div class="cal-row"><span class="cal-day">Per launch</span><span class="cal-topic"><span class="tag">Hacker News</span> <span class="tag">r/LocalLLaMA</span><div class="cal-desc">Show HN launches and community posts for major releases.</div></span></div>
    <div class="cal-row"><span class="cal-day">Ongoing</span><span class="cal-topic"><span class="tag">X/Twitter</span> <span class="tag">GitHub</span><div class="cal-desc">@sipiteno on X, GitHub Discussions for community support.</div></span></div>
  </div>
</div>

<style>
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:12px;margin:20px 0}
.stat{background:#1e293b;border:1px solid #334155;border-radius:10px;padding:16px;text-align:center}
.stat-num{font-size:1.8rem;font-weight:800;color:var(--accent);line-height:1.2}
.stat-label{font-size:.78rem;color:#64748b;margin-top:4px}
.cal-box{background:#1e293b;border:1px solid #334155;border-radius:12px;padding:20px 24px;margin:0 0 28px}
.cal-grid{display:grid;gap:4px;margin:12px 0}
.cal-row{display:grid;grid-template-columns:120px 1fr;gap:12px;padding:8px 0;border-bottom:1px solid #1e293b;font-size:.9rem}
.cal-row:last-child{border-bottom:none}
.cal-day{font-weight:700;color:var(--accent);font-size:.85rem;padding-top:2px}
.cal-topic{color:#e2e8f0}
.cal-desc{color:#64748b;font-size:.82rem;margin-top:2px}
.tag{display:inline-block;background:rgba(0,212,170,.15);color:#00d4aa;padding:2px 8px;border-radius:6px;font-size:.75rem;font-weight:600;margin-right:6px}
</style>
"""

PRIVACY_BODY = """<h1>Privacy Policy</h1>
<p class="lead">Last updated: 2026. sipi.bot collects the minimum data needed to evaluate transactions and operate the service.</p>
<h2>What we process</h2>
<p>When your agent submits a transaction for evaluation, we process the transaction metadata you send (amount, merchant, category, timestamps) to apply your rules and write an audit record. We do not store card numbers or payment credentials — sipi.bot is a decision layer, not a payment processor.</p>
<h2>Account data</h2>
<p>If you subscribe, we store your email and billing status (via Stripe). Stripe processes payment details under its own privacy policy; we never see full card data.</p>
<h2>Analytics</h2>
__ANALYTICS_DISCLOSURE__
<h2>Data retention & deletion</h2>
<p>Audit logs are retained for your account's configured window. To request export or deletion of your data, contact us via <a href="https://github.com/kindrat86/sipi-bot">GitHub</a>.</p>
<h2>Self-hosting</h2>
<p>If you self-host the open-source core, your transaction data never leaves your infrastructure and this policy does not apply to that deployment.</p>"""

_POSTHOG_DISCLOSURE = (
    "<p>With your explicit permission, we load "
    "<a href=\"https://posthog.com/privacy\" rel=\"noopener\" target=\"_blank\">PostHog</a> "
    "(EU region) for anonymous product analytics. Analytics stay off until you choose "
    "<strong>Allow analytics</strong>. Autocapture and session recording are disabled, "
    "anonymous visitor profiles are not created, and selecting <strong>No thanks</strong> "
    "does not affect the product. You can reopen the choice at any time using the "
    "<strong>Privacy choices</strong> button.</p>"
)
_NO_ADS_DISCLOSURE = (
    "<p>We run no advertising or retargeting pixels of any kind — no Meta, Reddit, LinkedIn, "
    "TikTok or Google Ads tags. You can block all of the above with any standard tracker blocker "
    "without affecting how the site works.</p>"
)
ANALYTICS_DISCLOSURE = _POSTHOG_DISCLOSURE + _NO_ADS_DISCLOSURE
PRIVACY_BODY = PRIVACY_BODY.replace("__ANALYTICS_DISCLOSURE__", ANALYTICS_DISCLOSURE)

# Security & status pages (audit 2026-07-27). Every claim below is verifiable
# from the production response headers, the open-source repo, or the public
# health endpoint. The "not yet in place" section is deliberately explicit —
# overstating compliance posture would be worse than the gap.
SECURITY_BODY = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","@id":"https://sipi.bot/security/#faq","mainEntity":[{"@type":"Question","name":"Does sipi.bot store credit card numbers?","acceptedAnswer":{"@type":"Answer","text":"No. sipi.bot is a decision layer, not a payment processor. Card data is handled entirely by Stripe under its own PCI-DSS compliance. sipi.bot only receives transaction metadata (amount, merchant, category) to evaluate against your rules."}},{"@type":"Question","name":"Is the sipi.bot source code public?","acceptedAnswer":{"@type":"Answer","text":"Yes. The core rules engine is open source under the MIT license at github.com/kindrat86/sipi-bot, so the decision logic and data handling are auditable."}},{"@type":"Question","name":"What security headers does sipi.bot set?","acceptedAnswer":{"@type":"Answer","text":"Every response ships HSTS with preload, a strict Content-Security-Policy, X-Content-Type-Options nosniff, X-Frame-Options DENY, a restrictive Permissions-Policy, and Cross-Origin isolation headers (COOP/COEP). Trusted Types are required for scripts."}},{"@type":"Question","name":"Does sipi.bot have a SOC 2 or ISO 27001 certification?","acceptedAnswer":{"@type":"Answer","text":"Not yet. sipi.bot is a solo-founded product that has not yet completed a SOC 2, ISO 27001, or formal penetration test. We state this plainly rather than imply compliance we do not hold."}}]}</script>
<h1>Security</h1>
<p class="lead">sipi.bot sits in front of payment decisions, so its security posture matters. This page states what is in place today — and, just as importantly, what is not.</p>

<h2>The model: a decision layer, not a payment processor</h2>
<p>sipi.bot never touches card data. It receives transaction <em>metadata</em> — amount, merchant, category — evaluates it against your rules, and returns <code>APPROVED</code>, <code>BLOCKED</code>, or <code>FLAGGED</code>. All payment credentials are handled by your payment provider (Stripe, an x402 wallet, etc.) under <em>their</em> security perimeter. sipi.bot is the gate in front of that provider, not the provider itself.</p>

<h2>Open source &amp; auditable</h2>
<p>The core rules engine is public under the MIT license at <a href="https://github.com/kindrat86/sipi-bot">github.com/kindrat86/sipi-bot</a>. The decision logic — what triggers a block, how velocity is counted, how rules are evaluated — is fully readable. There is no proprietary model in the decision path: the engine is deterministic.</p>

<h2>Transport &amp; response headers (in production now)</h2>
<p>Every response from <code>sipi.bot</code> ships these headers. You can verify them yourself with <code>curl -I https://sipi.bot/</code>:</p>
<table class="sec-table">
  <thead><tr><th>Header</th><th>Value</th></tr></thead>
  <tbody>
    <tr><td>Strict-Transport-Security</td><td><code>max-age=63072000; includeSubDomains; preload</code></td></tr>
    <tr><td>Content-Security-Policy</td><td>strict <code>default-src 'self'</code>; scripts limited to self, Stripe, and PostHog (EU); <code>require-trusted-types-for 'script'</code></td></tr>
    <tr><td>X-Content-Type-Options</td><td><code>nosniff</code></td></tr>
    <tr><td>X-Frame-Options</td><td><code>DENY</code> (no clickjacking)</td></tr>
    <tr><td>Referrer-Policy</td><td><code>strict-origin-when-cross-origin</code></td></tr>
    <tr><td>Permissions-Policy</td><td><code>camera=(), microphone=(), geolocation=(), payment=(), usb=(), browsing-topics=(), interest-cohort=()</code></td></tr>
    <tr><td>Cross-Origin-* </td><td><code>COOP: same-origin</code>, <code>COEP: credentialless</code></td></tr>
  </tbody>
</table>

<h2>Infrastructure</h2>
<p>Hosted on <a href="https://fly.io/">Fly.io</a> (single region: <code>iad</code>). Application state is held on an encrypted Fly volume. The public status of the underlying platform is at <a href="https://status.fly.io/">status.fly.io</a>; sipi.bot's own health endpoint is documented at <a href="/status">/status</a>.</p>

<h2>Self-hosting</h2>
<p>If you self-host the MIT-licensed core, transaction data never leaves your infrastructure and none of the hosted controls above apply — you own the full security perimeter. This is the right choice for workloads with hard data-residency requirements.</p>

<h2>What is <em>not</em> yet in place</h2>
<p>We believe in stating this plainly rather than implying compliance we do not hold:</p>
<ul>
  <li><strong>No SOC 2, ISO 27001, or HIPAA certification</strong> has been completed.</li>
  <li><strong>No formal third-party penetration test</strong> has been performed. The codebase is public and open to community review, but that is not equivalent to a paid pentest.</li>
  <li><strong>No published vulnerability-disclosure policy (VDP) or bug bounty.</strong> If you find a security issue, please report it responsibly to <a href="mailto:sales@sipiteno.com">sales@sipiteno.com</a>.</li>
  <li><strong>No SSO/SAML</strong> for the hosted dashboard.</li>
</ul>

<h2>Reporting a vulnerability</h2>
<p>Email <a href="mailto:sales@sipiteno.com">sales@sipiteno.com</a> with details and reproduction steps. For sensitive reports, you may also open a private security advisory on the <a href="https://github.com/kindrat86/sipi-bot/security/advisories/new">GitHub repository</a>. We acknowledge reports within two business days.</p>

<p class="quiet">For procurement and security questionnaires, contact <a href="mailto:sales@sipiteno.com">sales@sipiteno.com</a>.</p>"""

STATUS_BODY = """<script type="application/ld+json">{"@context":"https://schema.org","@type":"WebPage","@id":"https://sipi.bot/status","name":"System Status — sipi.bot","url":"https://sipi.bot/status","description":"sipi.bot service status: live health endpoint, platform status, and uptime expectations."}</script>
<h1>System Status</h1>
<p class="lead">sipi.bot exposes a live health endpoint and runs on Fly.io. This page tells you how to check status yourself and what to realistically expect.</p>

<h2>Live health check</h2>
<p>The service exposes a JSON health endpoint you can poll directly:</p>
<pre><code>curl https://sipi.bot/health</code></pre>
<p>Returns, when healthy:</p>
<pre><code>{"ok": true, "service": "sipi.bot", "version": "0.1.0"}</code></pre>
<p>If <code>ok</code> is not <code>true</code> or the request times out, the service is degraded.</p>

<h2>Platform status</h2>
<p>sipi.bot runs on <a href="https://fly.io/">Fly.io</a> in the <code>iad</code> (Northern Virginia) region. The real-time status of the underlying platform — including regional incidents that would affect sipi.bot — is published at <a href="https://status.fly.io/">status.fly.io</a>.</p>

<h2>What to expect</h2>
<ul>
  <li><strong>Decision latency:</strong> the rule engine is deterministic and returns in single-digit milliseconds. End-to-end latency depends on your distance from the <code>iad</code> region — measure from your deployment before relying on a number.</li>
  <li><strong>Availability:</strong> the hosted service is run as a best-effort solo product. There is no contracted SLA on Team or Business plans, and we do not publish a historical uptime figure we cannot independently verify. If you need an SLA, <a href="mailto:sales@sipiteno.com">ask</a>.</li>
  <li><strong>Maintenance:</strong> scheduled changes are announced in advance on <a href="https://x.com/sipiteno">X (@sipiteno)</a> when they may cause brief unavailability.</li>
</ul>

<h2>Incident history</h2>
<p>We do not yet maintain a public incident log. Significant incidents will be posted here with a timestamp, impact, and root cause.</p>

<p class="quiet">Questions about reliability for a specific integration? <a href="mailto:sales@sipiteno.com">Get in touch</a>.</p>"""

TERMS_BODY = """<h1>Terms of Service</h1>
<p class="lead">Last updated: 2026. By using sipi.bot you agree to these terms.</p>
<h2>The service</h2>
<p>sipi.bot evaluates transactions your agent submits against rules you configure and returns a decision (approve, block, or flag). It is a decision and control layer; it does not itself move money.</p>
<h2>Your responsibilities</h2>
<p>You are responsible for the rules you configure and for how your agent acts on sipi.bot's decisions. You must not use sipi.bot to facilitate unlawful transactions.</p>
<h2>Rule-integrity guarantee</h2>
<p>If sipi.bot returns "approve" for a transaction that violated one of your active rules, that month's subscription is refunded. This guarantee covers rule-evaluation errors only, not losses from rules you did not configure or from acting against a "block"/"flag" decision.</p>
<h2>Availability</h2>
<p>We aim for high availability but provide the hosted service "as is" without warranty. For mission-critical deployments, the open-source core is self-hostable.</p>
<h2>Changes</h2>
<p>We may update these terms; material changes will be reflected by the "last updated" date above.</p>"""


def dashboard_html() -> str:
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>sipi.bot — Control Room</title>
<meta name="description" content="Live control room for your AI agent's spending: real-time transaction feed, approval queue, rule editor, and agent management. See every approve, block, and flag.">
<link rel="canonical" href="https://sipi.bot/dashboard">
<meta property="og:title" content="sipi.bot Control Room — Live agent spend monitoring">
<meta property="og:description" content="Real-time transaction feed, approval queue, rule editor, and agent management for your spend firewall.">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot/dashboard"><meta property="og:image" content="https://sipi.bot/og.png"><meta name="robots" content="index, follow"><meta name="theme-color" content="#00d4aa">
<style>{CSS}
.tabs{{display:flex;gap:6px;border-bottom:1px solid var(--line);margin-bottom:24px;overflow-x:auto}}
.tab{{padding:12px 18px;cursor:pointer;color:var(--mut);border:0;border-bottom:2px solid transparent;white-space:nowrap;background:transparent;font:inherit}}
.tab.on{{color:var(--txt);border-bottom-color:var(--accent)}}
.pane{{display:none}}.pane.on{{display:block}}
.feed{{display:flex;flex-direction:column;gap:8px}}
.row{{display:flex;align-items:center;gap:12px;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-size:14px}}
.row .amt{{font-weight:700;min-width:90px}}
.row .meta{{color:var(--mut);flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.row .t{{color:var(--mut);font-size:12px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}
th,td{{text-align:left;padding:10px 12px;border-bottom:1px solid var(--line)}}
th{{color:var(--mut);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.06em}}
input,select{{background:var(--panel2);border:1px solid var(--line);color:var(--txt);padding:9px 11px;border-radius:8px;font-size:14px}}
.mini{{padding:7px 13px;font-size:13px}}
.connect{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:20px}}
.connect input{{flex:1;min-width:240px}}
.status{{font-size:13px;color:var(--mut)}}
</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span> <span style="color:var(--mut);font-size:13px;font-weight:400">/ control room</span></div>
<div class="nav-links"><a href="/">← Landing</a><a class="btn mini" href="/pricing">Get production access</a></div></div></nav>
<div class="wrap" style="padding-top:28px;padding-bottom:60px">
  <div class="card connect">
    <div style="flex:1;min-width:220px"><strong>Connect your workspace</strong><div class="status">Your API key stays in this browser tab and is sent only to sipi.bot.</div></div>
    <input id="workspace-key" type="password" autocomplete="off" spellcheck="false" placeholder="Paste sk_live_… or sk_sipi_… API key">
    <button class="btn mini" onclick="connectWorkspace()">Connect</button>
    <button class="btn mini ghost" onclick="clearWorkspace()">Clear</button>
    <span class="status" id="workspace-status">Showing labelled sample data</span>
  </div>
  <div class="kpis">
    <div class="kpi"><div class="n" id="k-approved">$1,248</div><div class="l">approved today</div></div>
    <div class="kpi"><div class="n" id="k-blocked">$6,950</div><div class="l">blocked today</div></div>
    <div class="kpi"><div class="n" id="k-pending">1</div><div class="l">pending approvals</div></div>
    <div class="kpi"><div class="n" id="k-agents">1</div><div class="l">workspace</div></div>
  </div>
  <div id="data-mode" style="background:rgba(0,212,170,.1);border:1px solid rgba(0,212,170,.3);border-radius:10px;padding:10px 16px;margin-bottom:16px;text-align:center;font-size:13px;color:var(--accent);font-weight:600">Sample mode — illustrative traffic, never live customer data.</div>
  <div class="tabs mt24">
    <button type="button" class="tab on" data-t="live">Live activity</button>
    <button type="button" class="tab" data-t="approvals">Approvals</button>
    <button type="button" class="tab" data-t="rules">Rules</button>
    <button type="button" class="tab" data-t="test">Test API</button>
  </div>

  <div class="pane on" id="p-live"><div class="feed" id="feed"><p style="color:var(--mut)">Waiting for transactions…</p></div></div>

  <div class="pane" id="p-approvals"><table><thead><tr><th>Amount</th><th>Merchant</th><th>Reason</th><th></th></tr></thead><tbody id="appr"></tbody></table></div>

  <div class="pane" id="p-rules">
    <table><thead><tr><th>Type</th><th>Params</th><th>Action</th><th>Priority</th><th></th></tr></thead><tbody id="rules"></tbody></table>
    <div class="card mt24"><h3>Add a rule</h3>
      <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px;align-items:center">
        <select id="r-type"><option value="per_transaction">per_transaction</option><option value="daily_total">daily_total</option><option value="velocity">velocity</option><option value="merchant_block">merchant_block</option><option value="merchant_allow">merchant_allow</option><option value="category_limit">category_limit</option><option value="approval_threshold">approval_threshold</option></select>
        <input id="r-params" placeholder='{{"max_amount":500}}' style="flex:1;min-width:220px" class="mono">
        <select id="r-action"><option>BLOCKED</option><option>FLAGGED</option></select>
        <input id="r-label" placeholder="label" style="flex:1;min-width:160px">
        <button class="btn mini" onclick="addRule()">Add</button>
      </div>
    </div>
  </div>

  <div class="pane" id="p-test"><div class="card"><h3>Evaluate a transaction</h3>
    <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px">
      <input id="t-amt" type="number" placeholder="amount" value="750" style="width:120px">
      <input id="t-mer" placeholder="merchant" value="unknown-gpu.ru" style="flex:1;min-width:160px">
      <input id="t-cat" placeholder="category" value="compute" style="width:140px">
      <button class="btn mini" onclick="testEval()">Evaluate</button>
    </div>
    <div class="codebox mono mt24" id="t-out">Result appears here…</div>
  </div></div>

  <div style="margin-top:56px;border-top:1px solid var(--line);padding-top:32px">
    <h2 style="font-size:22px;margin-bottom:10px">What the control room shows</h2>
    <p style="color:var(--mut);margin-bottom:14px">This is the private operations view of your spend firewall. Paste the API key delivered after checkout to load only that key's isolated workspace. The counters and activity refresh every 15 seconds.</p>
    <p style="color:var(--mut);margin-bottom:14px"><strong style="color:var(--txt)">Live activity</strong> lists every evaluation with its amount, decision badge, merchant, and the exact rule that produced the decision. <strong style="color:var(--txt)">Approvals</strong> is the human-in-the-loop queue: transactions that crossed your approval threshold wait here until you approve or deny them. <strong style="color:var(--txt)">Rules</strong> is the policy editor with seven rule types — per-transaction caps, daily totals, velocity limits, merchant block and allow lists, category limits, and approval thresholds — each with its own parameters, action, and priority.</p>
    <p style="color:var(--mut);margin-bottom:14px">The <strong style="color:var(--txt)">Test API</strong> tab sends a real request to the same <span class="mono">/v1/transactions/evaluate</span> endpoint your agents call, so you can watch a $750 purchase from an unknown merchant get blocked, then see the decision land in the feed and the audit log. Prefer a guided demo? The <a href="/playground/">public playground</a> runs the same endpoint with preset scenarios, and the <a href="/for/">framework integrations</a> show the five-line client for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK.</p>
    <p style="color:var(--mut)">Every decision shown here is written to the workspace audit log, and the engine behind it passes the public eval suite. Hosting starts at <a href="/pricing">$99/month</a>; the MIT-licensed core can also be <a href="/self-hosted/">self-hosted</a>.</p>
  </div>
</div>
<script>
document.querySelectorAll('.tab').forEach(t=>t.onclick=()=>{{
  document.querySelectorAll('.tab').forEach(x=>x.classList.remove('on'));
  document.querySelectorAll('.pane').forEach(x=>x.classList.remove('on'));
  t.classList.add('on');document.getElementById('p-'+t.dataset.t).classList.add('on');}});
const $=id=>document.getElementById(id);
function money(n){{return '$'+Number(n||0).toLocaleString(undefined,{{maximumFractionDigits:0}});}}
function badge(d){{const c={{APPROVED:'b-green',BLOCKED:'b-red',FLAGGED:'b-amber'}}[d]||'b-green';return '<span class="badge '+c+'">'+d+'</span>';}}
function esc(v){{return String(v==null?'':v).replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));}}
const DEMO_TX=[
  {{amount:6200,decision:'BLOCKED',merchant:'unknown-gpu.example',reason:'Per-transaction cap exceeded',created_at:'2026-01-01T12:04:00Z'}},
  {{amount:248,decision:'APPROVED',merchant:'Cloud compute',reason:'Within policy',created_at:'2026-01-01T11:58:00Z'}},
  {{amount:750,decision:'BLOCKED',merchant:'New infrastructure vendor',reason:'Per-transaction cap exceeded',created_at:'2026-01-01T11:42:00Z'}}
];
const DEMO_AP=[{{id:'demo',amount:250,merchant:'Design API',reason:'Approval threshold reached'}}];
const DEMO_RULES=[
  {{id:'demo1',rule_type:'per_transaction',params:{{max_amount:500}},action:'BLOCKED',priority:100}},
  {{id:'demo2',rule_type:'daily_total',params:{{max_amount:2000}},action:'BLOCKED',priority:90}},
  {{id:'demo3',rule_type:'velocity',params:{{max_count:10,window_seconds:3600}},action:'BLOCKED',priority:80}},
  {{id:'demo4',rule_type:'approval_threshold',params:{{amount:200}},action:'FLAGGED',priority:50}}
];
function workspaceKey(){{return sessionStorage.getItem('sipi_dashboard_key')||'';}}
function authH(){{const t=workspaceKey();return t?{{Authorization:'Bearer '+t}}:{{}};}}
function status(msg,bad){{$('workspace-status').textContent=msg;$('workspace-status').style.color=bad?'var(--danger)':'var(--mut)';}}
function setMode(live){{
  $('data-mode').textContent=live?'Private workspace — scoped to the connected API key.':'Sample mode — illustrative traffic, never live customer data.';
  $('data-mode').style.color=live?'var(--accent)':'var(--accent)';
}}
async function api(path,options){{
  const response=await fetch(path,{{...options,headers:{{...authH(),...(options&&options.headers||{{}})}}}});
  if(response.status===401||response.status===403)throw new Error('That API key is invalid or no longer active.');
  if(!response.ok)throw new Error('Request failed ('+response.status+').');
  return response.json();
}}
function renderStats(s){{
  $('k-approved').textContent=money(s.approved_24h);$('k-blocked').textContent=money(s.blocked_value_24h);
  $('k-pending').textContent=s.pending_approvals;$('k-agents').textContent=s.active_agents||1;
}}
function renderFeed(rows){{
  const f=$('feed');if(!rows.length){{f.innerHTML='<p style="color:var(--mut)">No transactions yet. Try the Test API tab.</p>';return;}}
  f.innerHTML=rows.map(r=>`<div class="row"><span class="amt">${{money(r.amount)}}</span>${{badge(esc(r.decision))}}<span class="meta">${{esc(r.merchant||'—')}} · ${{esc(r.reason||'')}}</span><span class="t">${{esc((r.created_at||'').slice(11,19))}}</span></div>`).join('');
}}
function renderApprovals(rows,demo){{
  $('appr').innerHTML=rows.length?rows.map(r=>`<tr><td>${{money(r.amount)}}</td><td>${{esc(r.merchant||'—')}}</td><td>${{esc(r.reason||'')}}</td><td>${{demo?'<span class="status">sample</span>':`<button class="btn mini" onclick="resolve('${{esc(r.id)}}','approve')">Approve</button> <button class="btn mini ghost" onclick="resolve('${{esc(r.id)}}','deny')">Deny</button>`}}</td></tr>`).join(''):'<tr><td colspan=4 style="color:var(--mut)">Nothing pending.</td></tr>';
}}
function renderRules(rows,demo){{
  $('rules').innerHTML=rows.map(r=>`<tr><td>${{esc(r.rule_type)}}</td><td class="mono">${{esc(JSON.stringify(r.params))}}</td><td>${{badge(esc(r.action))}}</td><td>${{esc(r.priority)}}</td><td>${{demo?'<span class="status">sample</span>':`<button class="btn mini ghost" onclick="delRule('${{esc(r.id)}}')">Delete</button>`}}</td></tr>`).join('');
}}
function sample(){{
  setMode(false);renderStats({{approved_24h:1248,blocked_value_24h:6950,pending_approvals:1,active_agents:1}});
  renderFeed(DEMO_TX);renderApprovals(DEMO_AP,true);renderRules(DEMO_RULES,true);
}}
async function refresh(){{
  if(!workspaceKey()){{sample();return;}}
  try{{
    const [s,tx,ap,rules]=await Promise.all([api('/api/stats'),api('/api/transactions'),api('/api/approvals'),api('/api/rules')]);
    setMode(true);renderStats(s);renderFeed(tx);renderApprovals(ap,false);renderRules(rules,false);
    status('Connected — key is held only for this tab',false);
  }}catch(e){{status(e.message,true);setMode(false);}}
}}
async function connectWorkspace(){{
  const key=$('workspace-key').value.trim();
  if(!key){{status('Paste an API key first.',true);return;}}
  sessionStorage.setItem('sipi_dashboard_key',key);$('workspace-key').value='';
  await refresh();
}}
function clearWorkspace(){{sessionStorage.removeItem('sipi_dashboard_key');$('workspace-key').value='';status('Showing labelled sample data',false);sample();}}
async function resolve(id,d){{
  try{{await api('/api/approvals/'+encodeURIComponent(id),{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{decision:d}})}});await refresh();}}
  catch(e){{status(e.message,true);}}
}}
async function addRule(){{
  if(!workspaceKey()){{status('Connect your API key before editing rules.',true);return;}}
  let p;try{{p=JSON.parse($('r-params').value||'{{}}');}}catch(e){{status('Rule parameters must be valid JSON.',true);return;}}
  try{{await api('/api/rules',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{rule_type:$('r-type').value,params:p,action:$('r-action').value,label:$('r-label').value}})}});$('r-label').value='';await refresh();}}
  catch(e){{status(e.message,true);}}
}}
async function delRule(id){{try{{await api('/api/rules/'+encodeURIComponent(id),{{method:'DELETE'}});await refresh();}}catch(e){{status(e.message,true);}}}}
async function testEval(){{
  if(!workspaceKey()){{status('Connect your API key before sending a private evaluation.',true);return;}}
  try{{
    const d=await api('/v1/transactions/evaluate',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{amount:Number($('t-amt').value),merchant:$('t-mer').value,category:$('t-cat').value}})}});
    $('t-out').textContent=JSON.stringify(d,null,2);await refresh();
  }}catch(e){{$('t-out').textContent=e.message;status(e.message,true);}}
}}
if(workspaceKey()){{status('Reconnecting this tab…',false);refresh();}}else{{sample();}}
setInterval(()=>{{if(workspaceKey())refresh();}},15000);
</script></body></html>"""


def pricing_html() -> str:
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>sipi.bot — Pricing</title>
<meta name="description" content="Flat $99/month for unlimited transaction evaluations, or $499/month for a managed spend policy. No per-call fees. Free self-hostable core. Rule-integrity guarantee.">
<link rel="canonical" href="https://sipi.bot/pricing">
<meta property="og:title" content="sipi.bot Pricing — Flat, no metered surprises">
<meta property="og:description" content="Flat $99/month for unlimited transaction evaluations, or $499/month for a managed spend policy. No per-call fees.">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot/pricing"><meta property="og:image" content="https://sipi.bot/og.png"><meta name="theme-color" content="#00d4aa">
<style>{CSS}</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span></div>
<div class="nav-links"><a href="/">Home</a><a href="/dashboard" class="btn">Dashboard</a></div></div></nav>
<section class="hero" style="padding-top:70px">
  <div class="wrap">
  <span class="tag">Your agent's spending department</span>
  <h1 style="font-size:clamp(28px,5vw,44px)">Flat price. No metered surprises.</h1>
  <p class="sub">Hosted Team gives every agent one deterministic control point,
  unlimited evaluations, and an API key immediately after checkout.</p>
  <!-- Team is the primary hosted offer. Free tools remain a clear secondary path. -->
  <div style="max-width:440px;margin:18px auto 0;text-align:center">
    <div class="price" style="margin:0 auto">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--accent)">Team · recommended</div>
      <div class="amt">$99<span> / month</span></div>
      <ul>
        <li><span class="c">✓</span> Unlimited transaction evaluations</li>
        <li><span class="c">✓</span> All rule types + human approval queue</li>
        <li><span class="c">✓</span> Dashboard, audit log, MCP, HTTP + CLI</li>
        <li><span class="c">✓</span> API key issued immediately after payment</li>
      </ul>
      <a href="/checkout/team?source=pricing_primary" rel="nofollow" onclick="window.sipiTrack&&window.sipiTrack('cta_clicked',{{cta_id:'pricing_team_checkout',destination:'/checkout/team',placement:'pricing_primary',plan:'team'}})" class="btn" style="width:100%">Start Team — $99/mo</a>
      <p style="color:var(--accent);font-size:12px;margin-top:8px;text-align:center">🛡️ Green-light an active-rule violation and that month is free</p>
    </div>
  </div>
  <div class="grid2" style="max-width:820px;margin:30px auto 0;text-align:left">
    <div class="price" style="margin:0;border-color:var(--line)">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)">Playground</div>
      <div class="amt">$0</div>
      <p style="color:var(--mut);font-size:15px;margin:18px 0 14px">Run sample transactions through the live production firewall. No signup, install, or card.</p>
      <a href="/playground/" onclick="window.sipiTrack&&window.sipiTrack('playground_opened',{{source:'pricing'}})" class="btn ghost" style="width:100%">Try the live firewall →</a>
    </div>
    <div class="price" style="margin:0;border-color:var(--line)">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)">Business</div>
      <div class="amt">$499<span> / month</span></div>
      <ul>
        <li><span class="c">✓</span> Everything in Team</li>
        <li><span class="c">✓</span> Managed policy onboarding</li>
        <li><span class="c">✓</span> Policy review and rule setup</li>
        <li><span class="c">✓</span> Priority email support</li>
      </ul>
      <a href="/checkout/business?source=pricing_business" onclick="window.sipiTrack&&window.sipiTrack('cta_clicked',{{cta_id:'pricing_business_checkout',destination:'/checkout/business',placement:'pricing_business',plan:'business'}})" class="btn ghost" style="width:100%">Start Business →</a>
      <p style="color:var(--accent);font-size:12px;margin-top:8px;text-align:center">🛡️ Guarantee: green-light a rule violation, month is free</p>
    </div>
  </div>
  <p class="mono" style="color:var(--mut);font-size:13px;margin-top:26px">
    Prefer your own infrastructure? <a href="/self-hosted/">Self-host the MIT-licensed core free forever.</a>
  </p>

  <div style="max-width:820px;margin:60px auto 0;text-align:left">
    <h2 style="font-size:clamp(22px,3.5vw,30px);text-align:center;margin-bottom:8px">What you're paying for, line by line</h2>
    <p class="sub" style="text-align:center;margin-bottom:30px">No per-call fees. No usage tiers. No surprise invoices when your agent fleet grows.</p>
    <table class="cmp">
      <thead><tr><th>Capability</th><th>Self-host (free)</th><th>Team $99/mo</th><th>Business $499/mo</th></tr></thead>
      <tbody>
        <tr><td>Transaction evaluations</td><td>Unlimited</td><td>Unlimited</td><td>Unlimited</td></tr>
        <tr><td>Rule types (per-tx, daily, velocity, merchant, category, time)</td><td>✓ All</td><td>✓ All</td><td>✓ All</td></tr>
        <tr><td>Human-in-the-loop approval queue</td><td>✓</td><td>✓</td><td>✓</td></tr>
        <tr><td>Queryable SQLite audit trail</td><td>✓ Local</td><td>✓ Hosted</td><td>✓ Hosted</td></tr>
        <tr><td>MCP tool, HTTP API, CLI</td><td>✓</td><td>✓</td><td>✓</td></tr>
        <tr><td>Dashboard</td><td>✓ Local</td><td>✓ Hosted</td><td>✓ Hosted + priority support</td></tr>
        <tr><td>Managed spend policy (we write your rules)</td><td>—</td><td>—</td><td>✓</td></tr>
        <tr><td>Rule-integrity guarantee</td><td>—</td><td>✓ Month free</td><td>✓ Month free</td></tr>
      </tbody>
    </table>
  </div>

  <div style="max-width:760px;margin:60px auto 0" id="faq">
    <h2 style="font-size:clamp(22px,3.5vw,30px);text-align:center;margin-bottom:8px">Pricing FAQ</h2>
    <p class="author" style="text-align:center;color:#8a8d96;font-size:14px;margin-bottom:30px"><span rel="author">By the sipi.bot engineering team</span> · Last updated 2026-07-17</p>
    <div class="faq">
      <details><summary>Is there a free plan?</summary><p>Yes. The entire open-source core is MIT-licensed and free to self-host forever — full policy engine, dashboard, audit trail, MCP tool, HTTP API, and CLI. The hosted plans add managed infrastructure, persistent log retention, and support.</p></details>
      <details><summary>What counts as a "transaction evaluation"?</summary><p>One call to the <code>/v1/transactions/evaluate</code> endpoint — your agent asking "should I spend $X at merchant Y?" Each plan includes unlimited evaluations. There is no per-call fee, no metering, no overage charge.</p></details>
      <details><summary>What is the rule-integrity guarantee?</summary><p>If sipi.bot returns "approve" for a transaction that violated one of your active rules, that month's subscription is refunded. The guarantee covers rule-evaluation engine errors, not losses from rules you didn't configure or from acting against a block/flag decision.</p></details>
      <details><summary>What happens immediately after payment?</summary><p>Stripe returns you to a private sipi.bot activation page where your API key is displayed with a copy button, a first protected transaction, and framework-specific integration links.</p></details>
      <details><summary>How do plan changes and cancellation work?</summary><p>Email <a href="mailto:sales@sipiteno.com">sales@sipiteno.com</a> from the billing email. We will confirm the effective date before the next renewal; there is no long-term contract.</p></details>
      <details><summary>What if a legitimate transaction is blocked?</summary><p>Every block includes the exact rule and reason. Adjust or disable that rule in the dashboard, then retry the transaction. A blocked evaluation never moves money itself.</p></details>
      <details><summary>How fast is a transaction evaluation?</summary><p>The policy check is deterministic local code with no model inference. End-to-end hosted latency depends on your network path and current service load, so measure it from your deployment region before putting it on a critical payment path.</p></details>
    </div>
  </div>

  <div style="max-width:760px;margin:60px auto 0;text-align:center" id="eeat">
    <p class="mono" style="color:var(--mut);font-size:13px;margin-bottom:16px">Why trust sipi.bot with your agent's spending</p>
    <div class="grid2" style="text-align:left">
      <div class="card"><h3>Deterministic, not probabilistic</h3><p>The rules engine is pure logic — no ML guessing. If a rule says block at $500, every $501 transaction is blocked, every time, with a reason you can audit.</p></div>
      <div class="card"><h3>Open source, auditable core</h3><p>The exact code running the hosted service is on <a href="https://github.com/kindrat86/sipi-bot">GitHub</a> (MIT). You can read every rule-evaluation path and self-host the same engine.</p></div>
      <div class="card"><h3>Queryable audit trail</h3><p>Every evaluation records its decision, rule, reason, amount, merchant, agent identity, and timestamp in SQLite for review.</p></div>
      <div class="card"><h3>Small decision path</h3><p>The rules engine is deterministic local code with no model call. Hosted latency still includes the network path between your agent and sipi.bot.</p></div>
    </div>
  </div>
  </div>
</section>
<script>(function(){{var q=new URLSearchParams(location.search);if(q.get('checkout')==='cancelled'){{window.sipiTrack&&window.sipiTrack('checkout_canceled',{{plan:(q.get('plan')||'unknown').slice(0,16)}});}}}})();</script>
</body></html>"""


def key_success_html(rec) -> str:
    if rec and rec.get("key"):
        inner = f"""
    <h1 style="color:var(--accent)">You're protected. ✅</h1>
    <p class="sub">Your <strong>{rec.get('tier','team')}</strong> subscription is active.
    Save this API key now—we show it only on this page.</p>
    <div class="codebox mono" id="issued-key" style="font-size:16px;word-break:break-all">{rec['key']}</div>
    <button type="button" class="btn ghost" id="copy-key" style="margin-top:12px">Copy API key</button>
    <div class="grid2" style="max-width:820px;margin:34px auto 0;text-align:left">
      <div class="card"><h3>1. Save the key</h3><p style="color:var(--mut)">Put it in your secret manager as <code>SIPI_BOT_API_KEY</code>. Never commit it to source control.</p></div>
      <div class="card"><h3>2. Protect the first spend</h3><p style="color:var(--mut)">Call the evaluation endpoint before your agent invokes any paid tool or payment API.</p></div>
    </div>
    <p class="lead center" style="margin-top:32px">Run your first protected transaction:</p>
    <div class="codebox mono" id="first-eval">curl -X POST https://sipi.bot/v1/transactions/evaluate \\<br>
&nbsp;&nbsp;-H <span class="s">"Authorization: Bearer {rec['key']}"</span> \\<br>
&nbsp;&nbsp;-d <span class="s">'{{"amount": 6200, "merchant": "unknown-gpu.ru"}}'</span></div>
    <div class="hero-actions">
      <a href="/for/" class="btn">Choose my integration →</a>
      <a href="/dashboard" class="btn ghost">Open the live dashboard</a>
    </div>
    <p style="color:var(--mut);font-size:14px;margin-top:22px">Need help? Email <a href="mailto:sales@sipiteno.com">sales@sipiteno.com</a>.</p>
    <script>
    (function(){{var b=document.getElementById('copy-key');if(!b)return;b.addEventListener('click',function(){{
      navigator.clipboard.writeText(document.getElementById('issued-key').textContent.trim()).then(function(){{
        b.textContent='Copied';
      }});
    }});history.replaceState({{}},'', '/keys/');}})();
    </script>"""
    else:
        inner = """
    <h1>Processing your subscription…</h1>
    <p class="sub">Stripe confirmed your payment. The webhook is issuing your API key now;
    refresh this page in a few seconds. If it still is not ready after one minute,
    email <a href="mailto:sales@sipiteno.com">sales@sipiteno.com</a>.</p>
    <button type="button" class="btn" onclick="location.reload()">Check again</button>
    <a href="/pricing" class="btn ghost" style="margin-left:10px">Back to pricing</a>"""
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>sipi.bot — Your API key</title>
<meta name="description" content="Your sipi.bot API key. Use it as a Bearer token to authenticate transaction evaluation calls from your AI agents.">
<link rel="canonical" href="https://sipi.bot/keys/">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#00d4aa">
<style>{CSS}</style></head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span></div>
<div class="nav-links"><a href="/">Home</a></div></div></nav>
<section class="hero" style="padding-top:70px"><div class="wrap">{inner}</div></section>
</body></html>"""


def masterclass_html() -> str:
    """Perfect Webinar / Masterclass: The 3 Secrets of Agent Spend Control (Ch 8)."""
    s = f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Masterclass — The 3 Secrets That Stop Agent Overspend | sipi.bot</title>
<meta name="description" content="A 10-minute recorded walkthrough covering the 3 secrets every builder needs before deploying an autonomous agent with a payment method.">
<link rel="canonical" href="https://sipi.bot/masterclass">
<meta name="theme-color" content="#00d4aa">
<meta property="og:title" content="The 3 Secrets That Stop Agent Overspend — Free Masterclass">
<meta property="og:description" content="Hook → Story → Offer. The complete framework for deploying autonomous agents that spend safely. 10-minute walkthrough.">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot/masterclass">
<style>{CSS}</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap">
  <div class="brand">sipi<span class="dot">.bot</span></div>
  <div class="nav-links"><a href="/">← Back to firewall</a></div>
</div></nav>

<section class="hero" style="padding:70px 0 50px"><div class="wrap">
  <span class="tag">Free Masterclass · 10 minutes</span>
  <h1 style="font-size:clamp(28px,5vw,44px)">The 3 Secrets That Stop<br>Agent Overspend Before It Starts</h1>
  <p class="sub">Hook → Story → Offer. The complete framework for deploying autonomous agents that spend safely — without babysitting the dashboard.</p>
  <p class="author" style="color:var(--mut);font-size:14px">By Maryan — founder, sipi.bot · 10-min read</p>
</div></section>

<!-- Secret #1: Hook — The One Thing -->
<section><div class="wrap">
  <div style="max-width:760px;margin:0 auto">
    <div class="badge b-red" style="margin-bottom:10px">SECRET #1 — The Hook</div>
    <h2>The One Thing Every Agent Payment Needs Before Money Moves</h2>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:18px">
      Most builders deploy agents with a spending budget and a prayer. They set a daily cap on OpenAI, maybe a rate limit on Anthropic, and call it a day. Then they wake up to Stripe notifications from a vendor they've never heard of.
    </p>
    
    <div style="border-left:3px solid var(--accent);padding:4px 0 4px 18px;margin:24px 0">
      <p style="font-size:17px;line-height:1.7;color:var(--txt);font-style:italic">
        "Your agent doesn't need a budget. It needs a firewall. Every transaction — before the money moves — must be evaluated against your rules. Not the provider's rules. Your rules. In without a model call."
      </p>
    </div>

    <div style="background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px">
      <h3 style="color:var(--accent);margin-bottom:12px">The Hook Test</h3>
      <p style="color:var(--mut);margin-bottom:10px">Ask yourself: can your agent explain WHY it spent $6,200 at unknown-gpu.ru at 2:15 AM? If the answer is "it followed the prompt," you don't have a spending policy. You have a wish.</p>
      <p style="color:var(--txt)"><strong>The One Thing:</strong> Every agent payment path gets one decision point — sipi.bot — that returns <span style="color:var(--green)">approve</span>, <span style="color:var(--red)">block</span>, or <span style="color:var(--amber)">flag</span> before a dollar moves.</p>
    </div>
  </div>
</div></section>

<!-- Secret #2: Story — The 3 False Walls -->
<section style="background:rgba(0,212,170,.03)"><div class="wrap">
  <div style="max-width:760px;margin:0 auto">
    <div class="badge b-amber" style="margin-bottom:10px">SECRET #2 — The Story</div>
    <h2>The 3 False Walls Every Builder Hits</h2>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:24px">
      Here's what happened when I shipped my first agent without a firewall. Here's what happens to every builder who deploys an autonomous spender. The walls aren't real — but they feel real until you see them for what they are.
    </p>

    <div style="display:flex;flex-direction:column;gap:18px">
      <div class="card">
        <h3 style="font-size:18px;color:var(--red);margin-bottom:8px">Wall #1: "The prompt will handle it"</h3>
        <p style="color:var(--mut)">You add "be careful with spending" to the system prompt. The agent buys compute, retries on failure, tips into overage — all while staying within its instructions. The prompt isn't broken. It was never a control.</p>
        <p style="color:var(--accent);margin-top:6px"><strong>What actually stops it:</strong> A velocity limit that kills the 40th retry before the 41st fires.</p>
      </div>

      <div class="card">
        <h3 style="font-size:18px;color:var(--amber);margin-bottom:8px">Wall #2: "I'll catch it in the morning"</h3>
        <p style="color:var(--mut)">You check your dashboards. You monitor logs. But at 2:14 AM, when the agent retries 40 times in three minutes, you're asleep. By 9:03 AM the damage is done. Human review is not a control — it's a post-mortem.</p>
        <p style="color:var(--accent);margin-top:6px"><strong>What actually stops it:</strong> A per-transaction cap and merchant allowlist that fires with a deterministic rules check.</p>
      </div>

      <div class="card">
        <h3 style="font-size:18px;color:var(--green);margin-bottom:8px">Wall #3: "Stripe will catch fraud"</h3>
        <p style="color:var(--mut)">Stripe Radar catches stolen cards and chargebacks. It doesn't catch "your agent bought from a weird vendor 40 times." To Stripe, that's legitimate API usage — the agent IS authorized. The spending is the problem.</p>
        <p style="color:var(--accent);margin-top:6px"><strong>What actually stops it:</strong> A category rule that blocks "compute" spend from unapproved merchants before it hits the payment rail.</p>
      </div>
    </div>
  </div>
</div></section>

<!-- Secret #3: Offer — The Stack + Close -->
<section><div class="wrap">
  <div style="max-width:760px;margin:0 auto">
    <div class="badge b-green" style="margin-bottom:10px">SECRET #3 — The Offer</div>
    <h2>One Curl Call. Six Rules. $0 Lost.</h2>
    <p style="font-size:17px;line-height:1.7;color:var(--txt);margin-bottom:24px">
      Here's what you actually get. Not a dashboard. Not a report. A decision — before the money moves.
    </p>

    <div style="background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:28px;margin-bottom:24px">
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)"><span>Per-transaction cap — hard ceiling on any single spend</span><span style="color:var(--accent);font-weight:700">$499/mo value</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)"><span>Daily total — rolling budget across all transactions</span><span style="color:var(--accent);font-weight:700">$299/mo value</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)"><span>Velocity limit — kills runaway retry loops instantly</span><span style="color:var(--accent);font-weight:700">$199/mo value</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)"><span>Merchant allowlist — only approved vendors go through</span><span style="color:var(--accent);font-weight:700">$199/mo value</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)"><span>Category + time rules — block by type and hour</span><span style="color:var(--accent);font-weight:700">$99/mo value</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid var(--line)"><span>🎁 BONUS: MCP tool + CLI + self-host option</span><span style="color:var(--accent);font-weight:700">INCLUDED</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0;margin-top:4px"><span style="font-weight:700">Total value</span><span style="color:var(--mut);text-decoration:line-through;font-size:18px">$1,295/mo</span></div>
      <div style="display:flex;justify-content:space-between;align-items:center;padding:10px 0"><span style="font-weight:700;font-size:20px">You pay</span><span style="color:var(--accent);font-weight:800;font-size:28px">$99/mo</span></div>
    </div>

    <div style="text-align:center;background:rgba(0,212,170,.08);border:1px solid rgba(0,212,170,.3);border-radius:12px;padding:18px;margin-bottom:24px">
      <p style="color:var(--txt);font-size:15px;margin-bottom:6px">🛡️ <strong>Guarantee:</strong> If sipi.bot green-lights a spend that breaks your active rules, that month is free.</p>
    </div>

    <div class="codebox mono" style="margin-bottom:32px">
<span class="c"># One curl call. A deterministic answer before the spend.</span><br>
curl -X POST https://sipi.bot/v1/transactions/evaluate \\\\<br>
&nbsp;&nbsp;-H <span class="s">"Authorization: Bearer YOUR_KEY"</span> \\\\<br>
&nbsp;&nbsp;-d <span class="s">'{{"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"}}'</span><br><br>
<span class="c"># sipi.bot returns with a deterministic rules check:</span><br>
{{ <span class="k">"decision"</span>: <span class="s">"BLOCKED"</span>, <span class="k">"reason"</span>: <span class="s">"Merchant not on allowlist"</span> }}
    </div>

    <div style="text-align:center">
      <a href="/playground/" class="btn" style="font-size:18px;padding:16px 36px">Try it free in the playground</a>
      <a href="/checkout/team?source=masterclass" rel="nofollow" onclick="window.sipiTrack&&window.sipiTrack('cta_clicked',{{cta_id:'masterclass_team_checkout',destination:'/checkout/team',placement:'masterclass',plan:'team'}})" class="btn ghost" style="font-size:16px;padding:14px 30px;margin-left:12px">Start Team — $99/mo</a>
      <p style="color:var(--accent);font-size:13px;margin-top:12px;text-align:center">🛡️ Guarantee: green-light a rule violation, month is free</p>
      <p style="color:var(--mut);font-size:14px;margin-top:14px">Free self-host core · MIT licensed · <a href="https://github.com/kindrat86/sipi-bot" style="color:var(--accent)">Open on GitHub</a></p>
    </div>
  </div>
</div></section>

<footer class="sipi-resources"><div class="wrap">
  <p>© 2026 sipi.bot — <a href="/">The pre-spend firewall for autonomous AI agents</a></p>
</div></footer>
</body></html>"""
    return s


# ─── Tripwire Page (Dotcom Secrets Ch 5) ────────────────────────────

def tripwire_html() -> str:
    """$7 one-time Agent Spend Audit Report — 15-min scarcity countdown."""
    s = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>Agent Spend Audit — $7 One-Time | sipi.bot</title>
<meta name="description" content="Get a personalized agent spend audit report showing exactly where your autonomous agents are bleeding money — $7 one-time, delivered in 10 minutes.">
<style>
:root{--bg:#0a0a0a;--card:#111;--mut:#888;--accent:#00d4aa;--danger:#ff4757;--text:#e0e0e0;--white:#fff}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.wrap{max-width:720px;margin:0 auto;padding:20px}
.hero{padding:60px 0 30px;text-align:center}
.hero h1{font-size:2.2em;color:var(--white);margin-bottom:12px;line-height:1.2}
.hero .sub{color:var(--mut);font-size:1.1em;max-width:520px;margin:0 auto}
.badge{display:inline-block;background:rgba(255,71,87,.15);color:var(--danger);padding:6px 16px;border-radius:6px;font-size:.85em;font-weight:600;margin-bottom:18px}
.countdown{background:var(--card);border:1px solid #222;border-radius:12px;padding:24px;text-align:center;margin:30px 0}
.countdown .timer{font-size:2.8em;font-weight:800;color:var(--accent);font-variant-numeric:tabular-nums}
.countdown .label{color:var(--mut);font-size:.9em;margin-top:4px}
.stack{background:var(--card);border:1px solid #222;border-radius:12px;padding:30px;margin:30px 0}
.stack h3{color:var(--white);font-size:1.1em;margin-bottom:18px}
.stack .item{display:flex;justify-content:space-between;align-items:center;padding:10px 0;border-bottom:1px solid #1a1a1a}
.stack .item .name{color:var(--text)}
.stack .item .val{color:var(--mut);text-decoration:line-through;font-size:.9em}
.stack .total{display:flex;justify-content:space-between;align-items:center;padding:14px 0;font-weight:700;font-size:1.05em}
.stack .total .old{color:var(--danger);text-decoration:line-through;font-size:1em}
.stack .total .new{color:var(--accent);font-size:1.5em}
.guarantee{background:rgba(0,212,170,.08);border:1px solid rgba(0,212,170,.3);border-radius:10px;padding:20px;margin:24px 0;text-align:center}
.guarantee .icon{font-size:1.4em}
.guarantee .text{color:var(--white);font-size:.95em;margin-top:6px}
.btn{display:inline-block;background:var(--accent);color:var(--bg);font-weight:700;font-size:1.15em;padding:16px 40px;border-radius:10px;text-decoration:none;transition:all .15s}
.btn:hover{opacity:.9;transform:translateY(-1px)}
.secondary{color:var(--mut);font-size:.9em;margin-top:12px}
.secondary a{color:var(--mut);text-decoration:underline}

.faq{margin:40px 0}
.faq h3{color:var(--white);font-size:1.1em;margin-bottom:16px}
.faq .q{color:var(--accent);font-weight:600;margin:16px 0 4px}
.faq .a{color:var(--mut);font-size:.95em}
footer{text-align:center;padding:40px 0;color:var(--mut);font-size:.8em}
footer a{color:var(--mut)}
@media(max-width:600px){.hero h1{font-size:1.6em}.countdown .timer{font-size:2em}}
</style>
</head>
<body>
<div class="wrap">
<div class="hero">
<div class="badge">⚡ LIMITED-TIME OFFER — EXPIRES IN:</div>
<h1>Your Agent Could Be Bleeding $12,400 Right Now. Let's Find Out.</h1>
<p class="sub">A personalized audit of your agent's spending patterns — 3 risk scores, 1 report, delivered in 10 minutes.</p>
</div>

<div class="countdown" id="countdown-block">
<div class="timer" id="timer">15:00</div>
<div class="label">offer expires — one-time audit at this price</div>
</div>

<div class="stack">
<h3>📊 What's in the Agent Spend Audit Report</h3>
<div class="item"><span class="name">① Transaction velocity risk score</span><span class="val">$49</span></div>
<div class="item"><span class="name">② Unknown merchant exposure map</span><span class="val">$39</span></div>
<div class="item"><span class="name">③ Category overspend detection</span><span class="val">$29</span></div>
<div class="item"><span class="name">④ Time-of-day anomaly scan</span><span class="val">$19</span></div>
<div class="item"><span class="name">🎁 BONUS: 5-rule firewall starter config</span><span class="val">$27</span></div>
<div class="item"><span class="name">🎁 BONUS: "First $10K safe" deployment checklist</span><span class="val">$19</span></div>
<div class="total">
<span>Total value:</span>
<span class="old">$182</span>
</div>
<div class="total" style="border:none;padding-top:4px">
<span>Today — one-time:</span>
<span class="new">$7</span>
</div>
</div>

<div class="guarantee">
<div class="icon">🛡️</div>
<div class="text"><strong>60-Day Guarantee:</strong> If the audit doesn't find at least one spending risk you weren't aware of, I'll refund your $7 and you keep the report. No questions.</div>
</div>

<div style="text-align:center;margin:30px 0">
<a href="https://buy.stripe.com/REPLACE_WITH_TRIPWIRE_LINK" class="btn" id="buy-btn">Get My Audit Report — $7 →</a>
<p class="secondary">One-time payment. Delivered to your email in under 10 minutes. <a href="/">No thanks, I'll take my chances →</a></p>
</div>

<!-- TESTIMONIALS REMOVED 2026-07-23: no verified named attribution. Restore only with real users. -->

<div class="faq">
<h3>Quick answers</h3>
<div class="q">What do I need to provide?</div>
<div class="a">Nothing. This is a self-assessment framework — you answer 12 questions about your agent's current setup and get a scored risk report with exact fixes. Takes 8 minutes.</div>
<div class="q">Is this different from the free 5-day playbook?</div>
<div class="a">Yes. The playbook teaches you the concepts. This audit scores YOUR actual setup and tells you exactly which gaps to fix first — ranked by dollar risk.</div>
<div class="q">What if I'm not technical?</div>
<div class="a">The audit is in plain English. No code. If you can describe what your agent buys, you can complete this audit.</div>
</div>
</div>

<footer class="sipi-resources">
<p>© 2026 sipi.bot — <a href="/">The pre-spend firewall for autonomous AI agents</a></p>
</footer></div>

<script>
// 15-min countdown
(function(){
var m=15,s=0,el=document.getElementById('timer'),block=document.getElementById('countdown-block');
function tick(){
if(s===0){if(m===0){block.innerHTML='<p style="color:var(--danger);font-weight:700;font-size:1.1em">This offer has expired. <a href="/pricing" style="color:var(--accent)">See regular pricing →</a></p>';return}m--;s=59}else{s--}
el.textContent=m+':'+(s<10?'0':'')+s;setTimeout(tick,1000)}
tick()
})();
</script>
</body></html>"""
    return s


def badge_page_html() -> str:
    """Badge showcase / installation page — the embeddable protected-by badge system."""
    s = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<title>Protected by sipi.bot — Badge</title>
<meta name="description" content="Embed a live 'Protected by sipi.bot' badge on your site. Show visitors your agent spending is firewall-protected, with real-time stats.">
<link rel="canonical" href="https://sipi.bot/badge">
<link rel="alternate" hreflang="en" href="https://sipi.bot/badge">
<link rel="alternate" hreflang="en-US" href="https://sipi.bot/badge">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot/badge">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Protected by sipi.bot — Spend Firewall Badge">
<meta property="og:description" content="Show the world your agents are protected by a spend firewall. Live stats, dark badge, free forever.">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot/badge">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="Protected by sipi.bot — Spend Firewall Badge"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Protected by sipi.bot — Spend Firewall Badge">
<meta name="twitter:description" content="Show the world your agents are protected by a spend firewall. Live stats, dark badge, free forever.">
<meta name="twitter:image" content="https://sipi.bot/og.png">
<meta name="theme-color" content="#00d4aa">
{CSS}
</head>
<body>
<nav>
<div class="wrap">
<a href="/" class="brand">sipi<span class="dot">.</span>bot</a>
<span class="nav-links"><a href="/pricing">Pricing</a><a href="/dashboard">Dashboard</a><a href="/badge" style="color:var(--accent)">Badge</a></span>
</div>
</nav>

<div class="wrap" style="padding-top:60px;padding-bottom:80px">
<h1 style="font-size:38px;letter-spacing:-.03em;margin-bottom:12px">Protected by <span style="color:var(--accent)">sipi.bot</span></h1>
<p style="font-size:18px;color:var(--mut);max-width:640px;margin-bottom:48px">
Show the world your autonomous agents are protected by a spend firewall. Every badge embed is a live status indicator — and a permanent backlink.
</p>

<!-- Full badge preview -->
<div style="background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:24px;margin-bottom:32px;overflow:hidden">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
    <h2 style="font-size:16px;margin:0">Full badge <span style="color:var(--mut);font-weight:400;font-size:13px">— live stats</span></h2>
    <span style="color:var(--green);font-size:12px;font-family:var(--mono)">● Live</span>
  </div>
  <img src="/api/badge/firewall-status?style=dark&w=760" alt="Protected by sipi.bot" style="max-width:100%;border-radius:8px" loading="lazy">
</div>

<!-- Variants -->
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:20px;margin-bottom:48px">
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px">
    <h3 style="font-size:14px;margin-bottom:12px">Flat badge <span style="color:var(--mut);font-weight:400;font-size:12px">— README</span></h3>
    <img src="/api/badge/firewall-status?style=flat" alt="Protected by sipi.bot" style="border-radius:6px" loading="lazy">
    <textarea readonly style="width:100%;height:52px;background:var(--bg);color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:8px;font-family:'SF Mono',ui-monospace,monospace;font-size:11px;margin-top:12px;resize:none" onclick="this.select()">&lt;img src="https://sipi.bot/api/badge/firewall-status?style=flat" alt="Protected by sipi.bot"&gt;</textarea>
  </div>
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px">
    <h3 style="font-size:14px;margin-bottom:12px">Shield badge <span style="color:var(--mut);font-weight:400;font-size:12px">— Shields.io style</span></h3>
    <img src="/api/badge/firewall-status?style=shield" alt="Protected by sipi.bot" style="border-radius:6px" loading="lazy">
    <textarea readonly style="width:100%;height:52px;background:var(--bg);color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:8px;font-family:'SF Mono',ui-monospace,monospace;font-size:11px;margin-top:12px;resize:none" onclick="this.select()">&lt;img src="https://sipi.bot/api/badge/firewall-status?style=shield" alt="Protected by sipi.bot"&gt;</textarea>
  </div>
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:20px">
    <h3 style="font-size:14px;margin-bottom:12px">Full badge <span style="color:var(--mut);font-weight:400;font-size:12px">— landing pages</span></h3>
    <img src="/api/badge/firewall-status?style=dark&w=380" alt="Protected by sipi.bot" style="max-width:100%;border-radius:6px" loading="lazy">
    <textarea readonly style="width:100%;height:52px;background:var(--bg);color:var(--txt);border:1px solid var(--line);border-radius:8px;padding:8px;font-family:'SF Mono',ui-monospace,monospace;font-size:11px;margin-top:12px;resize:none" onclick="this.select()">&lt;img src="https://sipi.bot/api/badge/firewall-status?style=dark" alt="Protected by sipi.bot"&gt;</textarea>
  </div>
</div>

<!-- Use cases -->
<h2 style="font-size:22px;margin-bottom:20px">Where to embed the badge</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;margin-bottom:48px">
  <div style="background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:20px">
    <h4 style="margin:0 0 8px">GitHub README</h4>
    <p style="color:var(--mut);font-size:13px;margin:0">Add the flat badge to your project README. Every visitor sees your agents are protected.</p>
  </div>
  <div style="background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:20px">
    <h4 style="margin:0 0 8px">Documentation site</h4>
    <p style="color:var(--mut);font-size:13px;margin:0">Embed the full badge in your docs sidebar. Builds trust with every integration partner.</p>
  </div>
  <div style="background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:20px">
    <h4 style="margin:0 0 8px">Landing page footer</h4>
    <p style="color:var(--mut);font-size:13px;margin:0">A single <code>&lt;img&gt;</code> tag in your footer. Zero JavaScript, zero dependencies, always current.</p>
  </div>
  <div style="background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:20px">
    <h4 style="margin:0 0 8px">Agent framework integration page</h4>
    <p style="color:var(--mut);font-size:13px;margin:0">Show users of your framework integration that you've wired the firewall. Trust signal.</p>
  </div>
  <div style="background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:20px">
    <h4 style="margin:0 0 8px">Security / compliance page</h4>
    <p style="color:var(--mut);font-size:13px;margin:0">Pair the badge with your security page. Every SOC 2 auditor and enterprise buyer sees it.</p>
  </div>
  <div style="background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:20px">
    <h4 style="margin:0 0 8px">MCP server listing</h4>
    <p style="color:var(--mut);font-size:13px;margin:0">Add the shield badge to your Smithery, MCPT, or Open Tools listing. Differentiates your listing.</p>
  </div>
</div>

<!-- URL parameters -->
<h2 style="font-size:22px;margin-bottom:20px">Customization</h2>
<table style="width:100%;border-collapse:collapse;background:var(--panel);border:1px solid var(--line);border-radius:12px;overflow:hidden;margin-bottom:48px">
<thead>
<tr style="background:var(--panel2);text-align:left">
<th style="padding:12px 16px;font-size:13px">Parameter</th>
<th style="padding:12px 16px;font-size:13px">Values</th>
<th style="padding:12px 16px;font-size:13px">Default</th>
<th style="padding:12px 16px;font-size:13px">Description</th>
</tr>
</thead>
<tbody>
<tr style="border-top:1px solid var(--line)">
<td style="padding:12px 16px;font-family:var(--mono);font-size:12px">style</td>
<td style="padding:12px 16px;font-size:12px"><code>dark</code>, <code>flat</code>, <code>shield</code></td>
<td style="padding:12px 16px;font-size:12px"><code>dark</code></td>
<td style="padding:12px 16px;font-size:12px;color:var(--mut)">Badge variant: full stats card, single-line, or Shields.io style</td>
</tr>
<tr style="border-top:1px solid var(--line)">
<td style="padding:12px 16px;font-family:var(--mono);font-size:12px">w</td>
<td style="padding:12px 16px;font-size:12px"><code>280</code>–<code>1200</code></td>
<td style="padding:12px 16px;font-size:12px"><code>760</code></td>
<td style="padding:12px 16px;font-size:12px;color:var(--mut)">Width in pixels (full badge only)</td>
</tr>
</tbody>
</table>

<!-- Stats explainer -->
<h2 style="font-size:22px;margin-bottom:12px">What the badge shows</h2>
<p style="color:var(--mut);margin-bottom:24px;max-width:640px">
The badge pulls live stats from the sipi.bot firewall engine. Every number is real — checks counted today, blocked transactions, approved/flagged breakdowns. No fake data, no cached static badge.
</p>

<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:48px">
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;text-align:center">
    <div style="font-size:28px;font-weight:700;margin-bottom:4px">✓</div>
    <div style="font-size:13px;color:var(--mut)">Real-time stats</div>
    <div style="font-size:11px;color:#555;margin-top:6px">30-second refresh from live firewall</div>
  </div>
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;text-align:center">
    <div style="font-size:28px;font-weight:700;margin-bottom:4px">⚡</div>
    <div style="font-size:13px;color:var(--mut)">Zero dependencies</div>
    <div style="font-size:11px;color:#555;margin-top:6px">One <code>&lt;img&gt;</code> tag, no JS needed</div>
  </div>
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;text-align:center">
    <div style="font-size:28px;font-weight:700;margin-bottom:4px">🔒</div>
    <div style="font-size:13px;color:var(--mut)">Always HTTPS</div>
    <div style="font-size:11px;color:#555;margin-top:6px">Served from sipi.bot CDN with HSTS</div>
  </div>
  <div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;text-align:center">
    <div style="font-size:28px;font-weight:700;margin-bottom:4px">∞</div>
    <div style="font-size:13px;color:var(--mut)">Free forever</div>
    <div style="font-size:11px;color:#555;margin-top:6px">No API key, no rate limit on badge</div>
  </div>
</div>

<!-- FAQ -->
<h2 style="font-size:22px;margin-bottom:20px">Frequently asked</h2>
<div style="max-width:640px;margin-bottom:48px">
<div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;margin-bottom:12px">
  <h4 style="margin:0 0 6px;font-size:14px">Does the badge slow down my page?</h4>
  <p style="margin:0;color:var(--mut);font-size:13px">No. The SVG payload is ~2KB, served with 30-second CDN cache. It loads in parallel with your page and never blocks rendering.</p>
</div>
<div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px;margin-bottom:12px">
  <h4 style="margin:0 0 6px;font-size:14px">Do I need a sipi.bot account?</h4>
  <p style="margin:0;color:var(--mut);font-size:13px">No. The badge is free for anyone to embed. It shows global firewall stats, not account-specific data. If you want a badge showing YOUR agent's protected status, <a href="/pricing">sign up for a plan</a> and we'll generate a per-account badge.</p>
</div>
<div style="background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px">
  <h4 style="margin:0 0 6px;font-size:14px">Can I use it in a commercial product?</h4>
  <p style="margin:0;color:var(--mut);font-size:13px">Yes. The badge is free for commercial use. Attribution to sipi.bot is built into the badge design — that's the whole point.</p>
</div>
</div>

<!-- CTA -->
<div style="text-align:center;padding:48px 0;border-top:1px solid var(--line)">
  <h2 style="font-size:24px;margin-bottom:16px">Ready to protect your agents?</h2>
  <p style="color:var(--mut);margin-bottom:24px;max-width:500px;margin-left:auto;margin-right:auto">
    The badge shows you care. The firewall behind it actually protects. Deploy both today.
  </p>
  <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap">
    <a href="/pricing" class="btn" style="background:var(--accent);color:#0a0a0a;padding:14px 32px;border-radius:10px;font-weight:700;font-size:15px">Get started — $99/mo</a>
    <a href="/self-hosted" class="btn" style="background:var(--panel2);color:var(--txt);padding:14px 32px;border-radius:10px;font-weight:600;font-size:15px;border:1px solid var(--line)">Self-host free</a>
  </div>
</div>

</div>

<footer class="sipi-resources">
<p>© 2026 sipi.bot — <a href="/">The pre-spend firewall for autonomous AI agents</a></p>
</footer></div>
</body></html>"""
    return s

BLOG_CASE_STUDY_BODY = """<h1>How my own AI agent spent $12,400 while I slept — and the firewall I built to stop it</h1>
<p class="author" style="color:#8a8d96;font-size:14px">By Maryan · July 2026</p>

<hr style="border:none;border-top:1px solid var(--line);margin:30px 0">

<p>I deployed my first autonomous purchasing agent on a Tuesday. It was beautiful — four lines of orchestration, an x402 payment rail, and a prompt that said "buy GPU compute when under 70% utilization." I went to sleep feeling like I'd shipped the future.</p>

<p>I woke up to Stripe notifications.</p>

<p>The agent had hit a rate-limit at 2:14 AM and retried 40 times. It bought compute from a vendor I'd never heard of — <code>unknown-gpu.ru</code>. It tipped an API into overage. Total damage: <strong>$12,400</strong>. In seven hours. While I was sleeping.</p>

<p>The agent didn't do anything wrong. It followed the prompt. It bought compute when utilization dipped. It retried on failure — exactly what we train agents to do. The problem wasn't the agent. The problem was that <strong>nobody was checking</strong>. The payment rails move money. They don't ask if the merchant is sketchy, if the amount is suspicious, or if forty retries in three minutes is a bug or a feature. There was no firewall.</p>

<hr style="border:none;border-top:1px solid var(--line);margin:30px 0">

<h2>The search for a pre-spend guardrail</h2>

<p>I spent the next week reading every provider's spend-control docs.</p>

<p><strong>OpenAI</strong> has usage limits — per-provider, and they're reactive. You find out after the bill arrives. <strong>Anthropic</strong> has rate limits — per-model, not per-use-case. <strong>Stripe</strong> has Radar — for fraud detection on card payments, not for agent spend policy. <strong>Cloud providers</strong> have budget alerts — email notifications after you've already spent the money.</p>

<p>Every solution was partial and reactive. Nobody was building the thing that says "no" <em>before</em> the money moves.</p>

<p>The gap is structural: the agent-economy payment rails — x402, AP2, AgentKit, MCP tool calls — are letting agents spend autonomously, but <strong>not one of them screens transactions before they settle</strong>. A prompt is not a policy. A retry loop is not a feature.</p>

<hr style="border:none;border-top:1px solid var(--line);margin:30px 0">

<h2>Building the missing layer</h2>

<p>So I stopped looking. I built sipi.bot: a spend firewall that sits in front of every transaction an autonomous agent attempts, evaluates it against your rules, and returns <code>APPROVED</code>, <code>BLOCKED</code>, or <code>FLAGGED</code> — with a deterministic rules check. Not a dashboard. Not a report. A decision. <strong>Before the money moves.</strong></p>

<h3>Design principles</h3>

<p><strong>Deterministic, not probabilistic.</strong> The rules engine is pure logic — no ML, no "risk scores." If a rule says block at $500, every $501 transaction is blocked, every time, with a reason you can audit.</p>

<p><strong>HTTP-first, MCP-native.</strong> Any agent that speaks HTTP can call it. Agents using Claude Code, Cursor, or Hermes can use the MCP tool directly. One <code>curl</code> call before every spend.</p>

<p><strong>Open source, MIT.</strong> The exact code running the hosted service is public on GitHub. You can read every rule-evaluation path and self-host the same engine — free, forever.</p>

<h3>The six rule types</h3>

<ol>
<li><strong>Per-transaction caps</strong> — "max $500 per purchase"</li>
<li><strong>Daily totals</strong> — "max $2,000 per day, across all agents"</li>
<li><strong>Velocity limits</strong> — "max 5 transactions per minute" (runaway-loop protection)</li>
<li><strong>Merchant allow/block lists</strong> — "never buy from <code>*.ru</code> domains"</li>
<li><strong>Category limits</strong> — "max $50/month on API credits from unknown vendors"</li>
<li><strong>Time-window constraints</strong> — "no purchases between 11 PM and 7 AM"</li>
</ol>

<p>Every rule is checked in priority order. The first <code>BLOCK</code> stops the transaction instantly. <code>FLAGGED</code> transactions enter a human-in-the-loop queue — not auto-approved, not silently blocked. Every decision is written to a queryable audit log with the rule, reason, amount, agent identity, and timestamp.</p>

<hr style="border:none;border-top:1px solid var(--line);margin:30px 0">

<h2>The shape of the problem today</h2>

<p>We're still in the early days of autonomous agents. But the trajectory is clear:</p>

<ul>
<li>Every week, more agents get deployed with real spending power</li>
<li>The payment rails — x402, AP2, AgentKit — are optimized for speed, not safety</li>
<li>A single runaway agent can cost five figures in a night</li>
<li><strong>Runaway retry loops are a concrete failure mode</strong> — test velocity and daily-total rules before giving an agent live payment access.</li>
</ul>

<p>The gap — between an agent's ability to spend and your ability to control it — is exactly where sipi.bot lives.</p>

<hr style="border:none;border-top:1px solid var(--line);margin:30px 0">

<h2>What's next</h2>

<p>sipi.bot is live today. The open-source core is MIT-licensed at <a href="https://github.com/kindrat86/sipi-bot">github.com/kindrat86/sipi-bot</a> — free to self-host. The hosted version ($99/mo Team, $499/mo Business) adds the dashboard, managed approval queue, and persistent audit log.</p>

<p>We're actively building: webhook/Slack alerts, compliance reporting, managed spend policies, and deeper framework integrations. The rule engine is extensible — if you need a rule type that doesn't exist, you can add it.</p>

<p><strong>Try it:</strong> <code>pip install sipi-bot && sipi-guard</code>, or drop the MCP config into your agent and call <code>POST /v1/transactions/evaluate</code>.</p>

<p><em>Built by Maryan in Kifisia, Greece. Previously: sanctions compliance tools for AI payments (sanctionsai.dev), churn analytics (churnlens.site).</em></p>
"""


def blog_page_html() -> str:
    """Single-founder origin-story blog post: how sipi.bot was born from a $12,400 runaway-agent incident."""
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.png">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>How my own AI agent spent $12,400 while I slept — sipi.bot</title>
<meta name="description" content="The origin story of sipi.bot: a runaway AI agent spent $12,400 in 7 hours. Here's how the spend firewall was built to stop it from happening again.">
<link rel="canonical" href="https://sipi.bot/blog/">
<link rel="alternate" hreflang="en" href="https://sipi.bot/blog/">
<link rel="alternate" hreflang="en-US" href="https://sipi.bot/blog/">
<link rel="alternate" hreflang="x-default" href="https://sipi.bot/blog/">
<link rel="author" href="https://sipi.bot/about/">
<meta name="robots" content="index, follow">
<meta property="og:title" content="How my own AI agent spent $12,400 while I slept — sipi.bot">
<meta property="og:description" content="The origin story of sipi.bot: a runaway AI agent spent $12,400 in 7 hours. Here's how the spend firewall was built to stop it from happening again.">
<meta property="og:type" content="article"><meta property="og:url" content="https://sipi.bot/blog/">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="sipi.bot — The pre-spend firewall for autonomous AI agents"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="How my own AI agent spent $12,400 while I slept — sipi.bot">
<meta name="twitter:description" content="The origin story of sipi.bot: a runaway AI agent spent $12,400 in 7 hours. Here's how the spend firewall was built to stop it from happening again.">
<meta name="twitter:image" content="https://sipi.bot/og.png">
<meta name="article:published_time" content="2026-07-21T00:00:00+00:00">
<meta name="article:author" content="Maryan">
<meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"Article","@id":"https://sipi.bot/blog/#article","headline":"How my own AI agent spent $12,400 while I slept — and the firewall I built to stop it","url":"https://sipi.bot/blog/","description":"The origin story of sipi.bot: a runaway AI agent spent $12,400 in 7 hours. Here's how the spend firewall was built to stop it from happening again.","datePublished":"2026-07-21T00:00:00+00:00","dateModified":"2026-07-21T00:00:00+00:00","author":{{"@type":"Person","name":"Maryan","url":"https://sipi.bot/about/"}},"publisher":{{"@type":"Organization","name":"sipi.bot","url":"https://sipi.bot/"}},"image":"https://sipi.bot/og.png","mainEntityOfPage":"https://sipi.bot/blog/"}}</script>
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Home","item":"https://sipi.bot/"}},{{"@type":"ListItem","position":2,"name":"Blog","item":"https://sipi.bot/blog/"}}]}}</script>
<style>{CSS}</style>{{POSTHOG_SNIPPET}}{{GA4_SNIPPET}}<!-- /ux.css + /ux.js removed 2026-07-26. They loaded AFTER this page's own <style>{CSS}</style>, and ux.css is light by default (--ux-text:#0f172a, --ux-surface:#fff, dark only inside a prefers-color-scheme query). So for every light-mode visitor body text became #0f172a while .card kept this page's own --panel #121316 — measured 1.04:1, i.e. the "Who uses a spend firewall" cards were invisible in production. This page uses no .ux-* class, no var(--ux-*) and no ux.js hook, so the pair contributed nothing but the bug (and two render-blocking requests). --></head><body>
<nav><div class="wrap">
  <div class="brand"><a href="/" style="color:var(--txt)">sipi<span class="dot">.bot</span></a></div>
  <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="mainnav" aria-label="Open menu"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
  <div class="nav-links" id="mainnav">
    <a href="/">Home</a>
    <a href="/pricing">Pricing</a>
    <a href="/learn/how-to-control-ai-agent-spending">Compare approaches</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>
<script>(function(){{var t=document.querySelector('.nav-toggle');if(!t)return;var n=t.closest('nav');function set(o){{n.classList.toggle('menu-open',o);t.setAttribute('aria-expanded',o);t.setAttribute('aria-label',o?'Close menu':'Open menu');}}t.addEventListener('click',function(){{set(!n.classList.contains('menu-open'));}});n.querySelectorAll('.nav-links a').forEach(function(a){{a.addEventListener('click',function(){{set(false);}});}});document.addEventListener('keydown',function(e){{if(e.key==='Escape'&&n.classList.contains('menu-open')){{set(false);t.focus();}}}});}})();</script>
<section><div class="wrap"><article class="doc" style="max-width:760px;margin:0 auto">
<div style="margin-bottom:20px"><a href="/" style="color:var(--accent);font-size:14px">← Back to sipi.bot</a></div>
{BLOG_CASE_STUDY_BODY}
</article></div></section>
<footer class="sipi-resources"><div class="wrap">
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/eval-report/">Eval report</a> · <a href="/.well-known/agent-card.json">Agent card</a> · <a href="/about">About</a> · <a href="/blog/">Blog</a> · <a href="/security">Security</a> · <a href="/status">Status</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
  <div style="margin-top:14px;color:var(--mut);font-size:13px">
    <a href="/benchmarks/">Benchmarks</a> ·
    <a href="/best/">Best-of comparisons</a> ·
    Find us where builders are:
    <a href="https://github.com/kindrat86/sipi-bot" rel="me noopener">GitHub</a> ·
    <a href="https://pypi.org/project/sipi-bot/" rel="me noopener">PyPI</a> ·
    <a href="https://x.com/sipiteno" rel="me noopener">X / Twitter</a> ·
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
  </div>
</div></footer>
</body></html>"""
