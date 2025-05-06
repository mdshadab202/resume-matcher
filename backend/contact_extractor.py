import re

def extract_contact_info(text):
    email = re.search(r"[\w\.-]+@[\w\.-]+", text)
    phone = re.search(r"\+?\d[\d\s\-()]{7,}\d", text)
    return (email.group(0) if email else None), (phone.group(0) if phone else None)