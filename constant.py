"""
Constants used throughout The Turing Game application.
This module centralizes all constant values to make maintenance easier.
"""

# Window and UI dimensions
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
CARD_EDITOR_WIDTH = 600
CARD_EDITOR_HEIGHT = 400
TEST_RUNNER_WIDTH = 800
TEST_RUNNER_HEIGHT = 600
TEST_RESULT_WIDTH = 400
TEST_RESULT_HEIGHT = 200
TEST_RESULT_FAILURE_HEIGHT = 250

# UI element sizes
PADDING = 50
BUTTON_HEIGHT = 50
TAB_HEIGHT = 50
BUTTON_WIDTH = 20
CARD_MIN_WIDTH = 300  # Estimated width of a card in pixels
CARD_COLUMN_WIDTH = 60  # Width of columns in card display
CELL_LABEL_WIDTH = 6  # Width of cell labels in cards
CELL_PADDING = 3  # Padding between cells

# Card display
MAX_CARDS_PER_ROW_MIN = 1
MAX_CARDS_PER_ROW_MAX = 6
CARD_HORIZONTAL_PADDING = 5
CARD_VERTICAL_PADDING = 5

# Tape display
TAPE_VISIBLE_CELLS_BEFORE = 7
TAPE_VISIBLE_CELLS_AFTER = 8
TAPE_PADDING_BEFORE = 50
TAPE_PADDING_AFTER = 50

# Colors
WHITE = "#FFFFFF"
BLACK = "#000000"
GRAY = "#C8C8C8"
DARK_GRAY = "#646464"
LIGHT_BLUE = "#6496FF"
LIGHT_GRAY = "#E6E6E6"
LIGHT_RED = "#FF6464"
SUCCESS_GREEN = "#90EE90"
HOVER_GREEN = "#70DA70"
FAILURE_RED = "#FFB6C1"

# Fonts
TITLE_FONT = ("Arial", 16, "bold")
HEADER_FONT = ("Arial", 12, "bold")
CARD_HEADER_FONT = ("Arial", 12, "bold")
CARD_CONTENT_FONT = ("Arial", 9, "bold")
NORMAL_FONT = ("Arial", 10)
SUCCESS_FONT = ("Arial", 12, "bold")
DETAILS_FONT = ("Arial", 10)
CHECKMARK_FONT = ("Arial", 18, "bold")

# TestRunner settings
SPEED_OPTIONS = [1, 5, 10, 20, 200, 1000]
DEFAULT_SPEED_INDEX = 1  # Start at 5x speed

# Movement directions
LEFT = "-1"
STAY = "0"
RIGHT = "1"

# Special states
HALT = "-1"

# File paths and naming
DATA_DIR = "data"
CARD_DIR_NAME = "card"
CARD_PREFIX = "c"
CARD_EXTENSION = ".json"
PROGRESS_FILENAME = "progress.json"
PROBLEM_DESCRIPTION_FILENAME = "problems_description.json"

# Symbols
CHECKMARK = "✓"
CROSS = "✗"
LEFT_ARROW = "←"
RIGHT_ARROW = "→"
DASH = "-"

# Tab indices
INFO_TAB_INDEX = 0
CARDS_TAB_INDEX = 1
TESTS_TAB_INDEX = 2