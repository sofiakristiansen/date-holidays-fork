import os
import re
import zipfile
import requests
import json
import sys
from urllib.parse import quote

# Force UTF-8 output to avoid Windows encoding issues
sys.stdout.reconfigure(encoding='utf-8')

def get_correct_english_title(search_query):
    """
    Search Wikipedia to find the correct English page title.
    If the search query redirects, return the actual Wikipedia page title.
    """
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={quote(search_query)}&srlimit=1"
    
    try:
        response = requests.get(search_url)
        if response.status_code != 200:
            return None  # Unable to fetch data

        data = response.json()
        search_results = data.get("query", {}).get("search", [])

        if search_results:
            return search_results[0]["title"]  # The best match Wikipedia title

        return None  # No results found

    except Exception as e:
        print(f"Error searching Wikipedia for '{search_query}': {e}")
        return None

def check_swedish_wikipedia(en_title):
    """
    Check if a Swedish Wikipedia page exists for the given English title.
    Returns the Swedish title if it exists, otherwise "MANUAL OPERATION REQUIRED".
    """
    if not en_title:
        return "MANUAL OPERATION REQUIRED"

    api_url = f"https://en.wikipedia.org/w/api.php?action=query&titles={quote(en_title)}&prop=langlinks&lllimit=500&format=json"
    
    try:
        response = requests.get(api_url)
        if response.status_code != 200:
            return "MANUAL OPERATION REQUIRED"

        data = response.json()
        pages = data.get("query", {}).get("pages", {})

        for page_id, page_data in pages.items():
            if "langlinks" in page_data:
                for lang_entry in page_data["langlinks"]:
                    if lang_entry["lang"] == "sv":  # Swedish language entry found
                        return lang_entry["*"]  # Return the exact Swedish Wikipedia title

        return "MANUAL OPERATION REQUIRED"
    
    except Exception as e:
        print(f"Error checking Swedish Wikipedia for '{en_title}': {e}")
        return "MANUAL OPERATION REQUIRED"

def process_yaml_file(file_path):
    """
    Process a single YAML file to add corresponding Swedish Wikipedia entries.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    updated_lines = []
    for line in lines:
        updated_lines.append(line)
        match = re.match(r'(\s*)en:\s*(.*)', line)
        if match:
            indent, en_title = match.groups()
            en_title = en_title.strip()

            # Step 1: Get the best-matching English Wikipedia title
            corrected_title = get_correct_english_title(en_title)
            if corrected_title:
                print(f"Corrected English title: '{en_title}' -> '{corrected_title}'")
            else:
                corrected_title = en_title  # If no match found, use original

            # Step 2: Find the Swedish Wikipedia title
            sv_title = check_swedish_wikipedia(corrected_title)
            updated_lines.append(f"{indent}sv: {sv_title}\n")
            print(f"Updated: {corrected_title} → {sv_title}")  # Debugging print statement

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(updated_lines)

def process_zip_file(zip_path, output_zip_path):
    """
    Process each YAML file in the provided ZIP archive.
    """
    print(f"Processing ZIP file: {zip_path}")
    
    # Extract files
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall("temp_extracted")
    
    yaml_files = [os.path.join("temp_extracted", f) for f in os.listdir("temp_extracted") if f.endswith(".yaml")]

    if not yaml_files:
        print("No YAML files found in the ZIP.")
        return

    for yaml_file in yaml_files:
        print(f"Processing: {yaml_file}")
        process_yaml_file(yaml_file)

    # Repackage into a new zip file
    with zipfile.ZipFile(output_zip_path, 'w') as zipf:
        for yaml_file in yaml_files:
            zipf.write(yaml_file, os.path.basename(yaml_file))
            print(f"Added to ZIP: {yaml_file}")

    # Clean up temporary files
    for yaml_file in yaml_files:
        os.remove(yaml_file)
    os.rmdir("temp_extracted")

    print(f"Updated ZIP file created: {output_zip_path}")

if __name__ == "__main__":
    process_zip_file("input_files.zip", "updated_files.zip")  # Change filenames as needed
