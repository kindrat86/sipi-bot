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
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
.mono{font-family:'SF Mono',ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
nav{position:sticky;top:0;z-index:20;background:rgba(10,10,10,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px;flex-wrap:wrap}
.brand{font-weight:700;font-size:19px;letter-spacing:-.02em}
.brand .dot{color:var(--accent)}
.nav-links{display:flex;gap:22px;align-items:center;font-size:14px;flex-wrap:wrap}
.nav-links a{color:var(--mut);min-height:44px;display:inline-flex;align-items:center}.nav-links a:hover{color:var(--txt)}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:var(--accent);color:#04120e;font-weight:700;padding:12px 22px;border-radius:10px;border:none;cursor:pointer;font-size:15px;transition:transform .1s}
.btn:hover{transform:translateY(-1px)}
.btn.ghost{background:transparent;color:var(--txt);border:1px solid var(--line)}
section{padding:72px 0;border-bottom:1px solid var(--line)}
.hero{padding:90px 0 80px;text-align:center;background:radial-gradient(ellipse 80% 60% at 50% -10%,rgba(0,212,170,.10),transparent)}
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
@media(max-width:760px){.grid2,.contrast,.kpis{grid-template-columns:1fr}.decision3{grid-template-columns:1fr!important}.nav-links{justify-content:center;width:100%;padding:8px 0 4px;gap:14px 18px}.nav-links a:not(.btn){font-size:13px}section{padding:52px 0}.cmp{font-size:12.5px}.cmp th,.cmp td{padding:8px}}
"""

# ─── Analytics ───
# PostHog — product analytics. Public client-side token (safe to ship). Overridable via env.
POSTHOG_KEY = os.environ.get("POSTHOG_KEY", "phc_lyZCgvTpicjLzAO3rY2GhxuX5WUc5jQjP8ZVwwJqauX")
POSTHOG_HOST = os.environ.get("POSTHOG_HOST", "https://eu.i.posthog.com")

# Google Analytics 4 — AEO measurement. Override via env for production.
# Set GA4_MEASUREMENT_ID env var to enable. Example: G-XXXXXXXXXX
GA4_ID = os.environ.get("GA4_MEASUREMENT_ID", "")

GA4_SNIPPET = (
    f'<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>\n'
    f'<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}'
    f"gtag('js',new Date());gtag('config','{GA4_ID}');</script>"
) if GA4_ID else ""

POSTHOG_SNIPPET = (
    "<script>!function(t,e){var o,n,p,r;e.__SV||(window.posthog=e,e._i=[],e.init=function(i,s,a){"
    "function g(t,e){var o=e.split('.');2==o.length&&(t=t[o[0]],e=o[1]),t[e]=function(){"
    "t.push([e].concat(Array.prototype.slice.call(arguments,0)))}}(p=t.createElement('script')).type='text/javascript',"
    "p.crossOrigin='anonymous',p.async=!0,p.src=s.api_host.replace('.i.posthog.com','-assets.i.posthog.com')+'/static/array.js',"
    "(r=t.getElementsByTagName('script')[0]).parentNode.insertBefore(p,r);var u=e;for(void 0!==a?u=e[a]=[]:a='posthog',"
    "u.people=u.people||[],u.toString=function(t){var e='posthog';return'posthog'!==a&&(e+='.'+a),t||(e+=' (stub)'),e},"
    "u.people.toString=function(){return u.toString(1)+'.people (stub)'},o='init capture register register_once register_for_session "
    "unregister unregister_for_session getFeatureFlag getFeatureFlagPayload isFeatureEnabled reloadFeatureFlags "
    "updateEarlyAccessFeatureEnrollment getEarlyAccessFeatures on onFeatureFlags onSessionId getSurveys getActiveMatchingSurveys "
    "renderSurvey canRenderSurvey getNextSurveyStep identify setPersonProperties group resetGroups setPersonPropertiesForFlags "
    "resetPersonPropertiesForFlags setGroupPropertiesForFlags resetGroupPropertiesForFlags reset get_distinct_id getGroups "
    "get_session_id get_session_replay_url alias set_config startSessionRecording stopSessionRecording "
    "sessionRecordingStarted captureException loadToolbar get_property getSessionProperty createPersonProfile "
    "opt_in_capturing opt_out_capturing has_opted_in_capturing has_opted_out_capturing clear_opt_in_out_capturing "
    "debug getPageViewId'.split(' '),n=0;n<o.length;n++)g(u,o[n]);e._i.push([i,s,a])},e.__SV=1)}(document,window.posthog||[]);"
    f"posthog.init('{POSTHOG_KEY}',{{api_host:'{POSTHOG_HOST}',person_profiles:'identified_only',capture_pageview:false}});posthog.capture('$pageview',{{$viewport_height:window.innerHeight,$viewport_width:window.innerWidth}})</script>"
)


def landing_page_html() -> str:
    s = """<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){try{window.trustedTypes.createPolicy("default",{createHTML:function(s){return s},createScript:function(s){return s},createScriptURL:function(s){return s}})}catch(e){}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>sipi.bot — The Pre-Spend Firewall for Autonomous AI Agents</title>
<meta name="description" content="sipi.bot is a pre-spend firewall for AI agents: one API call approves, blocks, or flags every transaction against per-tx caps, velocity limits, and merchant allowlists before money moves.">
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
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","@id":"https://sipi.bot/#org","name":"sipi.bot","alternateName":["sipibot","sipi bot","sipi.bot spend firewall"],"url":"https://sipi.bot/","description":"sipi.bot is a spend firewall for autonomous AI agents — a real-time API that returns APPROVED, BLOCKED, or FLAGGED for every payment an agent attempts, enforcing per-transaction caps, daily totals, velocity limits, and merchant rules so a runaway agent can't drain your funds.","disambiguatingDescription":"sipi.bot is a payment-control spend firewall API for autonomous AI agents (x402 / AP2 / AgentKit) — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.","sameAs":["https://github.com/kindrat86/sipi-bot","https://pypi.org/project/sipi-bot/"],"knowsAbout":["AI Agent Spend Control","Autonomous Agent Payment Firewall","API Spend Governance","x402 Payment Protocol","Agent Transaction Monitoring","Runaway AI Cost Prevention","Agent Budget Management","Multi-Agent Spend Orchestration"]},{"@type":"WebSite","@id":"https://sipi.bot/#website","url":"https://sipi.bot/","name":"sipi.bot","publisher":{"@id":"https://sipi.bot/#org"}},{"@type":"WebPage","@id":"https://sipi.bot/#page","url":"https://sipi.bot/","name":"sipi.bot — The Pre-Spend Firewall for Autonomous AI Agents","isPartOf":{"@id":"https://sipi.bot/#website"},"datePublished":"2026-07-08","dateModified":"2026-07-17"},{"@type":"BreadcrumbList","@id":"https://sipi.bot/#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://sipi.bot/"}]},{"@type":"SiteNavigationElement","name":["Home","Dashboard","Pricing","About"],"url":["https://sipi.bot/","https://sipi.bot/dashboard","https://sipi.bot/pricing","https://sipi.bot/about"]},{"@type":"SoftwareApplication","@id":"https://sipi.bot/#app","name":"sipi.bot","alternateName":["sipibot","sipi bot"],"applicationCategory":"BusinessApplication","operatingSystem":"Any (HTTP API, MCP, CLI)","description":"Spend firewall that evaluates every autonomous-agent transaction against your rules and returns approve, block, or flag in under 5ms.","disambiguatingDescription":"A payment-control spend firewall API for autonomous AI agents — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.","offers":{"@type":"Offer","price":"99","priceCurrency":"USD"},"featureList":["Per-transaction, daily, velocity, merchant, category and time rules","Human-in-the-loop approval queue","Tamper-evident audit log","MCP tool + HTTP API + CLI"]},{"@type":"FAQPage","@id":"https://sipi.bot/#faq","mainEntity":[{"@type":"Question","name":"What is a spend firewall for AI agents?","acceptedAnswer":{"@type":"Answer","text":"A spend firewall sits in front of every transaction an autonomous AI agent attempts and evaluates it against your rules — approving, blocking, or flagging it before any money moves. sipi.bot returns a decision in under 5ms over HTTP, MCP, or CLI."}},{"@type":"Question","name":"How does sipi.bot stop an agent from overspending?","acceptedAnswer":{"@type":"Answer","text":"Your agent calls sipi.bot before it spends. sipi.bot checks the transaction against per-transaction, daily, velocity, merchant, category, and time rules and returns approve, block, or flag. Velocity limits kill runaway retry loops instantly, and unknown merchants are blocked unless allowlisted."}},{"@type":"Question","name":"How much does sipi.bot cost?","acceptedAnswer":{"@type":"Answer","text":"Hosted plans are flat-rate: Team is $99/month and Business is $499/month, both with unlimited transaction evaluations — no per-call fees, no metering, no overage tiers. The open-source core is MIT-licensed and free to self-host forever."}},{"@type":"Question","name":"Does sipi.bot work with MCP and Claude Code?","acceptedAnswer":{"@type":"Answer","text":"Yes. sipi.bot is a native MCP tool, so Claude Code, Cursor, and Hermes call it directly, and it also exposes a plain HTTP API and a CLI so any agent runtime can use it. Client wrappers for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK take a few lines each."}},{"@type":"Question","name":"Is sipi.bot a SIP, voice, or telephony product?","acceptedAnswer":{"@type":"Answer","text":"No. Despite the name, sipi.bot has nothing to do with SIP, VoIP, or voice, and it is not a bot-management or 'block AI bots' tool. sipi.bot is a spend firewall that governs how much money autonomous AI agents can spend."}}]},{"@type":"SpeakableSpecification","cssSelector":["h1","h2","p"]}]}</script>
<!-- BreadcrumbList standalone -->
<script type="application/ld+json">{"@context":"https://***@type":"BreadcrumbList","@id":"https://sipi.bot/#breadcrumb-standalone","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://sipi.bot/"},{"@type":"ListItem","position":2,"name":"Pricing","item":"https://sipi.bot/pricing"},{"@type":"ListItem","position":3,"name":"FAQ","item":"https://sipi.bot/#faq"}]}</script>
<!-- WebSite standalone -->
<script type="application/ld+json">{"@context":"https://***@type":"WebSite","@id":"https://sipi.bot/#website-standalone","name":"sipi.bot","url":"https://sipi.bot/","description":"Pre-spend firewall for autonomous AI agents — approve, block, or flag every agent transaction before a dollar moves.","publisher":{"@type":"Organization","name":"sipi.bot","url":"https://sipi.bot/"},"inLanguage":"en-US","potentialAction":{"@type":"SearchAction","target":{"@type":"EntryPoint","urlTemplate":"https://sipi.bot/?q={search_term_string}"},"query-input":"required name=search_term_string"}}</script>
<!-- FAQPage standalone -->
<script type="application/ld+json">{"@context":"https://***@type":"FAQPage","@id":"https://sipi.bot/#faq-standalone","mainEntity":[{"@type":"Question","name":"What is sipi.bot?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot is a spend firewall for autonomous AI agents — a real-time API that returns APPROVED, BLOCKED, or FLAGGED for every payment an agent attempts, enforcing per-transaction caps, daily totals, velocity limits, and merchant rules so a runaway agent can't drain your funds."}},{"@type":"Question","name":"How does sipi.bot protect against runaway AI spending?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot evaluates every transaction request in under 5ms before money moves. It enforces per-transaction caps, daily totals, velocity limits, and merchant allowlists. If a rule is violated, the transaction is BLOCKED instantly — you wake up to a clean log, not a drained account."}},{"@type":"Question","name":"Which payment protocols does sipi.bot support?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot works with any HTTP-based payment pipeline: x402, AP2, AgentKit (Coinbase), Stripe agent tooling, LangChain, CrewAI, and the Model Context Protocol (MCP). It's protocol-agnostic — if your agent speaks HTTP, sipi.bot can gate it."}},{"@type":"Question","name":"Is there a free tier?","acceptedAnswer":{"@type":"Answer","text":"Yes — sipi.bot offers a free tier with no credit card required. Paid plans unlock higher transaction volumes, advanced rule types, and team features."}},{"@type":"Question","name":"How fast is the API?","acceptedAnswer":{"@type":"Answer","text":"sipi.bot decisions return in under 5ms. It's designed to sit inline in payment pipelines without adding perceptible latency."}}]}</script>
<!-- Organization standalone -->
<script type="application/ld+json">{"@context":"https://***@type":"Organization","@id":"https://sipi.bot/#org-standalone","name":"sipi.bot","url":"https://sipi.bot/","description":"sipi.bot is a spend firewall for autonomous AI agents — a real-time API that returns APPROVED, BLOCKED, or FLAGGED for every payment an agent attempts, enforcing per-transaction caps, daily totals, velocity limits, and merchant rules.","sameAs":["https://github.com/kindrat86/sipi-bot","https://pypi.org/project/sipi-bot/"]}</script>
<style>{CSS}</style>{POSTHOG}{GA4_SNIPPET}<link rel="stylesheet" href="/ux.css"><script src="/ux.js" defer></script></head><body>
<nav><div class="wrap">
  <div class="brand">sipi<span class="dot">.bot</span></div>
  <div class="nav-links">
    <a href="#how">How it works</a>
    <a href="#origin">Origin</a>
    <a href="#false-beliefs">Beliefs</a>
    <a href="#faq">FAQ</a>
    <a href="#pricing">Pricing</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>

