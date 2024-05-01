import argparse
import math
from pathlib import Path
import random
import sys
from tempfile import NamedTemporaryFile
import webbrowser
from .base import (
    DIFFICULTY_STEPS,
    Layout,
    print_debug,
    print_puzzles_debug,
)
from .puzzle import get_puzzles
from .draw import draw_puzzles


# The format to use for saving the output images. Must be understood by
# PIL and usable as a file suffix.
IMAGE_FORMAT = "PNG"


# This function does the work of the application. It takes the arguments
# provided by the CLI, then generates, draws, and saves the puzzles.
def generate_puzzles(difficulties, layout, outfile, do_open, debug):
    puzzles = get_puzzles(difficulties)
    print_puzzles_debug(puzzles, debug)

    image_bytes = draw_puzzles(puzzles, layout, IMAGE_FORMAT, debug)

    print_debug(f"Writing to {outfile.name}", debug)
    with outfile:
        outfile.write(image_bytes)

    if do_open:
        file_uri = Path(outfile.name).resolve().as_uri()
        print_debug(f"Opening {file_uri}", debug)
        webbrowser.open_new_tab(file_uri)


# Converts string difficulties into a list of integers. The special case of
# "_" is converted to None.
def difficulty_type(difficulty_str):
    difficulties_parts = [d.strip() for d in difficulty_str.split(",")]
    difficulties_raw = [None if d == "_" else int(d) for d in difficulties_parts]

    if any(type(d) is int and not 1 <= d <= DIFFICULTY_STEPS for d in difficulties_raw):
        raise ValueError(f"Difficulty must be between 1 and {DIFFICULTY_STEPS}")

    return difficulties_raw


# Converts the layout string into a Layout instance.
def layout_type(layout_str):
    layout_parts = layout_str.split("x")
    if len(layout_parts) != 2:
        raise ValueError("Layout must have format RxC")

    layout = Layout(int(layout_parts[0]), int(layout_parts[1]))

    if layout.rows < 1 or layout.cols < 1:
        raise ValueError(f"Layout elements must be positive")

    return layout


def rushcards_cli():
    parser = argparse.ArgumentParser(
        prog="rushcards", description="Generate puzzle cards for the game Rush Hour."
    )
    parser.add_argument(
        "difficulty",
        type=difficulty_type,
        help=f"comma-separated list of difficulties (1-{DIFFICULTY_STEPS} or _ for random)",
    )
    parser.add_argument(
        "-l",
        "--layout",
        type=layout_type,
        help="card layout expressed as [rows]x[cols]",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        help="image output file (use - for stdout or leave blank for a temporary file)",
    )
    parser.add_argument(
        "-n",
        "--no-open",
        action="store_true",
        help="don't display the image file after generation",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    args = parser.parse_args()

    if args.layout and len(args.difficulty) > (args.layout.rows * args.layout.cols):
        parser.error("Too many puzzles requested for given layout")

    # If there is only one difficulty but layout is provided, create as many
    # puzzles with that difficulty as necessary to fill the layout.
    difficulties_raw = args.difficulty
    if len(difficulties_raw) == 1 and args.layout:
        difficulties_raw *= args.layout.rows * args.layout.cols

    # Insert random difficulties where requested.
    difficulties = [
        d if d is not None else random.randrange(1, DIFFICULTY_STEPS + 1)
        for d in difficulties_raw
    ]

    # If a layout wasn't provided, create one to fit the requested number of puzzles
    # (showing preference for more columns and fewer rows).
    layout = args.layout
    if not layout:
        cols = int(math.ceil(math.sqrt(len(difficulties))))
        rows = int(math.ceil(len(difficulties) / cols))
        layout = Layout(rows, cols)

    do_open = not args.no_open

    # There are three possible write destinations.
    if args.outfile == "-":
        outfile = open(sys.stdout.fileno(), "wb", closefd=False)
        do_open = False  # Can't open data passed to stdout
    elif args.outfile:
        outfile = open(args.outfile, "wb")
    else:
        outfile = NamedTemporaryFile(suffix=f".{IMAGE_FORMAT.lower()}", delete=False)

    generate_puzzles(difficulties, layout, outfile, do_open, args.debug)
