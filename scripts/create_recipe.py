import os
import sys
import argparse
import re
import unicodedata
import subprocess

RECIPES_DIR = "recipes"

def slugify(text: str) -> str:
    """Generates a clean snake-case slug from the title."""
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

def create_bundle(title: str, generate_image: bool):
    slug = slugify(title)
    bundle_dir = os.path.join(RECIPES_DIR, slug)

    if os.path.exists(bundle_dir):
        print(f"🛑 Error: Bundle '{slug}' already exists!")
        sys.exit(1)

    print(f"🏗️ Creating new recipe bundle: {bundle_dir}...")
    os.makedirs(bundle_dir)

    # 1. Create meta.yaml template
    meta_content = """prep_time: 15
cook_time: 20
default_portions: 2
categories:
  - dinner
nutrition_per_portion:
  calories: 500
  protein_g: 30
  carbs_g: 40
  fat_g: 20
ingredients:
  - slug: "example_ingredient"
    amount: 100
"""
    with open(os.path.join(bundle_dir, "meta.yaml"), "w", encoding="utf-8") as f:
        f.write(meta_content)

    # 2. Create de.md template
    de_content = f"""---
title: "{title}"
---

## Zubereitung

1. **Vorbereitung:** ...
2. **Kochen:** ...
"""
    with open(os.path.join(bundle_dir, "de.md"), "w", encoding="utf-8") as f:
        f.write(de_content)

    # 3. Create en.md template
    en_content = f"""---
title: "{title} (Translation Needed)"
---

## Preparation

1. **Preparation:** ...
2. **Cooking:** ...
"""
    with open(os.path.join(bundle_dir, "en.md"), "w", encoding="utf-8") as f:
        f.write(en_content)

    print("✅ Files created successfully!")

    # 4. Optionally trigger AI image generation
    if generate_image:
        print("\n🤖 Triggering AI Image Generation...")
        script_path = os.path.join("scripts", "generate_image.py")
        
        try:
            subprocess.run([sys.executable, script_path, title, "--bundle", slug], check=True)
        except subprocess.CalledProcessError:
            print("⚠️ Image generation failed. You can run it manually later.")

    print(f"\n✨ Bundle '{slug}' is ready! Open '{bundle_dir}/meta.yaml' to start editing.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a new recipe bundle with boilerplate files.")
    parser.add_argument("title", type=str, help="The title of the recipe (e.g., 'Spaghetti Bolognese')")
    parser.add_argument("--ai-image", action="store_true", help="Automatically generate an image using AI")

    args = parser.parse_args()
    create_bundle(args.title, args.ai_image)