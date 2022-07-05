"""Turtle runtime."""

import io
import os
from io import BytesIO

import numpy as np
from cairosvg import svg2png  # noqa
from PIL import Image, ImageChops  # noqa

from .runtime_patch import InOutPatch, RuntimePatch, TimePatch, TurtlePatch


def run_file(file_path: str, width: int, height: int):
    """Run the submission file."""
    script_name = "<solution>"
    code = None

    decoded_path = os.path.abspath(os.fsdecode(file_path))
    with io.open_code(decoded_path) as code_file:
        code = compile(code_file.read(), script_name, "exec")

    run_code = __builtins__["exec"]  # noqa

    with (
        TurtlePatch(width, height) as turtle,
        InOutPatch(),
        TimePatch(),
        RuntimePatch(script_name),
    ):
        run_globals = dict(
            __name__=script_name,
            __file__=script_name,
            __cached__=None,
            __doc__=None,
            __loader__=None,
            __package__=script_name,
            __spec__=None,
        )

        run_code(code, run_globals)

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

    arr = np.array(diff)  # Make into Numpy array

    wrong_pixels = np.count_nonzero(arr.any(axis=-1))
    total_pixels = arr.shape[0] * arr.shape[1]
    correct_pixels = total_pixels - wrong_pixels

    return correct_pixels, total_pixels
