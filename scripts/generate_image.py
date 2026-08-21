import sys
import argparse
from io import BytesIO
from google import genai
from google.genai import types
from dotenv import load_dotenv

from image_processor import process_and_save_image

load_dotenv()
client = genai.Client()

def generate_recipe_image(dish_name: str) -> BytesIO:
    print(f"🎨 Generating authentic home-cook image for: '{dish_name}' via Gemini API...")
    
    prompt = (
        f"Casual smartphone food photo of {dish_name}, freshly cooked at home by a regular person, "
        "served on a clean everyday plate on a neat wooden kitchen table, "
        "shot on a standard smartphone camera with natural indoor window light, "
        "completely empty background with no people, tidy and peaceful atmosphere, "
        "natural realistic home cooking without professional styling, no text, no watermarks."
    )

    try:
        response = client.models.generate_content(
            model='gemini-3.1-flash-image',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"],
                image_config=types.ImageConfig(
                    aspect_ratio="1:1",
                    imageSize="1K"
                )
            )
        )

        image_part = None
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_part = part.inline_data
                break

        if not image_part:
            raise ValueError("The API did not return an image.")

        return BytesIO(image_part.data)

    except Exception as e:
        print(f"🛑 Error during image generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an optimized WebP recipe image using Gemini AI.")
    parser.add_argument("dish", type=str, help="The name or description of the dish (e.g., 'Red Thai Curry')")
    parser.add_argument("--bundle", type=str, default=None, help="Optional bundle folder name (slugified dish name if omitted)")

    args = parser.parse_args()
    bundle_name = args.bundle if args.bundle else args.dish.lower().replace(" ", "-").replace("/", "-")

    raw_image_data = generate_recipe_image(dish_name=args.dish)
    process_and_save_image(image_input=raw_image_data, bundle_name=bundle_name)