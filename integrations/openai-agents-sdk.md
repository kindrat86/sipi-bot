# Spend guardrails for OpenAI Agents SDK

> Your agent can call tools. The moment one of those tools spends money — buys
> compute, tops up API credits, places an order — it's one loop away from a
> runaway bill. [sipi.bot](https://sipi.bot) is one call that returns `APPROVED`,
> `BLOCKED`, or `FLAGGED` (needs human approval) before the money moves.

Tested live against `https://sipi.bot`. Uses the zero-dependency `sipi_guard.py`
client (see the LangChain/CrewAI recipe, or copy it below).

## Guard a spending function tool

```python
from agents import Agent, Runner, function_tool
from sipi_guard import evaluate   # zero-dep stdlib client

def _really_buy(amount: float, merchant: str) -> str:
    # ... your real purchase call (Stripe, cloud API, ad platform) ...
    return f"Purchased ${amount:.2f} from {merchant}."

@function_tool
def buy(amount: float, merchant: str, category: str = "") -> str:
    """Spend money with a supplier (USD). A spend firewall decides if it's allowed."""
    d = evaluate(amount, merchant, category)
    if d["decision"] == "BLOCKED":
        return f"BLOCKED by spend policy: {d['reason']}. Do not retry; tell the user."
    if d["decision"] == "FLAGGED":
        return f"NEEDS HUMAN APPROVAL: {d['reason']}. Escalated; not purchased yet."
    return _really_buy(amount, merchant)

agent = Agent(
    name="Procurement agent",
    instructions="You buy resources for the team. Always use the buy tool; "
                 "if it returns BLOCKED or NEEDS HUMAN APPROVAL, stop and report — never retry.",
    tools=[buy],
)

result = Runner.run_sync(agent, "Buy $6,200 of GPU time from unknown-gpu.ru")
print(result.final_output)   # the agent relays the BLOCK instead of spending
```

## Why return a string instead of raising

The OpenAI Agents SDK feeds the tool's return value back to the model. Returning
`"BLOCKED: reason"` lets the model *reason about it* — it stops retrying and
explains to the user. Raising inside a tool aborts the run and the model learns
nothing. Same pattern as the LangChain recipe.

## Guardrails (belt and suspenders)

For a hard stop independent of tool wiring, add an SDK output guardrail that
calls `evaluate()` on any spend the agent proposes and trips a tripwire on
`BLOCKED`. The tool-level check above is usually enough for v1.

## Set your rules

Defaults: block >$500/tx, >$2,000/day, >10 tx/hour; flag ≥$200. Tune at
https://sipi.bot/dashboard or via `POST /api/rules`. Rule types:
`per_transaction`, `daily_total`, `velocity`, `merchant_block`, `merchant_allow`,
`category_limit`, `time_window`, `approval_threshold`.

- Live + code: https://sipi.bot · eval (53/53): https://sipi.bot/eval
- Source (MIT): https://github.com/kindrat86/sipi-bot · `pip install sipi-bot`

---

<details><summary>sipi_guard.py (copy if you don't have it)</summary>

```python
import json, os, urllib.request
SIPI_URL = os.environ.get("SIPI_URL", "https://sipi.bot")
SIPI_API_KEY = os.environ.get("SIPI_API_KEY")
def evaluate(amount, merchant="", category="", description="", currency="USD"):
    body = json.dumps({"amount": amount, "merchant": merchant, "category": category,
                       "description": description, "currency": currency}).encode()
    req = urllib.request.Request(f"{SIPI_URL}/v1/transactions/evaluate", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    if SIPI_API_KEY: req.add_header("Authorization", f"Bearer {SIPI_API_KEY}")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())
```
</details>
