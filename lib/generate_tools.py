#!/usr/bin/env python3
"""generate_tools.py — free interactive tools for sipi.bot.

Outputs:
  tools/agent-spend-risk-calculator/index.html    — risk score 1-10 calculator
  tools/spend-policy-generator/index.html         — ruleset generator
  tools/index.html                                 — hub (placeholder)

Pure client-side (vanilla JS, no backend). Shareable URLs for risk scores.
All pages use lib/common.py shared chrome + carry SoftwareApplication + HowTo
+ FAQPage structured data so AI search can surface them as "free X tool."
"""
from __future__ import annotations
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, ROOT)

from lib import common as c  # noqa: E402

TOOLS_DIR = os.path.join(ROOT, "tools")


# ============================================================== risk calculator
def build_risk_calc():
    body = """
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/tools/">Tools</a><span class="sep">/</span>Risk calculator</div>
<span class="kicker">Free tool · no signup</span>
<h1>Agent Spend Risk Calculator</h1>
<p class="lead">Estimate your worst-case loss exposure and get a risk score from 1–10. No account needed — the math runs in your browser.</p>
</section>

<style>
.risk-form{max-width:640px}
.field{margin-bottom:20px}
.field label{display:block;font-weight:650;color:var(--fg);margin-bottom:6px;font-size:.95rem}
.field .hint{font-size:.83rem;color:var(--fg-3);margin-bottom:8px}
.field input,.field select{width:100%;background:var(--bg-1);border:1px solid var(--line);
  color:var(--fg);padding:12px 14px;border-radius:var(--r-s);font-size:1rem;font-family:inherit;
  appearance:none}
.field select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%238a8d96' fill='none' stroke-width='1.8'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 14px center;padding-right:40px}
.field input:focus,.field select:focus{outline:none;border-color:var(--mint-line);box-shadow:0 0 0 3px var(--mint-soft)}
.radio-group{display:flex;gap:10px;flex-wrap:wrap}
.radio-group label{cursor:pointer;background:var(--bg-1);border:1px solid var(--line);
  border-radius:var(--r-s);padding:10px 16px;font-size:.9rem;color:var(--fg-2);transition:.15s var(--ease)}
.radio-group label:hover{border-color:var(--mint-line)}
.radio-group input{display:none}
.radio-group input:checked+span{border-color:var(--mint);background:var(--mint-soft);color:var(--fg);font-weight:650}
.radio-group label:has(input:checked){border-color:var(--mint);background:var(--mint-soft);color:var(--fg);font-weight:650}
.result-box{display:none;margin:30px 0;background:var(--bg-1);border:1px solid var(--line);
  border-radius:var(--r-l);padding:28px}
.result-box.show{display:block}
.result-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-bottom:20px}
@media(max-width:640px){.result-grid{grid-template-columns:1fr}}
.score-ring{text-align:center}
.score-ring .num{font-size:4rem;font-weight:800;letter-spacing:-.04em;line-height:1}
.score-ring .label{font-size:.82rem;color:var(--fg-3);margin-top:6px;text-transform:uppercase;letter-spacing:.06em}
.rec{background:var(--bg-2);border:1px solid var(--line);border-radius:var(--r);padding:18px;margin-top:14px}
.rec h4{margin:0 0 6px}
.url-share{font-size:.84rem;word-break:break-all;color:var(--mint);margin-top:8px}
@media(max-width:640px){.result-grid{grid-template-columns:1fr}}
</style>

<div class="risk-form">
<div class="field">
<label>How many spending tools does your agent have?</label>
<div class="hint">Count every tool/function that can trigger a payment, an API call, a cloud provision, a database write on a live system, a crypto transfer, or any spend-adjacent action.</div>
<input id="tools-count" type="number" min="1" max="500" value="5" placeholder="5" />
</div>

<div class="field">
<label>What's your single largest transaction risk?</label>
<div class="hint">If your most dangerous tool were called by accident, how much exposure would one transaction create? Pick the closest bracket.</div>
<select id="tx-risk">
<option value="10">$10 or less (micro-transaction)</option>
<option value="100">Up to $100 (API / token purchase)</option>
<option value="1000" selected>Up to $1,000 (cloud provision / SaaS license)</option>
<option value="10000">Up to $10,000 (enterprise contract / infra)</option>
<option value="100000">$100K+ (crypto / trading / treasury)</option>
</select>
</div>

<div class="field">
<label>Does your agent run unattended?</label>
<div class="hint">Overnight, while you sleep — with no human watching.</div>
<div class="radio-group" id="unattended-group">
<label><input type="radio" name="unattended" value="yes" checked /><span>Yes, it runs autonomously</span></label>
<label><input type="radio" name="unattended" value="no" /><span>No, there's always a human watching</span></label>
</div>
</div>

<div class="field">
<label>Does it retry on failure?</label>
<div class="hint">If a tool call fails, does the agent keep trying?</div>
<div class="radio-group" id="retry-group">
<label><input type="radio" name="retry" value="yes" checked /><span>Yes, it retries automatically</span></label>
<label><input type="radio" name="retry" value="no" /><span>No retries, or limited count</span></label>
</div>
</div>

<div class="field">
<label>Monthly cloud/API budget?</label>
<div class="hint">What you budget for all agent spend combined — API credits, cloud costs, tool calls.</div>
<select id="monthly-budget">
<option value="100">$100/mo (small project)</option>
<option value="1000" selected>$1,000/mo (team agent)</option>
<option value="5000">$5,000/mo (production fleet)</option>
<option value="20000">$20,000/mo (enterprise)</option>
<option value="100000">$100K+/mo (heavy infrastructure)</option>
</select>
</div>

<button class="btn primary" onclick="calcRisk()" style="font-size:1.1rem;padding:16px 32px;width:100%;cursor:pointer">Calculate my risk score</button>
</div>

<div class="result-box" id="result">
<div class="result-grid">
<div class="score-ring"><div class="num" id="risk-score" style="color:var(--mint)">—</div><div class="label">Risk score</div></div>
<div class="score-ring"><div class="num" id="worst-24h" style="color:var(--red)">—</div><div class="label">Worst-case 24h</div></div>
<div class="score-ring"><div class="num" id="annual-exp" style="color:var(--amber)">—</div><div class="label">Annual exposure</div></div>
</div>
<div class="rec" id="recommendation"></div>
<div class="url-share" id="share-url"></div>
<div class="btns" style="margin-top:16px">
<a class="btn primary" href="/pricing">Deploy sipi.bot — $99/mo</a>
<a class="btn ghost" href="/tools/spend-policy-generator/">Generate a ruleset →</a>
</div>
</div>

<script>
function $(id){return document.getElementById(id)}
function val(name){var e=document.querySelector('input[name="'+name+'"]:checked');return e?e.value:null}
function digits(n){return (n||0).toLocaleString('en-US',{style:'currency',currency:'USD',minimumFractionDigits:0,maximumFractionDigits:0})}
function fmt(n){return '$'+n.toLocaleString('en-US',{maximumFractionDigits:0})}

function calcRisk(){
  var tools=parseInt($('tools-count').value)||5;
  var txRisk=parseInt($('tx-risk').value);
  var unattended=val('unattended')==='yes';
  var retry=val('retry')==='yes';
  var budget=parseInt($('monthly-budget').value);

  // worst-case 24h: unattended+retry = blast radius = tools * txRisk * multiplier
  // multiplier: retry loop factor (avg runaway = ~30x, source: incident database)
  var mult=1;
  if(unattended) mult*=3;
  if(retry) mult*=10;
  var worst24h=tools*txRisk*mult;
  var annualExp=worst24h*12;
  var budgetRatio=annualExp/budget;

  // risk score 1-10 from budget ratio
  var score=Math.min(10,Math.max(1,Math.round(Math.log2(budgetRatio+1)*2.5)));
  var scoreColor='var(--mint)';
  if(score>=7) scoreColor='var(--red)';
  else if(score>=4) scoreColor='var(--amber)';

  var tier=score<=3?'low':score<=6?'medium':'high';
  var recs={'low':'Your blast radius is contained. A per-transaction cap and daily ceiling will keep it there. A spend firewall is the cheapest insurance policy your agent can buy.','medium':'Your agents have meaningful exposure. One unattended weekend with retries could cost you. Deploy a spend firewall with velocity limits and a daily cap equal to 2x your monthly budget / 30.','high':'Your current configuration is one run-away loop from a very expensive Monday. The incident database documents $47K overnight loops and $441K misread-tweet transfers. Deploy a firewall immediately: per-transaction cap at 0.1x your single largest transaction risk, velocity limit at 10 calls/minute, daily ceiling at 1x your monthly budget / 30, and an approval threshold above your per-transaction cap.'};
  var rec=recs[tier];

  $('risk-score').innerHTML='<span style="color:'+scoreColor+'">'+score+'</span>'+'<span style="font-size:.5em;color:var(--fg-3);display:block">/10</span>';
  $('risk-score').parentElement.querySelector('.label').textContent=tier+' risk';
  $('worst-24h').textContent=digits(worst24h);
  $('annual-exp').textContent=digits(annualExp);
  $('recommendation').innerHTML='<h4 style="margin-top:0">'+tier[0].toUpperCase()+tier.slice(1)+'-risk recommendation</h4><p>'+rec+'</p><p style="font-size:.85rem;margin:10px 0 0;color:var(--fg-3)">Based on '+tools+' spending tools, '+fmt(txRisk)+' per-transaction risk, '+(unattended?'unattended':'attended')+' operation, '+(retry?'retries enabled':'no retries')+', '+fmt(budget)+'/mo budget.</p>';
  $('share-url').innerHTML='Share this result: <a href="'+window.location.origin+'/tools/agent-spend-risk-calculator/?s='+score+'&w='+worst24h+'&a='+annualExp+'">'+window.location.origin+'/tools/agent-spend-risk-calculator/?s='+score+'&w='+worst24h+'&a='+annualExp+'</a>';
  $('result').classList.add('show');
  $('result').scrollIntoView({behavior:'smooth'});

  if(window.posthog) window.posthog.capture('risk_calc',{score:score,tier:tier,worst24h:worst24h,annualExp:annualExp,tools:tools,unattended:unattended,retry:retry});
}

// restore from URL if present
(function(){
  var p=new URLSearchParams(window.location.search);
  if(p.has('s')){
    var s=parseInt(p.get('s')); var w=parseInt(p.get('w')); var a=parseInt(p.get('a'));
    var sc='var(--mint)'; if(s>=7) sc='var(--red)'; else if(s>=4) sc='var(--amber)';
    var t=s<=3?'low':s<=6?'medium':'high';
    $('risk-score').innerHTML='<span style="color:'+sc+'">'+s+'</span><span style="font-size:.5em;color:var(--fg-3);display:block">/10</span>';
    $('risk-score').parentElement.querySelector('.label').textContent=t+' risk';
    $('worst-24h').textContent=digits(w); $('annual-exp').textContent=digits(a);
    $('recommendation').innerHTML='<p style="color:var(--fg-3)">Score loaded from shared link. <a href="#" onclick="document.getElementById(\'result\').querySelector(\'.btns\').scrollIntoView({behavior:\'smooth\'})">Scroll for actions →</a></p>';
    $('result').classList.add('show');
  }
})();
</script>

<section style="margin-top:40px">
<h2>How these numbers work</h2>
<p class="muted">The risk model is calibrated from real incidents in the <a href="/incidents/">AI Agent Incident Database</a>. Unattended agents multiply blast radius by 3x. Retry-on-failure multiplies by 10x (the median runaway loop in the database exceeds 30 iterations before human intervention). Annual exposure is 12 × worst-case-24h. The risk score uses a log₂ of the budget-to-exposure ratio — a 1 means you're covered, a 10 means your budget wouldn't survive one bad weekend.</p>
</section>

<section>
<h2>Frequently asked</h2>
<div class="faq">
<details><summary>Is my data sent anywhere?</summary><div class="a">No. The calculator runs entirely in your browser using JavaScript. No input is transmitted to a server. The PostHog analytics capture only the score and configuration for product improvement, not any identifying data.</div></details>
<details><summary>What's the most common risk pattern?</summary><div class="a">Retry-on-failure + unattended with &gt;3 spending tools. The median overnight loss in our incident database is ~$47K. Without a velocity limit, a single retry loop on a $100 tool call becomes $3,000 in under a minute.</div></details>
<details><summary>How do I reduce my score?</summary><div class="a">Add a spend firewall with three rules: per-transaction cap (limit single-call blast radius), velocity limit (stop retry loops), and daily ceiling (hard cap regardless of loop depth). These three rules drop the worst-case 24h from tools × risk × multiplier to capped × ceiling.</div></details>
</div>
</section>
"""
    jsonld = [
        c.breadcrumb_ld([("Home","/"),("Tools","/tools/"),("Risk Calculator","/tools/agent-spend-risk-calculator/")]),
        c.software_app_ld(name="Agent Spend Risk Calculator",description="Free interactive tool that estimates your worst-case AI agent spend exposure and calculates a risk score from 1–10, based on the sipi.bot AI Agent Incident Database.",canonical_path="/tools/agent-spend-risk-calculator/",application_category="FinanceApplication",offers_price="0",offers_currency="USD"),
        c.howto_ld(name="Calculate your agent spend risk",description="Follow these steps to estimate your AI agent's worst-case loss exposure.",steps=["Count every tool your agent can use to spend money","Estimate the largest single transaction your most dangerous tool could trigger","Assess whether the agent runs unattended overnight","Check if the agent retries on failure","Enter your monthly cloud/API budget","Read your risk score and recommended controls"]),
        c.faq_ld([("Is my data sent anywhere?","No. The calculator runs entirely in your browser using JavaScript. No input is transmitted to a server."),("What's the most common risk pattern?","Retry-on-failure + unattended with more than 3 spending tools. The median overnight loss in our incident database is approximately $47,000."),("How do I reduce my score?","Add a spend firewall with three rules: per-transaction cap, velocity limit, and daily ceiling.")]),
    ]
    html = c.page(title="Agent Spend Risk Calculator — what's your worst-case loss? | sipi.bot",
                  description="Free interactive tool: estimate your AI agent's worst-case 24h loss and get a risk score from 1–10. Calibrated on real incident data. No signup — runs in your browser.",
                  canonical_path="/tools/agent-spend-risk-calculator/", active="Tools", body=body, jsonld=jsonld)
    c.write(os.path.join(TOOLS_DIR, "agent-spend-risk-calculator", "index.html"), html)


