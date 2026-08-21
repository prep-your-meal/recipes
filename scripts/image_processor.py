import os
import sys
import argparse
from io import BytesIO
from PIL import Image

def process_and_save_image(image_input, bundle_name: str):
    print(f"⚙️ Processing and optimizing image for bundle: '{bundle_name}'...")

    try:
        if isinstance(image_input, str):
            if not os.path.exists(image_input):
                print(f"🛑 Error: Input image file not found at '{image_input}'.")
                sys.exit(1)
            img = Image.open(image_input)
        elif isinstance(image_input, BytesIO):
            img = Image.open(image_input)
        else:
            raise TypeError("Invalid image input type. Must be a file path string or a BytesIO stream.")

        with img:
            img.thumbnail((1200, 1200))

            # Ensure bundle directory exists
            bundle_dir = os.path.join("recipes", bundle_name)
            os.makedirs(bundle_dir, exist_ok=True)
            output_path = os.path.join(bundle_dir, "image.webp")

            quality = 85
            while quality > 10:
                img.save(output_path, "WEBP", quality=quality)
                if os.path.getsize(output_path) <= 150 * 1024:
                    break
                quality -= 5

            file_size_kb = os.path.getsize(output_path) / 1024
            print(f"✨ Successfully processed and saved: {output_path} ({file_size_kb:.1f} KB, Format: WebP)")

    except Exception as e:
        print(f"🛑 Error during image processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process and optimize an image into a recipe bundle.")
    parser.add_argument("input", type=str, help="Path to the local source image")
    parser.add_argument("--bundle", type=str, required=True, help="Target bundle folder name (e.g., 'red-thai-curry')")

    args = parser.parse_args()
    process_and_save_image(image_input=args.input, bundle_name=args.bundle)