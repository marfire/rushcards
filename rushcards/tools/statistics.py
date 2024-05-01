import argparse
import pickle
from ..base import PUZZLE_PATH


# Show the number of available puzzles and number of steps for each difficulty level.
def print_statistics():
    with open(PUZZLE_PATH, "rb") as puzzle_file:
        all_puzzles = pickle.load(puzzle_file)

    for difficulty in sorted(all_puzzles):
        puzzle_defs = all_puzzles[difficulty]
        steps = set(int(p.split(" ", 1)[0]) for p in puzzle_defs)

        steps_str = ", ".join(str(s) for s in sorted(steps))
        print(
            f"Difficulty {difficulty} has {len(puzzle_defs)} puzzles and includes steps {steps_str}."
        )

    print(f"Total puzzles: {sum(len(pd) for pd in all_puzzles.values())}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Show statistics about the puzzle database."
    )
    parser.parse_args()

    print_statistics()
