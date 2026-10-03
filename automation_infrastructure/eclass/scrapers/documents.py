"""Read and write the eClass 'document' (Έγγραφα) module: list, mkdir, upload.

The module lives at ``/modules/document/index.php?course=<CODE>`` (Open eClass
4.4, recon October 2026 on ECON875). Every folder and file has an
**eClass-internal path** made of random names (``/652fc0d2jNsb/68a1b2c3XyZw.pdf``);
the names people see are stored separately. So a path such as
``lecture_01/reading_material/x.ipynb`` must be resolved one folder at a time by
listing each folder and matching the visible name.

Endpoints (teacher account):

- **list a folder**: ``GET index.php?course=<C>&openDir=<internal dir path>``
  (``/`` is the root). Each row of ``table.table-default`` carries a checkbox with
  ``filepath`` (internal path) and ``isdir``; a hidden row has class
  ``not_visible``. A file's real filename is the last segment of its
  ``file.php/<C>/...`` link — the link *text* may be a title instead.
- **create a folder**: ``POST index.php?course=<C>`` with ``newDirPath`` (internal
  path of the parent, ``''`` for the root), ``newDirName`` and ``token``. Created
  visible. Responds with a redirect; the new folder's internal path is only
  learned by listing the parent again.
- **upload a file**: ``POST index.php?course=<C>`` as ``multipart/form-data`` with
  ``userFile`` plus ``uploadPath`` (internal dir path), ``replace`` (``1`` replaces
  a same-named file in that folder), ``uncompress``, ``file_creator``,
  ``file_copyrighted``, ``token`` and ``XHRUpload`` — the fields the page's Uppy
  widget sends. With ``XHRUpload`` the server answers ``200`` on success or
  ``400`` with the reason parked in the session; the next page view renders it as
  an ``alert-danger``. Uploaded files are visible immediately.

``token`` is the per-session CSRF token from any page of the module. File types
are checked against the platform's upload whitelist (a rejected type is a 400).

This module is import-safe: the functions return data or raise and never print.
Run ``upload_documents`` (the sibling CLI) to drive it end-to-end.
"""

from __future__ import annotations

import mimetypes
from dataclasses import dataclass
from urllib.parse import unquote, urlparse

import requests
from bs4 import BeautifulSoup

from ..session import BASE

MODULE_URL = f"{BASE}/modules/document/index.php"


class DocumentError(RuntimeError):
    """eClass refused a document-module action (upload, mkdir)."""


@dataclass
class Entry:
    """One row of a document-module folder listing."""

    name: str           # filename (files) or folder name (folders) as stored by eClass
    path: str           # eClass-internal path, e.g. /652fc0d2jNsb/68a1b2c3XyZw.pdf
    is_dir: bool
    visible: bool       # False when eClass shows the row as hidden from students
    size_text: str      # human size as listed ("6.92 KB"); '' for folders
    date_text: str      # human date as listed ("18/10/23, 2:25 μ.μ.")


@dataclass
class Listing:
    """A folder's contents plus the CSRF token of the page it came from."""

    entries: list[Entry]
    token: str

    def find(self, name: str, *, is_dir: bool) -> Entry | None:
        """The entry with this exact name and kind, or None."""
        return next((e for e in self.entries if e.name == name and e.is_dir == is_dir), None)


def list_dir(session: requests.Session, course: str, dir_path: str = "") -> Listing:
    """List one folder, given its eClass-internal path (``''`` = the root)."""
    r = session.get(MODULE_URL, params={"course": course, "openDir": dir_path or "/"}, timeout=30)
    r.raise_for_status()
    return parse_listing(r.text)


def parse_listing(html: str) -> Listing:
    """Parse a folder page into a :class:`Listing` (split out for offline tests)."""
    soup = BeautifulSoup(html, "html.parser")
    token_input = soup.find("input", {"name": "token"})
    if token_input is None or not token_input.get("value"):
        raise DocumentError("CSRF token not found — not a teacher view of the document module?")

    entries: list[Entry] = []
    for row in soup.select("table.table-default tr"):
        checkbox = row.find("input", attrs={"filepath": True})
        if checkbox is None:
            continue  # header row
        is_dir = checkbox.get("isdir") == "1"
        if is_dir:
            link = row.find("a", class_="fileURL-link")
            name = " ".join(link.get_text().split()) if link else ""
        else:
            link = row.find("a", class_="fileURL")
            href = link.get("href", "") if link else ""
            name = unquote(urlparse(href).path.rsplit("/", 1)[-1]) if href else ""
        cells = row.find_all("td")
        entries.append(Entry(
            name=name,
            path=checkbox["filepath"],
            is_dir=is_dir,
            visible="not_visible" not in (row.get("class") or []),
            size_text=" ".join(cells[2].get_text().split()) if len(cells) > 2 else "",
            date_text=" ".join(cells[3].get_text().split()) if len(cells) > 3 else "",
        ))
    return Listing(entries=entries, token=token_input["value"])


def pending_errors(session: requests.Session, course: str) -> list[str]:
    """Pop the error messages eClass parked in the session after a failed upload.

    The server renders (and then clears) them on the next view of the module.
    """
    r = session.get(MODULE_URL, params={"course": course}, timeout=30)
    soup = BeautifulSoup(r.text, "html.parser")
    return [" ".join(div.get_text().split()) for div in soup.select("div.alert-danger")]


def create_dir(session: requests.Session, course: str, parent_path: str, name: str,
               token: str) -> Entry:
    """Create folder ``name`` inside ``parent_path`` and return its listing entry.

    eClass treats an existing name as success-with-warning, so this is safe to call
    for a folder that already exists: the existing entry is returned.
    """
    if "/" in name:
        raise ValueError(f"folder name must be a single component: {name!r}")
    r = session.post(
        MODULE_URL,
        params={"course": course},
        data={"newDirPath": parent_path, "newDirName": name, "token": token},
        timeout=30,
    )
    r.raise_for_status()
    created = list_dir(session, course, parent_path).find(name, is_dir=True)
    if created is None:
        raise DocumentError(f"folder {name!r} not found in {parent_path or '/'} after creating it")
    return created


def upload_file(session: requests.Session, course: str, dir_path: str, filename: str,
                content: bytes, token: str, *, replace: bool, creator: str = "") -> None:
    """Upload ``content`` as ``filename`` into the folder at ``dir_path``.

    ``replace=True`` overwrites a same-named file in that folder; without it a
    clash is an error. Raises :class:`DocumentError` with eClass's own message
    when the server refuses (file type not whitelisted, quota, clash).
    """
    mime = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    r = session.post(
        MODULE_URL,
        params={"course": course},
        data={
            "uploadPath": dir_path,
            "file_creator": creator,
            "file_copyrighted": "0",
            "replace": "1" if replace else "0",
            "uncompress": "0",
            "token": token,
            "XHRUpload": "true",
        },
        files={"userFile": (filename, content, mime)},
        timeout=300,
    )
    if r.status_code == 200:
        return
    messages = pending_errors(session, course) if r.status_code == 400 else []
    detail = "; ".join(messages) or r.text.strip()[:200] or "no message"
    raise DocumentError(f"HTTP {r.status_code}: {detail}")
