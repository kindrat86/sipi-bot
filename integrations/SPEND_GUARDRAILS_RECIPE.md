# Spend guardrails for your agents (LangChain & CrewAI)

> **The problem:** the moment your agent can call a tool that spends money —
> buying compute, topping up API credits, placing an ad — it is one retry loop
> away from a runaway bill. Prompts are not a spending policy.
>
> **The fix:** put one call in front of every spend. [sipi.bot](https://sipi.bot)
> returns `APPROVED`, `BLOCKED`, or `FLAGGED` (needs human approval) against your
> rules — per-transaction caps, daily totals, velocity (runaway-loop protection),
> merchant allow/block, category limits, time windows, approval thresholds.

This recipe is copy-paste and dependency-light. The client below is **stdlib
only** (no SDK to install). Every snippet here was tested live against
`https://sipi.bot`.

---

## 0. The 15-second client (`sipi_guard.py`)

Drop this file next to your agent. Zero dependencies.

```python
# sipi_guard.py
import json, os, urllib.request

SIPI_URL = os.environ.get("SIPI_URL", "https://sipi.bot")
SIPI_API_KEY = os.environ.get("SIPI_API_KEY")  # optional, for hosted tiers

class SpendBlocked(Exception):
    def __init__(self, reason, detail): super().__init__(reason); self.reason, self.detail = reason, detail
class SpendNeedsApproval(Exception):
    def __init__(self, reason, detail): super().__init__(reason); self.reason, self.detail = reason, detail

def evaluate(amount, merchant="", category="", description="", currency="USD"):
    body = json.dumps({"amount": amount, "merchant": merchant, "category": category,
                       "description": description, "currency": currency}).encode()
    req = urllib.request.Request(f"{SIPI_URL}/v1/transactions/evaluate", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if SIPI_API_KEY: req.add_header("Authorization", f"Bearer {SIPI_API_KEY}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

def guard(amount, merchant="", category="", description="", currency="USD"):
    d = evaluate(amount, merchant, category, description, currency)
    if d.get("decision") == "BLOCKED":   raise SpendBlocked(d.get("reason","blocked"), d)
    if d.get("decision") == "FLAGGED":   raise SpendNeedsApproval(d.get("reason","needs approval"), d)
    return d
```

Verify it works right now (no signup needed — the free tier is open):

```bash
python -c "from sipi_guard import evaluate; print(evaluate(6200,'unknown-gpu.ru','compute')['decision'])"
# -> BLOCKED
```

---

## 1. LangChain / LangGraph

Wrap any money-spending tool so the agent physically cannot spend past your
rules. The guard runs *inside* the tool, before the real action.

```python
from langchain_core.tools import tool
from sipi_guard import guard, SpendBlocked, SpendNeedsApproval

def _really_buy(amount: float, merchant: str) -> str:
    # ... your actual purchase call (Stripe, cloud API, ad platform) ...
    return f"Purchased ${amount:.2f} from {merchant}."

@tool
def buy(amount: float, merchant: str, category: str = "") -> str:
    """Spend money with a supplier. Amount in USD. Always call this to purchase;
    a spend firewall decides if it is allowed."""
    try:
        guard(amount=amount, merchant=merchant, category=category)
    except SpendBlocked as e:
        return f"BLOCKED by spend policy: {e.reason}. Do not retry; tell the user."
    except SpendNeedsApproval as e:
        return f"NEEDS HUMAN APPROVAL: {e.reason}. Escalated; not purchased yet."
    return _really_buy(amount, merchant)
```

Give `buy` to your agent as usual (`create_react_agent(llm, tools=[buy])`). The
model sees the BLOCKED/APPROVAL message in the tool result and reacts correctly —
it stops retrying and explains to the user, instead of hammering the endpoint.

**Tip:** return strings (not raised exceptions) from the tool so the agent can
*reason about* the block. Raising inside a tool usually aborts the run; a
returned "BLOCKED: reason" lets the agent recover gracefully.

---

## 2. CrewAI

Expose the firewall as a `BaseTool` your crew must consult before spending, or
wrap the spending tool directly.

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sipi_guard import evaluate

class SpendInput(BaseModel):
    amount: float = Field(..., description="Amount in USD")
    merchant: str = Field("", description="Who is being paid")
    category: str = Field("", description="compute | api | ads | goods | ...")

class SpendGuardTool(BaseTool):
    name: str = "spend_guard"
    description: str = ("Check whether a purchase is allowed BEFORE spending. "
                        "Returns APPROVED, BLOCKED, or FLAGGED (needs human approval).")
    args_schema: type[BaseModel] = SpendInput

    def _run(self, amount: float, merchant: str = "", category: str = "") -> str:
        d = evaluate(amount, merchant, category)
        if d["decision"] == "BLOCKED":
            return f"BLOCKED: {d['reason']}. Do not proceed."
        if d["decision"] == "FLAGGED":
            return f"FLAGGED for human approval: {d['reason']}. Wait for a human."
        return f"APPROVED: safe to spend ${amount:.2f} at {merchant}."
```

Add `SpendGuardTool()` to the agent that holds the purse, and put a line in its
backstory: *"You must call spend_guard before any purchase and obey its
decision."* For hard enforcement (not just instruction-following), wrap the
actual purchase tool the same way as the LangChain example — call `guard()`
inside `_run` and refuse on exception.

---

## 3. Set your rules (once)

Defaults ship sane (block >$500/tx, >$2000/day, >10 tx/hour; flag ≥$200). Tune
them from the dashboard at https://sipi.bot/dashboard, or via the API:

```bash
curl -X POST https://sipi.bot/api/rules -H "Content-Type: application/json" \
  -d '{"rule_type":"merchant_allow","params":{"patterns":["openai.com","aws*","anthropic.com"]},
       "action":"BLOCKED","label":"only pay known vendors"}'
```

Rule types: `per_transaction`, `daily_total`, `velocity`, `merchant_block`,
`merchant_allow`, `category_limit`, `time_window`, `approval_threshold`.

---

## 4. Why a call, not a hardcoded `if amount > X`

A per-transaction check misses the cases that actually cost money:
- **runaway loops** — 40 small retries in a minute (velocity rule catches this)
- **cumulative daily spend** across many calls and multiple agents
- **the "flag for human" path** — some spends should pause, not fail
- an **audit trail** of *why* each spend was allowed (what regulators/investors ask for)

Once you want those, you've rebuilt sipi.bot. So don't — it's one call, open
source, free to self-host.

- Live + code: https://sipi.bot
- Eval report (53/53 scenarios): https://sipi.bot/eval
- Source (MIT): https://github.com/kindrat86/sipi-bot
- `pip install sipi-bot` · MCP: `python -m spendfirewall.mcp_server`
