import os
import sys
import yaml
from PIL import Image

RECIPES_DIR = "recipes"
INGREDIENTS_REGISTRY_FILE = "ingredients.yaml"
CATEGORIES_SCHEMA_FILE = "categories.yaml"

REQUIRED_META = ["prep_time", "cook_time", "default_portions", "categories", "nutrition_per_portion", "ingredients"]
REQUIRED_NUTRITION = ["calories", "protein_g", "carbs_g", "fat_g"]

MAX_FILE_SIZE_KB = 150
MAX_WIDTH = 1200
MAX_HEIGHT = 1200

def get_allowed_categories():
    if not os.path.exists(CATEGORIES_SCHEMA_FILE):
        print(f"❌ Error: Missing schema file '{CATEGORIES_SCHEMA_FILE}'.")
        sys.exit(1)
        
    categories = set()
    with open(CATEGORIES_SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema = yaml.safe_load(f) or {}
        for group, items_list in schema.items():
            if isinstance(items_list, list):
                categories.update(items_list)
    return categories

def get_valid_ingredient_slugs():
    if not os.path.exists(INGREDIENTS_REGISTRY_FILE):
        print(f"❌ Error: Missing registry file '{INGREDIENTS_REGISTRY_FILE}'.")
        sys.exit(1)
        
    with open(INGREDIENTS_REGISTRY_FILE, "r", encoding="utf-8") as f:
        registry = yaml.safe_load(f) or {}
        return set(registry.keys())

def check_md_file(filepath, lang):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if not content.startswith("---"):
            return f"Missing YAML frontmatter block start (---) in {filepath}"
            
        parts = content.split("---", 2)
        if len(parts) < 3:
            return f"Malformed frontmatter block in {filepath}"
            
        data = yaml.safe_load(parts[1])
        if not isinstance(data, dict) or "title" not in data:
            return f"Missing required 'title' in {filepath} frontmatter"
            
        return None
    except Exception as e:
        return f"Error parsing {filepath}: {e}"

def validate_bundles():
    errors_found = False
    allowed_categories = get_allowed_categories()
    valid_ingredient_slugs = get_valid_ingredient_slugs()

    if not os.path.exists(RECIPES_DIR):
        print(f"❌ Error: Missing '{RECIPES_DIR}' directory.")
        sys.exit(1)

    for bundle_name in os.listdir(RECIPES_DIR):
        bundle_path = os.path.join(RECIPES_DIR, bundle_name)
        
        # Skip files in the root of recipes/ (if any)
        if not os.path.isdir(bundle_path):
            continue

        print(f"Checking bundle: {bundle_name}...")

        meta_path = os.path.join(bundle_path, "meta.yaml")
        de_path = os.path.join(bundle_path, "de.md")
        en_path = os.path.join(bundle_path, "en.md")
        img_path = os.path.join(bundle_path, "image.webp")

        # 1. Check required files
        missing_files = False
        for req_file in [meta_path, de_path, en_path, img_path]:
            if not os.path.exists(req_file):
                print(f"  🛑 Error: Missing required file '{os.path.basename(req_file)}' in bundle '{bundle_name}'")
                missing_files = True
                errors_found = True
        
        if missing_files:
            continue # Skip deeper validation if files are missing

        # 2. Validate meta.yaml
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = yaml.safe_load(f)

            if not isinstance(meta, dict):
                print(f"  🛑 Error: {meta_path} must be a valid YAML dictionary.")
                errors_found = True
                continue

            for field in REQUIRED_META:
                if field not in meta:
                    print(f"  🛑 Error: Missing required field '{field}' in {meta_path}")
                    errors_found = True

            categories = meta.get("categories", [])
            if not categories or not isinstance(categories, list):
                print(f"  🛑 Error: 'categories' must be a non-empty list in {meta_path}")
                errors_found = True
            else:
                for cat in categories:
                    if cat not in allowed_categories:
                        print(f"  🛑 Error: Invalid category '{cat}' in {meta_path}")
                        errors_found = True

            nutrition = meta.get("nutrition_per_portion", {})
            for nut_field in REQUIRED_NUTRITION:
                if nut_field not in nutrition:
                    print(f"  🛑 Error: Missing nutrition field '{nut_field}' in {meta_path}")
                    errors_found = True

            ingredients = meta.get("ingredients", [])
            if not ingredients or not isinstance(ingredients, list):
                print(f"  🛑 Error: 'ingredients' must be a non-empty list in {meta_path}")
                errors_found = True
            else:
                for idx, ing in enumerate(ingredients):
                    if "slug" not in ing or "amount" not in ing:
                        print(f"  🛑 Error: Ingredient #{idx+1} missing 'slug' or 'amount' in {meta_path}")
                        errors_found = True
                        continue
                    
                    slug = ing["slug"]
                    if slug not in valid_ingredient_slugs:
                        print(f"  🛑 Error: Unknown ingredient slug '{slug}' in {meta_path}. Add it to '{INGREDIENTS_REGISTRY_FILE}' first.")
                        errors_found = True

        except Exception as e:
            print(f"  🛑 Error parsing {meta_path}: {e}")
            errors_found = True

        # 3. Validate Markdown Files
        de_err = check_md_file(de_path, "de")
        if de_err:
            print(f"  🛑 {de_err}")
            errors_found = True
            
        en_err = check_md_file(en_path, "en")
        if en_err:
            print(f"  🛑 {en_err}")
            errors_found = True

        # 4. Validate Image
        try:
            file_size_kb = os.path.getsize(img_path) / 1024
            if file_size_kb > MAX_FILE_SIZE_KB:
                print(f"  🛑 Error: Image is too large ({file_size_kb:.1f} KB). Max is {MAX_FILE_SIZE_KB} KB.")
                errors_found = True

            with Image.open(img_path) as img:
                if img.format != "WEBP":
                    print(f"  🛑 Error: Image has format '{img.format}', must be WEBP.")
                    errors_found = True
                if img.size[0] > MAX_WIDTH or img.size[1] > MAX_HEIGHT:
                    print(f"  🛑 Error: Image dimensions {img.size} exceed max {MAX_WIDTH}x{MAX_HEIGHT}px.")
                    errors_found = True
        except Exception as e:
            print(f"  🛑 Error reading image {img_path}: {e}")
            errors_found = True

    if errors_found:
        print("\n❌ Validation failed! Please fix the errors above.")
        sys.exit(1)
    else:
        print("\n✨ All recipe bundles are perfectly valid!")
        sys.exit(0)

if __name__ == "__main__":
    validate_bundles()