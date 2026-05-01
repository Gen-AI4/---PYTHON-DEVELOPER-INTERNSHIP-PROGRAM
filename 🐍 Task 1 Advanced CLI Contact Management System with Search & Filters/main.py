"""Interactive CLI for the Contact Management System."""

from __future__ import annotations

import sys
from typing import Iterable

from contact_manager import (
    Contact,
    ContactManager,
    ContactNotFound,
    ValidationError,
)


PAGE_SIZE = 10


# ---------------- Display helpers ----------------

def _truncate(text: str, width: int) -> str:
    text = str(text)
    return text if len(text) <= width else text[: width - 1] + "…"


def render_table(contacts: Iterable[Contact]) -> None:
    rows = list(contacts)
    if not rows:
        print("\n(no contacts to display)\n")
        return

    header = ("ID", "★", "Name", "Phone", "Email", "City", "Company")
    widths = (8, 1, 22, 18, 28, 14, 18)

    line = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(line)
    print("| " + " | ".join(h.ljust(w) for h, w in zip(header, widths)) + " |")
    print(line)
    for c in rows:
        cells = (
            c.id, "★" if c.favorite else " ", c.name, c.phone, c.email, c.city, c.company,
        )
        print("| " + " | ".join(_truncate(v, w).ljust(w) for v, w in zip(cells, widths)) + " |")
    print(line)
    print(f"Total: {len(rows)} contact(s)\n")


def paginated_display(contacts: list[Contact]) -> None:
    if not contacts:
        render_table(contacts)
        return
    total_pages = (len(contacts) + PAGE_SIZE - 1) // PAGE_SIZE
    page = 1
    while True:
        page_items = ContactManager.paginate(contacts, page=page, page_size=PAGE_SIZE)
        print(f"\n--- Page {page} of {total_pages} ---")
        render_table(page_items)
        if total_pages <= 1:
            return
        choice = input("Enter [n]ext, [p]rev, or [q]uit pagination: ").strip().lower()
        if choice == "n" and page < total_pages:
            page += 1
        elif choice == "p" and page > 1:
            page -= 1
        elif choice == "q" or choice == "":
            return


# ---------------- Input helpers ----------------

