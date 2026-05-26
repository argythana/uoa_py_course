"""Scrape the user roster of one eClass course.

The roster page (/modules/user/index.php?course=<CODE>) renders an empty table
shell and populates rows via DataTables AJAX against the *same* URL. Server-side
mode (`bServerSide=true`) — the request needs the standard DataTables payload
plus `X-Requested-With: XMLHttpRequest`. Response is legacy DataTables 1.9 JSON
(`aaData` key).

This module is import-safe: `fetch_users(session, course_code)` returns a list
of dicts and never prints. Run it as a script to dump the parsed roster.
"""

from __future__ import annotations

import re
import sys
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs, urlparse

import requests
from bs4 import BeautifulSoup

from ..session import BASE

# DataTables column index → semantic name (Open eClass v3 layout, May 2026).
# Verified against ECON537. If eClass changes the table, fix here.
_COL_NAME, _COL_ROLE, _COL_GROUP, _COL_REGDATE = "0", "1", "2", "3"


def _datatables_payload(length: int = 1000) -> dict[str, str]:
    """Minimal DataTables server-side payload that asks for `length` rows."""
    payload = {
        "draw": "1",
        "start": "0",
        "length": str(length),
        "search[value]": "",
        "search[regex]": "false",
        "order[0][column]": "0",
        "order[0][dir]": "asc",
    }
    for i in range(5):
        payload.update({
            f"columns[{i}][data]": str(i),
            f"columns[{i}][searchable]": "true",
            f"columns[{i}][orderable]": "true",
            f"columns[{i}][search][value]": "",
            f"columns[{i}][search][regex]": "false",
        })
    return payload


def _parse_iso_date(greek_date: str) -> str | None:
    """Convert 'DD/M/YY' (Greek eClass format) to ISO-8601 YYYY-MM-DD."""
    greek_date = greek_date.strip()
    if not greek_date:
        return None
    try:
        dt = datetime.strptime(greek_date, "%d/%m/%y")
    except ValueError:
        return None
    return dt.date().isoformat()


def _parse_row(row: dict[str, Any]) -> dict[str, Any] | None:
    """Extract one user dict from one DataTables row. Returns None if unparseable."""
    name_cell = row.get(_COL_NAME, "")
    soup = BeautifulSoup(name_cell, "html.parser")

    # user_id from the profile link: /main/profile/display_profile.php?id=NNNN
    profile_link = soup.find("a", href=lambda h: h and "display_profile.php" in h)
    if profile_link is None:
        return None
    qs = parse_qs(urlparse(profile_link["href"]).query)
    user_id_str = qs.get("id", [None])[0]
    if not user_id_str or not user_id_str.isdigit():
        return None
    user_id = int(user_id_str)

    full_name = " ".join(profile_link.get_text().split())

    # email from mailto: link (may be absent for users who hid their address)
    mailto = soup.find("a", href=lambda h: h and h.startswith("mailto:"))
    email = mailto["href"][len("mailto:"):] if mailto else None

    # The trailing token in the cell text is usually the academic number (AM).
    # It sits after the email; both are space-separated within the .text.
    cell_tokens = " ".join(soup.get_text().split()).split()
    am: str | None = None
    if cell_tokens:
        last = cell_tokens[-1]
        # AM at UoA is a long digit string. Filter on length + digits-only to
        # avoid mistaking a surname for an AM if the layout changes.
        if last.isdigit() and len(last) >= 8:
            am = last

    role = " ".join(BeautifulSoup(row.get(_COL_ROLE, ""), "html.parser").get_text().split())
    group = " ".join(BeautifulSoup(row.get(_COL_GROUP, ""), "html.parser").get_text().split())
    regdate_raw = " ".join(BeautifulSoup(row.get(_COL_REGDATE, ""), "html.parser").get_text().split())

    return {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "am": am,
        "role": role,
        "user_group": group,
        "registration_date": _parse_iso_date(regdate_raw),
    }


def fetch_users(session: requests.Session, course_code: str) -> list[dict[str, Any]]:
    """Return the full roster for `course_code` as a list of user dicts.

    Each dict has keys: user_id, full_name, email, am, role, user_group,
    registration_date, course_code, last_scraped_at.
    """
    url = f"{BASE}/modules/user/index.php?course={course_code}"
    r = session.post(
        url,
        data=_datatables_payload(),
        headers={"X-Requested-With": "XMLHttpRequest"},
        timeout=30,
    )
    r.raise_for_status()
    payload = r.json()
    rows = payload.get("aaData", [])
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")

    users: list[dict[str, Any]] = []
    for raw in rows:
        parsed = _parse_row(raw)
        if parsed is None:
            continue
        parsed["course_code"] = course_code
        parsed["last_scraped_at"] = now
        users.append(parsed)
    return users


if __name__ == "__main__":
    # CLI smoke-test: log in, fetch ECON537 roster, print row count + first 3.
    from pathlib import Path
    from dotenv import load_dotenv
    from ..session import login, logout, LoginError

    load_dotenv(Path(__file__).resolve().parents[3] / ".env")
    course = sys.argv[1] if len(sys.argv) > 1 else "ECON537"
    try:
        s = login(next_path=f"/modules/user/index.php?course={course}")
    except LoginError as e:
        print(f"login failed: {e}", file=sys.stderr)
        sys.exit(1)
    try:
        users = fetch_users(s, course)
    finally:
        logout(s)
    print(f"{course}: parsed {len(users)} users")
    for u in users[:3]:
        # Redact email/AM in the smoke-test output — PII, even in admin_docs.
        redacted = {**u, "email": "<redacted>" if u["email"] else None,
                    "am": "<redacted>" if u["am"] else None,
                    "full_name": u["full_name"].split()[0] + " <redacted>"}
        print(f"  {redacted}")
