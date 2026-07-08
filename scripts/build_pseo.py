#!/usr/bin/env python3
"""build_pseo.py — generate genuinely-unique pSEO pages for sipi.bot.

Four framework integration pages under public/for/<framework>/index.html plus a
hub at public/for/index.html that links to all four (satisfies P5).

Each page reuses the REAL, verified integration recipe content (distinct code,
distinct copy) so it passes the unique-value gate (P2 jaccard >= 0.4) — these are
not doorway pages, they are the actual integration docs rendered as landing forks.

Run: python3 build_pseo.py   (writes into ../public/for/)
"""
import html
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PUB = os.path.normpath(os.path.join(HERE, "..", "public", "for"))

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#e8e8ea;font:16px/1.65 -apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif;-webkit-font-smoothing:antialiased}
a{color:#00d4aa;text-decoration:none}a:hover{text-decoration:underline}
.wrap{max-width:820px;margin:0 auto;padding:0 22px}
nav{border-bottom:1px solid #23242a;position:sticky;top:0;background:rgba(10,10,10,.9);backdrop-filter:blur(10px);z-index:10}
nav .wrap{display:flex;justify-content:space-between;align-items:center;height:58px}
.brand{font-weight:700;font-size:18px}.brand .d{color:#00d4aa}
.nav-links a{color:#8a8d96;margin-left:20px;font-size:14px}
main{padding:52px 0}
h1{font-size:clamp(28px,5vw,40px);line-height:1.1;letter-spacing:-.02em;margin-bottom:16px}
.lead{font-size:19px;color:#8a8d96;margin-bottom:28px}
h2{font-size:24px;margin:36px 0 12px;letter-spacing:-.01em}
p{color:#c9ccd3;margin-bottom:14px}
.tag{display:inline-block;font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:#00d4aa;border:1px solid rgba(0,212,170,.3);border-radius:100px;padding:5px 13px;margin-bottom:20px}
pre{background:#000;border:1px solid #23242a;border-radius:12px;padding:18px;overflow-x:auto;font-size:13.5px;line-height:1.5;color:#cfd2d8;margin:16px 0;font-family:'SF Mono',ui-monospace,Menlo,monospace}
code{font-family:'SF Mono',ui-monospace,Menlo,monospace}
.cta{display:inline-block;background:#00d4aa;color:#04120e;font-weight:700;padding:13px 24px;border-radius:10px;margin:8px 8px 8px 0}
.card{background:#121316;border:1px solid #23242a;border-radius:14px;padding:20px;margin:16px 0}
.hub-links{list-style:none;display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:22px 0}
.hub-links li{background:#121316;border:1px solid #23242a;border-radius:12px;padding:18px}
.hub-links a{font-weight:700;font-size:17px}
.hub-links p{font-size:14px;color:#8a8d96;margin:6px 0 0}
footer{border-top:1px solid #23242a;padding:30px 0;color:#8a8d96;font-size:14px}
@media(max-width:640px){.hub-links{grid-template-columns:1fr}}
"""

NAV = ('<nav><div class="wrap"><div class="brand">sipi<span class="d">.bot</span></div>'
       '<div class="nav-links"><a href="/for/">Integrations</a><a href="/pricing">Pricing</a>'
       '<a href="/dashboard">Dashboard</a></div></div></nav>')


def page(title, desc, canonical, body, faq):
    faq_ld = {
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]
    }
    import json
    return f"""<!doctype html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://sipi.bot{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="article"><meta name="theme-color" content="#00d4aa">
<script type="application/ld+json">{json.dumps(faq_ld)}</script>
<style>{CSS}</style></head><body>
{NAV}
<main><div class="wrap">{body}
<h2>Frequently asked</h2>
{''.join(f'<div class="card"><h3 style="color:#e8e8ea;font-size:17px;margin-bottom:8px">{html.escape(q)}</h3><p>{html.escape(a)}</p></div>' for q,a in faq)}
<p style="margin-top:30px"><a class="cta" href="/pricing">Get started — $99/mo</a>
<a class="cta" href="https://github.com/kindrat86/sipi-bot" style="background:transparent;border:1px solid #23242a;color:#e8e8ea">View source</a></p>
</div></main>
<footer><div class="wrap">sipi<span style="color:#00d4aa">.bot</span> — the spend firewall for autonomous AI agents ·
<a href="/for/">All integrations</a> · <a href="/">Home</a></div></footer>
</body></html>"""


# --- Four genuinely distinct pages (real recipe content, distinct code) ---

PAGES = {
    "langchain": {
        "title": "Spend guardrails for LangChain agents — sipi.bot",
        "desc": "Add a spend firewall to your LangChain agent in 5 lines. Approve, block, or flag every tool-driven purchase before a dollar moves.",
        "body": """<span class="tag">LangChain integration</span>
<h1>Stop your LangChain agent from overspending</h1>
<p class="lead">A LangChain agent with a money-spending tool is one retry loop away from a runaway bill. Wrap that tool with sipi.bot and every purchase is checked against your rules before it fires.</p>
<p>The pattern: call <code>guard()</code> inside your <code>@tool</code>, before the real spend. It raises on a blocked or flagged decision, so the agent physically cannot spend past your policy — and it gets a readable message back so it stops retrying instead of hammering the endpoint.</p>
<pre>from langchain_core.tools import tool
from sipi_guard import guard, SpendBlocked, SpendNeedsApproval

@tool
def buy(amount: float, merchant: str, category: str = "") -> str:
    "Spend money with a supplier. A spend firewall decides if it is allowed."
    try:
        guard(amount=amount, merchant=merchant, category=category)
    except SpendBlocked as e:
        return f"BLOCKED by spend policy: {e.reason}. Do not retry; tell the user."
    except SpendNeedsApproval as e:
        return f"NEEDS HUMAN APPROVAL: {e.reason}. Escalated; not purchased yet."
    return really_buy(amount, merchant)</pre>
<p>Give <code>buy</code> to <code>create_react_agent(llm, tools=[buy])</code> as usual. When sipi.bot blocks a spend, the model reads the reason in the tool result and explains it to the user rather than looping. LangGraph works identically — the guard lives inside the node.</p>
<h2>Why not a hardcoded check inside the tool?</h2>
<p>A single <code>if amount &gt; 500</code> misses the runaway loop (40 small retries), the cumulative daily cap across many tool calls, the flag-for-human path, and the audit trail of why each spend was allowed. sipi.bot centralizes all of that in one call.</p>""",
        "faq": [
            ("Does sipi.bot work with LangGraph?", "Yes. The guard call lives inside the tool or node function, so LangGraph agents get the same protection as LangChain ReAct agents — no extra wiring."),
            ("Do I need the LangChain SDK to call sipi.bot?", "No. sipi_guard.py is a zero-dependency stdlib client. LangChain is only used for the @tool decorator in this example; the guard itself is a plain HTTP call."),
            ("What happens when a spend is blocked mid-run?", "The tool returns a readable 'BLOCKED: reason' string. The LangChain agent reads it as the tool result and stops retrying, explaining the block to the user instead of looping."),
        ],
    },
    "crewai": {
        "title": "Spend guardrails for CrewAI — sipi.bot",
        "desc": "Give your CrewAI crew a spend firewall as a BaseTool. Every agent purchase is approved, blocked, or flagged against your rules.",
        "body": """<span class="tag">CrewAI integration</span>
<h1>A spend firewall for your CrewAI crew</h1>
<p class="lead">When one agent in your crew holds the purse, a bad merchant or a runaway task can drain it. sipi.bot becomes a BaseTool the crew must consult before spending.</p>
<p>Expose the firewall as a typed <code>BaseTool</code> with a Pydantic <code>args_schema</code>. The crew calls it before any purchase, and you put the obligation in the agent's backstory.</p>
<pre>from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sipi_guard import evaluate

class SpendInput(BaseModel):
    amount: float = Field(..., description="Amount in USD")
    merchant: str = Field("", description="Who is being paid")
    category: str = Field("", description="compute | api | ads | goods")

class SpendGuardTool(BaseTool):
    name: str = "spend_guard"
    description: str = "Check a purchase BEFORE spending. Returns APPROVED, BLOCKED, or FLAGGED."
    args_schema: type[BaseModel] = SpendInput

    def _run(self, amount: float, merchant: str = "", category: str = "") -> str:
        d = evaluate(amount, merchant, category)
        if d["decision"] == "BLOCKED":
            return f"BLOCKED: {d['reason']}. Do not proceed."
        if d["decision"] == "FLAGGED":
            return f"FLAGGED for human approval: {d['reason']}."
        return f"APPROVED: safe to spend ${amount:.2f} at {merchant}."</pre>
<p>Add <code>SpendGuardTool()</code> to the agent that holds the budget and add to its backstory: "You must call spend_guard before any purchase and obey its decision." For hard enforcement, wrap the actual purchase tool the same way.</p>
<h2>Crew-wide spend policy</h2>
<p>Because every agent hits the same firewall, your daily cap and velocity limits apply across the whole crew, not per agent. One runaway member can't blow the shared budget.</p>""",
        "faq": [
            ("How do I enforce the firewall across a whole crew?", "sipi.bot tracks daily totals and velocity globally, so a shared budget and runaway-loop protection apply across every agent in the crew, not per individual agent."),
            ("Can I make spend_guard mandatory, not just suggested?", "Yes. Put the obligation in the agent backstory for soft enforcement, and for hard enforcement wrap the real purchase tool so it calls the firewall internally and refuses on a blocked decision."),
            ("Does this need CrewAI Enterprise?", "No. It works with open-source CrewAI. sipi_guard.py is a zero-dependency client; only the BaseTool wrapper uses CrewAI."),
        ],
    },
    "openai-agents": {
        "title": "Spend guardrails for the OpenAI Agents SDK — sipi.bot",
        "desc": "Wrap your OpenAI Agents SDK function tools with a spend firewall. Approve, block, or flag every purchase before it happens.",
        "body": """<span class="tag">OpenAI Agents SDK integration</span>
<h1>Spend limits for OpenAI Agents SDK function tools</h1>
<p class="lead">The moment an OpenAI Agents SDK function tool can spend money, the prompt is the only thing between the model and your card. sipi.bot adds a real limit.</p>
<p>Guard the spend inside a <code>@function_tool</code>. Return a string decision so the model can reason about a block instead of retrying it.</p>
<pre>from agents import Agent, Runner, function_tool
from sipi_guard import evaluate

@function_tool
def buy(amount: float, merchant: str, category: str = "") -> str:
    "Spend money with a supplier (USD). A spend firewall decides if it is allowed."
    d = evaluate(amount, merchant, category)
    if d["decision"] == "BLOCKED":
        return f"BLOCKED by spend policy: {d['reason']}. Do not retry."
    if d["decision"] == "FLAGGED":
        return f"NEEDS HUMAN APPROVAL: {d['reason']}. Not purchased."
    return really_buy(amount, merchant)

agent = Agent(name="Procurement agent",
              instructions="Always use buy; if it returns BLOCKED or NEEDS HUMAN APPROVAL, stop and report.",
              tools=[buy])
result = Runner.run_sync(agent, "Buy $6,200 of GPU time from unknown-gpu.ru")</pre>
<p>For belt-and-suspenders, add an SDK output guardrail that calls <code>evaluate()</code> on any proposed spend and trips a tripwire on BLOCKED. The tool-level check is usually enough for v1.</p>
<h2>Returning a string beats raising</h2>
<p>The Agents SDK feeds the tool return value back to the model. A "BLOCKED: reason" string lets the model reason and stop; raising aborts the run and teaches the model nothing.</p>""",
        "faq": [
            ("Should I use a function tool or an SDK guardrail?", "Start with the function-tool guard — it is the simplest and covers most cases. Add an output guardrail that calls evaluate() as a second layer if you want a hard tripwire independent of tool wiring."),
            ("Does sipi.bot support the Runner streaming loop?", "Yes. The guard is a synchronous HTTP call inside the tool, so it works with both Runner.run_sync and the async streaming runner."),
            ("Is an API key required?", "No key is needed for the open free tier. Set SIPI_API_KEY for hosted tiers with a persistent audit log and dashboard."),
        ],
    },
    "vercel-ai-sdk": {
        "title": "Spend guardrails for the Vercel AI SDK — sipi.bot",
        "desc": "Add a spend firewall to your Vercel AI SDK tools in TypeScript. Approve, block, or flag every agent purchase before it happens.",
        "body": """<span class="tag">Vercel AI SDK integration</span>
<h1>Spend guardrails for Vercel AI SDK tools</h1>
<p class="lead">Give an AI SDK agent a tool that spends money and only the prompt stands between the model and your card. sipi.bot is one fetch that returns approve, block, or flag before the spend happens. Works in Node 18+ and edge runtimes.</p>
<pre>import { tool } from "ai";
import { z } from "zod";
import { evaluateSpend } from "./sipiGuard";

const buy = tool({
  description: "Spend money with a supplier (USD). A spend firewall decides if it is allowed.",
  parameters: z.object({
    amount: z.number(), merchant: z.string(), category: z.string().optional(),
  }),
  execute: async ({ amount, merchant, category }) => {
    const d = await evaluateSpend({ amount, merchant, category });
    if (d.decision === "BLOCKED")
      return { ok: false, message: `BLOCKED: ${d.reason}. Do not retry.` };
    if (d.decision === "FLAGGED")
      return { ok: false, message: `NEEDS HUMAN APPROVAL: ${d.reason}.` };
    return { ok: true, message: await reallyBuy(amount, merchant) };
  },
});</pre>
<p>Return an object, not a thrown error. The AI SDK feeds the return value back to the model as the tool result, so <code>{ ok: false, message }</code> lets the model reason about the block and stop, while throwing surfaces an error it cannot act on.</p>
<h2>Edge-ready TypeScript client</h2>
<p>The <code>sipiGuard.ts</code> client uses global <code>fetch</code>, so it runs unchanged in Node, Vercel Edge Functions, and Cloudflare Workers — no SDK, no Node-only dependencies.</p>""",
        "faq": [
            ("Does this run on Vercel Edge Functions?", "Yes. sipiGuard.ts uses global fetch with no Node-only dependencies, so it runs on Vercel Edge, Cloudflare Workers, and standard Node 18+ runtimes."),
            ("Why return an object instead of throwing?", "The Vercel AI SDK passes the tool's return value back to the model. Returning { ok: false, message } lets the model reason about the block and stop; throwing surfaces an error the model cannot gracefully handle."),
            ("Does it work with streamText and generateText?", "Yes. The guard runs inside tool.execute, which both streamText and generateText invoke during multi-step tool calls."),
        ],
    },
}


def main():
    os.makedirs(PUB, exist_ok=True)
    for slug, d in PAGES.items():
        canonical = f"/for/{slug}/"
        out_dir = os.path.join(PUB, slug)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "index.html"), "w") as f:
            f.write(page(d["title"], d["desc"], canonical, d["body"], d["faq"]))
        print("wrote", canonical)

    # Hub page linking to all four (satisfies P5)
    cards = "\n".join(
        f'<li><a href="/for/{slug}/">{d["title"].split(" — ")[0].replace("Spend guardrails for ","").replace("Stop your ","LangChain")}</a>'
        f'<p>{html.escape(d["desc"][:110])}…</p></li>'
        for slug, d in PAGES.items())
    hub_body = f"""<span class="tag">Integrations</span>
<h1>Add a spend firewall to your AI agent framework</h1>
<p class="lead">sipi.bot drops into every major agent framework with one call before a spend: approve, block, or flag against your rules. Pick your stack.</p>
<ul class="hub-links">{cards}</ul>
<p>Every integration uses the same core call — <code>evaluate(amount, merchant, category)</code> returning APPROVED, BLOCKED, or FLAGGED — over a zero-dependency client. Open-source core (MIT), free to self-host, or $99/mo hosted with a live dashboard and tamper-evident audit log.</p>"""
    hub_faq = [
        ("Which agent frameworks does sipi.bot support?", "sipi.bot works with LangChain, LangGraph, CrewAI, the OpenAI Agents SDK, and the Vercel AI SDK today, plus any runtime that can make an HTTP call or use an MCP tool."),
        ("Is there one client for all frameworks?", "Yes. Python frameworks use the zero-dependency sipi_guard.py; TypeScript frameworks use sipiGuard.ts. Both wrap the same /v1/transactions/evaluate endpoint."),
    ]
    with open(os.path.join(PUB, "index.html"), "w") as f:
        f.write(page("AI agent framework integrations — sipi.bot",
                     "Add a spend firewall to LangChain, CrewAI, OpenAI Agents SDK, or Vercel AI SDK. One call approves, blocks, or flags every agent purchase.",
                     "/for/", hub_body, hub_faq))
    print("wrote /for/ (hub)")


if __name__ == "__main__":
    main()