def prompt(label: str, *, allow_blank: bool = False, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{label}{suffix}: ").strip()
        if not value and default is not None:
            return default
        if value or allow_blank:
            return value
        print("Value cannot be empty.")


# ---------------- Menu actions ----------------

def action_add(mgr: ContactManager) -> None:
    print("\n-- Add New Contact --")
    try:
        contact = mgr.add_contact(
            name=prompt("Full Name"),
            phone=prompt("Phone Number"),
            email=prompt("Email Address"),
            city=prompt("City"),
            company=prompt("Company"),
        )
    except ValidationError as exc:
        print(f"❌ {exc}")
        return
    print(f"✅ Added contact '{contact.name}' (ID: {contact.id}).")


def action_view(mgr: ContactManager) -> None:
    print("\n-- All Contacts --")
    if not mgr.contacts:
        print("(no contacts saved yet)")
        return
    print("Sort by: 1) Name A–Z  2) Recently Added  3) City  4) Company  [Enter=Name]")
    choice = input("Choice: ").strip()
    key = {"1": "name", "2": "recent", "3": "city", "4": "company", "": "name"}.get(choice, "name")
    paginated_display(ContactManager.sort_contacts(mgr.contacts, key=key))


def action_search(mgr: ContactManager) -> None:
    print("\n-- Search Contacts --")
    print("Search by: 1) Name  2) Phone  3) Email  4) Any field")
    choice = input("Choice: ").strip()
    field_map = {
        "1": ("name",), "2": ("phone",), "3": ("email",),
        "4": ("name", "phone", "email"),
    }
    fields = field_map.get(choice)
    if not fields:
        print("Invalid choice.")
        return
    query = prompt("Query")
    results = mgr.search(query, fields=fields)
    render_table(results)


def action_filter(mgr: ContactManager) -> None:
    print("\n-- Filter Contacts --")
    print("Filter by: 1) City  2) Company  3) Favorites only")
    choice = input("Choice: ").strip()
    if choice == "1":
        results = mgr.filter_by(city=prompt("City"))
    elif choice == "2":
        results = mgr.filter_by(company=prompt("Company"))
    elif choice == "3":
        results = mgr.filter_by(favorites_only=True)
    else:
        print("Invalid choice.")
        return
    render_table(results)


def action_update(mgr: ContactManager) -> None:
    print("\n-- Update Contact --")
    contact_id = prompt("Contact ID")
    try:
        contact = mgr.get_by_id(contact_id)
    except ContactNotFound as exc:
        print(f"❌ {exc}")
        return
    print("Press Enter to keep the current value.")
    updates = {
        "name": prompt("Full Name", allow_blank=True, default=contact.name),
        "phone": prompt("Phone Number", allow_blank=True, default=contact.phone),
        "email": prompt("Email Address", allow_blank=True, default=contact.email),
        "city": prompt("City", allow_blank=True, default=contact.city),
        "company": prompt("Company", allow_blank=True, default=contact.company),
    }
    try:
        updated = mgr.update_contact(contact_id, **updates)
    except ValidationError as exc:
        print(f"❌ {exc}")
        return
    print(f"✅ Updated contact '{updated.name}'.")


def action_delete(mgr: ContactManager) -> None:
    print("\n-- Delete Contact --")
    print("Delete by: 1) ID  2) Name")
    choice = input("Choice: ").strip()
    try:
        if choice == "1":
            removed = mgr.delete_by_id(prompt("Contact ID"))
            print(f"✅ Removed '{removed.name}'.")
        elif choice == "2":
            removed = mgr.delete_by_name(prompt("Full Name (exact match)"))
            print(f"✅ Removed {len(removed)} contact(s).")
        else:
            print("Invalid choice.")
    except ContactNotFound as exc:
        print(f"❌ {exc}")


def action_favorite(mgr: ContactManager) -> None:
    print("\n-- Toggle Favorite --")
    try:
        contact = mgr.toggle_favorite(prompt("Contact ID"))
    except ContactNotFound as exc:
        print(f"❌ {exc}")
        return
    state = "starred ★" if contact.favorite else "unstarred"
    print(f"✅ '{contact.name}' is now {state}.")


def action_export(mgr: ContactManager) -> None:
    path = prompt("Export CSV path", default="contacts_export.csv")
    try:
        count = mgr.export_csv(path)
    except OSError as exc:
        print(f"❌ Could not write file: {exc}")
        return
    print(f"✅ Exported {count} contact(s) to {path}.")


def action_import(mgr: ContactManager) -> None:
    path = prompt("Import CSV path")
    try:
        count = mgr.import_csv(path)
    except (FileNotFoundError, OSError) as exc:
        print(f"❌ {exc}")
        return
    print(f"✅ Imported {count} contact(s) from {path}.")


# ---------------- Main loop ----------------

MENU = """
==============================================
   📇 Advanced Contact Management System
==============================================
 1. Add Contact
 2. View All Contacts
 3. Search Contacts
 4. Filter Contacts
 5. Update Contact
 6. Delete Contact
 7. Toggle Favorite ★
 8. Export to CSV
 9. Import from CSV
 0. Exit
----------------------------------------------"""


ACTIONS = {
    "1": action_add,
    "2": action_view,
    "3": action_search,
    "4": action_filter,
    "5": action_update,
    "6": action_delete,
    "7": action_favorite,
    "8": action_export,
    "9": action_import,
}


def main() -> int:
    try:
        mgr = ContactManager(storage_path="contacts.json")
    except RuntimeError as exc:
        print(f"❌ Startup error: {exc}")
        return 1

    print(f"Loaded {len(mgr.contacts)} contact(s) from contacts.json")

    while True:
        print(MENU)
        choice = input("Select an option: ").strip()
        if choice == "0":
            print("Goodbye! 👋")
            return 0
        action = ACTIONS.get(choice)
        if not action:
            print("❌ Invalid option. Please try again.")
            continue
        try:
            action(mgr)
        except KeyboardInterrupt:
            print("\n(cancelled)")
        except Exception as exc:  # last-resort safety net
            print(f"❌ Unexpected error: {exc}")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted. Goodbye!")
        sys.exit(0)
