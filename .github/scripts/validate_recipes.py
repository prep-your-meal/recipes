import os
import sys
import yaml
from PIL import Image

RECIPES_DIR = "recipes"
INGREDIENTS_REGISTRY_FILE = "ingredients.yaml"
CATEGORIES_SCHEMA_FILE = "categories.yaml"

REQUIRED_FIELDS = ["title", "prep_time", "cook_time", "default_portions", "categories", "nutrition_per_portion", "image"]
REQUIRED_NUTRITION = ["calories", "protein_g", "carbs_g", "fat_g"]

MAX_FILE_SIZE_KB = 150
MAX_WIDTH = 1200
MAX_HEIGHT = 1200

def get_allowed_categories():
    """Fetches allowed categories statically from the local schema file (Schema Contract)."""
    if not os.path.exists(CATEGORIES_SCHEMA_FILE):
        print(f"❌ Error: Missing categories schema file '{CATEGORIES_SCHEMA_FILE}'.")
        sys.exit(1)
        
    categories = set()
    try:
        with open(CATEGORIES_SCHEMA_FILE, "r", encoding="utf-8") as f:
            schema = yaml.safe_load(f) or {}
            for group, items_list in schema.items():
                if isinstance(items_list, list):
                    categories.update(items_list)
        print(f"✅ Successfully loaded {len(categories)} categories from '{CATEGORIES_SCHEMA_FILE}'.")
    except Exception as e:
        print(f"❌ Error reading '{CATEGORIES_SCHEMA_FILE}': {e}")
        sys.exit(1)
        
    return categories

