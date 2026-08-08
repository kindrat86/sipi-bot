"""Round 26 pSEO generator — sipi.bot (2026-08-08).

Seventh round. 10 static pages + 2 honest rewrites of fabricated-stat answers
pages + 2 blog posts (added via lib/generate_content.py separately).

- ANSWERS (public/, slash canonical via write_public_leaf): 3 new pages +
  rewrites of ai-spending-benchmarks-2026 and how-to-control-ai-api-costs
  (both contained invented market ranges — replaced with honest content).
- tutorials +2, scenarios +1, redflags +1, guides +1 (repo-root, bare).
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, "public")
sys.path.insert(0, HERE)

import common  # noqa: E402
from generate_pseo_round20 import write_leaf, build_leaf_body  # noqa: E402
from generate_pseo_round21 import patch_hub  # noqa: E402
from generate_pseo_round24 import write_public_leaf  # noqa: E402
from generate_pseo_round26_data import (  # noqa: E402
    ANSWERS, TUTORIALS, SCENARIOS, REDFLAGS, GUIDES,
)


def _body(meta, crumb_label, crumb_href, table_h2):
    m = dict(meta)
    m["crumb"] = (("Home", "/"), (crumb_label, crumb_href), (meta["h1"], None))
    m["table_h2"] = table_h2
    return build_leaf_body(m)


def build_answers():
    count = 0
    for a in ANSWERS:
        body = _body(a, "Answers", "/answers/", "At a glance")
        write_public_leaf("answers", a["slug"], a["title"], a["desc"], body,
                          a["faqs"], a["related"])
        count += 1
    # Patch the answers hub (public/)
    hub_path = os.path.join(PUBLIC, "answers", "index.html")
    if os.path.exists(hub_path):
        with open(hub_path, encoding="utf-8") as f:
            hub = f.read()
        if f"/answers/{ANSWERS[0]['slug']}/" not in hub:
            lis = "".join(
                f'<li><a href="/answers/{a["slug"]}/">{a["h1"]}</a> — {a["lead"]}</li>'
                for a in ANSWERS
            )
            block = f'<h2>Answers</h2><ul style="margin:0 0 2rem;padding-left:1.25rem">{lis}</ul>'
            if "</body>" in hub:
                hub = hub.replace("</body>", block + "</body>")
            else:
                hub += block
            with open(hub_path, "w", encoding="utf-8") as f:
                f.write(hub)
            print("  answers/ hub patched")
        else:
            print("  answers/ hub already up to date")
    else:
        print("  !! public/answers/index.html missing")
    print(f"public/answers/: {count} pages (3 new + 2 honest rewrites)")
    return count


def build_group(prefix, items, crumb_label, crumb_href, table_h2, heading):
    for it in items:
        body = _body(it, crumb_label, crumb_href, table_h2)
        write_leaf(prefix, it["slug"], it["title"], it["desc"], body,
                   it["faqs"], it["related"])
    patch_hub(prefix, items, "h1", "lead", heading)
    print(f"{prefix}/: {len(items)} pages + hub patched")
    return len(items)


def fix_data_canonical():
    """spendfirewall/data/* is served bare by _serve_pseo (/data/ prefix) but
    the page emitted a slash canonical — same contradiction pattern."""
    import re
    path = os.path.join(ROOT, "spendfirewall", "data",
                        "ai-agent-adoption-statistics", "index.html")
    if not os.path.exists(path):
        print("  !! data page not found")
        return
    html = open(path, encoding="utf-8").read()
    new = re.sub(r'<link rel="canonical" href="https://sipi\.bot/data/ai-agent-adoption-statistics/"',
                 '<link rel="canonical" href="https://sipi.bot/data/ai-agent-adoption-statistics"', html)
    new = re.sub(r'<meta property="og:url" content="https://sipi\.bot/data/ai-agent-adoption-statistics/"',
                 '<meta property="og:url" content="https://sipi.bot/data/ai-agent-adoption-statistics"', new)
    if new != html:
        open(path, "w", encoding="utf-8").write(new)
        print("  data/ai-agent-adoption-statistics canonical → bare")
    else:
        print("  data canonical: already bare or pattern not found")


def main():
    total = 0
    total += build_answers()
    total += build_group("tutorials", TUTORIALS, "Tutorials", "/tutorials/",
                         None, "Integrations & budgets")
    total += build_group("scenarios", SCENARIOS, "Scenarios", "/scenarios/",
                         "The rule set", "Policy in practice")
    total += build_group("redflags", REDFLAGS, "Red flags", "/redflags/",
                         "At a glance", "Subscriptions")
    total += build_group("guides", GUIDES, "Guides", "/guides/",
                         None, "New guide")
    fix_data_canonical()
    print(f"\n✓ Round 26 complete — {total} pages (+2 rewrites +1 canonical fix)")


if __name__ == "__main__":
    main()