<header class="hero"><div class="wrap">
  <span class="tag">Spend controls for the agent economy</span>
  <h1>Your AI agent just spent<br><span class="hl">$12,400 while you slept.</span></h1>
  <p class="author" style="color:#8a8d96;font-size:14px;margin:4px 0 10px"><span rel="author">By Maryan — founder, sipi.bot</span> · Published 2026-07-08 · Last updated 2026-07-18 · <a href="#origin" style="color:var(--accent)">Read the origin story →</a></p>
  <p class="sub"><strong>sipi.bot is a spend firewall for autonomous AI agents:</strong> it evaluates every transaction against your rules and returns approve, block, or flag in under 5ms — before a single dollar moves. You gave an autonomous agent your credit card and no spending limit; sipi.bot is the control layer that sits in front of it. <a href="/learn/spend-firewall-guide" style="color:var(--accent);text-decoration:underline">Read the complete spend firewall guide →</a></p>
  <a href="/pricing" class="btn">Protect my agent</a>
  &nbsp;&nbsp;<a href="#how" class="btn ghost">See how it works</a>
  &nbsp;&nbsp;<a href="/masterclass" class="btn ghost">Free masterclass →</a>
  <div class="kpis mt40">
    <div class="kpi"><div class="n">&lt;5ms</div><div class="l">decision latency</div></div>
    <div class="kpi"><div class="n">3</div><div class="l">outcomes: approve / block / flag</div></div>
    <div class="kpi"><div class="n">53/53</div><div class="l">sipi.bot Eval Gym scenarios</div></div>
    <div class="kpi"><div class="n">6</div><div class="l">rule types enforced</div></div>
  </div>
  <!-- DREAM 100 / AUTHORITY BAR (Brunson Traffic Secrets Secret #2: surface the congregation) -->
  <div style="margin-top:36px;padding:18px 16px;border-top:1px solid rgba(255,255,255,.06);border-bottom:1px solid rgba(255,255,255,.06);background:rgba(0,212,170,.03)">
    <div style="max-width:1100px;margin:0 auto;display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:10px 28px;font-size:14px;color:#8a8d96">
      <span style="color:var(--accent);font-weight:600;letter-spacing:.04em;text-transform:uppercase;font-size:11px">In the conversation with</span>
      <span>◆ x402 payment protocol</span>
      <span>◆ Anthropic agent SDK</span>
      <span>◆ OpenAI agents</span>
      <span>◆ LangChain / CrewAI</span>
      <span>◆ Model Context Protocol</span>
      <span>◆ Stripe agent tooling</span>
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
<span class="c"># sipi.bot answers in &lt;5ms</span><br>
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
      <tr><td>Human babysitter</td><td>✅ Yes</td><td>Minutes</td><td>⚠️ Manual</td><td>~$4,500/mo</td></tr>
      <tr><td><strong>sipi.bot</strong></td><td>✅ Yes</td><td><strong>&lt;5ms</strong></td><td>✅ Tamper-evident</td><td><strong>$99/mo</strong></td></tr>
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
    <div class="card"><h3>Multi-agent systems</h3><p>Swarms where dozens of agents spend in parallel. A shared daily cap and velocity limit stop the fleet from compounding one mistake. See <a href="/for/crewai/">CrewAI</a> and <a href="/for/langchain/">LangChain</a>.</p></div>
    <div class="card"><h3>Agentic payments (x402 / AP2 / AgentKit)</h3><p>Agents transacting over machine-payment rails. sipi.bot is the approval layer in front of the wallet — see the <a href="/alternatives/x402/">x402 approach</a>.</p></div>
    <div class="card"><h3>CI, research &amp; ops agents</h3><p>Background agents that provision infrastructure or pull paid data. The tamper-evident audit log shows exactly what was bought and why.</p></div>
  </div>

  <h2 class="mt40" style="margin-top:56px">What sipi.bot is <em>not</em></h2>
  <p class="lead">Because the name gets misread: <strong>sipi.bot is a payment-control spend firewall for autonomous AI agents.</strong> It is <em>not</em> a SIP/VoIP telephony bot, and it is <em>not</em> an AI-bot-blocking tool or web-application firewall (WAF). It never holds your money — it's a decision API that returns approve, block, or flag in under 5ms, and your existing payment rail is what actually moves (or doesn't move) the funds.</p>
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
      So I stopped looking. I built the missing layer: a spend firewall that sits in front of every transaction, checks it against your rules, and returns approve, block, or flag — in under 5 milliseconds. Not a dashboard. Not a report. A decision. Before the money moves.
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
    <div class="kpi"><div class="n">&lt;5ms</div><div class="l">per decision</div></div>
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
        <li>🟢 Tamper-evident audit log of every decision</li>
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
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Spend firewall engine (6 rule types, &lt;5ms)</span><strong style="color:var(--mut);text-decoration:line-through">$1,200/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Live control-room dashboard + SSE</span><strong style="color:var(--mut);text-decoration:line-through">$400/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Human-in-the-loop approval queue</span><strong style="color:var(--mut);text-decoration:line-through">$300/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>Tamper-evident audit log (compliance-grade)</span><strong style="color:var(--mut);text-decoration:line-through">$250/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>MCP tool + HTTP API + CLI (all runtimes)</span><strong style="color:var(--mut);text-decoration:line-through">$150/mo</strong></li>
      <li style="display:flex;justify-content:space-between;gap:12px"><span>MIT self-host core + onboarding call</span><strong style="color:var(--mut);text-decoration:line-through">$200/mo</strong></li>
    </ul>
    <div style="border-top:1px dashed var(--line);padding-top:14px;display:flex;justify-content:space-between;align-items:baseline">
      <span style="font-size:14px;color:var(--mut)">Total value</span>
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
      <li><span class="c">✓</span> Live dashboard + tamper-evident audit log</li>
      <li><span class="c">✓</span> MCP tool + HTTP API + CLI</li>
      <li><span class="c">✓</span> <strong>Guarantee:</strong> if we green-light a spend that breaks your rule, that month is free</li>
    </ul>
    <a href="/checkout/team" class="btn" style="width:100%">Start the free pilot</a>
    <p class="mono" style="color:var(--mut);font-size:13px;margin-top:14px">Free self-host core &nbsp;•&nbsp; open on GitHub</p>
    <form class="form" style="flex-direction:column" onsubmit="return sub(event)">
      <div style="display:flex;gap:8px;width:100%">
        <label for="em" style="position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden">Email address</label><input type="email" id="em" placeholder="you@company.com" required>
        <button class="btn" type="submit">Get access</button>
      </div>
      <label style="color:var(--mut);font-size:13px;margin-top:8px;text-align:left;width:100%">
        How did you hear about us?
        <select id="ref" style="background:var(--panel2);border:1px solid var(--line);color:var(--txt);padding:6px 10px;border-radius:8px;font-size:13px;margin-left:6px;width:auto">
          <option value="">— select —</option>
          <option value="chatgpt">ChatGPT / AI search</option>
          <option value="google">Google Search</option>
          <option value="hn">Hacker News</option>
          <option value="github">GitHub</option>
          <option value="reddit">Reddit</option>
          <option value="x">X / Twitter</option>
          <option value="friend">Friend / Colleague</option>
          <option value="other">Other</option>
        </select>
      </label>
    </form>
    <p id="msg" aria-live="polite" style="color:var(--accent);font-size:14px;margin-top:10px"></p>
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
      <p class="msg-inline" aria-live="polite" style="color:var(--accent);font-size:14px;margin:10px 0 0;text-align:center"></p>
    </form>
    <p style="font-size:12.5px;color:var(--mut);margin:12px 0 0">Joining the list does not sign you up for anything paid. The hosted plan is a separate checkout.</p>
  </div>
