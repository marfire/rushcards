from collections import defaultdict
import pickle
import random
import string
from .base import (
    BOARD_SIZE,
    PUZZLE_PATH,
    Position,
    Orientation,
    CarType,
    Car,
    Puzzle,
)


# Might as well load the puzzle database at import time since there's
# nothing this module can do without it.
with open(PUZZLE_PATH, "rb") as puzzle_file:
    all_puzzles = pickle.load(puzzle_file)


# Given the string board definition for the puzzle we return a list of
# the Car objects that represent it.
#
# The board_def format is defined in https://www.michaelfogleman.com/rush/,
# but is essentially a 36-character string representing a 6x6 board, with each
# car being represented by an uppercase letter ("A" for the escape car).
def get_cars(board_def):
    # Create a dictionary mapping car codes to the indices they appear at.
    car_indices = defaultdict(list)
    for i, code in enumerate(board_def):
        if code == "o":
            continue

        assert code in string.ascii_uppercase, code
        car_indices[code].append(i)

    # For each car code create a Car object.
    cars = []
    for code, indices in car_indices.items():
        car_type = CarType.ESCAPE if code == "A" else CarType.BLOCKING
        position = Position(indices[0] % BOARD_SIZE, indices[0] // BOARD_SIZE)
        size = len(indices)
        orientation = (
            Orientation.HORIZONTAL
            if indices[1] - indices[0] == 1
            else Orientation.VERTICAL
        )

        cars.append(Car(car_type, position, size, orientation))

    return cars


# Choose a random puzzle with the given difficulty.
#
# To avoid generating duplicate puzzles we destructively remove the chosen
# puzzle from the all_puzzles data structure before returning it.
def choose_puzzle(difficulty):
    difficulty_puzzles = all_puzzles[
        difficulty
    ]  # Will raise ValueError if we run out of puzzles
    index = random.randint(0, len(difficulty_puzzles) - 1)

    puzzle = difficulty_puzzles.pop(index)
    return puzzle


# Choose a random puzzle_def for the given difficulty, then turn it into
# a Puzzle data structure.
#
# Note that a puzzle is defined entirely by the placement of the cars. The
# difficulty and puzzle_def attributes are provided for display and
# debugging.
def get_puzzle(difficulty):
    puzzle_def = choose_puzzle(difficulty)
    _, board_def, _ = puzzle_def.split()
    cars = get_cars(board_def)

    return Puzzle(difficulty=difficulty, cars=cars, puzzle_def=puzzle_def)


# Return one Puzzle for each of the provided difficulty levels.
def get_puzzles(difficulties):
    return [get_puzzle(difficulty) for difficulty in difficulties]
