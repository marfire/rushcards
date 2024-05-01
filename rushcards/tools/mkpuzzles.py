import argparse
from collections import defaultdict, Counter
import pickle
import textwrap
from ..base import BOARD_SIZE, DIFFICULTY_STEPS, CAR_COLORS, PUZZLE_PATH


# The default value for the exponent used in the power function that scales
# the difficulty according to the number of required steps. A value of 1
# corresponds to a linear scale. This default value was chosen after a bit
# of experimentation.
DIFFICULTY_EXPONENT = 0.64


# Return a dictionary mapping a car size to the number of
# cars of that size available.
def get_allowed_cars(car_def):
    allowed_cars = defaultdict(int)
    for sizes in car_def.values():
        for size, colors in sizes.items():
            allowed_cars[size] += len(colors)

    return allowed_cars


# A filter that returns True if the puzzle represented by car_sizes
# can be achieved in the game represented by allowed_cars.
def cars_valid(car_sizes, allowed_cars):
    for size, number in car_sizes.items():
        if size not in allowed_cars:
            return False
        if number > allowed_cars[size]:
            return False

    return True


# A general approach to scaling a value from one integer scale to another
# according to a power function. Used to turn the number of steps needed
# for a puzzle into a difficulty.
def get_scaled_value(value_in, min_in, max_in, min_out, max_out, power):
    assert min_in <= value_in <= max_in, value_in

    # Normalize the input range to a fraction from [0 to 1).
    fraction_in = (value_in - min_in) / (max_in - min_in + 1)

    # Use the power function to adjust the fraction.
    fraction_out = fraction_in**power

    # Rescale the fraction to the output range
    value_out = int(fraction_out * (max_out - min_out + 1)) + min_out
    assert min_out <= value_out <= max_out, value_out

    return value_out


# Take the list of puzzles provided in infile, filter out the ones that
# can't be represented in the standard board game, assign difficulties
# to the ones that can, then return them in a convenient data structure.
#
# Note that the input puzzles described in https://www.michaelfogleman.com/rush/
# are just the "interesting" ones. We could generate many more puzzles by
# including the uninteresting variants of each one, but that wouldn't add
# much value.
#
# Note that this excludes some puzzles that would be possible with the
# standard game plus an expansion pack, since some expansion packs provide
# an additional car. Not worth worrying about.
def get_puzzles(infile, exponent):
    allowed_cars = get_allowed_cars(CAR_COLORS)

    # Create a mapping from steps to a list of valid puzzle definitions.
    puzzles_by_steps = defaultdict(list)
    with infile:
        for line in infile:
            puzzle_def = line.rstrip()  # get rid of trailing newline
            steps_str, board_def, _ = puzzle_def.split()

            # Ignore puzzles with the wrong size board.
            if len(board_def) != BOARD_SIZE * BOARD_SIZE:
                continue

            # Ignore puzzles with walls.
            code_nums = Counter(board_def)
            if "x" in code_nums:
                continue

            # Ignore puzzles that use more cars than we have available.
            car_sizes = Counter(
                size for code, size in code_nums.items() if code.isupper()
            )
            if not cars_valid(car_sizes, allowed_cars):
                continue

            # Ignore the puzzle with just 1 step, since that's insultingly easy.
            steps = int(steps_str)
            assert steps > 0, steps
            if steps == 1:
                continue

            puzzles_by_steps[steps].append(puzzle_def)

    # Create a mapping from difficulties to a list of valid puzzle definitions.
    max_steps = max(puzzles_by_steps)
    puzzles_by_difficulty = defaultdict(list)
    for steps, puzzle_defs in puzzles_by_steps.items():
        difficulty = get_scaled_value(
            steps, 2, max_steps, 1, DIFFICULTY_STEPS, exponent
        )

        puzzles_by_difficulty[difficulty].extend(puzzle_defs)

    return puzzles_by_difficulty


# Get the valid puzzles and save the data structure to a Pickle file.
def make_puzzles(infile, outfile, exponent):
    puzzles = get_puzzles(infile, exponent)

    # Save the mapping to a pickle file.
    with outfile:
        pickle.dump(puzzles, outfile)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            Generate the puzzle database used by the rushcards application.
            
            Given a source puzzle file, this will produce a database mapping
            difficulties to lists of puzzles for all puzzles that can be represented
            by the standard Rush Hour board game. The difficulties are based on 
            the number of steps required to solve a puzzle, and the mapping
            is done according to a power function.
            
            By default this saves the database (in the Pickle format) to the hardcoded
            location expected by the rushcards application. Use --outfile to choose
            a different location.
            
            See https://www.michaelfogleman.com/rush/ for a description of the
            expected input file format.
            """
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "infile",
        type=argparse.FileType("r"),
        help="the input puzzle file (use - for stdin)",
    )
    parser.add_argument(
        "-o",
        "--outfile",
        type=argparse.FileType("wb"),
        default=str(PUZZLE_PATH),  # Has to be a string to get passed to FileType
        help="the output puzzle file (use - for stdout)",
    )
    parser.add_argument(
        "-e",
        "--exponent",
        type=float,
        default=DIFFICULTY_EXPONENT,
        help="the exponent to use for the power function",
    )
    args = parser.parse_args()

    make_puzzles(args.infile, args.outfile, args.exponent)
