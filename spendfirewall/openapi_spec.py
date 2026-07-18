"""openapi_spec.py — static OpenAPI 3.0 spec for sipi.bot's public API.

Served at GET /openapi.json so AI agents (and AIO/AEO crawlers) can discover
the spend-firewall API. Hand-written (not auto-generated) because the API is
served via stdlib http.server, not FastAPI.

The spec documents the REAL endpoints implemented in api.py. Keep it in sync
when routes change.
"""
from __future__ import annotations

import json

from . import __version__

# Reusable schemas
_RULE_PARAM_EXAMPLES = {
    "per_transaction": {"max_amount": 500},
    "daily_total": {"max_amount": 1000},
    "velocity": {"max_count": 10, "window_seconds": 3600},
    "merchant_block": {"patterns": ["*.ru", "sketchy*"]},
    "merchant_allow": {"patterns": ["openai.com", "aws*"]},
    "category_limit": {"category": "compute", "max_amount": 2000},
    "time_window": {"start_hour": 9, "end_hour": 18},
    "approval_threshold": {"amount": 1000},
}

SPEC: dict = {
    "openapi": "3.0.3",
    "info": {
        "title": "sipi.bot — Spend Firewall for AI Agents",
        "description": (
            "sipi.bot sits in front of every transaction an autonomous AI agent "
            "attempts and evaluates it against your spend rules — per-transaction "
            "caps, daily totals, velocity (runaway-loop protection), merchant "
            "allow/block, category limits, time windows, and approval thresholds. "
            "It returns APPROVED, BLOCKED, or FLAGGED in under 5ms, before a "
            "single dollar moves. Every decision is written to a tamper-evident "
            "audit log.\n\n"
            "**The core call an agent makes before spending:** "
            "`POST /v1/transactions/evaluate`.\n\n"
            "Auth is optional in free / self-host mode. Pass "
            "`Authorization: Bearer <api_key>` to attribute transactions to a "
            "registered agent (keys are returned by `POST /api/agents`)."
        ),
        "version": __version__,
        "contact": {
            "name": "sipi.bot",
            "url": "https://sipi.bot",
            "email": "sales@sipiteno.com",
        },
        "license": {"name": "MIT", "url": "https://github.com/kindrat86/sipi-bot/blob/main/LICENSE"},
        "termsOfService": "https://sipi.bot/terms",
    },
    "servers": [
        {"url": "https://sipi.bot", "description": "Production"},
    ],
    "externalDocs": {
        "description": "Agent card (A2A discovery)",
        "url": "https://sipi.bot/.well-known/agent-card.json",
    },
    "tags": [
        {"name": "Evaluate", "description": "The core spend-decision call an agent makes"},
        {"name": "Rules", "description": "Create, list, and delete spend-policy rules"},
        {"name": "Approvals", "description": "Human-in-the-loop approval queue for FLAGGED transactions"},
        {"name": "Agents", "description": "Register agents and issue API keys"},
        {"name": "Budget", "description": "Live spend activity, budget status, and dashboard aggregates"},
        {"name": "System", "description": "Service health and metadata"},
    ],
    "components": {
        "securitySchemes": {
            "BearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "description": "Optional. Pass an agent API key (returned by POST /api/agents) to attribute transactions to that agent.",
            }
        },
        "schemas": {
            "TransactionRequest": {
                "type": "object",
                "required": ["amount"],
                "properties": {
                    "amount": {"type": "number", "format": "float", "description": "Transaction amount in the given currency.", "example": 6200},
                    "merchant": {"type": "string", "description": "Merchant name or domain the agent wants to pay.", "example": "unknown-gpu.ru"},
                    "category": {"type": "string", "description": "Spend category, e.g. compute / api / ads / travel.", "example": "compute"},
                    "currency": {"type": "string", "description": "ISO 4217 currency code.", "default": "USD", "example": "USD"},
                    "description": {"type": "string", "description": "Optional free-text description of the proposed spend.", "example": "A100 GPU rental"},
                    "timestamp": {"type": "string", "format": "date-time", "description": "Optional ISO-8601 timestamp; defaults to now (UTC).", "example": "2026-07-18T02:14:00Z"},
                },
            },
            "Decision": {
                "type": "string",
                "enum": ["APPROVED", "BLOCKED", "FLAGGED"],
                "description": "APPROVED = pass all rules. BLOCKED = violates a hard rule, no money moves. FLAGGED = allowed but crosses an approval threshold, routed to the human queue.",
            },
            "EvaluationResponse": {
                "type": "object",
                "properties": {
                    "decision": {"$ref": "#/components/schemas/Decision"},
                    "reason": {"type": "string", "description": "Human-readable explanation; the rule label if a rule tripped.", "example": "Merchant not on allowlist"},
                    "rule_id": {"type": "string", "nullable": True, "description": "ID of the rule that decided the outcome, if any."},
                    "triggered": {
                        "type": "array",
                        "description": "Every rule that matched this transaction (in evaluation order).",
                        "items": {
                            "type": "object",
                            "properties": {
                                "rule_id": {"type": "string"},
                                "rule_type": {"type": "string"},
                                "action": {"$ref": "#/components/schemas/Decision"},
                                "label": {"type": "string"},
                            },
                        },
                    },
                    "transaction_id": {"type": "string", "nullable": True, "description": "Audit-log ID for the recorded transaction."},
                    "amount": {"type": "number"},
                    "merchant": {"type": "string"},
                    "category": {"type": "string"},
                },
            },
            "Rule": {
                "type": "object",
                "properties": {
                    "id": {"type": "string", "example": "r_per_transaction_500"},
                    "rule_type": {
                        "type": "string",
                        "enum": list(_RULE_PARAM_EXAMPLES.keys()),
                        "description": "The rule check to apply.",
                    },
                    "params": {
                        "type": "object",
                        "description": "Rule-type-specific parameters.",
                        "example": {"max_amount": 500},
                    },
                    "action": {"$ref": "#/components/schemas/Decision"},
                    "priority": {"type": "integer", "default": 100, "description": "Higher priority rules are evaluated first. First BLOCK wins."},
                    "enabled": {"type": "boolean", "default": True},
                    "label": {"type": "string", "description": "Optional human label used as the reason when the rule trips."},
                    "agent_id": {"type": "string", "nullable": True, "description": "Scope this rule to a specific agent. null = global."},
                },
            },
            "RuleCreate": {
                "type": "object",
                "required": ["rule_type"],
                "properties": {
                    "rule_type": {"type": "string", "enum": list(_RULE_PARAM_EXAMPLES.keys())},
                    "params": {"type": "object", "description": "Rule-type-specific parameters.", "example": {"max_amount": 500}},
                    "action": {"$ref": "#/components/schemas/Decision", "default": "BLOCKED"},
                    "priority": {"type": "integer", "default": 100},
                    "label": {"type": "string", "default": ""},
                },
            },
            "Approval": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "transaction_id": {"type": "string"},
                    "status": {"type": "string", "enum": ["pending", "approved", "denied"]},
                    "amount": {"type": "number"},
                    "merchant": {"type": "string"},
                    "reason": {"type": "string"},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "Agent": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string", "example": "billing-agent"},
                    "api_key": {"type": "string", "description": "Bearer token for /v1/transactions/evaluate. Only returned once, at creation."},
                    "created_at": {"type": "string", "format": "date-time"},
                },
            },
            "Transaction": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "amount": {"type": "number"},
                    "merchant": {"type": "string"},
                    "category": {"type": "string"},
                    "decision": {"$ref": "#/components/schemas/Decision"},
                    "reason": {"type": "string"},
                    "agent_id": {"type": "string", "nullable": True},
                    "timestamp": {"type": "string", "format": "date-time"},
                },
            },
            "Stats": {
                "type": "object",
                "description": "Live dashboard aggregates: totals, decision breakdown, current budget posture.",
                "properties": {
                    "total_transactions": {"type": "integer"},
                    "approved": {"type": "integer"},
                    "blocked": {"type": "integer"},
                    "flagged": {"type": "integer"},
                    "pending_approvals": {"type": "integer"},
                    "active_rules": {"type": "integer"},
                    "daily_spend": {"type": "number"},
                },
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {"type": "string"},
                },
            },
        },
        "parameters": {
            "ApprovalDecision": {
                "name": "decision",
                "in": "query",
                "required": False,
                "schema": {"type": "string", "enum": ["approve", "deny"]},
                "description": "Resolution decision (sent in the request body by the API).",
            },
        },
        "examples": {
            "RuleParamsExamples": {"value": _RULE_PARAM_EXAMPLES},
        },
    },
    "security": [{"BearerAuth": []}],
    "paths": {
        "/v1/transactions/evaluate": {
            "post": {
                "tags": ["Evaluate"],
                "summary": "Evaluate a proposed agent spend",
                "description": (
                    "**The core call.** An autonomous agent calls this *before* it "
                    "spends money. sipi.bot evaluates the transaction against every "
                    "active rule and returns APPROVED, BLOCKED, or FLAGGED in "
                    "under 5ms.\n\n"
                    "Auth is optional in free / self-host mode; pass a Bearer agent "
                    "API key to attribute the transaction to a registered agent and "
                    "scope per-agent rules."
                ),
                "operationId": "evaluateTransaction",
                "security": [{}, {"BearerAuth": []}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/TransactionRequest"},
                            "examples": {
                                "blocked_unknown_merchant": {
                                    "summary": "Block an unknown merchant",
                                    "value": {"amount": 6200, "merchant": "unknown-gpu.ru", "category": "compute"},
                                },
                                "flag_over_threshold": {
                                    "summary": "Flag a high-value txn for human review",
                                    "value": {"amount": 2200, "merchant": "anthropic.com", "category": "api"},
                                },
                                "approve_normal": {
                                    "summary": "Approve a normal spend",
                                    "value": {"amount": 12.50, "merchant": "openai.com", "category": "api"},
                                },
                            },
                        }
                    },
                },
                "responses": {
                    "200": {
                        "description": "Decision returned.",
                        "content": {"application/json": {"schema": {"$ref": "#/components/schemas/EvaluationResponse"}}},
                    },
                    "400": {"description": "Invalid request body.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Error"}}}},
                },
            }
        },
        "/api/rules": {
            "get": {
                "tags": ["Rules"],
                "summary": "List all spend rules",
                "operationId": "listRules",
                "security": [{}],
                "responses": {
                    "200": {"description": "Rules list.", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Rule"}}}}},
                },
            },
            "post": {
                "tags": ["Rules"],
                "summary": "Add a spend rule",
                "operationId": "addRule",
                "security": [{}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RuleCreate"}}},
                },
                "responses": {
                    "200": {"description": "Created rule.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Rule"}}}},
                },
            },
        },
        "/api/rules/{rule_id}": {
            "delete": {
                "tags": ["Rules"],
                "summary": "Delete a spend rule",
                "operationId": "deleteRule",
                "security": [{}],
                "parameters": [
                    {"name": "rule_id", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "responses": {
                    "200": {"description": "Deletion result.", "content": {"application/json": {"schema": {"type": "object", "properties": {"deleted": {"type": "boolean"}}}}}},
                },
            }
        },
        "/api/approvals": {
            "get": {
                "tags": ["Approvals"],
                "summary": "List pending approvals",
                "description": "Returns FLAGGED transactions routed to the human-in-the-loop queue.",
                "operationId": "listApprovals",
                "security": [{}],
                "responses": {
                    "200": {"description": "Pending approvals.", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Approval"}}}}},
                },
            }
        },
        "/api/approvals/{approval_id}": {
            "post": {
                "tags": ["Approvals"],
                "summary": "Resolve a pending approval",
                "description": "Approve or deny a FLAGGED transaction in the human queue.",
                "operationId": "resolveApproval",
                "security": [{}],
                "parameters": [
                    {"name": "approval_id", "in": "path", "required": True, "schema": {"type": "string"}},
                ],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"type": "object", "required": ["decision"], "properties": {"decision": {"type": "string", "enum": ["approve", "deny"], "example": "approve"}}}}},
                },
                "responses": {
                    "200": {"description": "Resolution result.", "content": {"application/json": {"schema": {"type": "object", "properties": {"resolved": {"type": "boolean"}}}}}},
                },
            }
        },
        "/api/agents": {
            "get": {
                "tags": ["Agents"],
                "summary": "List registered agents",
                "operationId": "listAgents",
                "security": [{}],
                "responses": {
                    "200": {"description": "Agents list.", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Agent"}}}}},
                },
            },
            "post": {
                "tags": ["Agents"],
                "summary": "Register a new agent and get an API key",
                "operationId": "registerAgent",
                "security": [{}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string", "example": "billing-agent"}}}}},
                },
                "responses": {
                    "200": {"description": "Created agent. The api_key is only returned here — store it.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Agent"}}}},
                },
            },
        },
        "/api/transactions": {
            "get": {
                "tags": ["Budget"],
                "summary": "List recent transactions",
                "description": "Returns the 50 most recent recorded transactions (the audit-log tail).",
                "operationId": "listTransactions",
                "security": [{}],
                "responses": {
                    "200": {"description": "Recent transactions.", "content": {"application/json": {"schema": {"type": "array", "items": {"$ref": "#/components/schemas/Transaction"}}}}},
                },
            }
        },
        "/api/stats": {
            "get": {
                "tags": ["Budget"],
                "summary": "Dashboard aggregates and current budget posture",
                "description": "Live totals: transaction counts by decision, pending approvals, active rules, and current daily spend.",
                "operationId": "getStats",
                "security": [{}],
                "responses": {
                    "200": {"description": "Aggregates.", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/Stats"}}}},
                },
            }
        },
        "/billing/status": {
            "get": {
                "tags": ["Budget"],
                "summary": "Subscription / billing status",
                "description": "Whether the workspace is on a paid plan (drives whether rules are enforced).",
                "operationId": "billingStatus",
                "security": [{}],
                "responses": {
                    "200": {"description": "Billing status.", "content": {"application/json": {"schema": {"type": "object"}}}},
                },
            }
        },
        "/health": {
            "get": {
                "tags": ["System"],
                "summary": "Service health",
                "operationId": "health",
                "security": [{}],
                "responses": {
                    "200": {"description": "Service is up.", "content": {"application/json": {"schema": {"type": "object", "properties": {"ok": {"type": "boolean"}, "service": {"type": "string"}, "version": {"type": "string"}}}}}},
                },
            }
        },
        "/.well-known/agent-card.json": {
            "get": {
                "tags": ["System"],
                "summary": "Agent card (A2A discovery)",
                "description": "Machine-readable agent card for Agent-to-Agent discovery — name, capabilities, skills, and endpoint URLs.",
                "operationId": "agentCard",
                "security": [{}],
                "responses": {
                    "200": {"description": "Agent card.", "content": {"application/json": {"schema": {"type": "object"}}}},
                },
            }
        },
    },
}


def as_json() -> str:
    return json.dumps(SPEC)


def as_dict() -> dict:
    return SPEC
