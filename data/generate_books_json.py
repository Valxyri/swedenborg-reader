import os
import json

def guess_type(filename):
    lower = filename.lower()
    if 'nce' in lower:
        return "New Century Edition"
    if 'latin' in lower:
        return "Latin Edition"
    # Add more logic here if you want to identify Swedenborgiana by author or filename
    if "lagercrantz" in lower or "swedenborgiana" in lower: # example
        return "Swedenborgiana"
    return "Standard Edition"

def guess_title(filename):
    # Remove extension, underscores to spaces, capitalize words
    base = os.path.splitext(filename)[0]
    return base.replace("_", " ").title()

books = []
for f in os.listdir('.'):
    if f.endswith('.json') and f != "books.json":
        books.append({
            "id": os.path.splitext(f)[0],
            "title": guess_title(f),
            "type": guess_type(f),
            "language": "English",  # Change if you have language info
            "file": f
        })

with open('books.json', 'w', encoding='utf-8') as out:
    json.dump({"books": books}, out, indent=2, ensure_ascii=False)

print(f"Wrote {len(books)} entries to books.json")