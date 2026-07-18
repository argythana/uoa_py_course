"""Recon: log in to UoA eClass and snapshot the post-login portfolio page.

Read-only. One login, one fetch of portfolio.php, one logout.
Credentials come from .env (ECLASS_USERNAME, ECLASS_PASSWORD). Never echoed.
"""

from __future__ import annotations

import os
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

HERE = Path(__file__).parent
ROOT = HERE.parents[2]  # repo root
OUT = ROOT / "admin_docs" / "eclass_recon"  # snapshots contain PII — stays gitignored
OUT.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")
USER = os.environ["ECLASS_USERNAME"]
PASS = os.environ["ECLASS_PASSWORD"]

BASE = "https://eclass.uoa.gr"
LOGIN_POST = f"{BASE}/?login_page=1"
PORTFOLIO = f"{BASE}/main/portfolio.php"
LOGOUT = f"{BASE}/index.php?logout=yes"

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (uoa-py-course eclass recon)"

# Prime PHPSESSID by hitting the login form first (some installs need it)
s.get(f"{BASE}/main/login_form.php", timeout=20)

r = s.post(
    LOGIN_POST,
    data={"uname": USER, "pass": PASS, "next": "/main/portfolio.php", "submit": "Είσοδος"},
    timeout=20,
    allow_redirects=True,
)
print("post-login final url:", r.url)
print("post-login status:", r.status_code)
print("history:", [(h.status_code, h.url) for h in r.history])

# Heuristic: if we're back on login_form.php, login failed.
if "login_form.php" in r.url:
    print("\nLOGIN FAILED — still on login page.")
    raise SystemExit(1)

# Fetch portfolio.php explicitly (in case the redirect chain went elsewhere)
p = s.get(PORTFOLIO, timeout=20)
print("\nportfolio status:", p.status_code, "url:", p.url)
(OUT / "portfolio.html").write_text(p.text, encoding="utf-8")
print(f"saved -> {HERE / 'portfolio.html'} ({len(p.text)} bytes)")

soup = BeautifulSoup(p.text, "html.parser")
print("\npage title:", soup.title.string.strip() if soup.title else "(none)")

# What courses / sections does this account see?
links = soup.find_all("a", href=True)
print(f"\ntotal <a> links: {len(links)}")
# Group by interesting URL prefixes
buckets: dict[str, list[tuple[str, str]]] = {}
for a in links:
    href = a["href"]
    text = " ".join(a.get_text().split())[:80]
    if not href or href.startswith("#") or href.startswith("javascript"):
        continue
    # bucket by first path segment
    if href.startswith("/"):
        key = "/" + href.lstrip("/").split("/")[0].split("?")[0]
    elif href.startswith(BASE):
        rest = href[len(BASE):]
        key = "/" + rest.lstrip("/").split("/")[0].split("?")[0]
    elif href.startswith("http"):
        key = "(external)"
    else:
        key = "(relative)"
    buckets.setdefault(key, []).append((href, text))

print("\nlink prefixes seen:")
for k in sorted(buckets, key=lambda x: -len(buckets[x])):
    print(f"  {len(buckets[k]):4}  {k}")

# Look specifically for course links (Open eClass uses /modules/auth/courses.php and /courses/<code>/)
course_links = [a for a in links if "/courses/" in a["href"] or "course_code=" in a["href"]]
print(f"\ncourse-shaped links: {len(course_links)}")
for a in course_links[:20]:
    print(f"  {a['href']}  ->  {' '.join(a.get_text().split())[:80]}")

# Be polite — log out
s.get(LOGOUT, timeout=20)
print("\nlogged out.")
