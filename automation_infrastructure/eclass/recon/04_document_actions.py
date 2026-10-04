"""Recon step 4: how the document module deletes a file (read-only).

Logs in once, walks a course's Έγγραφα to the folder that holds one file (by
visible path), saves that folder's page, and prints the file's table row and
every form on the page, so the delete request can be read off the HTML. Only
GET requests: nothing on eClass changes.

    python -m automation_infrastructure.eclass.recon.04_document_actions ECON875 \
        lecture_01_ollama_models_prompts_langchain/reading_material/x.ipynb
"""

from __future__ import annotations

import sys
from pathlib import Path

from bs4 import BeautifulSoup
from dotenv import load_dotenv

from automation_infrastructure.eclass.scrapers.documents import MODULE_URL, list_dir
from automation_infrastructure.eclass.session import login, logout

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "admin_docs" / "eclass_recon"  # snapshots may contain PII — stays gitignored


def main(course: str, visible_path: str) -> None:
    load_dotenv(ROOT / ".env")
    OUT.mkdir(parents=True, exist_ok=True)
    session = login(next_path=f"/modules/document/index.php?course={course}")
    try:
        *folders, filename = visible_path.split("/")
        internal = ""
        for name in folders:
            entry = list_dir(session, course, internal).find(name, is_dir=True)
            if entry is None:
                sys.exit(f"folder {name!r} not found")
            internal = entry.path
        r = session.get(MODULE_URL, params={"course": course, "openDir": internal or "/"},
                        timeout=30)
    finally:
        logout(session)

    snapshot = OUT / f"documents_{course}_folder.html"
    snapshot.write_text(r.text, encoding="utf-8")
    print(f"saved {snapshot}\n")

    soup = BeautifulSoup(r.text, "html.parser")
    for row in soup.select("table.table-default tr"):
        if filename in str(row):
            print("── target row ──")
            print(row.prettify())
    for form in soup.find_all("form"):
        print("── form ──", form.get("action"), form.get("method"), form.get("id"))
        for field in form.find_all(["input", "button", "select"]):
            print("   ", field.name, field.get("type"), field.get("name"), field.get("value"))
    for script in soup.find_all("script"):
        text = script.get_text()
        if "delete" in text.lower():
            print("── script mentioning delete ──")
            print(text[:3000])


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
