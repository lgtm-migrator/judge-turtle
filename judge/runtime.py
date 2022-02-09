"""Turtle runtime."""

import runpy
import sys
from io import BytesIO
from typing import Any

from cairosvg import svg2png  # noqa
from PIL import Image, ImageChops  # noqa
from svg_turtle import SvgTurtle  # noqa
from svg_turtle.canvas import Canvas  # noqa


def monkey_patch() -> SvgTurtle:
    """Monkey patch the turtle module."""
    cls: Any = SvgTurtle
    cls._screen = SvgTurtle._Screen(Canvas(1000, 500))  # noqa: W0212
    cls._pen = SvgTurtle()  # noqa: W0212

    turtle_module: Any = sys.modules["turtle"]
    turtle_module.mainloop = turtle_module.done = lambda: None
    turtle_module.Turtle = SvgTurtle

    return cls._pen  # noqa: W0212


def run_file(file_path: str):
    """Run the submission file."""
    turtle_instance = monkey_patch()

    runpy.run_path(file_path)

    return turtle_instance


def generate_svg_byte_stream(file_path: str) -> bytes:
    """Generate SVG byte stream from file."""
    turtle_instance = run_file(file_path)
    return turtle_instance.to_svg().encode()


def generate_png_image(svg_bytes: bytes) -> Image.Image:
    """Generate PNG image from SVG bytes."""
    png_bytes = BytesIO()
    svg2png(bytestring=svg_bytes, write_to=png_bytes)
    return Image.open(png_bytes)


def diff_images(image1: Image.Image, image2: Image.Image) -> tuple[int, int]:
    """Generate difference between two images, and return the number differing pixels."""
    diff = ImageChops.difference(image1, image2)

    hist = diff.histogram()
    correct_pixels = hist[0] + hist[256] + hist[256 * 2] + hist[256 * 3]
    total_pixels = sum(hist)
    return correct_pixels, total_pixels
