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

```

---

## 📝 Recipe Format & Metadata

Each recipe is written in Markdown with a mandatory **YAML Frontmatter** block.

### Example (`recipes/en/thai-curry.md`)

```markdown
---
slug: "red-thai-curry"
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
    category: "Meat"
  - name: "Coconut milk"
    amount: 400
    unit: "ml"
    category: "Canned Goods"
  - name: "Red curry paste"
    amount: 2
    unit: "tbsp"
    category: "Asian"
  - name: "Bell pepper"
    amount: 1
    unit: "pc"
    category: "Vegetables"
---

## Preparation

1. **Preparation:** Cut the chicken breast into bite-sized pieces and slice the bell pepper.
2. **Searing:** Heat a little oil in a wok or pan, add the red curry paste, and sauté until fragrant (about 1 minute).
3. **Cooking:** Add the chicken pieces and sear them briefly on all sides. Pour in the coconut milk.
4. **Simmering:** Add the bell pepper, reduce the heat, and let it simmer for about 15 minutes until the chicken is fully cooked and the sauce has thickened.
5. **Serving:** Serve hot, optionally with jasmine rice.

```

### Allowed Categories (Whitelist)

Categories must use standardized internal keys. The frontend/backend translates them dynamically:

* **Meal Types:** `breakfast`, `lunch`, `dinner`, `snack`
* **Diets:** `vegan`, `vegetarian`, `keto`, `low-carb`, `gluten-free`, `dairy-free`
* **Fitness Profiles:** `high-protein`, `bulking`, `cutting`, `balanced`
* **Logistics:** `meal-prep-friendly`, `quick`, `one-pot`

---

## 🛠️ Local Development & Validation Setup

To ensure high data quality, this repository uses automated validation scripts and Markdown linters. Because modern operating systems protect system-wide Python environments, it is recommended to use a **Virtual Environment**.

### 1. Prerequisites

Make sure you have **Python 3.11+** installed on your machine.

### 2. Set up Virtual Environment & Install Dependencies

Clone the repository, create a virtual environment, activate it, and install the required packages:

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

### 3. Activate Automated Git Hooks

Configure Git to use the versioned hooks included in this project so checks run automatically upon committing:

```bash
git config core.hooksPath .githooks

```

*(Note: Ensure your virtual environment is active when making commits so the pre-commit hooks can execute the local linters successfully).*

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

*(Note: The `.env` file is safely ignored by Git and will never be committed).*

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
* `recipes/images/spaghetti-bolognese.webp (compressed WebP, max ~1200px width`

### 3. **Commit your changes** following the **Conventional Commits** specification

```bash
# Make sure your virtual environment is active!
source venv/bin/activate

git add recipes/
git commit -m "feat(recipe): add spaghetti bolognese in german and english"

```

*(Local hooks will validate your YAML structure, macro fields, category whitelist, paired file existence, and Markdown format).*

### 4. **Push your branch and open a Pull Request:**

```bash
git push origin feat/add-spaghetti-bolognese

```

### 5. **CI Checks:** Once the Pull Request is opened, GitHub Actions will automatically verify

* Data integrity (YAML schema, required fields, and ingredient arrays).
* Presence of both language counterparts.
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

*(The script automatically handles the prompt, downloads the image, optimizes it, and saves it to the correct folder).*

### Option B: Processing Your Own Photo

If you took your own photo, you can use the local image processor to automatically scale, convert, and compress it to meet all repository standards—no API key required.

1. Place your source image (JPG, PNG, etc.) anywhere on your machine.
2. Run the processor script pointing to your image and target filename:

```bash
python .github/scripts/image_processor.py path/to/your-photo.jpg --output thai-curry

```

*(This will resize the image, enforce the WebP format, compress it below 150 KB, and place it ready-to-commit in `recipes/images/thai-curry.webp`).*

---

## 📄 License

This project is open-source and licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for more details.
