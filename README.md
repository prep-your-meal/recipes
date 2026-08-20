# PrepYourMeal Recipes

This repository acts as the **Single Source of Truth** for all cooking recipes used by the PrepYourMeal API. Recipes are maintained as structured Markdown files and automatically synchronized with the application backend.

---

## 📂 Repository Structure & Language Policy

⚠️ **Important Rule:** Every recipe **must** be provided in **both languages** (German and English). To link them together, files in different language folders must share the **exact same filename** (e.g., `thai-curry.md`). Furthermore, every recipe requires exactly one optimized WebP image.

```text
recipes/
├── de/
│   └── thai-curry.md    # German version (mandatory counterpart)
├── en/
│   └── thai-curry.md    # English version (mandatory counterpart)
└── images/
    └── thai-curry.webp  # Optimized WebP image (max ~1200px width, <150KB)
ingredients.yaml         # The Master Registry for all ingredients
categories.yaml          # The Schema Contract for all allowed categories

```

---

## 📝 Recipe Format & Metadata

Each recipe is written in Markdown with a mandatory **YAML Frontmatter** block.
*Note: The `slug` is automatically generated from the filename by the backend. Do not include it in the YAML.*

### Example (`recipes/en/thai-curry.md`)

```yaml
---
title: "Red Thai Curry with Chicken"
image: "recipes/images/red-thai-curry.webp"
prep_time: 15
cook_time: 20
default_portions: 2
categories:
  - "dinner"
  - "high-protein"
  - "meal-prep-friendly"
nutrition_per_portion:
  calories: 520
  protein_g: 44
  carbs_g: 18
  fat_g: 28
ingredients:
  - name: "Chicken breast"
    amount: 400
    unit: "g"
  - name: "Coconut milk"
    amount: 400
    unit: "ml"
  - name: "Red curry paste"
    amount: 2
    unit: "tbsp"
  - name: "Bell pepper"
    amount: 1
    unit: "pc"
---

```

## Preparation

1. **Preparation:** Cut the chicken breast into bite-sized pieces and slice the bell pepper
2. **Searing:** Heat a little oil in a wok or pan, add the red curry paste, and sauté until fragrant (about 1 minute)
3. **Cooking:** Add the chicken pieces and sear them briefly on all sides. Pour in the coconut milk
4. **Simmering:** Add the bell pepper, reduce the heat, and let it simmer for about 15 minutes until the chicken is fully cooked and the sauce has thickened
5. **Serving:** Serve hot, optionally with jasmine rice

### Allowed Categories (Schema Contract)

To ensure high reliability and offline capability, the allowed categories are defined in a local schema contract: the `categories.yaml` file. The validation pipeline checks against this file directly.

If you need to introduce a new category (e.g., a new allergy or diet), you must add it to `categories.yaml` first.

*Note: During synchronization, the application backend will read this file to dynamically update its own category endpoints.*

---

## 🥒 Ingredients & The Master Registry

To ensure automated shopping lists work perfectly and identical items are aggregated correctly across different languages, this project uses a strict **Single Source of Truth** for ingredients: the `ingredients.yaml` file in the root directory.

**Crucial Rules for Ingredients:**

1. You must **always use the singular form** in your recipes (e.g., `Tomato` instead of `Tomatoes`).
2. Every ingredient you use in a Markdown recipe *must* be defined in the `ingredients.yaml` file.

### 🤖 Intelligent Plural Gatekeeper (spaCy NLP)

To prevent pluralization errors automatically, the helper scripts leverage **spaCy NLP**. When extracting ingredients, the script analyzes the grammatical lemma of each word in both German and English. If a plural form is detected (e.g., *"Tomaten"* or *"potatoes"*), the script aborts and forces you to use the singular form.

### ⚡ The Automated Workflow (How to save time)

If you are writing a new recipe with new ingredients:

**Step 1:** Write your Markdown recipe normally using singular ingredient names.

**Step 2:** Run the extraction script:

```bash
python .github/scripts/extract_ingredients.py

```

*(This scans your recipes, uses spaCy to verify singular forms, generates clean slugs, and automatically extracts fully translated entries into `ingredients.yaml`).*

**Step 3:** Review `ingredients.yaml` to ensure categories and units are correct.

---

## 🛠️ Local Development & Validation Setup

To ensure high data quality, this repository uses automated validation scripts and Markdown linters. Because modern operating systems protect system-wide Python environments, it is recommended to use a **Virtual Environment**.

