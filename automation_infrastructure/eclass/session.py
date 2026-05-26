"""Reusable CAS-authenticated session for UoA eClass.

Usage:
    from eclass_session import login
    s = login(next_path="/courses/ECON537/")
    r = s.get("https://eclass.uoa.gr/...")
    ...
    s.get("https://eclass.uoa.gr/index.php?logout=yes")

Single-attempt semantics: if CAS rejects the credentials, the function exits
with a non-zero status rather than retrying. Repeated bad-password POSTs
against sso.uoa.gr can lock the account.

Credentials come from environment variables ECLASS_USERNAME and ECLASS_PASSWORD
(loaded from the repo-root .env by the caller — this module does not load .env
itself, to keep the dependency surface small).
"""

from __future__ import annotations

import os
import sys
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

BASE = "https://eclass.uoa.gr"
SSO_HOST = "sso.uoa.gr"
DEFAULT_UA = "Mozilla/5.0 (eclass mirror; argythana@gmail.com)"


class LoginError(RuntimeError):
    pass


def login(next_path: str = "/main/portfolio.php", *, user_agent: str = DEFAULT_UA) -> requests.Session:
    """Perform a CAS login and return an authenticated requests.Session.

    Raises LoginError if credentials are rejected. Caller is responsible for
    calling session.get(f"{BASE}/index.php?logout=yes") when done.
    """
    user = os.environ.get("ECLASS_USERNAME")
    password = os.environ.get("ECLASS_PASSWORD")
    if not user or not password:
        raise LoginError("ECLASS_USERNAME / ECLASS_PASSWORD not set in environment")

    s = requests.Session()
    s.headers["User-Agent"] = user_agent

    entry = f"{BASE}/modules/auth/cas.php?next={quote(next_path, safe='')}"
    r = s.get(entry, timeout=20, allow_redirects=True)
    if SSO_HOST not in r.url:
        # Already logged in somehow (unlikely on a fresh session), or eClass
        # didn't bounce us to CAS. Either way, return the session as-is.
        return s

    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form", action=lambda a: a and "login" in a.lower())
    if form is None:
        raise LoginError("CAS login form not found on SSO page")
    execution = form.find("input", {"name": "execution"})
    if execution is None or not execution.get("value"):
        raise LoginError("CAS execution token missing on SSO page")

    r = s.post(
        r.url,
        data={
            "username": user,
            "password": password,
            "execution": execution["value"],
            "_eventId": "submit",
            "geolocation": "",
            "submit": "",
        },
        timeout=20,
        allow_redirects=True,
    )
    if SSO_HOST in r.url:
        # Still on CAS → credentials rejected. Do NOT retry.
        raise LoginError(
            "CAS rejected credentials (still on sso.uoa.gr after POST). "
            "Check ECLASS_USERNAME / ECLASS_PASSWORD. Do not retry blindly — "
            "repeated failures can lock the account."
        )
    return s


def logout(session: requests.Session) -> None:
    """Best-effort polite logout. Never raises."""
    try:
        session.get(f"{BASE}/index.php?logout=yes", timeout=10)
    except requests.RequestException:
        pass


if __name__ == "__main__":
    # Smoke test: load .env, log in, verify portfolio.php is reachable, log out.
    from pathlib import Path
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parents[2] / ".env")
    try:
        s = login()
    except LoginError as e:
        print(f"login failed: {e}", file=sys.stderr)
        sys.exit(1)
    r = s.get(f"{BASE}/main/portfolio.php", timeout=20)
    ok = "login_form.php" not in r.url
    print(f"portfolio reachable: {ok}  ({r.status_code} {r.url})")
    logout(s)
    sys.exit(0 if ok else 1)
