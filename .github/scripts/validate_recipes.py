import os
import sys
import yaml
from PIL import Image

RECIPES_DIR = "recipes"
REQUIRED_FIELDS = ["slug", "title", "prep_time", "cook_time", "default_portions", "categories", "nutrition_per_portion", "image"]
REQUIRED_NUTRITION = ["calories", "protein_g", "carbs_g", "fat_g"]

ALLOWED_CATEGORIES = {
    # Meal Types
    "breakfast", "lunch", "dinner", "snack",
    # Diets
    "vegan", "vegetarian", "keto", "low-carb", "gluten-free", "dairy-free",
    # Fitness Goals / Profiles
    "high-protein", "bulking", "cutting", "balanced",
    # Logistics
    "meal-prep-friendly", "quick", "one-pot"
}

# Image constraints
MAX_FILE_SIZE_KB = 150
MAX_WIDTH = 1200
MAX_HEIGHT = 1200

def validate_recipes():
    errors_found = False
    
    de_dir = os.path.join(RECIPES_DIR, "de")
    en_dir = os.path.join(RECIPES_DIR, "en")

    if not os.path.exists(de_dir) or not os.path.exists(en_dir):
        print("❌ Error: Missing 'recipes/de' or 'recipes/en' directory.")
        sys.exit(1)

    # Check for mandatory language pairing
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

    # Validate individual markdown files
    for lang in ["de", "en"]:
        lang_dir = os.path.join(RECIPES_DIR, lang)
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

                # Check required top-level fields
                for field in REQUIRED_FIELDS:
                    if field not in data:
                        print(f"  🛑 Error: Missing required field '{field}' in {filepath}")
                        errors_found = True

                # Validate image (Real format, dimensions, and file size)
                image_path = data.get("image")
                if image_path:
                    if not os.path.exists(image_path):
                        print(f"  🛑 Error: Image file not found on disk at '{image_path}' referenced in {filepath}")
                        errors_found = True
                    else:
                        # 1. Check File Size
                        file_size_kb = os.path.getsize(image_path) / 1024
                        if file_size_kb > MAX_FILE_SIZE_KB:
                            print(f"  🛑 Error: Image '{image_path}' is too large ({file_size_kb:.1f} KB). Max allowed is {MAX_FILE_SIZE_KB} KB.")
                            errors_found = True

                        # 2. Check Real Format & Dimensions using Pillow
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

                # Validate categories against whitelist
                categories = data.get("categories", [])
                if not isinstance(categories, list) or len(categories) == 0:
                    print(f"  🛑 Error: 'categories' must be a non-empty list in {filepath}")
                    errors_found = True
                else:
                    for cat in categories:
                        if cat not in ALLOWED_CATEGORIES:
                            print(f"  🛑 Error: Invalid category '{cat}' in {filepath}. Allowed: {sorted(list(ALLOWED_CATEGORIES))}")
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
                        for req_key in ["name", "amount", "unit", "category"]:
                            if req_key not in ing:
                                print(f"  🛑 Error: Ingredient #{idx+1} is missing required key '{req_key}' in {filepath}")
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
        print("\n✨ All recipes are valid!")
        sys.exit(0)

if __name__ == "__main__":
    validate_recipes()