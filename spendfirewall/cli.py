"""cli.py — argparse smoke-test harness. Verify the firewall without an agent.

Examples:
  python -m spendfirewall.cli status
  python -m spendfirewall.cli eval --amount 750 --merchant unknown-gpu.ru --category compute
  python -m spendfirewall.cli agent --name my-bot
  python -m spendfirewall.cli rules
  python -m spendfirewall.cli serve --port 8080
"""
from __future__ import annotations

import argparse
import json

from . import core, store


def main() -> None:
    p = argparse.ArgumentParser(prog="spendfirewall", description="sipi.bot spend firewall")
    sub = p.add_subparsers(dest="cmd", required=True)

    pe = sub.add_parser("eval", help="evaluate a transaction")
    pe.add_argument("--amount", type=float, required=True)
    pe.add_argument("--merchant", default="")
    pe.add_argument("--category", default="")
    pe.add_argument("--description", default="")

    sub.add_parser("status", help="show firewall stats")
    sub.add_parser("rules", help="list rules")

    pa = sub.add_parser("agent", help="register an agent")
    pa.add_argument("--name", required=True)

    ps = sub.add_parser("serve", help="run the HTTP server")
    ps.add_argument("--port", type=int, default=8080)
    ps.add_argument("--host", default="0.0.0.0")

    args = p.parse_args()
    store.init_db()

    if args.cmd == "eval":
        print(json.dumps(core.evaluate_transaction(
            amount=args.amount, merchant=args.merchant,
            category=args.category, description=args.description), indent=2))
    elif args.cmd == "status":
        print(json.dumps(core.status(), indent=2))
    elif args.cmd == "rules":
        print(json.dumps(store.list_rules(), indent=2))
    elif args.cmd == "agent":
        print(json.dumps(core.register_agent(args.name), indent=2))
    elif args.cmd == "serve":
        from . import api
        api.serve(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
