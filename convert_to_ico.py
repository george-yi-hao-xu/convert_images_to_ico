"""Convert PNG and JPEG images to multi-size Windows icon files."""

from __future__ import annotations

import argparse
from collections.abc import Iterable
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError


SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
ICON_SIZES = (16, 32, 48, 64, 128, 256)


def find_images(paths: Iterable[Path], recursive: bool) -> list[Path]:
    """Return supported image files from the supplied files and directories."""
    images: set[Path] = set()

    for path in paths:
        if path.is_file():
            if path.suffix.lower() in SUPPORTED_EXTENSIONS:
                images.add(path)
            continue

        if not path.is_dir():
            print(f"Warning: path does not exist: {path}")
            continue

        candidates = path.rglob("*") if recursive else path.iterdir()
        images.update(
            candidate
            for candidate in candidates
            if candidate.is_file()
            and candidate.suffix.lower() in SUPPORTED_EXTENSIONS
        )

    return sorted(images, key=lambda item: str(item).lower())


def convert_image(image_path: Path, overwrite: bool = False) -> bool:
    """Convert one image and return whether a new icon was written."""
    ico_path = image_path.with_suffix(".ico")
    if ico_path.exists() and not overwrite:
        print(f"Skipped: {ico_path} already exists")
        return False

    with Image.open(image_path) as source:
        # Respect camera/phone rotation metadata before removing EXIF data.
        image = ImageOps.exif_transpose(source).convert("RGBA")

    # Build a 256 px master image. Pillow creates the smaller icon frames from it.
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
    print(f"Created: {ico_path}")
    return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Convert PNG/JPEG images to multi-size .ico files."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path.cwd()],
        help="image files or directories (default: current directory)",
    )
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="search directories recursively"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="overwrite existing .ico files"
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    images = find_images(args.paths, args.recursive)

    if not images:
        print("No PNG or JPEG images found.")
        return 0

    created = 0
    failed = 0
    for image_path in images:
        try:
            created += convert_image(image_path, args.force)
        except (OSError, ValueError, UnidentifiedImageError) as error:
            failed += 1
            print(f"Failed: {image_path} -> {error}")

    skipped = len(images) - created - failed
    print(f"Done: {created} created, {skipped} skipped, {failed} failed.")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
