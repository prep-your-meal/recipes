import os
import sys
import time
import subprocess

RECIPES_DIR = "recipes"
GENERATE_SCRIPT = os.path.join("scripts", "generate_image.py")

def generate_missing_images():
    if not os.path.exists(RECIPES_DIR):
        print(f"❌ Error: Directory '{RECIPES_DIR}' not found.")
        sys.exit(1)

    # Get all subdirectories (bundles) in the recipes folder
    bundles = [d for d in os.listdir(RECIPES_DIR) if os.path.isdir(os.path.join(RECIPES_DIR, d))]
    
    missing_count = 0
    
    for bundle in bundles:
        bundle_path = os.path.join(RECIPES_DIR, bundle)
        image_path = os.path.join(bundle_path, "image.webp")
        
        # Only act if the image is missing
        if not os.path.exists(image_path):
            missing_count += 1
            
            # Create a clean dish name from the slug (e.g., "red-thai-curry" -> "Red Thai Curry")
            dish_name = bundle.replace("-", " ").title()
            
            print(f"\n🖼️ Missing image detected for bundle: '{bundle}'")
            print(f"🚀 Triggering AI generation for: '{dish_name}'")
            
            try:
                # Call your existing image generator script
                subprocess.run([sys.executable, GENERATE_SCRIPT, dish_name, "--bundle", bundle], check=True)
                
                print("⏳ Sleeping for 5 seconds to respect API rate limits...")
                time.sleep(5)
            except subprocess.CalledProcessError:
                print(f"🛑 Failed to generate image for '{bundle}'. Skipping to the next one...")
                
    if missing_count == 0:
        print("\n✨ All recipe bundles already have an 'image.webp'. Nothing to do!")
    else:
        print(f"\n✅ Finished processing {missing_count} missing images.")

if __name__ == "__main__":
    generate_missing_images()