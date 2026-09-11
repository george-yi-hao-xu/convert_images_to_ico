from pathlib import Path
from PIL import Image

# iterate all png/jpg images and gen coresponding .ico files

folder = Path.cwd()

image_extensions = {".png", ".jpg", ".jpeg"}

for image_path in folder.iterdir():
    if not image_path.is_file():
        continue

    if image_path.suffix.lower() not in image_extensions:
        continue

    ico_path = image_path.with_suffix(".ico")

    if ico_path.exists():
        print(f"Skip: {ico_path.name} already exists")
        continue

    try:
        img = Image.open(image_path).convert("RGBA")

        # Make image square without stretching
        size = max(img.size)
        canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))

        x = (size - img.width) // 2
        y = (size - img.height) // 2

        canvas.paste(img, (x, y), img)

        canvas.save(
            ico_path,
            format="ICO",
            sizes=[
                (16, 16),
                (32, 32),
                (48, 48),
                (64, 64),
                (128, 128),
                (256, 256),
            ],
        )

        print(f"Created: {ico_path.name}")

    except Exception as e:
        print(f"Failed: {image_path.name} -> {e}")

print("Done.")
