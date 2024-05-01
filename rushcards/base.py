from collections import namedtuple
from enum import Enum
from pathlib import Path
import pprint
import sys


# Helper types
Orientation = Enum("Orientation", ["HORIZONTAL", "VERTICAL"])
Position = namedtuple("Position", ["x", "y"])
CarType = Enum("CarType", ["ESCAPE", "BLOCKING"])
Car = namedtuple("Car", ["type", "position", "size", "orientation"])
Puzzle = namedtuple("Puzzle", ["difficulty", "cars", "puzzle_def"])
Layout = namedtuple("Layout", ["rows", "cols"])

# Difficulties are integer values in the range 1 to DIFFICULTY_STEPS (inclusive).
DIFFICULTY_STEPS = 10

# Colors were sampled from the car tops on the official game instruction card.
BOARD_SIZE = 6
CAR_COLORS = {
    CarType.ESCAPE: {
        2: ["#EB2227"],
    },
    CarType.BLOCKING: {
        2: [
            "#90CB87",
            "#F6852A",
            "#23BAED",
            "#EF7DA1",
            "#6764AD",
            "#0F986C",
            "#D7D9DA",
            "#FBE4C2",
            "#FFF453",
            "#926455",
            "#8A8D09",
        ],
        3: [
            "#FCD404",
            "#A080BA",
            "#0B7CBF",
            "#07AF99",
        ],
    },
}

# The path to the puzzle database. This is hardcoded since it's included
# with the distribution.
PUZZLE_PATH = Path(__file__).parent / "puzzles.pickle"


def print_debug(text, debug):
    if debug:
        print(text, file=sys.stderr)


# A special case of print_debug() that works around a problem with namedtuples.
def print_puzzles_debug(puzzles, debug):
    if debug:
        # Need to use _asdict() to get pprint to work well with namedtuples.
        print("\n".join(pprint.pformat(p._asdict()) for p in puzzles), file=sys.stderr)
