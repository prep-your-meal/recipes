import os
import sys
import re
import time
import argparse
from google import genai
from dotenv import load_dotenv

# Load the API key from the .env file
load_dotenv()
client = genai.Client()

RECIPES_DIR = "recipes"

def split_frontmatter(content: str) -> tuple[str, str]:
    """Splits the markdown file into frontmatter and body."""
    match = re.match(r'^(---\s*\n.*?\n---\s*\n)(.*)', content, re.DOTALL)
    if match:
        return match.group(1), match.group(2)
    return "", content

def normalize_text_with_ai(text: str, language: str) -> str:
    """Uses Gemini to standardize the tone of voice and formatting of the instructions."""
    if not text.strip():
        return text

    print(f"🤖 Normalizing instructions ({language})...")
    
    prompt = f"""
    You are the Lead Culinary Editor for the PrepYourMeal app. I will provide you with a raw recipe draft in {language}.
    Your task is to rewrite and normalize these instructions to match our standardized 'Tone of Voice'.
    
    Editorial Guidelines:
    1. Maintain the original language ({language}).
    2. Ensure a professional, encouraging, and clear tone.
    3. Standardize the Markdown formatting (use headings like '##', create clear numbered lists for steps).
    4. Remove any personal anecdotes or messy notes from the raw text; focus purely on the culinary execution.
    5. Return ONLY the normalized markdown text. Do NOT wrap it in ```markdown code blocks. No conversational filler.
    
    RAW DRAFT TO NORMALIZE:
    {text}
    """

    try:
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=prompt
        )
        
        # Clean up in case Gemini still adds markdown wrappers
        clean_text = response.text.replace('```markdown', '').replace('```', '').strip()
        return clean_text
    except Exception as e:
        print(f"🛑 API Error: {e}")
        return text # Fallback to original text on error

def process_bundle(bundle_name: str):
    """Processes both de.md and en.md for a specific recipe bundle."""
    bundle_path = os.path.join(RECIPES_DIR, bundle_name)
    
    if not os.path.exists(bundle_path):
        print(f"❌ Error: Bundle '{bundle_name}' not found.")
        return

    print(f"\n🍳 Processing bundle: '{bundle_name}'")

    for filename, lang in [("de.md", "German"), ("en.md", "English")]:
        file_path = os.path.join(bundle_path, filename)
        
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        frontmatter, body = split_frontmatter(content)

        if not body.strip():
            print(f"⚠️ Skipped '{filename}': No instruction text found.")
            continue

        normalized_body = normalize_text_with_ai(body, lang)

        # Reassemble the file
        new_content = f"{frontmatter}{normalized_body}\n"

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"✅ Successfully normalized: {filename}")
        time.sleep(3)  # Sleep for 3 seconds to respect API rate limits

def process_all():
    """Iterates through all bundles in the recipes directory."""
    if not os.path.exists(RECIPES_DIR):
        print(f"❌ Error: Directory '{RECIPES_DIR}' not found.")
        sys.exit(1)

    bundles = [d for d in os.listdir(RECIPES_DIR) if os.path.isdir(os.path.join(RECIPES_DIR, d))]
    
    print(f"🚀 Starting bulk normalization for {len(bundles)} recipes...")
    for bundle in bundles:
        process_bundle(bundle)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize recipe instructions to match the app's Tone of Voice and formatting standards.")
    parser.add_argument("--bundle", type=str, help="Specify a single bundle slug to process (e.g., 'red-thai-curry')")
    
    args = parser.parse_args()

    if args.bundle:
        process_bundle(args.bundle)
    else:
        # User confirmation for bulk operation
        print("⚠️ WARNING: This will overwrite ALL .md files in your recipes directory with normalized AI-generated text.")
        confirm = input("Are you sure you want to proceed? Make sure you have committed your current state to Git! (y/N): ")
        if confirm.lower() == 'y':
            process_all()
        else:
            print("Aborted.")