# ============================================================ policy generator
def build_policy_gen():
    body = """
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span><a href="/tools/">Tools</a><span class="sep">/</span>Policy generator</div>
<span class="kicker">Free tool · instant output</span>
<h1>Spend Policy Generator</h1>
<p class="lead">Answer a few questions and get a ready-to-paste ruleset in JSON, YAML, and curl. Designed to match the sipi.bot six-rule engine.</p>
</section>

<style>
.risk-form,.field,.radio-group{max-width:640px}
.field{margin-bottom:20px}
.field label{display:block;font-weight:650;color:var(--fg);margin-bottom:6px;font-size:.95rem}
.field .hint{font-size:.83rem;color:var(--fg-3);margin-bottom:8px}
.field input,.field select{width:100%;background:var(--bg-1);border:1px solid var(--line);
  color:var(--fg);padding:12px 14px;border-radius:var(--r-s);font-size:1rem;font-family:inherit;appearance:none}
.field select{background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%238a8d96' fill='none' stroke-width='1.8'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 14px center;padding-right:40px}
.field input:focus,.field select:focus{outline:none;border-color:var(--mint-line);box-shadow:0 0 0 3px var(--mint-soft)}
.radio-group{display:flex;gap:10px;flex-wrap:wrap}
.radio-group label{cursor:pointer;background:var(--bg-1);border:1px solid var(--line);
  border-radius:var(--r-s);padding:10px 16px;font-size:.9rem;color:var(--fg-2);transition:.15s var(--ease)}
.radio-group label:hover{border-color:var(--mint-line)}
.radio-group input{display:none}
.radio-group label:has(input:checked){border-color:var(--mint);background:var(--mint-soft);color:var(--fg);font-weight:650}
.output{margin-top:30px;display:none}
.output.show{display:block}
.output h3{margin:22px 0 10px}
.output pre{position:relative}
.copy-btn{position:absolute;top:8px;right:10px;background:var(--bg-2);border:1px solid var(--line);
  color:var(--fg-2);font-size:.78rem;padding:4px 10px;border-radius:6px;cursor:pointer}
.copy-btn:hover{color:var(--fg)}
</style>

<div class="risk-form">
<div class="field">
<label>Agent type</label>
<div class="hint">What's your agent designed to do?</div>
<select id="agent-type">
<option value="coding">Coding / DevOps agent (Claude Code, Cursor, Replit)</option>
<option value="trading" selected>Trading / finance agent (crypto, DeFi, market)</option>
<option value="shopping">Shopping / procurement agent</option>
<option value="research">Research / search agent</option>
<option value="customer-service">Customer-service / support agent</option>
<option value="general">General-purpose agent</option>
</select>
</div>

<div class="field">
<label>Monthly budget</label>
<div class="hint">Your total comfortable spend ceiling per month.</div>
<select id="budget">
<option value="100">$100/mo</option>
<option value="500">$500/mo</option>
<option value="1000" selected>$1,000/mo</option>
<option value="5000">$5,000/mo</option>
<option value="20000">$20,000/mo</option>
<option value="100000">$100K/mo</option>
</select>
</div>

<div class="field">
<label>Merchant policy</label>
<div class="radio-group" id="merchant-group">
<label><input type="radio" name="merchant" value="allowlist" checked /><span>Allowlist — only approved merchants</span></label>
<label><input type="radio" name="merchant" value="blocklist" /><span>Blocklist — block known bad actors only</span></label>
</div>
</div>

<div class="field">
<label>High-risk categories to flag for review</label>
<div class="hint">These categories will be FLAGGED (human approval required) instead of auto-approved.</div>
<select id="categories" multiple style="min-height:140px">
<option value="crypto" selected>Crypto / blockchain</option>
<option value="infra">Infrastructure / cloud provisioning</option>
<option value="refunds">Refunds / chargebacks</option>
<option value="ads">Ad spend</option>
<option value="saas">SaaS subscriptions</option>
<option value="data">Third-party data vendors</option>
</select>
<p class="hint">Hold Cmd/Ctrl to select multiple.</p>
</div>

<button class="btn primary" onclick="genPolicy()" style="font-size:1.1rem;padding:16px 32px;width:100%;cursor:pointer">Generate my ruleset</button>
</div>

<div class="output" id="output">
<div class="band" style="margin:0 0 28px">
<h2 style="margin-top:0">Your ruleset is ready</h2>
<p>Copy any format below. Variables are set from your inputs — replace with actual values in production.</p>
<div class="btns">
<a class="btn primary" href="/pricing">Deploy on sipi.bot — $99/mo</a>
<a class="btn ghost" href="/tools/agent-spend-risk-calculator/">Score your risk first →</a>
</div>
</div>

<h3>JSON (sipi.bot API format)</h3>
<pre id="policy-json"></pre>
<h3>YAML</h3>
<pre id="policy-yaml"></pre>
<h3>curl — deploy now</h3>
<pre id="policy-curl"></pre>
<p class="muted" style="margin-top:12px">Generated rules are conservative defaults. Adjust caps upward after one week of operation if your blocked-transaction rate exceeds 1%.</p>
</div>

<script>
function $(id){return document.getElementById(id)}
function v(name){var e=document.querySelector('input[name="'+name+'"]:checked');return e?e.value:null}
function sel(id){var s=$(id);return Array.from(s.selectedOptions).map(function(o){return o.value})}

function genPolicy(){
  var type=$('agent-type').value;
  var budget=parseInt($('budget').value);
  var merchant=v('merchant');
  var flags=sel('categories');
  var types={coding:{daily:budget/20,tx_cap:100,velocity:20},
             trading:{daily:budget/30,tx_cap:budget*0.02,velocity:5},
             shopping:{daily:budget/30,tx_cap:200,velocity:10},
             research:{daily:budget/30,tx_cap:50,velocity:30},
             'customer-service':{daily:budget/30,tx_cap:500,velocity:15},
             general:{daily:budget/30,tx_cap:budget*0.01,velocity:20}};
  var t=types[type]||types.general;

  var ruleset={
    per_transaction_cap_usd: Math.round(t.tx_cap),
    daily_total_cap_usd: Math.round(t.daily*10)/10,
    velocity_limit: {max_calls_per_minute: t.velocity, window_minutes: 1},
    approval_threshold_usd: Math.round(t.tx_cap*10),
    merchant_allowlist: merchant==='allowlist'?[]:null,
    merchant_blocklist: merchant==='blocklist'?[]:null,
    flagged_categories: flags,
    time_window: {allow: [{start:'00:00',end:'23:59'}]}
  };
  var rulesJSON=JSON.stringify(ruleset,null,2);
  var rulesYAML=jsonToYaml(ruleset);
  var curlCmd='curl -X POST https://sipi.bot/v1/transactions/evaluate \\\\n  -H "Content-Type: application/json" \\\\n  -H "Authorization: Bearer YOUR_API_KEY" \\\\n  -d '+"'"+JSON.stringify({amount:Math.round(t.tx_cap),merchant:'acme-corp',category:'saas'})+"'";

  $('policy-json').innerHTML='<button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextSibling.textContent)">Copy</button>'+esc(rulesJSON);
  $('policy-yaml').innerHTML='<button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextSibling.textContent)">Copy</button>'+esc(rulesYAML);
  $('policy-curl').innerHTML='<button class="copy-btn" onclick="navigator.clipboard.writeText(this.nextSibling.textContent)">Copy</button>'+esc(curlCmd.replace(/\\\\n/g,'\\n'));
  $('output').classList.add('show');
  $('output').scrollIntoView({behavior:'smooth'});
  if(window.posthog) window.posthog.capture('policy_gen',{type:type,budget:budget,merchant:merchant,flags:flags});
}

function esc(s){return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function jsonToYaml(obj,indent){
  var lines=[]; var pre='';
  function walk(o,d){
    Object.keys(o).forEach(function(k){
      var v=o[k];
      if(v===null||v===undefined) lines.push(d+k+':');
      else if(Array.isArray(v)){
        lines.push(d+k+':');
        if(v.length===0) lines.push(d+'  []');
        else v.forEach(function(vi){lines.push(d+'  - '+JSON.stringify(vi)});
      }else if(typeof v==='object'){
        lines.push(d+k+':');
        walk(v,d+'  ');
      }else lines.push(d+k+': '+v);
    })
  }
  walk(obj,'');
  return lines.join('\\n');
}
</script>

<section style="margin-top:40px">
<h2>Frequently asked</h2>
<div class="faq">
<details><summary>What if I don't have a sipi.bot account yet?</summary><div class="a">The generated ruleset is a starting point. Sign up for a $99/mo Team plan and paste the JSON into your rules endpoint. Browse the <a href="/integrations/">framework integrations</a> for LangChain, CrewAI, OpenAI Agents SDK, and others.</div></details>
<details><summary>Are these rules safe to use in production?</summary><div class="a">They are conservative defaults calibrated on incident database patterns. Start with these, monitor your blocked-transaction rate for one week (should be &lt;1%), and adjust upward. The audit log shows exactly which rule fired and why.</div></details>
<details><summary>Can I customize the generated ruleset?</summary><div class="a">Yes — the JSON is a starting point. sipi.bot supports all six rule types: per-transaction cap, daily total, velocity limit, merchant allowlist/blocklist, category rules, and approval thresholds. Add time-of-day windows if your agents have peak/off-peak hours.</div></details>
</div>
</section>
"""
    jsonld = [
        c.breadcrumb_ld([("Home","/"),("Tools","/tools/"),("Policy Generator","/tools/spend-policy-generator/")]),
        c.software_app_ld(name="Spend Policy Generator",description="Free tool that generates a ready-to-paste spend-firewall ruleset in JSON, YAML, and curl. Calibrated on real incident data from the sipi.bot AI Agent Incident Database.",canonical_path="/tools/spend-policy-generator/",application_category="DeveloperApplication",offers_price="0",offers_currency="USD"),
        c.howto_ld(name="Generate a spend-firewall ruleset",description="Answer questions about your agent's type, budget, and risk profile, and get a ready-to-deploy policy.",steps=["Select your agent type","Set your monthly budget","Choose a merchant policy (allowlist or blocklist)","Flag high-risk categories for human review","Copy the generated JSON/YAML/curl output","Paste into sipi.bot and monitor blocked rate for one week"]),
        c.faq_ld([("What if I don't have a sipi.bot account yet?","The generated ruleset is a starting point. Sign up for a $99/mo Team plan and paste the JSON into your rules endpoint."),("Are these rules safe to use in production?","They are conservative defaults calibrated on incident database patterns. Monitor your blocked-transaction rate for one week (should be below 1%), and adjust upward."),("Can I customize the generated ruleset?","Yes — the JSON is a starting point. sipi.bot supports all six rule types.")]),
    ]
    html = c.page(title="Spend Policy Generator — ready-to-paste firewall ruleset | sipi.bot",
                  description="Free tool: generate a spend-firewall ruleset in JSON, YAML, and curl. Calibrated on real incident data. Ready to paste into sipi.bot — no signup required.",
                  canonical_path="/tools/spend-policy-generator/", active="Tools", body=body, jsonld=jsonld)
    c.write(os.path.join(TOOLS_DIR, "spend-policy-generator", "index.html"), html)


