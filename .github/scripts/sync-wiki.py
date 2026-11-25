#!/usr/bin/env python3
"""Convert docs/ into a flat GitHub Wiki tree and clone/update the wiki repo.

Usage: sync-wiki.py <output-dir>

The script clones the wiki repo into <output-dir>, replaces every page with the
current docs/ content (flat filenames, rewritten links, sidebar and footer), and
leaves it ready for `git add -A && git commit && git push`.

Requires GH_TOKEN in the environment (used for the wiki clone URL).
"""

import os
import re
import subprocess
import sys

# ── page map ────────────────────────────────────────────────────────────────
# relative path in docs/ → wiki page name (without .md)
PAGE_MAP = {
    "README.md":                        "Home",
    "architecture.md":                  "Architecture",
    "decisions.md":                     "Decisions",
    "delivery.md":                      "Delivery",
    "security.md":                      "Security",
    "onboarding.md":                    "Onboarding",
    "contracts/auth.md":                "Contract:-Auth",
    "contracts/site.md":                "Contract:-Site",
    "contracts/adding-a-service.md":    "Adding-a-Service",
    "services/auth.md":                 "Service:-Auth",
    "services/site.md":                 "Service:-Site",
    "services/headscale.md":            "Service:-Headscale",
    "services/nextcloud.md":            "Service:-Nextcloud",
    "services/monitoring.md":           "Service:-Monitoring",
    "services/stalwart.md":             "Service:-Stalwart",
    "operations/lost-node.md":          "Runbook:-Lost-Node",
    "operations/rebuild-node.md":       "Runbook:-Rebuild-Node",
    "operations/restore.md":            "Runbook:-Restore",
    "operations/secrets.md":            "Runbook:-Secrets",
    "operations/storage-box.md":        "Runbook:-Storage-Box",
    "operations/initial-release.md":    "Runbook:-Initial-Release",
}

LINK_MAP: dict[str, str] = {}
for _rel, _wiki in PAGE_MAP.items():
    LINK_MAP[_rel] = _wiki
    LINK_MAP[os.path.basename(_rel)] = _wiki

SIDEBAR = """\
### 📖 Start here
- [[Home]]
- [[Architecture]]
- [[Decisions]]
- [[Delivery]]
- [[Security]]
- [[Onboarding]]

### 📋 Contracts
- [[Contract: Auth|Contract:-Auth]]
- [[Contract: Site|Contract:-Site]]
- [[Adding a Service|Adding-a-Service]]

### ⚙️ Services
- [[Auth|Service:-Auth]]
- [[Site|Service:-Site]]
- [[Headscale|Service:-Headscale]]
- [[Stalwart|Service:-Stalwart]]
- [[Nextcloud|Service:-Nextcloud]]
- [[Monitoring|Service:-Monitoring]]

### 🔧 Runbooks
- [[Initial Release|Runbook:-Initial-Release]]
- [[Rebuild Node|Runbook:-Rebuild-Node]]
- [[Lost Node|Runbook:-Lost-Node]]
- [[Restore|Runbook:-Restore]]
- [[Secrets|Runbook:-Secrets]]
- [[Storage Box|Runbook:-Storage-Box]]
"""

FOOTER = """\
---
Source: [cglc-main/docs](https://github.com/cglc-main/docs) · \
A change to any repository that changes how things work changes the page here \
in the same pull request.
"""


# ── helpers ─────────────────────────────────────────────────────────────────

def convert_links(content: str, source_rel: str) -> str:
    """Rewrite relative markdown links to wiki page names."""
    source_dir = os.path.dirname(source_rel)

    def _replace(m: re.Match) -> str:
        text, target = m.group(1), m.group(2)
        if target.startswith(("http://", "https://", "#")):
            return m.group(0)
        anchor = ""
        if "#" in target:
            target, anchor = target.rsplit("#", 1)
            anchor = "#" + anchor
        resolved = os.path.normpath(os.path.join(source_dir, target)) if source_dir else os.path.normpath(target)
        wiki = PAGE_MAP.get(resolved) or LINK_MAP.get(os.path.basename(target))
        if wiki:
            return f"[{text}]({wiki.replace(' ', '-')}{anchor})"
        return m.group(0)

    return re.sub(r"\[([^\]]*)\]\(([^)]+)\)", _replace, content)


# ── main ────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: sync-wiki.py <output-dir>")

    out = sys.argv[1]
    token = os.environ.get("GH_TOKEN", "")
    repo_url = f"https://x-access-token:{token}@github.com/cglc-main/docs.wiki.git" if token else "git@github.com:cglc-main/docs.wiki.git"

    # Clone (or reuse) the wiki repo
    if not os.path.isdir(out):
        subprocess.run(["git", "clone", repo_url, out], check=True)
    else:
        subprocess.run(["git", "-C", out, "pull", "--ff-only"], check=True)

    # Remove old pages (keep .git)
    for f in os.listdir(out):
        if f == ".git":
            continue
        os.remove(os.path.join(out, f))

    # Find the docs root (the directory that contains this script's repo)
    docs_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    # Convert and write pages
    for rel, wiki_name in PAGE_MAP.items():
        src = os.path.join(docs_root, rel)
        if not os.path.isfile(src):
            print(f"  SKIP (not found): {rel}")
            continue
        with open(src) as fh:
            content = convert_links(fh.read(), rel)
        with open(os.path.join(out, wiki_name + ".md"), "w") as fh:
            fh.write(content)
        print(f"  {rel:45s} → {wiki_name}.md")

    # Sidebar and footer
    with open(os.path.join(out, "_Sidebar.md"), "w") as fh:
        fh.write(SIDEBAR)
    with open(os.path.join(out, "_Footer.md"), "w") as fh:
        fh.write(FOOTER)
    print("  _Sidebar.md, _Footer.md")


if __name__ == "__main__":
    main()
