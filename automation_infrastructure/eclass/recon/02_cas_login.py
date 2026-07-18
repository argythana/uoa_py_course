"""Recon step 2: log in via UoA CAS (Apereo) and snapshot portfolio.php.

Flow:
  1. GET https://eclass.uoa.gr/modules/auth/cas.php?next=/main/portfolio.php
       -> redirects to sso.uoa.gr/login?service=...
  2. Scrape the `execution` token from the CAS login form.
  3. POST username/password/execution/_eventId=submit back to sso.uoa.gr/login.
  4. CAS 302s back to eClass with ?ticket=ST-..., eClass validates it,
     creates PHPSESSID session, redirects to /main/portfolio.php.

Read-only after login. Runs ONE login attempt; on failure, exits with the
diagnostic so we don't trigger CAS lockout by retrying blindly.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

HERE = Path(__file__).parent
ROOT = HERE.parents[2]
OUT = ROOT / "admin_docs" / "eclass_recon"  # snapshots contain PII — stays gitignored
OUT.mkdir(parents=True, exist_ok=True)

load_dotenv(ROOT / ".env")
USER = os.environ["ECLASS_USERNAME"]
PASS = os.environ["ECLASS_PASSWORD"]

CAS_ENTRY = "https://eclass.uoa.gr/modules/auth/cas.php?next=%2Fmain%2Fportfolio.php"
PORTFOLIO = "https://eclass.uoa.gr/main/portfolio.php"
LOGOUT = "https://eclass.uoa.gr/index.php?logout=yes"

s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (uoa-py-course eclass recon)"

# 1+2. Get the CAS login page and extract the execution token
r = s.get(CAS_ENTRY, timeout=20, allow_redirects=True)
print(f"[1] reached CAS login: {r.url}  (status {r.status_code})")
soup = BeautifulSoup(r.text, "html.parser")
form = soup.find("form", action=lambda a: a and "login" in a.lower())
if form is None:
    print("FATAL: no login form on CAS page", file=sys.stderr)
    sys.exit(2)
execution = form.find("input", {"name": "execution"})
if execution is None or not execution.get("value"):
    print("FATAL: no execution token on CAS page", file=sys.stderr)
    sys.exit(2)
print(f"[2] got execution token (length {len(execution['value'])})")

# Build the absolute action URL (form action is just 'login')
cas_post_url = r.url  # CAS expects the POST to the same URL we GETed (preserves ?service=...)

# 3. POST credentials
post_data = {
    "username": USER,
    "password": PASS,
    "execution": execution["value"],
    "_eventId": "submit",
    "geolocation": "",
    "submit": "",
}
print(f"[3] POSTing credentials to CAS  (user={USER!r}, password=<hidden>)")
r2 = s.post(cas_post_url, data=post_data, timeout=20, allow_redirects=True)
print(f"    final url: {r2.url}")
print(f"    status: {r2.status_code}")
for h in r2.history:
    print(f"    history: {h.status_code}  {h.url[:120]}")
print(f"    cookies: {sorted({c.name + '@' + c.domain for c in s.cookies})}")

# Diagnose
if "sso.uoa.gr/login" in r2.url:
    # CAS kept us — credentials likely wrong or MFA challenge served
    print("\nLOGIN FAILED: still on CAS server. Possible causes:")
    soup2 = BeautifulSoup(r2.text, "html.parser")
    title2 = soup2.title.string.strip() if soup2.title else "(none)"
    print(f"  CAS page title: {title2!r}")
    # Look for error / MFA hints
    err_div = soup2.find(class_=lambda c: c and ("error" in c.lower() or "alert" in c.lower()))
    if err_div:
        print(f"  error msg: {' '.join(err_div.get_text().split())[:300]}")
    (OUT / "cas_failure.html").write_text(r2.text, encoding="utf-8")
    print(f"  full CAS response saved -> {HERE / 'cas_failure.html'}")
    sys.exit(1)

# 4. We should now be logged in at eClass — confirm by fetching portfolio.php
p = s.get(PORTFOLIO, timeout=20)
print(f"\n[4] portfolio.php status {p.status_code}  url {p.url}")
if "login_form.php" in p.url:
    print("LOGIN FAILED: portfolio.php bounced to login_form.php (no session)", file=sys.stderr)
    (OUT / "portfolio_bounce.html").write_text(p.text, encoding="utf-8")
    sys.exit(1)

(OUT / "portfolio_authed.html").write_text(p.text, encoding="utf-8")
print(f"    saved portfolio HTML -> {HERE / 'portfolio_authed.html'} ({len(p.text)} bytes)")
soup = BeautifulSoup(p.text, "html.parser")
print(f"    title: {soup.title.string.strip() if soup.title else '(none)'}")

# Quick capability summary
links = [(a["href"], " ".join(a.get_text().split())[:80]) for a in soup.find_all("a", href=True)]
print(f"\n    {len(links)} links on authed portfolio")
# Group by first path segment
buckets: dict[str, int] = {}
for href, _ in links:
    if href.startswith("/"):
        k = "/" + href.lstrip("/").split("/")[0].split("?")[0]
    elif href.startswith("http"):
        k = "(external)"
    else:
        k = "(other)"
    buckets[k] = buckets.get(k, 0) + 1
for k in sorted(buckets, key=lambda x: -buckets[x]):
    print(f"      {buckets[k]:4}  {k}")

# Course-shaped links
course_links = [(h, t) for h, t in links if "/courses/" in h or "course_code=" in h]
print(f"\n    course-shaped links: {len(course_links)}")
for h, t in course_links[:25]:
    print(f"      {h}  ->  {t}")

# Log out politely
s.get(LOGOUT, timeout=20)
print("\n[5] logged out.")
