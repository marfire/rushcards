import copy
from io import BytesIO
import random
from PIL import Image, ImageDraw
from .base import BOARD_SIZE, CAR_COLORS, Orientation


# All sizes are based off of CELL_WIDTH. This is a constant since we can rely
# on image viewers and printers to scale the final image as desired.
CELL_WIDTH = 100

BOARD_WIDTH = BOARD_SIZE * CELL_WIDTH
BOARD_BORDER_WIDTH = 4
BOARD_GRID_WIDTH = 2
PAGE_BACKGROUND_COLOR = "#FFFFFF"
BOARD_BORDER_COLOR = "#909090"
BOARD_GRID_COLOR = "#E8E8E8"
EXIT_SIZE = CELL_WIDTH // 6
BOARD_PADDING = EXIT_SIZE

CAR_PADDING = CELL_WIDTH // 12
CAR_WIDTH = CELL_WIDTH - 2 * CAR_PADDING
CAR_BORDER_RADIUS = CAR_WIDTH // 4
BOARD_BORDER_RADIUS = CAR_BORDER_RADIUS + CAR_PADDING  # Match rounded corners

TEXT_COLOR = "#555555"
TEXT_BOX_HEIGHT = CELL_WIDTH  # This is fairly arbitrary
TEXT_BOX_TOP_PADDING = CELL_WIDTH // 6
TEXT_BOX_LEFT_PADDING = CELL_WIDTH // 8
TEXT_FONT_SIZE = CELL_WIDTH // 3
TEXT_DEBUG_FONT_SIZE = CELL_WIDTH // 5


# Draw the board border, grid lines, and exit mark.
def draw_board(drawer, debug):
    # Draw the grid lines first so board border is drawn over them.
    for line_num in range(1, BOARD_SIZE):
        # Draw both a horizontal and a vertical line.
        line_position = line_num * CELL_WIDTH - BOARD_GRID_WIDTH // 2
        drawer.line(
            (0, line_position, BOARD_WIDTH, line_position),
            fill=BOARD_GRID_COLOR,
            width=BOARD_GRID_WIDTH,
        )
        drawer.line(
            (line_position, 0, line_position, BOARD_WIDTH),
            fill=BOARD_GRID_COLOR,
            width=BOARD_GRID_WIDTH,
        )

    # Draw the border. Make the fill transparent so the grid lines show through.
    drawer.rounded_rectangle(
        (0, 0, BOARD_WIDTH, BOARD_WIDTH),
        fill=(0, 0, 0, 0),
        outline=BOARD_BORDER_COLOR,
        width=BOARD_BORDER_WIDTH,
        radius=BOARD_BORDER_RADIUS,
    )

    # Draw the exit mark (a triangle) at the right end of the third row.
    start_x = BOARD_WIDTH
    start_y = int(CELL_WIDTH * 2.5) - EXIT_SIZE
    drawer.polygon(
        (
            (start_x, start_y),
            (start_x, start_y + 2 * EXIT_SIZE),
            (start_x + EXIT_SIZE, start_y + EXIT_SIZE),
        ),
        fill=BOARD_BORDER_COLOR,
    )


# Draw the car with the provided color.
def draw_car(drawer, car, color):
    # The start pixel is determined solely by the Car's position but
    # the end pixel depends on its orientation as well.
    start_x = car.position.x * CELL_WIDTH + CAR_PADDING
    start_y = car.position.y * CELL_WIDTH + CAR_PADDING
    end_x = (
        (car.position.x + car.size) * CELL_WIDTH - CAR_PADDING
        if car.orientation is Orientation.HORIZONTAL
        else start_x + CAR_WIDTH
    )
    end_y = (
        (car.position.y + car.size) * CELL_WIDTH - CAR_PADDING
        if car.orientation is Orientation.VERTICAL
        else start_y + CAR_WIDTH
    )

    drawer.rounded_rectangle(
        (start_x, start_y, end_x, end_y),
        fill=color,
        radius=CAR_BORDER_RADIUS,
    )


