"""templates.py — landing page (Brunson H/S/O + Isenberg teardown) + dashboard.

Dark, code-forward, mobile-first. Stdlib string templates (no jinja).
"""
from __future__ import annotations

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
@media(max-width:760px){.grid2,.contrast,.kpis{grid-template-columns:1fr}.nav-links a:not(.btn){display:none}section{padding:52px 0}}
"""


def landing_page_html() -> str:
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>sipi.bot — The Spend Firewall for AI Agents</title>
<meta name="description" content="Your autonomous AI agent has your credit card. sipi.bot approves, blocks, or flags every transaction against your rules — before a dollar moves. Spend controls for the agent economy.">
<meta property="og:title" content="sipi.bot — The Spend Firewall for AI Agents">
<meta property="og:description" content="Approve, block, or flag every agent transaction before a dollar moves.">
<meta property="og:type" content="website"><meta name="theme-color" content="#00d4aa">
<style>{CSS}</style></head><body>
<nav><div class="wrap">
  <div class="brand">sipi<span class="dot">.bot</span></div>
  <div class="nav-links">
    <a href="#how">How it works</a>
    <a href="#pricing">Pricing</a>
    <a href="/dashboard" class="btn">Live Dashboard</a>
  </div>
</div></nav>

<header class="hero"><div class="wrap">
  <span class="tag">Spend controls for the agent economy</span>
  <h1>Your AI agent just spent<br><span class="hl">$12,400 while you slept.</span></h1>
  <p class="sub">You gave an autonomous agent your credit card and no spending limit. sipi.bot is the firewall that sits in front of every transaction and approves, blocks, or flags it against <em>your</em> rules — before a single dollar moves.</p>
  <a href="/pricing" class="btn">Protect my agent</a>
  &nbsp;&nbsp;<a href="#how" class="btn ghost">See how it works</a>
  <div class="kpis mt40">
    <div class="kpi"><div class="n">&lt;5ms</div><div class="l">decision latency</div></div>
    <div class="kpi"><div class="n">3</div><div class="l">outcomes: approve / block / flag</div></div>
    <div class="kpi"><div class="n">50</div><div class="l">scenario eval gym</div></div>
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
&nbsp;&nbsp;-H <span class="s">"Authorization: Bearer sk_live_..."</span> \\<br>
&nbsp;&nbsp;-d <span class="s">'{{"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"}}'</span><br><br>
<span class="c"># sipi.bot answers in &lt;5ms</span><br>
{{ <span class="k">"decision"</span>: <span class="s">"BLOCKED"</span>, <span class="k">"reason"</span>: <span class="s">"Merchant not on allowlist"</span> }}
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
    <form class="form" onsubmit="return sub(event)">
      <input type="email" id="em" placeholder="you@company.com" required>
      <button class="btn" type="submit">Get access</button>
    </form>
    <p id="msg" style="color:var(--accent);font-size:14px;margin-top:10px"></p>
  </div>
</div></section>

<footer><div class="wrap">
  sipi<span style="color:var(--accent)">.bot</span> — the spend firewall for autonomous AI agents.<br>
  <a href="/dashboard">Dashboard</a> · <a href="/eval">Eval report</a> · <a href="/health">Status</a> · <a href="/.well-known/agent-card.json">Agent card</a>
</div></footer>
<script>
function sub(e){{e.preventDefault();var m=document.getElementById('msg');
fetch('/subscribe',{{method:'POST',headers:{{'Content-Type':'application/json'}},
body:JSON.stringify({{email:document.getElementById('em').value}})}})
.then(r=>r.json()).then(d=>{{m.textContent=d.message||'You are on the list.';document.getElementById('em').value='';}})
.catch(()=>{{m.textContent='You are on the list.';}});return false;}}
</script>
</body></html>"""


def dashboard_html() -> str:
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>sipi.bot — Control Room</title><style>{CSS}
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
</style></head><body>
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
function resolve(id,d){{fetch('/api/approvals/'+id,{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{decision:d}})}}).then(()=>{{loadApprovals();loadStats();}});}}
function addRule(){{let p;try{{p=JSON.parse($('r-params').value||'{{}}');}}catch(e){{alert('params must be JSON');return;}}
  fetch('/api/rules',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{rule_type:$('r-type').value,params:p,action:$('r-action').value,label:$('r-label').value}})}}).then(()=>{{loadRules();$('r-label').value='';}});}}
function delRule(id){{fetch('/api/rules/'+id,{{method:'DELETE'}}).then(loadRules);}}
function addAgent(){{fetch('/api/agents',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{name:$('a-name').value||'agent'}})}}).then(r=>r.json()).then(d=>{{$('a-key').textContent='API key (save it now): '+d.api_key;loadAgents();}});}}
function testEval(){{fetch('/v1/transactions/evaluate',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{amount:Number($('t-amt').value),merchant:$('t-mer').value,category:$('t-cat').value}})}}).then(r=>r.json()).then(d=>{{$('t-out').textContent=JSON.stringify(d,null,2);loadFeed();loadStats();loadApprovals();}});}}
try{{const es=new EventSource('/v1/activity');es.onmessage=e=>{{if(e.data&&e.data!=='ping'){{loadFeed();loadStats();loadApprovals();}}}};}}catch(e){{}}
function all(){{loadStats();loadFeed();loadApprovals();loadRules();loadAgents();}}
all();setInterval(loadStats,15000);
</script></body></html>"""


def pricing_html() -> str:
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>sipi.bot — Pricing</title><style>{CSS}</style></head><body>
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
<title>sipi.bot — Your API key</title><style>{CSS}</style></head><body>
<nav><div class="wrap"><div class="brand">sipi<span class="dot">.bot</span></div>
<div class="nav-links"><a href="/">Home</a></div></div></nav>
<section class="hero" style="padding-top:70px"><div class="wrap">{inner}</div></section>
</body></html>"""

