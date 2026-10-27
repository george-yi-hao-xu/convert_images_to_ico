"""Launch the Image to ICO Converter GUI."""

from converter_gui import run_app
from ico_converter import convert_image, unique_output_path

__all__ = ["convert_image", "unique_output_path"]


if __name__ == "__main__":
    run_app()
