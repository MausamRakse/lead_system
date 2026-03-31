def extract_email(person: dict) -> str:
    """Extract the best available email from an Apollo person dict."""
    # 1. Top-level email
    if person.get("email"):
        return person["email"]
    # 2. Top-level contact_emails array
    for ce in (person.get("contact_emails") or []):
        if ce.get("email"):
            return ce["email"]
    # 3. Nested contact object
    contact = person.get("contact") or {}
    if contact.get("email"):
        return contact["email"]
    # 4. contact.contact_emails array
    for ce in (contact.get("contact_emails") or []):
        if ce.get("email"):
            return ce["email"]
    return "Not available"


def extract_phone(person: dict) -> str:
    """Extract the best available phone number from an Apollo person dict."""
    # 1. Top-level phone_numbers array
    for pn in (person.get("phone_numbers") or []):
        number = pn.get("sanitized_number") or pn.get("raw_number") or ""
        if number:
            return number
    # 2. contact.phone_numbers array
    contact = person.get("contact") or {}
    for pn in (contact.get("phone_numbers") or []):
        number = pn.get("sanitized_number") or pn.get("raw_number") or ""
        if number:
            return number
    # 3. Organization fallback
    org = person.get("organization") or {}
    return org.get("sanitized_phone") or org.get("phone") or "Not available"
