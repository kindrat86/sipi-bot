"""eval_scenarios.py — 50 labeled scenarios covering every rule path.

Each scenario is a dict:
  name, txn (inputs), rules (agent-specific rules to add on top of defaults),
  prior (list of prior APPROVED txns to seed cumulative state),
  expected (Decision), category, note

The default global rules (seeded by store) are:
  per_transaction  max_amount 500   -> BLOCKED
  daily_total      max_amount 2000  -> BLOCKED
  velocity         max_count 10/hr  -> BLOCKED
  approval_thresh  amount 200       -> FLAGGED
"""

# Standard default policy replicated so the runner can seed a clean DB.
DEFAULT_RULES = [
    ("per_transaction", {"max_amount": 500}, "BLOCKED", 100, "default per-tx"),
    ("daily_total", {"max_amount": 2000}, "BLOCKED", 90, "default daily"),
    ("velocity", {"max_count": 10, "window_seconds": 3600}, "BLOCKED", 80, "default velocity"),
    ("approval_threshold", {"amount": 200}, "FLAGGED", 50, "default approval flag"),
]

SCENARIOS = [
    # --- clean_approval (under all thresholds) ---
    {"name": "tiny coffee-money api call", "txn": {"amount": 5, "merchant": "openai.com", "category": "api"},
     "expected": "APPROVED", "category": "clean_approval", "note": "well under everything"},
    {"name": "small compute spend", "txn": {"amount": 49, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "APPROVED", "category": "clean_approval"},
    {"name": "just under approval flag", "txn": {"amount": 199.99, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "APPROVED", "category": "clean_approval", "note": "199.99 < 200 flag threshold"},
    {"name": "modest ads spend", "txn": {"amount": 120, "merchant": "google.com", "category": "ads"},
     "expected": "APPROVED", "category": "clean_approval"},
    {"name": "cheap subscription", "txn": {"amount": 20, "merchant": "github.com", "category": "subscription"},
     "expected": "APPROVED", "category": "clean_approval"},
    {"name": "zero-dollar auth check", "txn": {"amount": 0, "merchant": "stripe.com", "category": "api"},
     "expected": "APPROVED", "category": "clean_approval", "note": "zero always fine"},

    # --- approval_flag (>= 200, < 500) ---
    {"name": "exactly at approval threshold", "txn": {"amount": 200, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "FLAGGED", "category": "approval_flag", "note": "boundary: 200 >= 200"},
    {"name": "mid-range flag", "txn": {"amount": 350, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "FLAGGED", "category": "approval_flag"},
    {"name": "just under per-tx block but flagged", "txn": {"amount": 499, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "FLAGGED", "category": "approval_flag", "note": "499<500 so no block, but >=200 flag"},
    {"name": "flag on ads", "txn": {"amount": 275, "merchant": "meta.com", "category": "ads"},
     "expected": "FLAGGED", "category": "approval_flag"},

    # --- per_tx_block (> 500) ---
    {"name": "exactly at per-tx limit (allowed)", "txn": {"amount": 500, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "FLAGGED", "category": "edge_case", "note": "500 not > 500, so no block; but >=200 flag"},
    {"name": "one cent over per-tx limit", "txn": {"amount": 500.01, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "BLOCKED", "category": "per_tx_block", "note": "boundary: 500.01 > 500"},
    {"name": "big single compute buy", "txn": {"amount": 6200, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "BLOCKED", "category": "per_tx_block"},
    {"name": "huge single spend", "txn": {"amount": 12400, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "BLOCKED", "category": "per_tx_block", "note": "the 3am nightmare"},
    {"name": "block wins over flag", "txn": {"amount": 900, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "BLOCKED", "category": "per_tx_block", "note": ">500 blocks even though >=200 would flag"},

    # --- daily_limit (cumulative) ---
    {"name": "pushes over daily cap", "txn": {"amount": 300, "merchant": "aws.amazon.com", "category": "compute"},
     "prior": [{"amount": 450}, {"amount": 450}, {"amount": 450}, {"amount": 450}],
     "expected": "BLOCKED", "category": "daily_limit", "note": "1800 prior + 300 = 2100 > 2000"},
    {"name": "exactly reaches daily cap (allowed edge)", "txn": {"amount": 200, "merchant": "aws.amazon.com", "category": "compute"},
     "prior": [{"amount": 450}, {"amount": 450}, {"amount": 450}, {"amount": 450}],
     "expected": "FLAGGED", "category": "edge_case", "note": "1800+200=2000 not >2000; but 200>=flag"},
    {"name": "daily cap not yet reached", "txn": {"amount": 100, "merchant": "aws.amazon.com", "category": "compute"},
     "prior": [{"amount": 400}, {"amount": 400}],
     "expected": "APPROVED", "category": "daily_limit", "note": "800+100=900 < 2000, <200 flag"},
    {"name": "daily cap with small txn still blocks", "txn": {"amount": 60, "merchant": "aws.amazon.com", "category": "compute"},
     "prior": [{"amount": 490}, {"amount": 490}, {"amount": 490}, {"amount": 490}],
     "expected": "BLOCKED", "category": "daily_limit", "note": "1960+60=2020>2000; daily beats small amount"},

    # --- velocity / runaway ---
    {"name": "11th txn in an hour (runaway)", "txn": {"amount": 10, "merchant": "openai.com", "category": "api"},
     "prior": [{"amount": 10}] * 10,
     "expected": "BLOCKED", "category": "velocity", "note": "10 prior + this = 11 > 10 max"},
    {"name": "10th txn still allowed", "txn": {"amount": 10, "merchant": "openai.com", "category": "api"},
     "prior": [{"amount": 10}] * 9,
     "expected": "APPROVED", "category": "velocity", "note": "9 prior + this = 10, not > 10"},
    {"name": "runaway loop of tiny charges", "txn": {"amount": 3, "merchant": "openai.com", "category": "api"},
     "prior": [{"amount": 3}] * 15,
     "expected": "BLOCKED", "category": "velocity", "note": "velocity catches loop even when amounts tiny"},

    # --- merchant_block (agent-specific) ---
    {"name": "blocklisted sketchy TLD", "txn": {"amount": 50, "merchant": "unknown-gpu.ru", "category": "compute"},
     "rules": [("merchant_block", {"patterns": ["*.ru", "sketchy*"]}, "BLOCKED", 120, "block sketchy merchants")],
     "expected": "BLOCKED", "category": "merchant_block"},
    {"name": "blocklist pattern match", "txn": {"amount": 30, "merchant": "sketchy-vendor-99", "category": "goods"},
     "rules": [("merchant_block", {"patterns": ["*.ru", "sketchy*"]}, "BLOCKED", 120, "block sketchy")],
     "expected": "BLOCKED", "category": "merchant_block"},
    {"name": "clean merchant passes blocklist", "txn": {"amount": 40, "merchant": "openai.com", "category": "api"},
     "rules": [("merchant_block", {"patterns": ["*.ru", "sketchy*"]}, "BLOCKED", 120, "block sketchy")],
     "expected": "APPROVED", "category": "merchant_block"},

    # --- merchant_allow (allowlist mode) ---
    {"name": "merchant not on allowlist", "txn": {"amount": 50, "merchant": "random-shop.com", "category": "goods"},
     "rules": [("merchant_allow", {"patterns": ["openai.com", "aws*", "google.com"]}, "BLOCKED", 130, "allowlist only")],
     "expected": "BLOCKED", "category": "merchant_block", "note": "allowlist blocks strangers"},
    {"name": "merchant on allowlist", "txn": {"amount": 50, "merchant": "aws.amazon.com", "category": "compute"},
     "rules": [("merchant_allow", {"patterns": ["openai.com", "aws*", "google.com"]}, "BLOCKED", 130, "allowlist only")],
     "expected": "APPROVED", "category": "merchant_block"},
    {"name": "allowlist flag instead of block", "txn": {"amount": 50, "merchant": "stranger.io", "category": "goods"},
     "rules": [("merchant_allow", {"patterns": ["openai.com"]}, "FLAGGED", 130, "flag non-allowlisted")],
     "expected": "FLAGGED", "category": "merchant_block", "note": "allowlist can flag not block"},

    # --- category_limit ---
    {"name": "ads over category cap", "txn": {"amount": 300, "merchant": "google.com", "category": "ads"},
     "rules": [("category_limit", {"category": "ads", "max_amount": 100}, "BLOCKED", 140, "ads cap $100")],
     "expected": "BLOCKED", "category": "category_limit", "note": "300>100 ads cap"},
    {"name": "ads under category cap", "txn": {"amount": 80, "merchant": "google.com", "category": "ads"},
     "rules": [("category_limit", {"category": "ads", "max_amount": 100}, "BLOCKED", 140, "ads cap $100")],
     "expected": "APPROVED", "category": "category_limit"},
    {"name": "category cap doesn't touch other categories", "txn": {"amount": 150, "merchant": "aws.amazon.com", "category": "compute"},
     "rules": [("category_limit", {"category": "ads", "max_amount": 100}, "BLOCKED", 140, "ads cap $100")],
     "expected": "APPROVED", "category": "category_limit", "note": "compute unaffected by ads cap"},
    {"name": "category cap flag mode", "txn": {"amount": 120, "merchant": "meta.com", "category": "ads"},
     "rules": [("category_limit", {"category": "ads", "max_amount": 100}, "FLAGGED", 140, "flag big ads")],
     "expected": "FLAGGED", "category": "category_limit"},

    # --- time_window ---
    {"name": "spend outside business hours", "txn": {"amount": 50, "merchant": "openai.com", "category": "api", "timestamp": "2026-07-08T03:00:00+00:00"},
     "rules": [("time_window", {"start_hour": 9, "end_hour": 18}, "BLOCKED", 110, "no 3am spend")],
     "expected": "BLOCKED", "category": "time_window", "note": "3am outside 9-18"},
    {"name": "spend inside business hours", "txn": {"amount": 50, "merchant": "openai.com", "category": "api", "timestamp": "2026-07-08T14:00:00+00:00"},
     "rules": [("time_window", {"start_hour": 9, "end_hour": 18}, "BLOCKED", 110, "no 3am spend")],
     "expected": "APPROVED", "category": "time_window", "note": "2pm inside window"},
    {"name": "time window flag at night", "txn": {"amount": 50, "merchant": "openai.com", "category": "api", "timestamp": "2026-07-08T23:30:00+00:00"},
     "rules": [("time_window", {"start_hour": 9, "end_hour": 18}, "FLAGGED", 110, "flag off-hours")],
     "expected": "FLAGGED", "category": "time_window"},

    # --- edge_case: rule composition & priority ---
    {"name": "block beats flag on same txn", "txn": {"amount": 700, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "BLOCKED", "category": "edge_case", "note": "700>500 block, also >=200 flag -> block wins"},
    {"name": "merchant block beats approval flag", "txn": {"amount": 250, "merchant": "bad.ru", "category": "goods"},
     "rules": [("merchant_block", {"patterns": ["*.ru"]}, "BLOCKED", 120, "block ru")],
     "expected": "BLOCKED", "category": "edge_case", "note": "250 would flag, but .ru blocks"},
    {"name": "negative amount treated as zero-ish", "txn": {"amount": -50, "merchant": "openai.com", "category": "api"},
     "expected": "APPROVED", "category": "edge_case", "note": "refund/negative not a spend risk"},
    {"name": "flag when only approval rule trips", "txn": {"amount": 480, "merchant": "aws.amazon.com", "category": "compute"},
     "expected": "FLAGGED", "category": "edge_case", "note": "480<500 no block, >=200 flag"},
    {"name": "daily block beats per-tx approval", "txn": {"amount": 150, "merchant": "aws.amazon.com", "category": "compute"},
     "prior": [{"amount": 490}, {"amount": 490}, {"amount": 490}, {"amount": 490}],
     "expected": "BLOCKED", "category": "edge_case", "note": "under per-tx but blows daily cap"},
    {"name": "velocity block beats approval flag", "txn": {"amount": 300, "merchant": "openai.com", "category": "api"},
     "prior": [{"amount": 10}] * 10,
     "expected": "BLOCKED", "category": "edge_case", "note": "300 would flag, but 11th txn blocks"},
    {"name": "high priority merchant block over daily", "txn": {"amount": 50, "merchant": "evil.ru", "category": "goods"},
     "rules": [("merchant_block", {"patterns": ["*.ru"]}, "BLOCKED", 200, "top-priority block")],
     "prior": [{"amount": 500}],
     "expected": "BLOCKED", "category": "edge_case"},
    {"name": "case-insensitive merchant match", "txn": {"amount": 50, "merchant": "BAD.RU", "category": "goods"},
     "rules": [("merchant_block", {"patterns": ["*.ru"]}, "BLOCKED", 120, "block ru")],
     "expected": "BLOCKED", "category": "edge_case", "note": "uppercase merchant still matches"},

    # --- more clean/flag/block variety to reach 50 ---
    {"name": "large travel booking flagged", "txn": {"amount": 460, "merchant": "booking.com", "category": "travel"},
     "expected": "FLAGGED", "category": "approval_flag"},
    {"name": "domain purchase small", "txn": {"amount": 12, "merchant": "namecheap.com", "category": "domains"},
     "expected": "APPROVED", "category": "clean_approval"},
    {"name": "gpu rental blocked over per-tx", "txn": {"amount": 800, "merchant": "runpod.io", "category": "compute"},
     "expected": "BLOCKED", "category": "per_tx_block"},
    {"name": "api topup flagged mid", "txn": {"amount": 210, "merchant": "anthropic.com", "category": "api"},
     "expected": "FLAGGED", "category": "approval_flag"},
    {"name": "many small under velocity ok", "txn": {"amount": 5, "merchant": "openai.com", "category": "api"},
     "prior": [{"amount": 5}] * 5,
     "expected": "APPROVED", "category": "velocity", "note": "6th of hour, fine"},
    {"name": "category cap exact boundary allowed", "txn": {"amount": 100, "merchant": "google.com", "category": "ads"},
     "rules": [("category_limit", {"category": "ads", "max_amount": 100}, "BLOCKED", 140, "ads cap")],
     "expected": "APPROVED", "category": "edge_case", "note": "100 not > 100"},
    {"name": "combined: daily near cap small ok", "txn": {"amount": 30, "merchant": "openai.com", "category": "api"},
     "prior": [{"amount": 500}, {"amount": 500}, {"amount": 500}],
     "expected": "APPROVED", "category": "daily_limit", "note": "1500+30=1530<2000, <200"},
    {"name": "flag then human territory", "txn": {"amount": 350, "merchant": "shopify.com", "category": "goods"},
     "expected": "FLAGGED", "category": "approval_flag"},
    {"name": "blocklist plus under-limit amount", "txn": {"amount": 15, "merchant": "malware-host.ru", "category": "compute"},
     "rules": [("merchant_block", {"patterns": ["*.ru", "malware*"]}, "BLOCKED", 120, "block bad")],
     "expected": "BLOCKED", "category": "merchant_block", "note": "small amount, still bad merchant"},
    {"name": "clean high-freq legit ok", "txn": {"amount": 8, "merchant": "aws.amazon.com", "category": "compute"},
     "prior": [{"amount": 8}] * 8,
     "expected": "APPROVED", "category": "velocity", "note": "9th txn, under 10"},
]