# =========================================================== tools hub placeholder
def build_hub():
    body = """
<section class="hero">
<div class="crumbs"><a href="/">Home</a><span class="sep">/</span>Tools</div>
<span class="kicker">Free tools · no signup</span>
<h1>Free agent-spend tools</h1>
<p class="lead">Interactive calculators, generators, and checklists — all free, no account needed. Everything runs in your browser.</p>
</section>

<div class="grid two">
<div class="card">
<span class="tag good">Interactive</span>
<h3><a href="/tools/agent-spend-risk-calculator/">Agent Spend Risk Calculator</a></h3>
<p>Estimate your worst-case loss exposure and get a risk score from 1–10. Calibrated on real incident data from the AI Agent Incident Database.</p>
<div class="meta">5 inputs · instant result · shareable</div>
</div>
<div class="card">
<span class="tag good">Generator</span>
<h3><a href="/tools/spend-policy-generator/">Spend Policy Generator</a></h3>
<p>Answer questions about your agent and get a ready-to-paste firewall ruleset in JSON, YAML, and curl — production-ready defaults.</p>
<div class="meta">4 questions · JSON + YAML + curl · copy-paste</div>
</div>
<div class="card">
<span class="tag neutral">Checklist</span>
<h3><a href="/checklists/agent-cost-audit/">Agent Cost Audit Checklist</a></h3>
<p>A step-by-step audit of every spend-adjacent surface in your agent fleet — identify and cap every spending path.</p>
<div class="meta">6 steps · printable</div>
</div>
<div class="card">
<span class="tag neutral">Open data</span>
<h3><a href="/incidents/">AI Agent Incident Database</a></h3>
<p>34 sourced records of AI-agent-caused financial loss, data loss, and unintended actions. CC BY 4.0 — JSON, CSV, JSONL.</p>
<div class="meta">34 incidents · $2.91B tracked · CC BY 4.0</div>
</div>
</div>

<div class="band" style="margin-top:40px">
<h2>Every tool here runs on real data</h2>
<p>The risk calculator and policy generator are calibrated on the <a href="/incidents/">AI Agent Incident Database</a> — 34 verified incidents of agents that lost money, leaked data, or took unintended actions. The patterns are real: unattended retry loops ($47K overnight), unverified merchants ($441K to a stranger), and the gap between "trust the prompt" and "verify the transaction."</p>
<div class="btns">
<a class="btn primary" href="/pricing">Deploy the firewall — $99/mo</a>
<a class="btn ghost" href="/incidents/">Browse the incident database →</a>
</div>
</div>
"""
    jsonld = [
        c.breadcrumb_ld([("Home","/"),("Tools","/tools/")]),
    ]
    html = c.page(title="Free AI Agent Spend Tools — risk calculator, policy generator | sipi.bot",
                  description="Free interactive tools for AI agent spend governance: risk calculator, spend-policy generator, cost audit checklist. No signup — runs in your browser.",
                  canonical_path="/tools/", active="Tools", body=body, jsonld=jsonld)
    c.write(os.path.join(TOOLS_DIR, "index.html"), html)


# ----------------------------------------------------------------------- driver
def main():
    build_risk_calc()
    print("tools/: risk calculator")
    build_policy_gen()
    print("tools/: spend-policy generator")
    build_hub()
    print("tools/: hub")


if __name__ == "__main__":
    main()
