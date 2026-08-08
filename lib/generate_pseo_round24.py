"""Round 24 pSEO generator — sipi.bot (2026-08-08).

Fifth round — "tightening": technical canonical fix (see rebuild_sitemap.py
+ /tmp/fix_public_canonicals.py) plus 24 targeted pages:
  repo-root: sectors +3, cost-of +4, glossary +4, for +2, use-cases +2,
             faq +2, best +2, templates +2   (21 pages)
  public/:   checklists +3 (slash-canonical — matches _serve_static 301s)

Reuses Round 20 renderers and Round 21's patch_hub. Checklists get a
public-root leaf writer with trailing-slash canonical.
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
from generate_pseo_round24_data import (  # noqa: E402
    SECTORS, COST_OF, GLOSSARY, FOR, USE_CASES, FAQ, BEST, TEMPLATES, CHECKLISTS,
)


def _body(meta, crumb_label, crumb_href, table_h2):
    m = dict(meta)
    m["crumb"] = (("Home", "/"), (crumb_label, crumb_href), (meta["h1"], None))
    m["table_h2"] = table_h2
    return build_leaf_body(m)


def write_public_leaf(prefix, slug, title, description, body, faqs, related):
    """Write public/<prefix>/<slug>/index.html with TRAILING-SLASH canonical
    (public/ leaves are served by _serve_static, which 301s bare → slash)."""
    import common
    path = os.path.join(PUBLIC, prefix, slug)
    os.makedirs(path, exist_ok=True)
    canonical = f"/{prefix}/{slug}/"
    jsonld = [
        common.breadcrumb_ld([
            {"name": "Home", "url": common.SITE + "/"},
            {"name": prefix, "url": common.SITE + f"/{prefix}/"},
            {"name": slug, "url": common.SITE + canonical},
        ]),
        common.faq_ld([{"question": q, "answer": a} for q, a in faqs]),
    ]
    html = common.page(
        title=title, description=description, canonical_path=canonical,
        active=None, body=body, jsonld=jsonld,
    )
    common.write(os.path.join(path, "index.html"), html)
    return canonical


def patch_checklists_hub():
    hub_path = os.path.join(PUBLIC, "checklists", "index.html")
    if not os.path.exists(hub_path):
        print("  !! public/checklists/index.html missing")
        return
    with open(hub_path, encoding="utf-8") as f:
        hub = f.read()
    if f"/checklists/{CHECKLISTS[0]['slug']}" in hub:
        print("  !! checklists hub already contains new pages")
        return
    lis = "".join(
        f'<li><a href="/checklists/{c["slug"]}/">{c["h1"]}</a> — {c["lead"]}</li>'
        for c in CHECKLISTS
    )
    block = f'<h2>New checklists</h2><ul style="margin:0 0 2rem;padding-left:1.25rem">{lis}</ul>'
    if "</body>" in hub:
        hub = hub.replace("</body>", block + "</body>")
    else:
        hub += block
    with open(hub_path, "w", encoding="utf-8") as f:
        f.write(hub)
    print("  checklists/ hub patched")


def build_group(prefix, items, crumb_label, crumb_href, table_h2, heading):
    for it in items:
        body = _body(it, crumb_label, crumb_href, table_h2)
        write_leaf(prefix, it["slug"], it["title"], it["desc"], body,
                   it["faqs"], it["related"])
    patch_hub(prefix, items, "h1", "lead", heading)
    print(f"{prefix}/: {len(items)} pages + hub patched")
    return len(items)


def build_checklists():
    count = 0
    for c in CHECKLISTS:
        body = _body(c, "Checklists", "/checklists/", "The checklist")
        write_public_leaf("checklists", c["slug"], c["title"], c["desc"], body,
                          c["faqs"], c["related"])
        count += 1
    patch_checklists_hub()
    print(f"public/checklists/: {count} pages + hub patched")
    return count


def main():
    total = 0
    total += build_group("sectors", SECTORS, "Sectors", "/sectors/",
                         "The rules that matter most", "More sectors")
    total += build_group("cost-of", COST_OF, "Cost of AI", "/cost-of/",
                         "Where the money goes", "Subscriptions & plans")
    total += build_group("glossary", GLOSSARY, "Glossary", "/glossary/",
                         None, "Rule types")
    total += build_group("for", FOR, "For teams", "/for/",
                         "What you get", "More teams")
    total += build_group("use-cases", USE_CASES, "Use cases", "/use-cases/",
                         "Spend map", "More use cases")
    total += build_group("faq", FAQ, "FAQ", "/faq/",
                         "At a glance", "The firewall, plainly")
    total += build_group("best", BEST, "Best-of", "/best/",
                         "At a glance", "New in 2026")
    total += build_group("templates", TEMPLATES, "Templates", "/templates/",
                         None, "More templates")
    total += build_checklists()
    print(f"\n✓ Round 24 complete — {total} new pages")


if __name__ == "__main__":
    main()