# For each car in cars, choose a random allowable color and then draw
# the car with that color.
def draw_cars(drawer, cars, debug):
    # Create a copy of the available colors for each puzzle since we
    # remove the chosen colors as we go to avoid duplicates.
    colors = copy.deepcopy(CAR_COLORS)
    for car in cars:
        color_options = colors[car.type][car.size]
        color = color_options.pop(random.randrange(len(color_options)))
        draw_car(drawer, car, color)


# Draw the puzzle text. This is just the difficulty unless debug=True, in
# which case we also draw the puzzle_def.
def draw_text(drawer, puzzle, debug):
    text = f"Difficulty: {puzzle.difficulty}"

    # Just use the default font, it's not worth packaging one.
    drawer.text((TEXT_BOX_LEFT_PADDING, TEXT_BOX_TOP_PADDING), text, fill=TEXT_COLOR, font_size=TEXT_FONT_SIZE)

    if debug:
        debug_text = puzzle.puzzle_def
        drawer.text(
            (TEXT_BOX_LEFT_PADDING, TEXT_BOX_TOP_PADDING * 2 + TEXT_FONT_SIZE),
            debug_text,
            fill=TEXT_COLOR,
            font_size=TEXT_DEBUG_FONT_SIZE,
        )


# Return an Image representing a single puzzle. Draw the board, then the cars, then
# the difficulty text. For convenience we draw different parts as separate images and
# then combine them in the end.
def draw_puzzle(puzzle, debug):
    board_image = Image.new(
        "RGB", (BOARD_WIDTH + EXIT_SIZE, BOARD_WIDTH), PAGE_BACKGROUND_COLOR
    )
    board_drawer = ImageDraw.Draw(board_image, mode="RGBA")
    draw_board(board_drawer, debug)
    draw_cars(board_drawer, puzzle.cars, debug)

    text_image = Image.new("RGB", (BOARD_WIDTH, TEXT_BOX_HEIGHT), PAGE_BACKGROUND_COLOR)
    text_drawer = ImageDraw.Draw(text_image, mode="RGBA")
    draw_text(text_drawer, puzzle, debug)

    # Before saving we want to add padding on the left and top matching the right
    # so that the final image is centered.
    final_image = Image.new(
        "RGB",
        (
            BOARD_PADDING + BOARD_WIDTH + EXIT_SIZE,
            BOARD_PADDING + BOARD_WIDTH + TEXT_BOX_HEIGHT,
        ),
        PAGE_BACKGROUND_COLOR,
    )
    final_image.paste(board_image, (BOARD_PADDING, BOARD_PADDING))
    final_image.paste(text_image, (BOARD_PADDING, BOARD_PADDING + BOARD_WIDTH))
    return final_image


# Return a single image (as a string of bytes) showing all the puzzles
# represented by puzzles in the layout represented by layout.
def draw_puzzles(puzzles, layout, image_format, debug):
    assert len(puzzles) == layout.rows * layout.cols, puzzles

    # Draw an image for each puzzle.
    puzzle_images = [draw_puzzle(puzzle, debug) for puzzle in puzzles]

    # Create a composite image with each puzzle image placed as specified by layout.
    puzzle_size = puzzle_images[0].size  # Assumes all images are the same size
    composite_size = (puzzle_size[0] * layout.cols, puzzle_size[1] * layout.rows)
    composite_image = Image.new("RGB", composite_size, PAGE_BACKGROUND_COLOR)
    for i, puzzle_image in enumerate(puzzle_images):
        position = (
            (i % layout.cols) * puzzle_size[0],
            (i // layout.cols) * puzzle_size[1],
        )
        composite_image.paste(puzzle_image, position)

    # Save the composite image as a byte stream and return it.
    image_bytes = BytesIO()
    composite_image.save(image_bytes, format=image_format)
    return image_bytes.getvalue()
