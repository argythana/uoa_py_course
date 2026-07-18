"""Recon step 3: log in, fetch ECON537 course home, enumerate enabled modules.

Open eClass exposes each course's enabled "tools" (announcements, documents,
assignments, gradebook, etc.) as links in the left sidebar of the course
index page. Mapping these tells us which areas of the course are candidates
for automation.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

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

BASE = "https://eclass.uoa.gr"
COURSE_CODE = "ECON537"
COURSE_URL = f"{BASE}/courses/{COURSE_CODE}/"
LOGOUT = f"{BASE}/index.php?logout=yes"


def cas_login(s: requests.Session, next_path: str = "/main/portfolio.php") -> None:
    entry = f"{BASE}/modules/auth/cas.php?next={requests.utils.quote(next_path, safe='')}"
    r = s.get(entry, timeout=20, allow_redirects=True)
    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form", action=lambda a: a and "login" in a.lower())
    execution = form.find("input", {"name": "execution"})["value"]
    r = s.post(
        r.url,
        data={
            "username": USER, "password": PASS,
            "execution": execution, "_eventId": "submit",
            "geolocation": "", "submit": "",
        },
        timeout=20, allow_redirects=True,
    )
    if "sso.uoa.gr/login" in r.url:
        print("LOGIN FAILED", file=sys.stderr)
        sys.exit(1)


s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0 (uoa-py-course eclass recon)"
cas_login(s, f"/courses/{COURSE_CODE}/")

# Fetch course home
r = s.get(COURSE_URL, timeout=20)
print(f"course home: {r.status_code}  {r.url}")
(OUT / f"{COURSE_CODE}_home.html").write_text(r.text, encoding="utf-8")
print(f"saved -> {OUT / (COURSE_CODE + '_home.html')} ({len(r.text)} bytes)")

soup = BeautifulSoup(r.text, "html.parser")
print(f"title: {soup.title.string.strip() if soup.title else '(none)'}")

# Open eClass module URLs look like /modules/<modname>/<modname>.php?course=ECON537
# Enumerate distinct module slugs reachable from the course home
module_links: dict[str, list[tuple[str, str]]] = {}
for a in soup.find_all("a", href=True):
    href = a["href"]
    text = " ".join(a.get_text().split())[:80]
    m = re.search(r"/modules/([^/?]+)/", href)
    if m:
        slug = m.group(1)
        # only links scoped to THIS course (course= param or path /courses/CODE/)
        qs = parse_qs(urlparse(href).query)
        scoped = (qs.get("course", [None])[0] == COURSE_CODE) or (f"/courses/{COURSE_CODE}/" in href)
        if scoped or "course" not in qs:  # be lenient — some modules don't pass ?course
            module_links.setdefault(slug, []).append((href, text))

print(f"\nenabled-looking modules: {len(module_links)}")
for slug in sorted(module_links):
    entries = module_links[slug]
    # pick the representative link (first one with a non-empty text)
    rep = next((e for e in entries if e[1]), entries[0])
    print(f"  {slug:20}  {len(entries):2}x  e.g. {rep[1][:60]!r}  ->  {rep[0][:90]}")

# Also dump any "course tools" sidebar by common Open eClass class names
print("\nlooking for course tools sidebar...")
for selector in [
    ("div", {"id": "tools_list"}),
    ("ul", {"class": "course-tools"}),
    ("div", {"class": "course_units"}),
    ("nav", {"id": "leftmenu"}),
]:
    el = soup.find(*selector[:1], **{k: v for k, v in [list(selector[1].items())[0]]}) if selector[1] else None
    if el:
        print(f"  found {selector}: contains {len(el.find_all('a'))} links")

# Logout
s.get(LOGOUT, timeout=20)
print("\nlogged out.")