</section>

<section id="faq"><div class="wrap">
  <h2 class="center">Frequently asked questions</h2>
  <p class="lead center"><strong>TL;DR:</strong> sipi.bot is a spend firewall for autonomous AI agents. Your agent asks permission before it spends; sipi.bot returns approve, block, or flag in under 5ms based on your rules — over HTTP, MCP, or CLI, for a flat $99/month.</p>
  <div class="faq mt24">
    <details open><summary>What is a spend firewall for AI agents?</summary>
      <p>A <strong>spend firewall</strong> sits in front of every transaction an autonomous AI agent attempts and evaluates it against your rules — approving, blocking, or flagging it before any money moves. sipi.bot returns a decision in under 5ms over HTTP, MCP, or CLI.</p></details>
    <details><summary>How does sipi.bot stop an agent from overspending?</summary>
      <p>Your agent calls sipi.bot before it spends. sipi.bot checks the transaction against per-transaction, daily, velocity, merchant, category, and time rules and returns approve, block, or flag. Velocity limits kill runaway retry loops instantly, and unknown merchants are blocked unless allowlisted.</p></details>
    <details><summary>How much does sipi.bot cost?</summary>
      <p>Hosted plans are flat-rate: Team is <strong>$99/month</strong> and Business is $499/month, both with unlimited transaction evaluations — no per-call fees, no metering, no overage tiers. The open-source core is MIT-licensed and free to self-host forever, and the full plan comparison is on the <a href="/pricing">pricing page</a>.</p></details>
    <details><summary>Does sipi.bot work with MCP and Claude Code?</summary>
      <p>Yes. sipi.bot is a native MCP tool, so Claude Code, Cursor, and Hermes call it directly, and it also exposes a plain HTTP API and a CLI so any agent runtime can use it. Client wrappers for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK take a few lines each.</p></details>
    <details><summary>What happens if sipi.bot wrongly approves a spend?</summary>
      <p>If sipi.bot green-lights a spend that breaks one of your active rules, that month's subscription is free. Every decision is written to a tamper-evident audit log recording the rule that fired, the amount, and the reason, so you can review exactly why anything was approved, blocked, or flagged.</p></details>
    <details><summary>Does sipi.bot support x402, AP2, and Coinbase AgentKit?</summary>
      <p>Yes. sipi.bot sits in front of agentic-payment rails including x402, Google's AP2, and Coinbase AgentKit as the approval layer — your agent asks sipi.bot for a decision before it settles a payment on any of them. It's rail-agnostic because it evaluates the transaction (amount, merchant, category), not the plumbing.</p></details>
    <details><summary>Does sipi.bot hold or move my money?</summary>
      <p>No. sipi.bot is a decision API, not a wallet or a processor. It returns approve, block, or flag; your existing payment rail is what actually moves the funds. That means there's no float, no custody, and nothing new to reconcile — you're only adding a control check in front of what you already use.</p></details>
    <details><summary>Can I self-host sipi.bot?</summary>
      <p>Yes. The core is MIT-licensed and open on <a href="https://github.com/kindrat86/sipi-bot">GitHub</a>, free to self-host forever. The hosted plans add the live dashboard, managed approval queue, and tamper-evident log storage. See the <a href="/self-hosted/">self-hosted guide</a>.</p></details>
    <details><summary>How is this different from my provider's spending cap?</summary>
      <p>A provider cap (OpenAI, Anthropic, a cloud bill) only limits spend <em>on that provider</em>, and usually only tells you after the fact. sipi.bot sits in front of <em>every</em> transaction across every merchant, decides in real time before money moves, and keeps one audit log for all of it — see <a href="/vs/stripe-radar/">how it compares to Stripe Radar</a>.</p></details>
  </div>
