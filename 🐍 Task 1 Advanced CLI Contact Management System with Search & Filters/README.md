# 📇 Advanced CLI Contact Management System

A professional, menu-driven Command-Line Contact Management System written in
pure Python. It simulates a mini-CRM where you can store, search, filter, and
manage contacts with persistent JSON storage and CSV import/export.

---

## 🎯 Objective

Build an interactive, modular CLI application to manage contacts — add, view,
search, filter, update, delete — and persist them to disk.

---

## ✨ Features

### Core
- ✅ **Add Contact** with full input validation (no empty fields, valid email/phone)
- ✅ **View All Contacts** in a formatted table
- ✅ **Search** by Name / Phone / Email / Any field (partial, case-insensitive)
- ✅ **Filter** by City, Company, or Favorites
- ✅ **Update Contact** — edit any field, keep others by pressing Enter
- ✅ **Delete Contact** by ID or by Name
- ✅ **Persistent Storage** — auto-saves to `contacts.json` and reloads on start
- ✅ **Unique IDs** auto-generated for every contact
- ✅ **Exception handling** for all I/O and user errors
- ✅ **Modular design** — `contact_manager.py` (logic) + `main.py` (CLI)

### Bonus
- ⭐ **Favorite / Starred Contacts**
- 📤 **Export to CSV**
- 📥 **Import from CSV**
- 📄 **Pagination** (10 per page) for large lists
- 🔤 **Sorting** — A–Z, Recently Added, City, or Company

---

## 🗂 Contact Fields

| Field    | Validation                                 |
|----------|--------------------------------------------|
| Name     | Non-empty                                  |
| Phone    | 7–20 digits, optional `+`, spaces, dashes, parens |
| Email    | Standard email format                      |
| City     | Non-empty                                  |
| Company  | Non-empty                                  |

Each contact also carries: `id`, `favorite`, `created_at`.

---

## 📁 Project Structure

```
.
├── main.py              # Interactive menu-driven CLI
├── contact_manager.py   # Core ContactManager class + Contact dataclass
├── contacts.json        # Sample data (auto-loaded on startup)
└── README.md
```

---

## 🚀 How to Run

**Requirements:** Python 3.10+ (uses `from __future__` annotations and PEP 604 unions). No third-party dependencies.

```bash
python3 main.py
```

You'll see the main menu:

```
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
```

The included `contacts.json` ships with 6 sample records so you can try every
feature immediately.

---

## 🧪 Quick Walkthrough

1. **View** all contacts → option `2`, then choose a sort order.
2. **Search** for "aisha" → option `3` → `1` (Name) → returns Aisha Khan.
3. **Filter** by city "Karachi" → option `4` → `1` → returns Aisha Khan & Hamza Raza.
4. **Star** Bilal as favorite → option `7` → enter ID `e5f6a7b8`.
5. **Export** → option `8` → writes `contacts_export.csv`.

---

## 🛡 Validation & Error Handling

- Empty fields, malformed emails, and bad phone numbers are rejected with a
  clear message — your data file is never corrupted.
- File I/O errors (missing CSV, unreadable JSON) are caught and reported.
- Unknown contact IDs raise a friendly "not found" message.
- `Ctrl+C` exits cleanly.

---

## 💾 Data Persistence

- All changes are written to `contacts.json` immediately after each
  add / update / delete / favorite-toggle.
- On startup, contacts are loaded automatically from the same file.
- CSV import skips invalid rows so partial imports never corrupt your data.

---

## 📦 Deliverables Checklist

- ✅ Source code (`main.py`, `contact_manager.py`)
- ✅ Sample data file (`contacts.json`)
- ✅ README with features + run instructions
- ✅ Modular structure, exception handling, validation, unique IDs
- ✅ Bonus: favorites, CSV import/export, pagination, sorting
