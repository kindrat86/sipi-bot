"""Round 27 pSEO generator — sipi.bot (2026-08-08).

Eighth round. 23 static pages (18 repo-root bare + 5 public slash) + 2 blog
posts (added via lib/generate_content.py separately).
"""
from __future__ import annotations
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PUBLIC = os.path.join(ROOT, "public")
sys.path.insert(0, HERE)

from generate_pseo_round20 import write_leaf, build_leaf_body  # noqa: E402
from generate_pseo_round21 import patch_hub  # noqa: E402
from generate_pseo_round24 import write_public_leaf  # noqa: E402
from generate_pseo_round27_data import (  # noqa: E402
    INTEGRATIONS, VS, SECTORS, USE_CASES, GUIDES, TEMPLATES, ANSWERS, CHECKLISTS,
)


def _body(meta, crumb_label, crumb_href, table_h2):
    m = dict(meta)
    m["crumb"] = (("Home", "/"), (crumb_label, crumb_href), (meta["h1"], None))
    m["table_h2"] = table_h2
    return build_leaf_body(m)


def build_group(prefix, items, crumb_label, crumb_href, table_h2, heading):
    for it in items:
        body = _body(it, crumb_label, crumb_href, table_h2)
        write_leaf(prefix, it["slug"], it["title"], it["desc"], body,
                   it["faqs"], it["related"])
    patch_hub(prefix, items, "h1", "lead", heading)
    print(f"{prefix}/: {len(items)} pages + hub patched")
    return len(items)


def _patch_public_hub(prefix, items, heading):
    hub_path = os.path.join(PUBLIC, prefix, "index.html")
    if not os.path.exists(hub_path):
        print(f"  !! {prefix}/index.html missing")
        return
    with open(hub_path, encoding="utf-8") as f:
        hub = f.read()
    if f"/{prefix}/{items[0]['slug']}/" in hub:
        print(f"  {prefix}/ hub already up to date")
        return
    lis = "".join(
        f'<li><a href="/{prefix}/{it["slug"]}/">{it["h1"]}</a> — {it["lead"]}</li>'
        for it in items
    )
    block = f'<h2>{heading}</h2><ul style="margin:0 0 2rem;padding-left:1.25rem">{lis}</ul>'
    if "</body>" in hub:
        hub = hub.replace("</body>", block + "</body>")
    else:
        hub += block
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(hub)
    print(f"  {prefix}/ hub patched")


def build_public(prefix, items, heading):
    for it in items:
        body = _body(it, prefix.capitalize(), f"/{prefix}/", "At a glance")
        write_public_leaf(prefix, it["slug"], it["title"], it["desc"], body,
                          it["faqs"], it["related"])
    _patch_public_hub(prefix, items, heading)
    print(f"public/{prefix}/: {len(items)} pages + hub patched")
    return len(items)


def main():
    total = 0
    total += build_group("integrations", INTEGRATIONS, "Integrations", "/integrations/",
                         "Rules that fit this workload", "Frameworks & SDKs")
    total += build_group("vs", VS, "Comparisons", "/vs/",
                         "Side by side", "Cloud cost platforms")
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "More sectors")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "More use cases")
    total += build_group("guides", GUIDES, "Guides", "/guides/",
                         None, "New guides")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "More templates")
    total += build_public("answers", ANSWERS, "Agent spend controls")
    total += build_public("checklists", CHECKLISTS, "Launch & tuning")
    print(f"\n✓ Round 27 complete — {total} new pages")


if __name__ == "__main__":
    main()
