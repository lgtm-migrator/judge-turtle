"""Turtle runtime."""

import runpy
from io import BytesIO

from cairosvg import svg2png  # noqa
from PIL import Image, ImageChops  # noqa

from .runtime_patch import InOutPatch, TimePatch, TurtlePatch


def run_file(file_path: str, width: int, height: int):
    """Run the submission file."""
    with (
        TurtlePatch(width, height) as turtle,
        InOutPatch(),
        TimePatch(),
    ):
        runpy.run_path(file_path)

        return turtle


def generate_svg_byte_stream(file_path: str, width: int, height: int) -> bytes:
    """Generate SVG byte stream from file."""
    turtle_instance = run_file(file_path, width, height)
    return turtle_instance.to_svg().encode()


def generate_png_image(svg_bytes: bytes, width: int, height: int) -> Image.Image:
    """Generate PNG image from SVG bytes."""
    png_bytes = BytesIO()
    svg2png(bytestring=svg_bytes, write_to=png_bytes, output_width=width, output_height=height)
    return Image.open(png_bytes)


def diff_images(image1: Image.Image, image2: Image.Image) -> tuple[int, int]:
    """Generate difference between two images, and return the number differing pixels."""
    diff = ImageChops.difference(image1, image2)

    hist = diff.histogram()
    correct_pixels = hist[256 * 0] + hist[256 * 1] + hist[256 * 2] + hist[256 * 3]
    total_pixels = sum(hist)
    return correct_pixels // 4, total_pixels // 4
