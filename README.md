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
  - slug: red_curry_paste
    amount: 2

```

### 2. Localized Content (`de.md` / `en.md`)

Only contains the translated title in the frontmatter and the localized preparation text. No system data.

```markdown
---
title: "Red Thai Curry with Chicken"
---
## Preparation

1. **Preparation:** Cut the chicken breast into bite-sized pieces...
2. **Searing:** Heat a little oil in a wok or pan...

```

---

## 🥒 Ingredients & Categories (Schema Contracts)

### Ingredients (`ingredients.yaml`)

Before adding an ingredient to a recipe's `meta.yaml`, it **must** exist in `ingredients.yaml`. This acts as our Master Registry to ensure automated shopping lists aggregate perfectly.

```yaml
chicken_breast:
  en: "Chicken breast"
  de: "Hähnchenbrust"
  unit: "g"
  category: "Meat"

```

### Categories (`categories.yaml`)

To ensure high reliability and offline capability, all allowed categories are defined in the `categories.yaml` schema contract. If you need a new category, add it here first.

---

## 🛠️ Local Development & Validation Setup

To ensure high data quality, this repository uses automated validation scripts.

### 1. Prerequisites & Virtual Environment

Make sure you have **Python 3.11+** installed.

```bash
# 1. Create virtual environment
python3 -m venv venv

# 2. Activate it
# On Linux/macOS:
source venv/bin/activate
# On Windows (Git Bash):
source venv/Scripts/activate

# 3. Install dependencies
pip install -r requirements.txt

```

*(Note: You can safely remove `spacy` from your `requirements.txt` as linguistic parsing is no longer required under the Bundle architecture).*

### 2. Activate Automated Git Hooks

Configure Git to use the versioned hooks so checks run automatically upon committing:

```bash
git config core.hooksPath .githooks

```

---

## 🚀 How to Add or Update Recipes

We maintain strict quality control through automated CI checks and Pull Requests. Direct pushes to `main` are restricted.

1. **Create a new branch:** `git checkout -b feat/add-spaghetti-bolognese`
2. **Register Ingredients:** Ensure all required ingredients exist in `ingredients.yaml`.
3. **Create the Bundle:** Create a new folder in `recipes/` (e.g., `recipes/spaghetti-bolognese/`).
4. **Populate Data:** Add your `meta.yaml`, `de.md`, `en.md`, and process the `image.webp`.
5. **Commit:** `git add . && git commit -m "feat(recipe): add spaghetti bolognese bundle"`
6. **Push & PR:** GitHub Actions will automatically validate bundle completeness, schema compliance, and data integrity.

---

## 📸 Image Guidelines & Generation Tools

Every bundle requires exactly one optimized WebP image named `image.webp`. We provide two helper scripts in `.github/scripts/`:

### Option A: AI Generation (Requires `.env` with `GEMINI_API_KEY`)

Generates an authentic, approachable home-cooked style image and saves it directly to the bundle.

```bash
python .github/scripts/generate_image.py "Red Thai Curry" --bundle red-thai-curry

```

### Option B: Processing Your Own Photo

Automatically scales, converts, and compresses a local photo to meet repository standards.

```bash
python .github/scripts/image_processor.py path/to/your-photo.jpg --bundle red-thai-curry

```

---

## 📄 License

This project is open-source and licensed under the **Apache 2.0 License**. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for more details.
