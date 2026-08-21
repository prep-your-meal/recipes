# PrepYourMeal Recipes

This repository acts as the **Single Source of Truth** for all cooking recipes used by the PrepYourMeal API. Recipes are maintained as structured "Recipe Bundles" to guarantee strict DRY (Don't Repeat Yourself) principles and are automatically synchronized with the application backend.

---

## 📂 Repository Structure (The Bundle Pattern)

To avoid duplicating metadata across different languages, every recipe is structured as an isolated **Bundle Directory**. The name of the directory serves as the unique identifier (`slug`) for the application backend.

```text
recipes/
├── red-thai-curry/          # <-- The bundle folder (acts as the recipe slug)
│   ├── meta.yaml            # <-- Universal metadata, categories, and ingredients
│   ├── de.md                # <-- German title and instructions
│   ├── en.md                # <-- English title and instructions
│   └── image.webp           # <-- Optimized recipe image
ingredients.yaml             # The Master Registry for all ingredients
categories.yaml              # The Schema Contract for all allowed categories

```

---

## 📝 Recipe Format & Metadata

Inside each bundle, data is strictly separated between system configuration (`meta.yaml`) and localized content (`de.md` / `en.md`).

### 1. `meta.yaml` (System Data)

Defines all technical properties. Ingredients are linked purely by their `slug` to the Master Registry.

```yaml
prep_time: 15
cook_time: 20
default_portions: 2
categories:
  - dinner
  - high-protein
nutrition_per_portion:
  calories: 520
  protein_g: 44
  carbs_g: 18
  fat_g: 28
ingredients:
  - slug: chicken_breast
    amount: 400
  - slug: coconut_milk
    amount: 400

```

### 2. Localized Content (`de.md` / `en.md`)

Only contains the translated title in the frontmatter and the localized preparation text.

```markdown
---
title: "Red Thai Curry with Chicken"
---
## Preparation

1. **Preparation:** Cut the chicken breast into bite-sized pieces...

```

---

## 🥒 Ingredients & Categories (Schema Contracts)

### Ingredients (`ingredients.yaml`)

Before adding an ingredient to a recipe's `meta.yaml`, it **must** exist in `ingredients.yaml`. This acts as our Master Registry to ensure automated shopping lists aggregate perfectly.

### Categories (`categories.yaml`)

To ensure high reliability, all allowed categories are defined in the `categories.yaml` schema contract.

---

## 🛠️ Local Development & Validation Setup

Make sure you have **Python 3.11+** installed and set up your environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: source venv/Scripts/activate
pip install -r requirements.txt

```

*(Note: AI generation scripts require a `.env` file containing your `GEMINI_API_KEY`).*

---

## 🚀 How to Add or Update Recipes

We provide automated Python scripts to eliminate manual boilerplate work.

### Option A: Create a Single Recipe (Scaffolding)

If you want to write a recipe from scratch, use the scaffolding script. It will generate the bundle folder, pre-fill all necessary YAML/Markdown files, and optionally generate an AI image immediately.

```bash
python scripts/create_recipe.py "Spaghetti Bolognese" --ai-image

```

### Option B: Bulk Import from Raw Text/Markdown

If you have unstructured recipe notes, you can use the AI-powered bulk importer to parse, translate, and format them automatically.

1. **Prepare Files:** Run `python scripts/import_recipes.py` once to create the `imports/` folder.
2. **Add Raw Data:** Drop your unstructured `.txt` or `.md` files into the `imports/` folder. The formatting does not matter; the AI will read the raw text.
3. **Execute Import:**

```bash
python scripts/import_recipes.py

```

The script will generate complete bundles for every file.
4. **Master Registry Check:** Because the AI generates new English ingredient slugs automatically, **you must validate the repository afterward**:

```bash
python scripts/validate_recipes.py

```

If the script warns you about "unknown ingredient slugs," add them to your `ingredients.yaml` until the validation passes.

---

## ✍️ Content Normalization (Tone of Voice)

To ensure a consistent user experience across the app, we use an AI-powered editorial tool. This script takes raw, imported recipe notes and normalizes the text to match our standardized "Tone of Voice." It ensures professional phrasing, clear instructions, and uniform Markdown structure (e.g., lists and headings) across all languages.

### Normalize a single recipe bundle

```bash
python scripts/normalize_instructions.py --bundle red-thai-curry

```

### Bulk normalize all recipes in the repository

```bash
python scripts/normalize_instructions.py

```

> **Note:** Always commit your current state to Git before running a bulk editorial update!

---

## 📸 Image Guidelines & Generation Tools

Every bundle requires exactly one optimized WebP image named `image.webp`.

### 1. Bulk AI Generation (For Imported Recipes)

If you just bulk-imported multiple recipes, you can automatically generate missing images for all bundles at once:

```bash
python scripts/generate_missing_images.py

```

### 2. Single AI Generation

Generates an authentic, approachable home-cooked style image for a specific bundle:

```bash
python scripts/generate_image.py "Red Thai Curry" --bundle red-thai-curry

```

### 3. Processing Your Own Photo

Automatically scales, converts, and compresses a local photo to meet the 1200px / WebP repository standards:

```bash
python scripts/image_processor.py path/to/your-photo.jpg --bundle red-thai-curry

```

---

## 📄 License

This project is open-source and licensed under the **Apache 2.0 License**.