### 1. Prerequisites

Make sure you have **Python 3.11+** installed on your machine.

### 2. Set up Virtual Environment & Install Dependencies

Clone the repository, create a virtual environment, activate it, and install the required packages (including spaCy NLP models):

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

# 4. Download spaCy linguistic models for DE and EN plural checks
python -m spacy download de_core_news_sm
python -m spacy download en_core_web_sm

```

### 3. Activate Automated Git Hooks

Configure Git to use the versioned hooks included in this project so checks run automatically upon committing:

```bash
git config core.hooksPath .githooks

```

(Note: Ensure your virtual environment is active when making commits so the pre-commit hooks can execute the local linters successfully).

### 4. Setting up your Gemini API Key (Optional for AI Generation)

To use the automated AI image generator, you need a free Gemini API key:

1. Generate your API key at [Google AI Studio](https://aistudio.google.com/).
2. In the root directory of the repository, copy the example environment file:

```bash
cp .env.example .env

```

3. Open the newly created `.env` file and insert your API key:

```env
GEMINI_API_KEY=your_actual_api_key_here

```

(Note: The `.env` file is safely ignored by Git and will never be committed).

---

## 🚀 How to Add or Update Recipes (Via Pull Request)

We maintain strict quality control through automated CI checks and Pull Requests. Direct pushes to `main` are restricted.

### 1. **Create a new branch:**

```bash
git checkout -b feat/add-spaghetti-bolognese

```

### 2. **Add both language versions:** Create your recipe file with the **same filename** in both folders

* `recipes/de/spaghetti-bolognese.md`
* `recipes/en/spaghetti-bolognese.md`
* `recipes/images/spaghetti-bolognese.webp` (compressed WebP, max ~1200px width)

### 3. **Extract and Sync Ingredients:**

Run the extraction script to update `ingredients.yaml`:

```bash
# Make sure your virtual environment is active!
source venv/bin/activate

python .github/scripts/extract_ingredients.py

```

### 4. **Commit your changes** following the **Conventional Commits** specification

```bash
git add recipes/ ingredients.yaml
git commit -m "feat(recipe): add spaghetti bolognese in german and english"

```

(Local hooks will validate your YAML structure, macro fields, ingredient registry, paired file existence, and Markdown format).

### 5. **Push your branch and open a Pull Request:**

```bash
git push origin feat/add-spaghetti-bolognese

```

### 6. **CI Checks:** Once the Pull Request is opened, GitHub Actions will automatically verify

* Data integrity (YAML schema, required fields, and ingredient arrays).
* Presence of both language counterparts.
* Strict validation against the `ingredients.yaml` master registry.
* Markdown style rules.
* Pull Request title formatting (Conventional Commits).

Once all checks turn green and your changes are reviewed, your recipe will be merged and synchronized!

---

## 📸 Image Guidelines & Generation Tools

Every recipe requires exactly one optimized WebP image stored in `recipes/images/` (named identically to your markdown file, e.g., `recipes/images/thai-curry.webp`).

To make adding images effortless and ensure they meet all technical requirements (max 1200px width, WebP format, under 150 KB), we provide two helper scripts in `.github/scripts/`:

### Option A: AI Generation (Ambitious Home Cook Style)

If you don't have a photo ready, you can automatically generate an authentic, approachable home-cooked style image using the Gemini API.

1. Ensure your virtual environment is active and your `.env` file contains your `GEMINI_API_KEY`.
2. Run the generator script with your dish name:

```bash
python .github/scripts/generate_image.py "Red Thai Curry with Chicken" --output thai-curry

```

(The script automatically handles the prompt, downloads the image, optimizes it, and saves it to the correct folder).

### Option B: Processing Your Own Photo

If you took your own photo, you can use the local image processor to automatically scale, convert, and compress it to meet all repository standards—no API key required.

1. Place your source image (JPG, PNG, etc.) anywhere on your machine.
2. Run the processor script pointing to your image and target filename:

```bash
python .github/scripts/image_processor.py path/to/your-photo.jpg --output thai-curry

```

(This will resize the image, enforce the WebP format, compress it below 150 KB, and place it ready-to-commit in `recipes/images/thai-curry.webp`).

---

## 📄 License

This project is open-source and licensed under the **Apache 2.0 License**. See the [LICENSE](https://www.google.com/search?q=LICENSE) file for more details.
