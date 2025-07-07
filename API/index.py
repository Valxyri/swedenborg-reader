import os
import json
import re
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import PyPDF2

# --- CONFIGURATION ---
SOURCE_DIRECTORY = 'swedenborg_source_files' 
OUTPUT_DIRECTORY = 'swedenborg_app_content' 

# --- HELPER FUNCTIONS ---

def clean_text(text):
    """Removes excessive newlines and whitespace from text."""
    if not text: return ""
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_id_from_title(title):
    """Creates a clean, URL-friendly ID from a book title."""
    s = re.sub(r'[^\w\s]', '', title).lower()
    s = re.sub(r'\s+', '_', s)
    return s

def get_epub_chapters(epub_path):
    """Extracts chapters from an ePub file."""
    try:
        book = epub.read_epub(epub_path)
        chapters = []
        section_number = 1
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            content = item.get_content()
            soup = BeautifulSoup(content, 'html.parser')
            title_tag = soup.find(['h1', 'h2', 'h3'])
            title = clean_text(title_tag.get_text()) if title_tag else f"Chapter {section_number}"
            text = clean_text(soup.get_text())
            if text:
                chapters.append({'section': section_number, 'title': title, 'text': text})
                section_number += 1
        return chapters
    except Exception as e:
        print(f"  [ERROR] Could not process ePub {os.path.basename(epub_path)}: {e}")
        return None

def get_pdf_pages(pdf_path):
    """Extracts pages from a PDF file."""
    try:
        pages = []
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text:
                    pages.append({'section': i + 1, 'title': f"Page {i + 1}", 'text': clean_text(text)})
        return pages
    except Exception as e:
        print(f"  [ERROR] Could not process PDF {os.path.basename(pdf_path)}: {e}")
        return None

def get_txt_content(txt_path):
    """Reads content from a plain text file and splits it into sections."""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            full_text = f.read()
        
        paragraphs = re.split(r'\n\s*\n+', full_text)
        sections = []
        for i, para in enumerate(paragraphs):
            cleaned_para = clean_text(para)
            if len(cleaned_para.split()) > 4: # Only include paragraphs with more than 4 words
                match = re.match(r'\[?(\d+)\]?\.?', cleaned_para)
                section_num = match.group(1) if match else i + 1
                sections.append({
                    'section': int(section_num),
                    'title': f"Paragraph {section_num}",
                    'text': cleaned_para
                })
        return sections
    except Exception as e:
        print(f"  [ERROR] Could not process TXT {os.path.basename(txt_path)}: {e}")
        return None

# --- MAIN SCRIPT LOGIC ---

def main():
    """Main function to run the conversion process."""
    print("Starting Swedenborg content conversion...")
    if not os.path.exists(SOURCE_DIRECTORY):
        os.makedirs(SOURCE_DIRECTORY)
        print(f"Created source directory: '{SOURCE_DIRECTORY}'")
        return
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
        print(f"Created output directory: '{OUTPUT_DIRECTORY}'")

    master_book_list = []
    
    for root, dirs, files in os.walk(SOURCE_DIRECTORY):
        for filename in files:
            # This ensures we don't process files in the root of the source directory
            if root == SOURCE_DIRECTORY:
                continue

            parent_folder = os.path.basename(root)
            print(f"\nProcessing: {filename} (in {parent_folder})")
            
            # --- Smart Title and Category Logic ---
            raw_title = os.path.splitext(filename)[0]
            
            category = "Standard Edition" # Default
            if parent_folder == 'swedenborg_original':
                category = "Latin Edition"
            elif parent_folder == 'swedenborgiana':
                category = "Swedenborgiana"
            elif 'nce' in raw_title.lower() or 'new century' in parent_folder.lower():
                category = "New Century Edition"

            # Clean the title for display
            clean_title = re.sub(r'^(nce|foundation|sf)_?', '', raw_title, flags=re.IGNORECASE)
            clean_title = clean_title.replace('_', ' ').replace('-', ' ').title()
            clean_title = re.sub(r'\s*\d+$', '', clean_title).strip() # Remove trailing numbers
            if not clean_title: clean_title = raw_title # Fallback

            print(f"  Title: '{clean_title}', Category: '{category}'")
            # --- End of Smart Logic ---

            file_path = os.path.join(root, filename)
            sections = None
            if filename.lower().endswith('.epub'):
                sections = get_epub_chapters(file_path)
            elif filename.lower().endswith('.pdf'):
                sections = get_pdf_pages(file_path)
            elif filename.lower().endswith('.txt'):
                sections = get_txt_content(file_path)
            else:
                print(f"  [SKIP] '{filename}' is not a supported file type.")
                continue

            if sections:
                book_id = generate_id_from_title(raw_title) # Use raw title for unique ID
                output_filename = f"{book_id}.json"
                book_data = {
                    "id": book_id, "title": clean_title,
                    "type": category, # Use the new category field
                    "language": "Latin" if category == "Latin Edition" else "English",
                    "sections": sections
                }
                output_path = os.path.join(OUTPUT_DIRECTORY, output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(book_data, f, indent=2, ensure_ascii=False)
                print(f"  [SUCCESS] Converted '{filename}' to '{output_filename}'")
                
                # We only need a subset of the data for the master list
                master_book_list.append({
                    "id": book_id,
                    "title": clean_title,
                    "type": category,
                    "language": "Latin" if category == "Latin Edition" else "English",
                    "file": output_filename
                })

    if master_book_list:
        master_index_path = os.path.join(OUTPUT_DIRECTORY, 'books.json')
        with open(master_index_path, 'w', encoding='utf-8') as f:
            json.dump({"books": master_book_list}, f, indent=2, ensure_ascii=False)
        print(f"\nSuccessfully created master index file: 'books.json'")

    print("\nConversion complete.")

if __name__ == '__main__':
    main()
