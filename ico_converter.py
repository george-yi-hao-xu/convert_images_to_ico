"""Core image-to-ICO conversion functions."""

from pathlib import Path

from PIL import Image, ImageOps


ICON_SIZES = (16, 32, 48, 64, 128, 256)


def unique_output_path(image_path: Path, output_dir: Path) -> Path:
    """Return an unused ICO path, adding `` (n)`` when necessary."""
    candidate = output_dir / f"{image_path.stem}.ico"
    counter = 1
    while candidate.exists():
        candidate = output_dir / f"{image_path.stem} ({counter}).ico"
        counter += 1
    return candidate


def convert_image(image_path: Path, output_dir: Path) -> Path:
    """Convert one image and return the path of the ICO file that was created."""
    ico_path = unique_output_path(image_path, output_dir)

    with Image.open(image_path) as source:
        # Apply camera/phone rotation metadata before removing EXIF data.
        image = ImageOps.exif_transpose(source).convert("RGBA")

    # Pillow creates all smaller icon frames from this 256 px master image.
    image.thumbnail((ICON_SIZES[-1], ICON_SIZES[-1]), Image.Resampling.LANCZOS)
    canvas = Image.new(
        "RGBA", (ICON_SIZES[-1], ICON_SIZES[-1]), (0, 0, 0, 0)
    )
    position = (
        (canvas.width - image.width) // 2,
        (canvas.height - image.height) // 2,
    )
    canvas.alpha_composite(image, position)
    canvas.save(
        ico_path,
        format="ICO",
        sizes=[(size, size) for size in ICON_SIZES],
    )
    return ico_path