def validate_recipes():
    errors_found = False
    
    # Fetch allowed categories from local schema
    allowed_categories = get_allowed_categories()
    
    # 1. Load the Master Ingredients Registry
    valid_ingredients_de = set()
    valid_ingredients_en = set()
    
    if not os.path.exists(INGREDIENTS_REGISTRY_FILE):
        print(f"❌ Error: Missing master registry file '{INGREDIENTS_REGISTRY_FILE}'.")
        sys.exit(1)
        
    try:
        with open(INGREDIENTS_REGISTRY_FILE, "r", encoding="utf-8") as f:
            registry = yaml.safe_load(f) or {}
            for key, data in registry.items():
                if "de" in data and data["de"]:
                    valid_ingredients_de.add(data["de"])
                if "en" in data and data["en"]:
                    valid_ingredients_en.add(data["en"])
    except Exception as e:
        print(f"❌ Error reading '{INGREDIENTS_REGISTRY_FILE}': {e}")
        sys.exit(1)

    # 2. Check Directories
    de_dir = os.path.join(RECIPES_DIR, "de")
    en_dir = os.path.join(RECIPES_DIR, "en")

    if not os.path.exists(de_dir) or not os.path.exists(en_dir):
        print("❌ Error: Missing 'recipes/de' or 'recipes/en' directory.")
        sys.exit(1)

    # 3. Check for mandatory language pairing
    de_files = set(f for f in os.listdir(de_dir) if f.endswith(".md"))
    en_files = set(f for f in os.listdir(en_dir) if f.endswith(".md"))

    missing_in_en = de_files - en_files
    missing_in_de = en_files - de_files

    for f in missing_in_en:
        print(f"🛑 Error: Recipe 'recipes/de/{f}' has no English counterpart in 'recipes/en/'")
        errors_found = True

    for f in missing_in_de:
        print(f"🛑 Error: Recipe 'recipes/en/{f}' has no German counterpart in 'recipes/de/'")
        errors_found = True

    # 4. Check for identical ingredient counts in paired files
    paired_files = de_files.intersection(en_files)
    for f in paired_files:
        de_path = os.path.join(de_dir, f)
        en_path = os.path.join(en_dir, f)
        try:
            with open(de_path, "r", encoding="utf-8") as f_de, open(en_path, "r", encoding="utf-8") as f_en:
                de_yml = yaml.safe_load(f_de.read().split("---", 2)[1])
                en_yml = yaml.safe_load(f_en.read().split("---", 2)[1])
                
                de_count = len(de_yml.get("ingredients", []))
                en_count = len(en_yml.get("ingredients", []))
                
                if de_count != en_count:
                    print(f"🛑 Error: Ingredient count mismatch in '{f}'! DE has {de_count}, EN has {en_count}. They must match exactly for the extraction script to work.")
                    errors_found = True
        except Exception:
            pass

    # 5. Validate individual markdown files
    for lang in ["de", "en"]:
        lang_dir = os.path.join(RECIPES_DIR, lang)
        
        valid_names_for_lang = valid_ingredients_de if lang == "de" else valid_ingredients_en
        
        for file in os.listdir(lang_dir):
            if not file.endswith(".md"):
                continue
            
            filepath = os.path.join(lang_dir, file)
            print(f"Checking {filepath}...")

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()

                if not content.startswith("---"):
                    print(f"  🛑 Error: Missing YAML frontmatter block start (---) in {filepath}")
                    errors_found = True
                    continue

                parts = content.split("---", 2)
                if len(parts) < 3:
                    print(f"  🛑 Error: Malformed frontmatter block in {filepath}")
                    errors_found = True
                    continue

                data = yaml.safe_load(parts[1])
                if not isinstance(data, dict):
                    print(f"  🛑 Error: Frontmatter is not a valid YAML dictionary in {filepath}")
                    errors_found = True
                    continue

                for field in REQUIRED_FIELDS:
                    if field not in data:
                        print(f"  🛑 Error: Missing required field '{field}' in {filepath}")
                        errors_found = True

                # Validate image
                image_path = data.get("image")
                if image_path:
                    if not os.path.exists(image_path):
                        print(f"  🛑 Error: Image file not found on disk at '{image_path}' referenced in {filepath}")
                        errors_found = True
                    else:
                        file_size_kb = os.path.getsize(image_path) / 1024
                        if file_size_kb > MAX_FILE_SIZE_KB:
                            print(f"  🛑 Error: Image '{image_path}' is too large ({file_size_kb:.1f} KB). Max allowed is {MAX_FILE_SIZE_KB} KB.")
                            errors_found = True

                        try:
                            with Image.open(image_path) as img:
                                width, height = img.size
                                img_format = img.format

                                if img_format != "WEBP":
                                    print(f"  🛑 Error: Image '{image_path}' has format '{img_format}', but must be a real WebP file.")
                                    errors_found = True

                                if width > MAX_WIDTH or height > MAX_HEIGHT:
                                    print(f"  🛑 Error: Image dimensions ({width}x{height}) exceed maximum allowed ({MAX_WIDTH}x{MAX_HEIGHT}px).")
                                    errors_found = True

                        except Exception as img_err:
                            print(f"  🛑 Error: Could not read image file '{image_path}': {img_err}")
                            errors_found = True

                # CATEGORY SCHEMA VALIDATION
                categories = data.get("categories", [])
                if not isinstance(categories, list) or len(categories) == 0:
                    print(f"  🛑 Error: 'categories' must be a non-empty list in {filepath}")
                    errors_found = True
                else:
                    for cat in categories:
                        if cat not in allowed_categories:
                            print(f"  🛑 Error: Invalid recipe category '{cat}' in {filepath}. Check 'categories.yaml' for allowed values.")
                            errors_found = True

                # Validate nutrition structure
                nutrition = data.get("nutrition_per_portion", {})
                if not isinstance(nutrition, dict):
                    print(f"  🛑 Error: 'nutrition_per_portion' must be a dictionary in {filepath}")
                    errors_found = True
                else:
                    for nut_field in REQUIRED_NUTRITION:
                        if nut_field not in nutrition:
                            print(f"  🛑 Error: Missing nutrition field '{nut_field}' in {filepath}")
                            errors_found = True

                # Validate ingredients structure
                ingredients = data.get("ingredients", [])
                if not isinstance(ingredients, list) or len(ingredients) == 0:
                    print(f"  🛑 Error: 'ingredients' must be a non-empty list in {filepath}")
                    errors_found = True
                else:
                    for idx, ing in enumerate(ingredients):
                        for req_key in ["name", "amount", "unit"]:
                            if req_key not in ing:
                                print(f"  🛑 Error: Ingredient #{idx+1} is missing required key '{req_key}' in {filepath}")
                                errors_found = True

                        ing_name_raw = ing.get("name", "")
                        ing_name_stripped = ing_name_raw.strip()
                        
                        if ing_name_raw != ing_name_stripped:
                            print(f"  🛑 Error: Ingredient #{idx+1} '{ing_name_raw}' in {filepath} has leading or trailing spaces.")
                            errors_found = True

                        if ing_name_stripped and ing_name_stripped not in valid_names_for_lang:
                            print(f"  🛑 Error: Ingredient '{ing_name_stripped}' in {filepath} is not defined in '{INGREDIENTS_REGISTRY_FILE}'. Please run the extraction script or add it manually.")
                            errors_found = True

            except yaml.YAMLError as e:
                print(f"  🛑 YAML Parsing Error in {filepath}: {e}")
                errors_found = True
            except Exception as e:
                print(f"  🛑 Unexpected Error in {filepath}: {e}")
                errors_found = True

    if errors_found:
        print("\n❌ Validation failed! Please fix the errors above.")
        sys.exit(1)
    else:
        print("\n✨ All recipes, categories and ingredients are valid!")
        sys.exit(0)

if __name__ == "__main__":
    validate_recipes()