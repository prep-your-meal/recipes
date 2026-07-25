import os
import sys
import argparse
from io import BytesIO
from PIL import Image

def process_and_save_image(image_input, output_filename: str):
    print(f"⚙️ Processing and optimizing image for: '{output_filename}'...")

    try:
        # Handle both local file paths (str) and in-memory byte streams (BytesIO)
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
            # Enforce technical specs: Max 1200x1200px
            img.thumbnail((1200, 1200))

            # Ensure target directory exists in the repository
            os.makedirs("recipes/images", exist_ok=True)
            output_path = os.path.join("recipes/images", f"{output_filename}.webp")

            # Iteratively compress until file size is <= 150 KB
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
    parser = argparse.ArgumentParser(description="Process and optimize any local image into a repository-compliant WebP recipe image.")
    parser.add_argument("input", type=str, help="Path to the local source image (e.g., 'my_photo.jpg')")
    parser.add_argument("--output", type=str, required=True, help="Target filename for the WebP file (without extension)")

    args = parser.parse_args()
    process_and_save_image(image_input=args.input, output_filename=args.output)