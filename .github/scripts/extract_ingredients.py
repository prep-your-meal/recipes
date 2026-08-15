import os
import re
import sys
import unicodedata
import yaml
import spacy

RECIPES_DIR = "recipes"
INGREDIENTS_REGISTRY_FILE = "ingredients.yaml"

# Load spaCy language models for linguistic plural/singular checks
print("Loading NLP models...")
try:
    nlp_de = spacy.load("de_core_news_sm")
    nlp_en = spacy.load("en_core_web_sm")
except OSError:
    print("❌ Error: spaCy models missing. Please run:")
    print("   python -m spacy download de_core_news_sm")
    print("   python -m spacy download en_core_web_sm")
    sys.exit(1)

def slugify(text: str) -> str:
    """Generates a clean snake_case slug key from ingredient name."""
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '_', text)

def is_plural(name: str, lang: str) -> tuple[bool, str]:
    """Uses spaCy to check if a word is in plural form and returns its singular lemma."""
    nlp = nlp_de if lang == "de" else nlp_en
    doc = nlp(name)
    
    if not doc:
        return False, name
        
    token = doc[0]
    original = token.text
    lemma = token.lemma_

    # Check if the POS (Part of Speech) is a noun and the text differs from its lemma
    if token.pos_ == "NOUN" and original.lower() != lemma.lower():
        return True, lemma
        
    return False, original

def extract_unknown_ingredients():
    registry = {}
    if os.path.exists(INGREDIENTS_REGISTRY_FILE):
        try:
            with open(INGREDIENTS_REGISTRY_FILE, "r", encoding="utf-8") as f:
                registry = yaml.safe_load(f) or {}
        except Exception as e:
            print(f"❌ Error loading '{INGREDIENTS_REGISTRY_FILE}': {e}")
            sys.exit(1)

    known_names = set()
    for key, data in registry.items():
        known_names.add(key.lower())
        if isinstance(data, dict):
            if data.get("de"): known_names.add(str(data["de"]).strip().lower())
            if data.get("en"): known_names.add(str(data["en"]).strip().lower())

    new_entries_count = 0
    added_keys = []
    plural_errors_found = False

    en_dir = os.path.join(RECIPES_DIR, "en")
    de_dir = os.path.join(RECIPES_DIR, "de")

    if not os.path.exists(en_dir) or not os.path.exists(de_dir):
        print("❌ Language directories missing.")
        sys.exit(1)

    for file in os.listdir(en_dir):
        if not file.endswith(".md"): continue

        en_filepath = os.path.join(en_dir, file)
        de_filepath = os.path.join(de_dir, file)

        if not os.path.exists(de_filepath):
            continue 

        try:
            with open(en_filepath, "r", encoding="utf-8") as f:
                en_data = yaml.safe_load(f.read().split("---", 2)[1])
            with open(de_filepath, "r", encoding="utf-8") as f:
                de_data = yaml.safe_load(f.read().split("---", 2)[1])

            en_ingredients = en_data.get("ingredients", [])
            de_ingredients = de_data.get("ingredients", [])

            if len(en_ingredients) != len(de_ingredients):
                continue

            for en_ing, de_ing in zip(en_ingredients, de_ingredients):
                en_name = en_ing.get("name", "").strip()
                de_name = de_ing.get("name", "").strip()

                if not en_name or not de_name: continue
                
                # --- NLP Plural Check (German) ---
                is_de_plur, de_singular = is_plural(de_name, "de")
                if is_de_plur:
                    print(f"🛑 Plural Error in {file} (DE): '{de_name}' appears to be plural. Please use the singular form (e.g., '{de_singular}').")
                    plural_errors_found = True
                    continue

                # --- NLP Plural Check (English) ---
                is_en_plur, en_singular = is_plural(en_name, "en")
                if is_en_plur:
                    print(f"🛑 Plural Error in {file} (EN): '{en_name}' appears to be plural. Please use the singular form (e.g., '{en_singular}').")
                    plural_errors_found = True
                    continue

                # Check if this ingredient is already known
                if en_name.lower() in known_names or de_name.lower() in known_names:
                    continue

                # Add new ingredient
                base_key = slugify(en_name)
                ing_key = base_key
                counter = 1
                while ing_key in registry:
                    ing_key = f"{base_key}_{counter}"
                    counter += 1

                registry[ing_key] = {
                    "en": en_name,
                    "de": de_name,
                    "unit": en_ing.get("unit", ""), 
                    "category": en_ing.get("category", "") 
                }

                known_names.update([en_name.lower(), de_name.lower(), ing_key])
                added_keys.append((ing_key, en_name, de_name))
                new_entries_count += 1

        except Exception as e:
            print(f"⚠️ Warning: Could not process '{file}': {e}")

    if plural_errors_found:
        print("\n❌ Plural forms detected by NLP! The extraction was aborted.")
        print("👉 Please correct the plural ingredients in your Markdown files and run the script again.")
        sys.exit(1)

    if new_entries_count > 0:
        with open(INGREDIENTS_REGISTRY_FILE, "w", encoding="utf-8") as f:
            yaml.dump(registry, f, allow_unicode=True, sort_keys=True, default_flow_style=False)
        
        print(f"✅ Added {new_entries_count} fully translated ingredient(s) to '{INGREDIENTS_REGISTRY_FILE}':\n")
        for key, en_name, de_name in added_keys:
            print(f"  • [{key}] (EN: '{en_name}' | DE: '{de_name}')")
    else:
        print("✨ No unknown ingredients found. 'ingredients.yaml' is completely up to date!")

if __name__ == "__main__":
    extract_unknown_ingredients()