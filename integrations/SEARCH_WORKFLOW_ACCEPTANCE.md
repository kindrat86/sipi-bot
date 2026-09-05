# Fixed-price research-agent search boundary

Local acceptance implementation, not a deployed customer workflow or buyer commitment.

## The single workflow

A research agent searches once per stable request ID. Its paid search-tool callable is invoked only after a durable budget reservation. This uses the existing SipiBot policy engine plus SQLite integer-cent accounting. The agent does not supply the price, budget or ledger. Owner configuration does.

```python
from integrations.search_workflow import SearchWorkflow

# Synthetic illustrative amounts, NOT a quote or current provider price.
workflow = SearchWorkflow("/owner-controlled/path/search-budget.sqlite",
                          budget_cents=100, unit_cents=10)
results = workflow.search("job-001-search-001", "research query", paid_search_tool)
```

The callable must represent exactly ONE bounded-price provider invocation, with retries disabled or their full worst-case cost included in unit_cents. The reservation is conservative: it is never automatically refunded, including timeout, exception or process death after reservation. This sacrifices utilization to prevent uncertain charges being retried for free. Duplicate IDs are denied, not replayed. The budget is lifetime-per-ledger, not daily, despite using the engine's daily_total rule with lifetime context. No automatic resets. Monetary scope is one configured currency, expressed in cents.

All processes must share this owner-controlled SQLite file on local disk. BEGIN IMMEDIATE serializes reservations; integer arithmetic is the authoritative budget ceiling. An inaccessible or locked ledger raises before dispatch. Raising budget or changing unit cost against the same file is denied at construction. Creating another ledger is NOT permitted as a budget-reset technique.

## Acceptance command

From repository root, using Python 3.11 or newer:

    python3.11 -m unittest discover -s tests -p test_search_workflow.py -v
    python3.11 -m unittest discover -s tests -p test_sipi_guard_fail_closed.py -v
    python3.11 -m unittest discover -s tests -q

Local results: 5 workflow tests plus 2 guard tests pass; full suite 88 passes.

Positive: approved search dispatches and returns the tool result.
Negative: exhausted budget after restart; simultaneous attempts (one dispatch, seven blocked); duplicate request; timeout with uncertain billing retains reservation; malformed owner prices; mismatched ledger policy; storage unavailable. Guard regression verifies missing, null, lowercase and REVIEW decisions cannot reach dispatch. Explicit APPROVED is the only allow decision. Test provider functions are labeled synthetic and make no network requests.

## Buyer acceptance gates

1. Buyer identifies one existing search callable and authorizes local integration.
2. Owner verifies the provider's maximum per-invocation bill, currency, retry behavior and billing unit. Variable/unbounded billing is out of scope until safely bounded.
3. Owner routes every call in this workflow through this boundary; caller cannot change the ledger/policy. Do not expose the unguarded callable to the agent's tool registry.
4. Buyer runs the positive and negative tests with a synthetic provider, then separately authorizes any billable provider check.
5. Agree fee, exact workflow, acceptance, exclusions and rollback in writing before payment or external promises. No invented fee is included here.

Limitations: no account-wide/provider billing cap, no protection against stolen keys, direct calls or other ledgers, no sandbox against malicious local code, no guarantee provider charges stay below an unverified price estimate. A callback reference is a trust boundary, not a credential-isolation boundary. No support for distributed/network filesystem coordination. A new-day reset or refunds require explicit owner reconciliation, not automatic behavior.

## Related minimal correction

integrations/sipi_guard.py previously returned any decision except BLOCKED or FLAGGED. Four reproduced cases reached the paid-call line. It now requires explicit APPROVED. No API or public-page changes, no dependency installs and no deployment.
