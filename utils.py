import re

def clean_text(text):
    # Simple cleaner: remove extra spaces, newlines, etc.
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

