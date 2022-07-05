"""turtle judge main script."""

import base64
import os
import sys

from judge.dodona_command import (
    Context,
    DodonaException,
    ErrorType,
    Judgement,
    MessageFormat,
    MessagePermission,
    Tab,
    Test,
    TestCase,
)
from judge.dodona_config import DodonaConfig
from judge.runtime import diff_images, generate_png_image, generate_svg_byte_stream
from judge.translator import Translator

# extract info from exercise configuration
config = DodonaConfig.from_json(sys.stdin.read())

with Judgement():
    config.sanity_check()

    # Initiate translator
    config.translator = Translator.from_str(config.natural_language)

    # Set 'solution_file' to "./solution.py" if not set
    config.solution_file = str(getattr(config, "solution_file", "./solution.py"))
    config.solution_file = os.path.join(config.resources, config.solution_file)

    if not os.path.exists(config.solution_file):
        raise DodonaException(
            config.translator.error_status(ErrorType.INTERNAL_ERROR),
            permission=MessagePermission.STAFF,
            description=f"Could not find solution file: '{config.solution_file}'.",
            format=MessageFormat.TEXT,
        )

    with Tab("Comparing PNGs"):
        with Context(), TestCase(
            format=MessageFormat.PYTHON,
            description="",
        ):
            svg_submission = generate_svg_byte_stream(config.source)
            png_submission = generate_png_image(svg_submission)

            svg_solution = generate_svg_byte_stream(config.solution_file)
            png_solution = generate_png_image(svg_solution)

            correct_pixels, total_pixels = diff_images(png_submission, png_solution)

            base64_submission = base64.b64encode(svg_submission).decode("utf-8")
            base64_solution = base64.b64encode(svg_solution).decode("utf-8")

            html = f"""
            <div style="display:inline-block;width:50%;">
                <p style="padding:10px">Submission:</p>
                <img
                    alt="submission result"
                    style="width:98%;background-color:#fff"
                    src="data:image/svg+xml;base64,{base64_submission}" />
            </div>
            <div style="display:inline-block;float:right;width:50%;">
                <p style="padding:10px">Solution:</p>
                <img
                    alt="solution result"
                    style="width:98%;background-color:#fff"
                    src="data:image/svg+xml;base64,{base64_solution}" />
            </div>
            """

            with Test(
                {
                    "format": MessageFormat.HTML,
                    "description": " ".join(html.split()),
                },
                f"{total_pixels}/{total_pixels} pixels correct",
            ) as test:
                test.generated = f"{correct_pixels}/{total_pixels} pixels correct"

                if correct_pixels < total_pixels:
                    test.status = config.translator.error_status(ErrorType.WRONG)
                else:
                    test.status = config.translator.error_status(ErrorType.CORRECT)
