"""Core contact management module.

Provides the ContactManager class which handles all contact operations:
CRUD, validation, search, filtering, sorting, favorites, pagination, and
JSON/CSV import/export.
"""

from __future__ import annotations

import csv
import json
import os
import re
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Callable, Iterable


EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^\+?[0-9\s\-()]{7,20}$")


class ValidationError(ValueError):
    """Raised when contact field validation fails."""


class ContactNotFound(LookupError):
    """Raised when a contact cannot be located by ID or name."""


@dataclass
class Contact:
    name: str
    phone: str
    email: str
    city: str
    company: str
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    favorite: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Contact":
        allowed = {f for f in cls.__dataclass_fields__}
        clean = {k: v for k, v in data.items() if k in allowed}
        return cls(**clean)


def validate_fields(name: str, phone: str, email: str, city: str, company: str) -> None:
    if not name or not name.strip():
        raise ValidationError("Name cannot be empty.")
    if not city or not city.strip():
        raise ValidationError("City cannot be empty.")
    if not company or not company.strip():
        raise ValidationError("Company cannot be empty.")
    if not PHONE_RE.match(phone or ""):
        raise ValidationError(
            "Invalid phone number. Use 7-20 digits, optional +, spaces, dashes, or parens."
        )
    if not EMAIL_RE.match(email or ""):
        raise ValidationError("Invalid email address.")


class ContactManager:
    def __init__(self, storage_path: str = "contacts.json") -> None:
        self.storage_path = storage_path
        self.contacts: list[Contact] = []
        self.load()

    # ---------------- Persistence ----------------
    def load(self) -> None:
        if not os.path.exists(self.storage_path):
            self.contacts = []
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            self.contacts = [Contact.from_dict(item) for item in raw]
        except (json.JSONDecodeError, OSError) as exc:
            raise RuntimeError(f"Failed to load {self.storage_path}: {exc}") from exc

    def save(self) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.contacts], f, indent=2, ensure_ascii=False)

    # ---------------- CRUD ----------------
    def add_contact(self, name: str, phone: str, email: str, city: str, company: str) -> Contact:
        validate_fields(name, phone, email, city, company)
        contact = Contact(
            name=name.strip(),
            phone=phone.strip(),
            email=email.strip(),
            city=city.strip(),
            company=company.strip(),
        )
        self.contacts.append(contact)
        self.save()
        return contact

    def get_by_id(self, contact_id: str) -> Contact:
        for c in self.contacts:
            if c.id == contact_id:
                return c
        raise ContactNotFound(f"No contact with ID '{contact_id}'.")

    def find_by_name(self, name: str) -> list[Contact]:
        target = name.strip().lower()
        return [c for c in self.contacts if c.name.lower() == target]

    def update_contact(self, contact_id: str, **fields) -> Contact:
        contact = self.get_by_id(contact_id)
        merged = {
            "name": fields.get("name", contact.name),
            "phone": fields.get("phone", contact.phone),
            "email": fields.get("email", contact.email),
            "city": fields.get("city", contact.city),
            "company": fields.get("company", contact.company),
        }
        validate_fields(**merged)
        for k, v in merged.items():
            setattr(contact, k, v.strip())
        if "favorite" in fields:
            contact.favorite = bool(fields["favorite"])
        self.save()
        return contact

    def delete_by_id(self, contact_id: str) -> Contact:
        contact = self.get_by_id(contact_id)
        self.contacts.remove(contact)
        self.save()
        return contact

    def delete_by_name(self, name: str) -> list[Contact]:
        matches = self.find_by_name(name)
        if not matches:
            raise ContactNotFound(f"No contact named '{name}'.")
        for c in matches:
            self.contacts.remove(c)
        self.save()
        return matches

    def toggle_favorite(self, contact_id: str) -> Contact:
        contact = self.get_by_id(contact_id)
        contact.favorite = not contact.favorite
        self.save()
        return contact

    # ---------------- Search & Filter ----------------
    def search(self, query: str, fields: Iterable[str] = ("name", "phone", "email")) -> list[Contact]:
        q = query.strip().lower()
        if not q:
            return []
        return [
            c for c in self.contacts
            if any(q in str(getattr(c, f, "")).lower() for f in fields)
        ]

    def filter_by(self, *, city: str | None = None, company: str | None = None,
                  favorites_only: bool = False) -> list[Contact]:
        results = list(self.contacts)
        if city:
            city_l = city.strip().lower()
            results = [c for c in results if c.city.lower() == city_l]
        if company:
            comp_l = company.strip().lower()
            results = [c for c in results if c.company.lower() == comp_l]
        if favorites_only:
            results = [c for c in results if c.favorite]
        return results

    # ---------------- Sorting & Pagination ----------------
    @staticmethod
    def sort_contacts(contacts: list[Contact], key: str = "name") -> list[Contact]:
        sorters: dict[str, Callable[[Contact], object]] = {
            "name": lambda c: c.name.lower(),
            "recent": lambda c: c.created_at,
            "city": lambda c: c.city.lower(),
            "company": lambda c: c.company.lower(),
        }
        if key not in sorters:
            raise ValueError(f"Unknown sort key '{key}'. Use one of: {list(sorters)}")
        reverse = key == "recent"
        return sorted(contacts, key=sorters[key], reverse=reverse)

    @staticmethod
    def paginate(contacts: list[Contact], page: int = 1, page_size: int = 10) -> list[Contact]:
        if page < 1 or page_size < 1:
            raise ValueError("Page and page_size must be >= 1.")
        start = (page - 1) * page_size
        return contacts[start:start + page_size]

    # ---------------- Import / Export ----------------
    def export_csv(self, path: str) -> int:
        fieldnames = ["id", "name", "phone", "email", "city", "company", "favorite", "created_at"]
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in self.contacts:
                writer.writerow(c.to_dict())
        return len(self.contacts)

    _HEADER_ALIASES = {
        "full name": "name", "name": "name",
        "phone number": "phone", "phone": "phone", "mobile": "phone",
        "email address": "email", "email": "email", "e-mail": "email",
        "city": "city",
        "company": "company", "organization": "company", "organisation": "company",
        "id": "id", "favorite": "favorite", "starred": "favorite",
        "created_at": "created_at", "created at": "created_at",
    }

    def import_csv(self, path: str) -> int:
        if not os.path.exists(path):
            raise FileNotFoundError(path)
        added = 0
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for raw in reader:
                row = {}
                for key, value in raw.items():
                    if key is None:
                        continue
                    canonical = self._HEADER_ALIASES.get(key.strip().lower(), key.strip().lower())
                    row[canonical] = (value or "").strip()
                try:
                    validate_fields(row.get("name", ""), row.get("phone", ""),
                                    row.get("email", ""), row.get("city", ""),
                                    row.get("company", ""))
                except ValidationError:
                    continue
                row["favorite"] = str(row.get("favorite", "")).lower() in {"true", "1", "yes"}
                self.contacts.append(Contact.from_dict(row))
                added += 1
        if added:
            self.save()
        return added
