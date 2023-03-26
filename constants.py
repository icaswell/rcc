import enum

# an "enum"
MODES_OF_MOVEMENT = ["normal", "jumping"]

class InteractionType(enum.Enum):
    # This piece takes whatever it lands on.
    TAKING = 1
    # This piece will push the occupant in the direction
    # of the movement, and all other pieces in the line of movement.
    PUSHING = 2
    # This piece swaps with whatever it lands on.
    SWAPPING = 3

COLOR_SCHEME = {
  # primarily used in game.py:
  "SELECT_COLOR": "pink_highlight",
  "PIECE_MOVE_SELECT_COLOR": "yellow_highlight",
  "PIECE_TAKABLE_SELECT_COLOR": "red_highlight",
  "GRAVEYARD_HEADER_COLOR": "green_highlight",
  "ANNOTATE_COLOR": "teal_highlight",
  "MESSAGE_COLOR": "green",

  # primarily used in board.py:
  "BLACK_SQUARE_COLOR": "black_highlight",
  "WHITE_SQUARE_COLOR": "white_highlight",
  "BORDER_COLOR": "red_highlight",
}


# Command loop exceptions
NORENDER = "norender"
BREAK = "break"

# CENTER_FOUR_SQUARE_NAMES = "d4 d5 e4 e5".split()

DEV_MODE = []


