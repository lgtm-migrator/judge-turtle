"""Turtle runtime patches."""

import sys
from abc import ABC
from io import StringIO
from types import TracebackType
from typing import Any, Literal

from svg_turtle import SvgTurtle  # noqa
from svg_turtle.canvas import Canvas  # noqa


class Patch(ABC):
    """A patch helper class that allows to enter and exit a patch."""

    def __init__(self):
        """Base class for patches, each patch is fully defined by a generator function."""
        self.generator = self.patch()

    def patch(self):
        """Patch generator."""
        yield

    def __enter__(self) -> Any:
        """Start generator when entering the 'with' block.

        Returns:
            Value yielded by the generator
        """
        return next(self.generator)

    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> Literal[False]:
        """Drop generator when leaving the 'with' block. This invokes the finally block in the generator.

        Returns:
            False: the patch 'with' block should not do any error handling.
        """
        self.generator = None

        return False  # don't handle any errors


class TurtlePatch(Patch):  # noqa: R0903
    """Patch the turtle module."""

    def patch(self):
        """Patch generator."""
        turtle_mod = sys.modules["turtle"]

        old_mainloop = turtle_mod.mainloop
        old_done = turtle_mod.done
        old_turtle = turtle_mod.Turtle
        try:
            SvgTurtle._screen = SvgTurtle._Screen(Canvas(1000, 500))  # noqa: W0212
            SvgTurtle._pen = SvgTurtle()  # noqa: W0212

            turtle_mod.mainloop = lambda: None
            turtle_mod.done = lambda: None
            turtle_mod.Turtle = SvgTurtle

            yield SvgTurtle._pen  # noqa: W0212
        finally:
            turtle_mod.mainloop = old_mainloop
            turtle_mod.done = old_done
            turtle_mod.Turtle = old_turtle


class TimePatch(Patch):  # noqa: R0903
    """Patch the time module."""

    def patch(self):
        """Patch generator."""
        time_module: Any = sys.modules["time"]
        old_sleep = time_module.sleep
        try:
            time_module.sleep = lambda x: None
            yield
        finally:
            time_module.sleep = old_sleep


class InOutPatch(Patch):  # noqa: R0903
    """Patch stdin, stdout, stderr."""

    def patch(self):
        """Patch generator."""
        old_in, old_out, old_err = sys.stdin, sys.stdout, sys.stderr
        try:
            sys.stdin, sys.stdout, sys.stderr = StringIO(), StringIO(), StringIO()
            yield sys.stdin, sys.stdout, sys.stderr
        finally:
            sys.stdin, sys.stdout, sys.stderr = old_in, old_out, old_err