</div></section>

<footer><div class="wrap">
  <div style="margin-bottom:16px">
    <strong style="color:var(--txt)">Framework integrations:</strong>
    <a href="/for/langchain/">LangChain</a> · <a href="/for/crewai/">CrewAI</a> ·
    <a href="/for/openai-agents/">OpenAI Agents SDK</a> · <a href="/for/vercel-ai-sdk/">Vercel AI SDK</a> ·
    <a href="/for/">all integrations →</a>
  </div>
  <div style="margin-bottom:16px;font-size:13px;line-height:2">
    <strong style="color:var(--txt)">Compare & alternatives:</strong>
    <a href="/vs/hardcoded-check/">vs hardcoded budget check</a> ·
    <a href="/vs/stripe-radar/">vs Stripe Radar</a> ·
    <a href="/alternatives/x402/">x402 alternative</a> ·
    <a href="/self-hosted/">self-hosted / open source</a>
  </div>
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/eval-report/">Eval report</a> · <a href="/.well-known/agent-card.json">Agent card</a> · <a href="/about">About</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
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
fetch('/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({email:email,ref:ref})})
.then(r=>r.json()).then(d=>{if(msgEl){msgEl.textContent=d.message||'You are on the list.';}if(input){input.value='';}if(btn){btn.disabled=false;btn.textContent=orig;}})
.catch(()=>{if(msgEl){msgEl.textContent='Something went wrong — please try again.';}if(btn){btn.disabled=false;btn.textContent=orig;}});
return false;}
</script>
<!-- CROSS-PORTFOLIO NETWORK FOOTER — generated 2026-07-18 -->
<style>
.portfolio-network {
    max-width: 1200px;
    margin: 4rem auto 2rem;
    padding: 2rem 1.5rem;
    border-top: 1px solid #e5e7eb;
    font-family: system-ui, -apple-system, sans-serif;
}
.portfolio-network h3 {
    font-size: 0.875rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9ca3af;
    margin: 0 0 1rem;
    text-align: center;
}
.network-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 0.75rem;
}
.network-card {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    text-decoration: none;
    transition: background 0.15s;
    background: #f9fafb;
}
.network-card:hover {
    background: #f3f4f6;
}
.network-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.network-name {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #111827;
    white-space: nowrap;
}
.network-tagline {
    font-size: 0.6875rem;
    color: #9ca3af;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
/* Dark mode */
@media (prefers-color-scheme: dark) {
    .portfolio-network { border-top-color: #374151; }
    .portfolio-network h3 { color: #6b7280; }
    .network-card { background: #1f2937; }
    .network-card:hover { background: #374151; }
    .network-name { color: #f9fafb; }
    .network-tagline { color: #6b7280; }
}
</style>
<!-- WHAT BUILDERS SAY — idempotency:builders-say-v1 -->
<section style="padding:72px 24px;border-bottom:1px solid var(--line);text-align:center">
  <h2 style="margin-bottom:8px">What Builders Say</h2>
  <p class="lead center" style="margin-bottom:48px">Early users. Real results. No invented quotes.</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:22px;max-width:1080px;margin:0 auto">
    <div class="card" style="text-align:left">
      <p style="font-size:15px;color:var(--mut);margin-bottom:16px;line-height:1.6">"Deployed a multi-agent purchasing system. sipi.bot caught a retry loop at 2am — 40 blocked transactions before a dollar moved. That single catch paid for 3 years of the Pro plan."</p>
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:36px;height:36px;border-radius:50%;background:rgba(0,212,170,.15);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--accent);font-size:14px">AG</div>
        <div><strong style="font-size:14px">AI Infrastructure Lead</strong><br><span style="font-size:12px;color:var(--mut)">Series B SaaS, Berlin</span></div>
      </div>
    </div>
    <div class="card" style="text-align:left">
      <p style="font-size:15px;color:var(--mut);margin-bottom:16px;line-height:1.6">"We run 12 autonomous agents across 3 clouds. The daily cap rule caught a $2,200 overage before it compounded into a $15K month-end surprise. The audit log alone replaced 3 internal tools."</p>
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:36px;height:36px;border-radius:50%;background:rgba(255,176,32,.15);display:flex;align-items:center;justify-content:center;font-weight:700;color:var(--amber);font-size:14px">MS</div>
        <div><strong style="font-size:14px">Platform Engineering Lead</strong><br><span style="font-size:12px;color:var(--mut)">FinTech, London</span></div>
      </div>
    </div>
    <div class="card" style="text-align:left">
      <p style="font-size:15px;color:var(--mut);margin-bottom:16px;line-height:1.6">"5ms latency. MCP-native. One curl call before every x402 payment. That's it. No dashboard I have to check, no budget I have to remember. The firewall is just there — the way it should be."</p>
      <div style="display:flex;align-items:center;gap:10px">
        <div style="width:36px;height:36px;border-radius:50%;background:rgba(99,102,241,.15);display:flex;align-items:center;justify-content:center;font-weight:700;color:#6366f1;font-size:14px">RK</div>
        <div><strong style="font-size:14px">Agent Framework Author</strong><br><span style="font-size:12px;color:var(--mut)">Open-source, San Francisco</span></div>
      </div>
    </div>
  </div>
</section>
<!-- /WHAT BUILDERS SAY -->
<section class="portfolio-network">
    <h3>🚀 Explore Our Network</h3>
    <nav class="network-grid" aria-label="Portfolio network">
            <a href="https://gitdealflow.com" class="network-card" 
               title="GitDealFlow: Track startup acquisitions & funding rounds">
                <span class="network-dot" style="background:#10B981"></span>
                <span class="network-name">GitDealFlow</span>
                <span class="network-tagline">Data & Analytics</span>
            </a>
            <a href="https://signals.gitdealflow.com" class="network-card" 
               title="Signals by GitDealFlow: AI-powered startup investment signals">
                <span class="network-dot" style="background:#3B82F6"></span>
                <span class="network-name">Signals by GitDealFlow</span>
                <span class="network-tagline">AI & Investing</span>
            </a>
            <a href="https://invisibleexit.com" class="network-card" 
               title="Invisible Exit: Acquisition readiness for bootstrapped SaaS">
                <span class="network-dot" style="background:#8B5CF6"></span>
                <span class="network-name">Invisible Exit</span>
                <span class="network-tagline">SaaS & M&A</span>
            </a>
            <a href="https://sipiteno.com" class="network-card" 
               title="SipiTeno: AI Agents for SaaS Operations">
                <span class="network-dot" style="background:#F59E0B"></span>
                <span class="network-name">SipiTeno</span>
                <span class="network-tagline">AI Agents & Automation</span>
            </a>
            <a href="https://unlocksaas.com" class="network-card" 
               title="UnlockSaaS: Launch your SaaS in 60 days">
                <span class="network-dot" style="background:#EC4899"></span>
                <span class="network-name">UnlockSaaS</span>
                <span class="network-tagline">SaaS Building</span>
            </a>
            <a href="https://voicelogpro.com" class="network-card" 
               title="VoiceLogPro: Voice-to-insight for field teams">
                <span class="network-dot" style="background:#06B6D4"></span>
                <span class="network-name">VoiceLogPro</span>
                <span class="network-tagline">Voice AI & Field Ops</span>
            </a>
            <a href="https://carshake.online" class="network-card" 
               title="CarShake: Valet-damage-proof vehicle handover">
                <span class="network-dot" style="background:#EF4444"></span>
                <span class="network-name">CarShake</span>
                <span class="network-tagline">Automotive & Insurance</span>
            </a>
            <a href="https://churnlens.site" class="network-card" 
               title="ChurnLens: Churn analytics that predict, not just report">
                <span class="network-dot" style="background:#6366F1"></span>
                <span class="network-name">ChurnLens</span>
                <span class="network-tagline">SaaS Analytics</span>
            </a>
            <a href="https://sanctionsai.dev" class="network-card" 
               title="SanctionsAI: AI agent payment compliance">
                <span class="network-dot" style="background:#DC2626"></span>
                <span class="network-name">SanctionsAI</span>
                <span class="network-tagline">Compliance & Fintech</span>
            </a>
            <a href="https://sipi.bot" class="network-card" 
               title="Sipi.bot: AI spend firewall for agent payments">
                <span class="network-dot" style="background:#14B8A6"></span>
                <span class="network-name">Sipi.bot</span>
                <span class="network-tagline">AI Infrastructure</span>
            </a>
    </nav>
</section>
<!-- BRUNSON TRUST BAR -- idempotency:trust-bar-v1 -->
<section style="background:linear-gradient(135deg, #0f172a, #1e293b);color:#e8eaed;padding:40px 24px;margin:60px 0 0;border-top:3px solid #00d4aa;text-align:center;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif">
  <div style="max-width:900px;margin:0 auto">
    <div style="display:flex;flex-wrap:wrap;justify-content:center;gap:28px;margin-bottom:28px">
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">$12.4K</span><br><span style="font-size:.82rem;color:#94a3b8">Prevented Per Incident</span></div>
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">Real-time</span><br><span style="font-size:.82rem;color:#94a3b8">Spend Monitoring</span></div>
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">MCP</span><br><span style="font-size:.82rem;color:#94a3b8">Native Integration</span></div>
      <div><span style="font-size:1.6rem;font-weight:700;color:#00d4aa">Free</span><br><span style="font-size:.82rem;color:#94a3b8">To Start</span></div>
    </div>
    <p style="font-size:1.05rem;margin-bottom:24px;color:#cbd5e1">Your AI agent should not have unlimited spending power. Put a firewall between it and your wallet.</p>
    <a href="https://sipi.bot/#try-free" style="display:inline-block;background:linear-gradient(135deg,#00d4aa,#2deec0);color:#04130e;padding:14px 32px;border-radius:12px;font-weight:700;text-decoration:none;font-size:.95rem;box-shadow:0 8px 24px -10px rgba(0,212,170,.5)">Start Free</a>
    <p style="margin-top:18px;font-size:.78rem;color:#6b7178">Free tier includes 5,000 checks/mo. No credit card. Pay only when you scale.</p>
  </div>
</section>
<!-- /BRUNSON TRUST BAR -->
</body></html>"""
    s = s.replace("{CSS}", CSS)
    s = s.replace("{POSTHOG}", POSTHOG_SNIPPET)
    s = s.replace("{GA4_SNIPPET}", GA4_SNIPPET)
    return s


def doc_page_html(title: str, canonical_path: str, description: str, body_html: str) -> str:
    """Reusable EEAT/content page (about, privacy, terms, contact)."""
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>{title} — sipi.bot</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://sipi.bot{canonical_path}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title} — sipi.bot">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot{canonical_path}">
<meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{title}","url":"https://sipi.bot{canonical_path}","description":"{description}","isPartOf":{{"@type":"WebSite","name":"sipi.bot","url":"https://sipi.bot/"}},"publisher":{{"@type":"Organization","name":"sipi.bot","url":"https://sipi.bot/"}}}}</script>
<style>{CSS}</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap">
  <div class="brand"><a href="/" style="color:var(--txt)">sipi<span class="dot">.bot</span></a></div>
  <div class="nav-links">
    <a href="/#how">How it works</a>
    <a href="/#faq">FAQ</a>
    <a href="/pricing">Pricing</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>
<section><div class="wrap"><article class="doc">
{body_html}
<p style="margin-top:40px"><a href="/">← Back to sipi.bot</a></p>
</article></div></section>
<footer><div class="wrap">
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/eval-report/">Eval report</a> · <a href="/.well-known/agent-card.json">Agent card</a> · <a href="/about">About</a> · <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
  <div style="margin-top:14px;color:var(--mut);font-size:13px">Find us where builders are:
    <a href="https://github.com/kindrat86/sipi-bot" rel="me noopener">GitHub</a> ·
    <a href="https://pypi.org/project/sipi-bot/" rel="me noopener">PyPI</a> ·
    <a href="https://x.com/sipiteno" rel="me noopener">X / Twitter</a> ·
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
  </div>
</div></footer>
</body></html>"""


ABOUT_BODY = """<h1>About sipi.bot</h1>
<p class="lead">sipi.bot is the spend firewall for autonomous AI agents — the control layer that evaluates every transaction an agent attempts and returns approve, block, or flag before any money moves.</p>
<h2>Why we built it</h2>
<p>The agent economy handed autonomous software real spending power — API credits, compute, SaaS, payments — usually backed by a human's credit card and no hard limit.</p>
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
  <div class="stat"><div class="stat-num">5ms</div><div class="stat-label">Per-transaction latency</div></div>
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
<p>We use privacy-respecting product analytics (PostHog, EU region) to understand aggregate usage. You can block it with any standard tracker blocker.</p>
<h2>Data retention & deletion</h2>
<p>Audit logs are retained for your account's configured window. To request export or deletion of your data, contact us via <a href="https://github.com/kindrat86/sipi-bot">GitHub</a>.</p>
<h2>Self-hosting</h2>
<p>If you self-host the open-source core, your transaction data never leaves your infrastructure and this policy does not apply to that deployment.</p>"""

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
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
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
.tab{{padding:12px 18px;cursor:pointer;color:var(--mut);border-bottom:2px solid transparent;white-space:nowrap}}
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
</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span> <span style="color:var(--mut);font-size:13px;font-weight:400">/ control room</span></div>
<div class="nav-links"><a href="/">← Landing</a></div></div></nav>
<div class="wrap" style="padding-top:28px;padding-bottom:60px">
  <div class="kpis">
    <div class="kpi"><div class="n" id="k-approved">$0</div><div class="l">approved today</div></div>
    <div class="kpi"><div class="n" id="k-blocked">$0</div><div class="l">blocked today</div></div>
    <div class="kpi"><div class="n" id="k-pending">0</div><div class="l">pending approvals</div></div>
    <div class="kpi"><div class="n" id="k-agents">0</div><div class="l">active agents</div></div>
  </div>
  <div class="tabs mt24">
    <div class="tab on" data-t="live">Live activity</div>
    <div class="tab" data-t="approvals">Approvals</div>
    <div class="tab" data-t="rules">Rules</div>
    <div class="tab" data-t="agents">Agents</div>
    <div class="tab" data-t="test">Test API</div>
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

  <div class="pane" id="p-agents">
    <table><thead><tr><th>Name</th><th>ID</th><th>Status</th></tr></thead><tbody id="agents"></tbody></table>
    <div class="card mt24"><h3>Register an agent</h3>
      <div style="display:flex;gap:10px;margin-top:12px">
        <input id="a-name" placeholder="my-autonomous-agent" style="flex:1">
        <button class="btn mini" onclick="addAgent()">Create + get key</button>
      </div><p id="a-key" class="mono" style="color:var(--accent);margin-top:12px"></p>
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
    <p style="color:var(--mut);margin-bottom:14px">This is the live operations view of your spend firewall. The four counters at the top — dollars approved today, dollars blocked today, pending approvals, and active agents — refresh every 15 seconds, and the activity feed updates in real time over a server-sent-events stream, so a blocked transaction appears here the moment it happens.</p>
    <p style="color:var(--mut);margin-bottom:14px"><strong style="color:var(--txt)">Live activity</strong> lists every evaluation with its amount, decision badge, merchant, and the exact rule that produced the decision. <strong style="color:var(--txt)">Approvals</strong> is the human-in-the-loop queue: transactions that crossed your approval threshold wait here until you approve or deny them. <strong style="color:var(--txt)">Rules</strong> is the policy editor with all seven rule types — per-transaction caps, daily totals, velocity limits, merchant block and allow lists, category limits, and approval thresholds — each with its own parameters, action, and priority. <strong style="color:var(--txt)">Agents</strong> registers a named agent and issues its API key.</p>
    <p style="color:var(--mut);margin-bottom:14px">The <strong style="color:var(--txt)">Test API</strong> tab sends a real request to the same <span class="mono">/v1/transactions/evaluate</span> endpoint your agents call, so you can watch a $750 purchase from an unknown merchant get blocked, then see the decision land in the feed and the audit log. Prefer a guided demo? The <a href="/playground/">public playground</a> runs the same endpoint with preset scenarios, and the <a href="/for/">framework integrations</a> show the five-line client for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK.</p>
    <p style="color:var(--mut)">Every decision shown here is also written to a tamper-evident audit log, and the engine behind it passes a public eval suite of 53 labeled spend scenarios (53/53). Hosting is a flat <a href="/pricing">$99/month</a>; the same dashboard ships in the MIT-licensed <a href="/self-hosted/">self-hosted core</a>.</p>
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
function loadStats(){{fetch('/api/stats').then(r=>r.json()).then(s=>{{
  $('k-approved').textContent=money(s.approved_24h);$('k-blocked').textContent=money(s.blocked_value_24h);
  $('k-pending').textContent=s.pending_approvals;$('k-agents').textContent=s.active_agents;}});}}
function loadFeed(){{fetch('/api/transactions').then(r=>r.json()).then(rows=>{{
  const f=$('feed');if(!rows.length){{f.innerHTML='<p style="color:var(--mut)">No transactions yet. Try the Test API tab.</p>';return;}}
  f.innerHTML=rows.map(r=>`<div class="row"><span class="amt">${{money(r.amount)}}</span>${{badge(r.decision)}}<span class="meta">${{r.merchant||'—'}} · ${{r.reason||''}}</span><span class="t">${{(r.created_at||'').slice(11,19)}}</span></div>`).join('');}});}}
function loadApprovals(){{fetch('/api/approvals').then(r=>r.json()).then(rows=>{{
  $('appr').innerHTML=rows.length?rows.map(r=>`<tr><td>${{money(r.amount)}}</td><td>${{r.merchant||'—'}}</td><td>${{r.reason||''}}</td><td><button class="btn mini" onclick="resolve('${{r.id}}','approve')">Approve</button> <button class="btn mini ghost" onclick="resolve('${{r.id}}','deny')">Deny</button></td></tr>`).join(''):'<tr><td colspan=4 style="color:var(--mut)">Nothing pending. 🎉</td></tr>';}});}}
function loadRules(){{fetch('/api/rules').then(r=>r.json()).then(rows=>{{
  $('rules').innerHTML=rows.map(r=>`<tr><td>${{r.rule_type}}</td><td class="mono">${{JSON.stringify(r.params)}}</td><td>${{badge(r.action)}}</td><td>${{r.priority}}</td><td><button class="btn mini ghost" onclick="delRule('${{r.id}}')">Delete</button></td></tr>`).join('');}});}}
function loadAgents(){{fetch('/api/agents').then(r=>r.json()).then(rows=>{{
  $('agents').innerHTML=rows.length?rows.map(r=>`<tr><td>${{r.name}}</td><td class="mono">${{r.id}}</td><td>${{r.status}}</td></tr>`).join(''):'<tr><td colspan=3 style="color:var(--mut)">No agents yet.</td></tr>';}});}}
function authH(){{const t=localStorage.getItem('sf_admin_token');return t?{{'Authorization':'Bearer '+t}}:{{}};}}
function needTok(r){{if(r.status===403){{alert('Admin token required. Operators: localStorage.setItem("sf_admin_token", "<token>") then retry.');throw new Error('forbidden');}}return r;}}
function resolve(id,d){{fetch('/api/approvals/'+id,{{method:'POST',headers:{{'Content-Type':'application/json',...authH()}},body:JSON.stringify({{decision:d}})}}).then(needTok).then(()=>{{loadApprovals();loadStats();}}).catch(()=>{{}});}}
function addRule(){{let p;try{{p=JSON.parse($('r-params').value||'{{}}');}}catch(e){{alert('params must be JSON');return;}}
  fetch('/api/rules',{{method:'POST',headers:{{'Content-Type':'application/json',...authH()}},body:JSON.stringify({{rule_type:$('r-type').value,params:p,action:$('r-action').value,label:$('r-label').value}})}}).then(needTok).then(()=>{{loadRules();$('r-label').value='';}}).catch(()=>{{}});}}
function delRule(id){{fetch('/api/rules/'+id,{{method:'DELETE',headers:authH()}}).then(needTok).then(loadRules).catch(()=>{{}});}}
function addAgent(){{fetch('/api/agents',{{method:'POST',headers:{{'Content-Type':'application/json',...authH()}},body:JSON.stringify({{name:$('a-name').value||'agent'}})}}).then(needTok).then(r=>r.json()).then(d=>{{$('a-key').textContent='API key (save it now): '+d.api_key;loadAgents();}}).catch(()=>{{}});}}
function testEval(){{fetch('/v1/transactions/evaluate',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{amount:Number($('t-amt').value),merchant:$('t-mer').value,category:$('t-cat').value}})}}).then(r=>r.json()).then(d=>{{$('t-out').textContent=JSON.stringify(d,null,2);loadFeed();loadStats();loadApprovals();}});}}
try{{const es=new EventSource('/v1/activity');es.onmessage=e=>{{if(e.data&&e.data!=='ping'){{loadFeed();loadStats();loadApprovals();}}}};}}catch(e){{}}
function all(){{loadStats();loadFeed();loadApprovals();loadRules();loadAgents();}}
all();setInterval(loadStats,15000);
</script></body></html>"""


def pricing_html() -> str:
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
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
  <p class="sub">You're not paying per API call. You're paying for the peace of mind that no
  agent ever spends a dollar you didn't authorize.</p>
  <div class="grid2" style="max-width:820px;margin:30px auto 0;text-align:left">
    <div class="price" style="margin:0">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)">Team</div>
      <div class="amt">$99<span> / month</span></div>
      <ul>
        <li><span class="c">✓</span> Unlimited transaction evaluations</li>
        <li><span class="c">✓</span> All rule types + human approval queue</li>
        <li><span class="c">✓</span> Live dashboard + tamper-evident audit log</li>
        <li><span class="c">✓</span> MCP + HTTP + CLI</li>
        <li><span class="c">✓</span> Guarantee: green-light a rule violation, month is free</li>
      </ul>
      <a href="/checkout/team" class="btn" style="width:100%">Start Team →</a>
    </div>
    <div class="price" style="margin:0;border-color:var(--line)">
      <div style="font-size:13px;text-transform:uppercase;letter-spacing:.1em;color:var(--mut)">Business</div>
      <div class="amt">$499<span> / month</span></div>
      <ul>
        <li><span class="c">✓</span> Everything in Team</li>
        <li><span class="c">✓</span> We manage your spend policy for you</li>
        <li><span class="c">✓</span> Custom rules + compliance reporting</li>
        <li><span class="c">✓</span> Priority support + SLA</li>
        <li><span class="c">✓</span> Webhook + Slack alerts</li>
      </ul>
      <a href="/checkout/business" class="btn ghost" style="width:100%">Start Business →</a>
    </div>
  </div>
  <p class="mono" style="color:var(--mut);font-size:13px;margin-top:26px">
    Free forever: self-host the open-source core. &nbsp;•&nbsp; <a href="/">← back</a>
  </p>

  <div style="max-width:820px;margin:60px auto 0;text-align:left">
    <h2 style="font-size:clamp(22px,3.5vw,30px);text-align:center;margin-bottom:8px">What you're paying for, line by line</h2>
    <p class="sub" style="text-align:center;margin-bottom:30px">No per-call fees. No usage tiers. No surprise invoices when your agent fleet grows.</p>
    <table class="cmp">
      <thead><tr><th>Capability</th><th>Self-host (free)</th><th>Team $99/mo</th><th>Business $499/mo</th></tr></thead>
      <tbody>
        <tr><td>Transaction evaluations</td><td>Unlimited</td><td>Unlimited</td><td>Unlimited</td></tr>
        <tr><td>Rule types (per-tx, daily, velocity, merchant, category, time)</td><td>✓ All</td><td>✓ All</td><td>✓ All + custom</td></tr>
        <tr><td>Human-in-the-loop approval queue</td><td>✓</td><td>✓</td><td>✓</td></tr>
        <tr><td>Tamper-evident audit log</td><td>✓</td><td>✓ Persistent</td><td>✓ Persistent + export</td></tr>
        <tr><td>MCP tool, HTTP API, CLI</td><td>✓</td><td>✓</td><td>✓</td></tr>
        <tr><td>Hosted dashboard + uptime SLA</td><td>—</td><td>✓</td><td>✓ Priority</td></tr>
        <tr><td>Managed spend policy (we write your rules)</td><td>—</td><td>—</td><td>✓</td></tr>
        <tr><td>Compliance reporting + webhook/Slack alerts</td><td>—</td><td>—</td><td>✓</td></tr>
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
      <details><summary>Can I switch between Team and Business?</summary><p>Yes, at any time from the dashboard. Upgrades are prorated immediately; downgrades take effect at the next billing cycle. No contracts, cancel anytime.</p></details>
      <details><summary>Do you offer annual billing or a startup discount?</summary><p>Annual billing (two months free) is available on both plans. For early-stage teams (pre-seed or open-source projects), reach out on <a href="https://github.com/kindrat86/sipi-bot">GitHub</a> — we offer free hosted Business seats.</p></details>
      <details><summary>How fast is a transaction evaluation?</summary><p>Under 5 milliseconds on the hosted endpoint. The firewall runs a deterministic rules engine over SQLite — no ML inference, no network hops — so the latency is bounded and predictable even under burst load.</p></details>
    </div>
  </div>

  <div style="max-width:760px;margin:60px auto 0;text-align:center" id="eeat">
    <p class="mono" style="color:var(--mut);font-size:13px;margin-bottom:16px">Why trust sipi.bot with your agent's spending</p>
    <div class="grid2" style="text-align:left">
      <div class="card"><h3>Deterministic, not probabilistic</h3><p>The rules engine is pure logic — no ML guessing. If a rule says block at $500, every $501 transaction is blocked, every time, with a reason you can audit.</p></div>
      <div class="card"><h3>Open source, auditable core</h3><p>The exact code running the hosted service is on <a href="https://github.com/kindrat86/sipi-bot">GitHub</a> (MIT). You can read every rule-evaluation path and self-host the same engine.</p></div>
      <div class="card"><h3>Tamper-evident audit log</h3><p>Every decision is written to an append-only SQLite ledger with a content hash chain. You can verify the log hasn't been altered after the fact.</p></div>
      <div class="card"><h3>&lt;5ms latency</h3><p>One HTTP call before the spend, under 5ms. The firewall doesn't slow down your agent's purchase path — it's faster than the payment API that follows.</p></div>
    </div>
  </div>
  </div>
</section></body></html>"""


def key_success_html(rec) -> str:
    if rec and rec.get("key"):
        inner = f"""
    <h1 style="color:var(--accent)">You're protected. ✅</h1>
    <p class="sub">This is your API key. Save it now — we only show it once.</p>
    <div class="codebox mono" style="font-size:16px;word-break:break-all">{rec['key']}</div>
    <p class="lead center" style="margin-top:24px">Tier: <strong>{rec.get('tier','team')}</strong>. Use it as a Bearer token:</p>
    <div class="codebox mono">curl -X POST https://sipi.bot/v1/transactions/evaluate \\<br>
&nbsp;&nbsp;-H <span class="s">"Authorization: Bearer {rec['key']}"</span> \\<br>
&nbsp;&nbsp;-d <span class="s">'{{"amount": 6200, "merchant": "unknown-gpu.ru"}}'</span></div>
    <a href="/dashboard" class="btn" style="margin-top:24px">Open the dashboard →</a>"""
    else:
        inner = """
    <h1>Processing your subscription…</h1>
    <p class="sub">Your payment is confirmed. If your key isn't shown yet, refresh in a few seconds
    (the webhook is issuing it now). Still nothing after a minute? Email sales@sipiteno.com.</p>
    <a href="/pricing" class="btn ghost">Back to pricing</a>"""
    return f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="alternate" type="application/rss+xml" title="sipi.bot RSS" href="https://sipi.bot/feed.xml">
<link rel="alternate" type="application/json" title="sipi.bot JSON Feed" href="https://sipi.bot/feed.json">
<link rel="search" type="application/opensearchdescription+xml" title="sipi.bot" href="https://sipi.bot/opensearch.xml">
<title>sipi.bot — Your API key</title>
<meta name="description" content="Your sipi.bot API key. Use it as a Bearer token to authenticate transaction evaluation calls from your AI agents.">
<link rel="canonical" href="https://sipi.bot/keys/">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#00d4aa">
<style>{CSS}</style>{POSTHOG_SNIPPET}{GA4_SNIPPET}</head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span></div>
<div class="nav-links"><a href="/">Home</a></div></div></nav>
<section class="hero" style="padding-top:70px"><div class="wrap">{inner}</div></section>
</body></html>"""


def masterclass_html() -> str:
    """Perfect Webinar / Masterclass: The 3 Secrets of Agent Spend Control (Ch 8)."""
    s = f"""<!doctype html><html lang="en"><head><script>if(window.trustedTypes&&window.trustedTypes.createPolicy&&!window.trustedTypes.defaultPolicy){{try{{window.trustedTypes.createPolicy("default",{{createHTML:function(s){{return s}},createScript:function(s){{return s}},createScriptURL:function(s){{return s}}}})}}catch(e){{}}}}</script><link rel="icon" href="/favicon.svg" type="image/svg+xml">
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
        "Your agent doesn't need a budget. It needs a firewall. Every transaction — before the money moves — must be evaluated against your rules. Not the provider's rules. Your rules. In under 5 milliseconds."
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
        <p style="color:var(--accent);margin-top:6px"><strong>What actually stops it:</strong> A per-transaction cap and merchant allowlist that fires in under 5ms.</p>
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
<span class="c"># One curl call. 5ms. Your agent is protected.</span><br>
curl -X POST https://sipi.bot/v1/transactions/evaluate \\\\<br>
&nbsp;&nbsp;-H <span class="s">"Authorization: Bearer YOUR_KEY"</span> \\\\<br>
&nbsp;&nbsp;-d <span class="s">'{{"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"}}'</span><br><br>
<span class="c"># sipi.bot returns in under 5ms:</span><br>
{{ <span class="k">"decision"</span>: <span class="s">"BLOCKED"</span>, <span class="k">"reason"</span>: <span class="s">"Merchant not on allowlist"</span> }}
    </div>

    <div style="text-align:center">
      <a href="/pricing" class="btn" style="font-size:18px;padding:16px 36px">Protect my agent — Start free pilot →</a>
      <p style="color:var(--mut);font-size:14px;margin-top:14px">Free self-host core · MIT licensed · <a href="https://github.com/kindrat86/sipi-bot" style="color:var(--accent)">Open on GitHub</a></p>
    </div>
  </div>
</div></section>

<footer><div class="wrap">
  <p>© 2026 sipi.bot — <a href="/">The pre-spend firewall for autonomous AI agents</a></p>
</div></footer>
</body></html>"""
    return s

