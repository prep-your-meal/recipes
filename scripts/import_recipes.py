import os
import sys
import json
import re
import unicodedata
from google import genai
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
client = genai.Client()

IMPORTS_DIR = "imports"
RECIPES_DIR = "recipes"

def slugify(text: str) -> str:
    """Generates a clean snake-case slug."""
    replacements = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "Ä": "ae", "Ö": "oe", "Ü": "ue"}
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    return re.sub(r'[-\s]+', '-', text)

def parse_recipe_with_ai(raw_text: str) -> dict:
    """Sends the raw text to Gemini and strictly requests a JSON format back."""
    print("🤖 Analyzing and translating recipe via Gemini...")
    
    prompt = f"""
    You are an expert culinary data assistant. I will provide you with an unstructured recipe text (usually in German).
    Your task is to extract all relevant information, translate it into English where necessary, and return EXCLUSIVELY a valid JSON object.

    Rules for the JSON:
    1. If nutritional values or times are missing, estimate realistic values based on the dish type.
    2. 'categories' MUST be an array containing only allowed values: breakfast, lunch, dinner, snack, vegan, vegetarian, high-protein, quick, meal-prep-friendly.
    3. 'ingredients' MUST be an array of objects. Generate an English 'slug' for each ingredient (singular, snake_case, e.g., 'red_onion', 'olive_oil') and estimate the amount as a number (only the bare number, no units!).
    4. Reply ONLY with the pure JSON. Do not include Markdown blocks (```json) or any conversational text.

    Expected JSON Format:
    {{
      "bundle_slug": "red-thai-curry",
      "title_de": "Rotes Thai Curry",
      "title_en": "Red Thai Curry",
      "prep_time": 15,
      "cook_time": 20,
      "default_portions": 2,
      "calories": 500,
      "protein_g": 30,
      "carbs_g": 40,
      "fat_g": 20,
      "categories": ["dinner", "high-protein"],
      "ingredients": [
        {{"slug": "chicken_breast", "amount": 400}}
      ],
      "instructions_de": "## Zubereitung\\n\\n1. Erster Schritt...",
      "instructions_en": "## Preparation\\n\\n1. First step..."
    }}
    
    HERE IS THE RECIPE:
    {raw_text}
    """

    response = client.models.generate_content(
        model='gemini-3.5-flash-lite',
        contents=prompt
    )
    
    # Clean up the response in case Gemini includes Markdown blocks despite the instructions
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def process_imports():
    if not os.path.exists(IMPORTS_DIR):
        os.makedirs(IMPORTS_DIR)
        print(f"📁 I created the folder '{IMPORTS_DIR}' for you.")
        print("👉 Please place your raw .txt or .md files there and run the script again.")
        sys.exit(0)

    # NEW: Check for both .txt and .md files
    files = [f for f in os.listdir(IMPORTS_DIR) if f.lower().endswith((".txt", ".md"))]
    
    if not files:
        print(f"🤷 No .txt or .md files found in the '{IMPORTS_DIR}' folder.")
        sys.exit(0)

    for filename in files:
        filepath = os.path.join(IMPORTS_DIR, filename)
        print(f"\n📄 Processing '{filename}'...")

        with open(filepath, "r", encoding="utf-8") as f:
            raw_text = f.read()

        try:
            # 1. Let AI structure the data
            data = parse_recipe_with_ai(raw_text)
            
            # 2. Create bundle folder
            # NEW: Safely remove any extension (.txt or .md) for the fallback slug
            fallback_name = os.path.splitext(filename)[0]
            slug = slugify(data.get("bundle_slug", fallback_name))
            bundle_dir = os.path.join(RECIPES_DIR, slug)

            if os.path.exists(bundle_dir):
                print(f"⚠️ Skipping '{slug}' - Bundle already exists.")
                continue

            os.makedirs(bundle_dir, exist_ok=True)

            # 3. Write meta.yaml
            meta_content = f"""prep_time: {data.get('prep_time', 15)}
cook_time: {data.get('cook_time', 20)}
default_portions: {data.get('default_portions', 2)}
categories:
"""
            for cat in data.get('categories', []):
                meta_content += f"  - {cat}\n"
                
            meta_content += f"""nutrition_per_portion:
  calories: {data.get('calories', 0)}
  protein_g: {data.get('protein_g', 0)}
  carbs_g: {data.get('carbs_g', 0)}
  fat_g: {data.get('fat_g', 0)}
ingredients:
"""
            for ing in data.get('ingredients', []):
                meta_content += f"  - slug: {ing['slug']}\n    amount: {ing['amount']}\n"

            with open(os.path.join(bundle_dir, "meta.yaml"), "w", encoding="utf-8") as f:
                f.write(meta_content)

            # 4. Write de.md
            with open(os.path.join(bundle_dir, "de.md"), "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: \"{data.get('title_de', 'Unknown')}\"\n---\n\n{data.get('instructions_de', '')}")

            # 5. Write en.md
            with open(os.path.join(bundle_dir, "en.md"), "w", encoding="utf-8") as f:
                f.write(f"---\ntitle: \"{data.get('title_en', 'Unknown')}\"\n---\n\n{data.get('instructions_en', '')}")

            print(f"✅ Bundle successfully created: {bundle_dir}")
            
            # Optional: Delete the file after successful import
            # os.remove(filepath)

        except Exception as e:
            print(f"🛑 Error processing '{filename}': {e}")

if __name__ == "__main__":
    process_imports()