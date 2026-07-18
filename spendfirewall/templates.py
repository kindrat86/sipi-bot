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
nav .wrap{display:flex;align-items:center;justify-content:space-between;height:60px}
.brand{font-weight:700;font-size:19px;letter-spacing:-.02em}
.brand .dot{color:var(--accent)}
.nav-links{display:flex;gap:22px;align-items:center;font-size:14px}
.nav-links a{color:var(--mut)}.nav-links a:hover{color:var(--txt)}
.btn{display:inline-block;background:var(--accent);color:#04120e;font-weight:700;padding:12px 22px;border-radius:10px;border:none;cursor:pointer;font-size:15px;transition:transform .1s}
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
@media(max-width:760px){.grid2,.contrast,.kpis{grid-template-columns:1fr}.nav-links a:not(.btn){display:none}section{padding:52px 0}.cmp{font-size:12.5px}.cmp th,.cmp td{padding:8px}}
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
    s = """<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>sipi.bot — The Spend Firewall for AI Agents</title>
<meta name="description" content="sipi.bot is a spend firewall for autonomous AI agents: one API call returns APPROVED, BLOCKED, or FLAGGED against your caps, velocity, and merchant rules before an agent spends. Not a SIP/VoIP telephony bot.">
<link rel="canonical" href="https://sipi.bot/">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:title" content="sipi.bot — The Spend Firewall for AI Agents">
<meta property="og:description" content="sipi.bot is a spend firewall (payment-control API) for autonomous AI agents: approve, block, or flag every agent transaction before a dollar moves. Not a SIP/VoIP telephony bot.">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot/">
<meta property="og:image" content="https://sipi.bot/og.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:alt" content="sipi.bot — The spend firewall for AI agents"><meta property="og:site_name" content="sipi.bot">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="sipi.bot — The Spend Firewall for AI Agents">
<meta name="twitter:description" content="Approve, block, or flag every agent transaction before a dollar moves.">
<meta name="twitter:image" content="https://sipi.bot/og.png">
<meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{"@context":"https://schema.org","@graph":[{"@type":"Organization","@id":"https://sipi.bot/#org","name":"sipi.bot","alternateName":["sipibot","sipi bot","sipi.bot spend firewall"],"url":"https://sipi.bot/","description":"sipi.bot is a spend firewall for autonomous AI agents — a real-time API that returns APPROVED, BLOCKED, or FLAGGED for every payment an agent attempts, enforcing per-transaction caps, daily totals, velocity limits, and merchant rules so a runaway agent can't drain your funds.","disambiguatingDescription":"sipi.bot is a payment-control spend firewall API for autonomous AI agents (x402 / AP2 / AgentKit) — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.","sameAs":["https://github.com/kindrat86/sipi-bot","https://pypi.org/project/sipi-bot/"]},{"@type":"WebSite","@id":"https://sipi.bot/#website","url":"https://sipi.bot/","name":"sipi.bot","publisher":{"@id":"https://sipi.bot/#org"}},{"@type":"WebPage","@id":"https://sipi.bot/#page","url":"https://sipi.bot/","name":"sipi.bot — The Spend Firewall for AI Agents","isPartOf":{"@id":"https://sipi.bot/#website"},"datePublished":"2026-07-08","dateModified":"2026-07-17"},{"@type":"BreadcrumbList","@id":"https://sipi.bot/#breadcrumb","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":"https://sipi.bot/"}]},{"@type":"SiteNavigationElement","name":["Home","Dashboard","Pricing","About"],"url":["https://sipi.bot/","https://sipi.bot/dashboard","https://sipi.bot/pricing","https://sipi.bot/about"]},{"@type":"SoftwareApplication","@id":"https://sipi.bot/#app","name":"sipi.bot","alternateName":["sipibot","sipi bot"],"applicationCategory":"BusinessApplication","operatingSystem":"Any (HTTP API, MCP, CLI)","description":"Spend firewall that evaluates every autonomous-agent transaction against your rules and returns approve, block, or flag in under 5ms.","disambiguatingDescription":"A payment-control spend firewall API for autonomous AI agents — not a SIP/VoIP telephony bot and not an AI-bot-blocking / WAF tool.","offers":{"@type":"Offer","price":"99","priceCurrency":"USD"},"featureList":["Per-transaction, daily, velocity, merchant, category and time rules","Human-in-the-loop approval queue","Tamper-evident audit log","MCP tool + HTTP API + CLI"]},{"@type":"FAQPage","@id":"https://sipi.bot/#faq","mainEntity":[{"@type":"Question","name":"What is a spend firewall for AI agents?","acceptedAnswer":{"@type":"Answer","text":"A spend firewall sits in front of every transaction an autonomous AI agent attempts and evaluates it against your rules — approving, blocking, or flagging it before any money moves. sipi.bot returns a decision in under 5ms over HTTP, MCP, or CLI."}},{"@type":"Question","name":"How does sipi.bot stop an agent from overspending?","acceptedAnswer":{"@type":"Answer","text":"Your agent calls sipi.bot before it spends. sipi.bot checks the transaction against per-transaction, daily, velocity, merchant, category, and time rules and returns approve, block, or flag. Velocity limits kill runaway retry loops instantly, and unknown merchants are blocked unless allowlisted."}},{"@type":"Question","name":"How much does sipi.bot cost?","acceptedAnswer":{"@type":"Answer","text":"Hosted plans are flat-rate: Team is $99/month and Business is $499/month, both with unlimited transaction evaluations — no per-call fees, no metering, no overage tiers. The open-source core is MIT-licensed and free to self-host forever."}},{"@type":"Question","name":"Does sipi.bot work with MCP and Claude Code?","acceptedAnswer":{"@type":"Answer","text":"Yes. sipi.bot is a native MCP tool, so Claude Code, Cursor, and Hermes call it directly, and it also exposes a plain HTTP API and a CLI so any agent runtime can use it. Client wrappers for LangChain, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK take a few lines each."}},{"@type":"Question","name":"Is sipi.bot a SIP, voice, or telephony product?","acceptedAnswer":{"@type":"Answer","text":"No. Despite the name, sipi.bot has nothing to do with SIP, VoIP, or voice, and it is not a bot-management or 'block AI bots' tool. sipi.bot is a spend firewall that governs how much money autonomous AI agents can spend."}}]}]}</script>
<style>{CSS}</style>{POSTHOG}{GA4_SNIPPET}</head><body>
<nav><div class="wrap">
  <div class="brand">sipi<span class="dot">.bot</span></div>
  <div class="nav-links">
    <a href="#how">How it works</a>
    <a href="#faq">FAQ</a>
    <a href="#pricing">Pricing</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>

<header class="hero"><div class="wrap">
  <span class="tag">Spend controls for the agent economy</span>
  <h1>Your AI agent just spent<br><span class="hl">$12,400 while you slept.</span></h1>
  <p class="author" style="color:#8a8d96;font-size:14px;margin:4px 0 10px"><span rel="author">By the sipi.bot engineering team</span> · Published 2026-07-08 · Last updated 2026-07-17</p>
  <p class="sub"><strong>sipi.bot is a spend firewall for autonomous AI agents:</strong> it evaluates every transaction against your rules and returns approve, block, or flag in under 5ms — before a single dollar moves. You gave an autonomous agent your credit card and no spending limit; sipi.bot is the control layer that sits in front of it.</p>
  <a href="/pricing" class="btn">Protect my agent</a>
  &nbsp;&nbsp;<a href="#how" class="btn ghost">See how it works</a>
  <div class="kpis mt40">
    <div class="kpi"><div class="n">&lt;5ms</div><div class="l">decision latency</div></div>
    <div class="kpi"><div class="n">3</div><div class="l">outcomes: approve / block / flag</div></div>
    <div class="kpi"><div class="n">53/53</div><div class="l">eval scenarios passing</div></div>
    <div class="kpi"><div class="n">MCP</div><div class="l">+ HTTP + CLI native</div></div>
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
        <input type="email" id="em" placeholder="you@company.com" required>
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
    <p id="msg" style="color:var(--accent);font-size:14px;margin-top:10px"></p>
  </div>
</div></section>

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
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
  </div>
</div></footer>
<script>
function sub(e){e.preventDefault();var m=document.getElementById('msg');
var ref=document.getElementById('ref')?document.getElementById('ref').value:'';
fetch('/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},
body:JSON.stringify({email:document.getElementById('em').value,ref:ref})})
.then(r=>r.json()).then(d=>{m.textContent=d.message||'You are on the list.';document.getElementById('em').value='';document.getElementById('ref').value='';})
.catch(()=>{m.textContent='You are on the list.';});return false;}
</script>
</body></html>"""
    s = s.replace("{CSS}", CSS)
    s = s.replace("{POSTHOG}", POSTHOG_SNIPPET)
    return s


def doc_page_html(title: str, canonical_path: str, description: str, body_html: str) -> str:
    """Reusable EEAT/content page (about, privacy, terms, contact)."""
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — sipi.bot</title>
<meta name="description" content="{description}">
<link rel="canonical" href="https://sipi.bot{canonical_path}">
<meta name="robots" content="index, follow">
<meta property="og:title" content="{title} — sipi.bot">
<meta property="og:description" content="{description}">
<meta property="og:type" content="website"><meta property="og:url" content="https://sipi.bot{canonical_path}">
<meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{{"@context":"https://schema.org","@type":"WebPage","name":"{title}","url":"https://sipi.bot{canonical_path}","description":"{description}","isPartOf":{{"@type":"WebSite","name":"sipi.bot","url":"https://sipi.bot/"}},"publisher":{{"@type":"Organization","name":"sipi.bot","url":"https://sipi.bot/"}}}}</script>
<style>{CSS}</style>{POSTHOG_SNIPPET}</head><body>
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
    <a href="/.well-known/mcp.json">MCP manifest</a> ·
    <a href="/agents.md">Agent guide</a>
  </div>
</div></footer>
</body></html>"""


ABOUT_BODY = """<h1>About sipi.bot</h1>
<p class="lead">sipi.bot is the spend firewall for autonomous AI agents — the control layer that evaluates every transaction an agent attempts and returns approve, block, or flag before any money moves.</p>
<h2>Why we built it</h2>
<p>The agent economy handed autonomous software real spending power — API credits, compute, SaaS, payments — usually backed by a human's credit card and no hard limit. One infinite retry loop or one compromised prompt can drain thousands of dollars before anyone notices. "Trust the prompt" is not a spending policy.</p>
<p>sipi.bot puts a deterministic firewall in front of that spending power. Your agent asks permission first; sipi.bot checks the transaction against per-transaction, daily, velocity, merchant, category, and time rules and answers in under 5&nbsp;ms. Every decision is written to a tamper-evident audit log, and the transactions that matter go to a human-in-the-loop approval queue.</p>
<h2>How it works</h2>
<p>sipi.bot exposes three native surfaces so any agent runtime can call it: a plain HTTP API, an MCP tool (for Claude Code, Cursor, and Hermes), and a CLI. The core engine is open source and self-hostable on GitHub; the hosted service is a flat $99/month for unlimited evaluations.</p>
<h2>Who it's for</h2>
<p>Teams and builders running autonomous agents that can spend money — payment agents, procurement bots, DevOps automations, and AI copilots with billing access — who need real spend controls, an audit trail, and human oversight without slowing the agent down.</p>
<h2>Contact</h2>
<p>Questions, security reports, or partnership requests: reach us on <a href="https://github.com/kindrat86/sipi-bot">GitHub</a>.</p>"""

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
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
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
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
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
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>sipi.bot — Your API key</title>
<meta name="description" content="Your sipi.bot API key. Use it as a Bearer token to authenticate transaction evaluation calls from your AI agents.">
<link rel="canonical" href="https://sipi.bot/keys/">
<meta name="robots" content="noindex, nofollow"><meta name="theme-color" content="#00d4aa">
<style>{CSS}</style>{POSTHOG_SNIPPET}</head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span></div>
<div class="nav-links"><a href="/">Home</a></div></div></nav>
<section class="hero" style="padding-top:70px"><div class="wrap">{inner}</div></section>
</body></html>"""

