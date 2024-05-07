# Rush Cards

![Sample Rush Cards puzzle](https://raw.githubusercontent.com/marfire/rushcards/main/docs/images/sample.png)

Rush Cards provides a Python command line application for generating puzzle cards 
for the game [Rush Hour](https://en.wikipedia.org/wiki/Rush_Hour_(puzzle)). It 
builds on [a project](https://www.michaelfogleman.com/rush/) by Michael Fogelman to 
identify all possible Rush Hour puzzles. Put simply, this project takes that 
database of puzzles, keeps the puzzles that can be expressed in the standard board 
game, maps a 1-10 difficulty scale onto them, and provides an interface to generate 
endless puzzle cards.

## Installation

Make sure you have [Python](https://www.python.org/downloads/) installed. Then run:

    $ pip install rushcards

## Usage

Cards are generated from the command line using either `rushcards` or `python -m 
rushcards`.

    $ rushcards 5

This will generate a single card representing a random puzzle with difficulty `5`; save 
the PNG image to a temporary directory; then open it in a native image-viewing 
application chosen by the operating system.

In addition to numbers `1` through `10` you can also specify `_` (underscore) to 
choose a random difficulty.

To put multiple cards into the same image use a comma-separated list of difficulties.

    $ # Create a single image with 6 puzzles in a 2x3 layout.
    $ rushcards 2,_,4,5,6,10

A compact layout will be chosen automatically, but you can also specify a layout 
with the `--layout` option.

    $ # Create a single image with 6 rows of 1 puzzle each.
    $ rushcards 2,_,4,5,6,10 --layout 6x1

As a special case, if you specify a single difficulty but a larger layout, enough 
puzzles with that difficulty will be chosen to fill the layout.

    $ # Create an image with 8 puzzles of difficulty 5.
    $ rushcards 5 --layout 2x4.

Use the `--outfile` option to specify an output file.

    $ # Save the image to a file.
    $ rushcards 5 --outfile puzzle.png

Specify the file as `-` (hyphen) to output to stdout.

    $ # Send the image to stdout and pipe it to another program.
    $ rushcards 5 --outfile - | wc -c
    7987

Note that when writing to stdout the image can't be opened automatically. You can 
also manually suppress opening the file with the `--no-open` option.

    $ # Write the puzzle to a file but don't open it.
    $ rushcards 5 --outfile puzzle.png --no-open

## Notes

The puzzle cards do not show solutions. The puzzle database doesn't include them, 
and in any case they aren't really necessary to enjoy the game.

The pixel size of the PNG image is fixed to a fairly arbitrary value since image 
viewing applications all have the ability to scale as needed for viewing or printing.

This package also includes the `mkpuzzles` tool (invoked with 
`python -m rushcards.tools.mkpuzzles`). This was used to filter the original Rush Hour 
puzzle database, assign difficulties, and save the data for later use with the 
`rushcards` application.

In total the program can generate 443,266 distinct puzzles.
