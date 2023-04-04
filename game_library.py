"""Each config is a separate type of game!

Note: the config validator ensures that there cannot be any square co-occupation.
This can happen later in the game of course, but it is inadvisable as a starting position.
"""

import random

from piece import *
from card import Deck, TEST_DECK, ALL_CARDS

def validate_config(config):
    required_keys = ["board_height", "initial_positions", "board_width", "die_roll_function", "square_height", "square_width", "players", "deck", "players_orientations"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"config missing {key}")
    extra_keys =  set(config.keys()) - set(required_keys)
    if extra_keys:
        raise ValueError(f"extra keys: {extra_keys}")
    for k in config["players"]:
        assert(isinstance(k, str))
    assert len(config["players"]) == len(config["players_orientations"])
    for p, o in config["players_orientations"].items():
        assert o in ["n", "e", "s", "w"]
    assert callable(config["die_roll_function"])
    seen_positions = set()
    for (row, col), piece_generator in config["initial_positions"]:
      assert 0 <= row < config["board_height"]
      assert 0 <= col < config["board_width"]
      assert callable(piece_generator)
      if (row, col)  in seen_positions:
          print(f"{(row, col)} already is occupied!")
          assert False
      seen_positions.add((row, col))

# there is some redundancy with the initial_positions map with the team= parameter
# also with the players key
STANDARD_CHESS = {
        "players": ["White", "Black"],
        "players_orientations": {"White": "s", "Black": "n"},  # TODO unify above?
        "board_height": 8,
        "board_width": 8,
        "square_height": 8,
        "square_width": 16,
        "die_roll_function": lambda turn_n: 0,  # never draw a card
        "deck": lambda: Deck([]), # initialize an empty, unused deck
        "initial_positions": [
              ((1, 0), lambda: Pawn(team="White", name=f"white_pawn_1")),
              ((1, 1), lambda: Pawn(team="White", name=f"white_pawn_2")),
              ((1, 2), lambda: Pawn(team="White", name=f"white_pawn_3")),
              ((1, 3), lambda: Pawn(team="White", name=f"white_pawn_4")),
              ((1, 4), lambda: Pawn(team="White", name=f"white_pawn_5")),
              ((1, 5), lambda: Pawn(team="White", name=f"white_pawn_6")),
              ((1, 6), lambda: Pawn(team="White", name=f"white_pawn_7")),
              ((1, 7), lambda: Pawn(team="White", name=f"white_pawn_8")),
              ((0, 0), lambda: Rook(team="White", name=f"white_rook_1")),
              ((0, 7), lambda: Rook(team="White", name=f"white_rook_2")),
              ((0, 1), lambda: Knight(team="White", name=f"white_knight_1")),
              ((0, 6), lambda: Knight(team="White", name=f"white_knight_2")),
              ((0, 2), lambda: Bishop(team="White", name=f"white_bishop_1")),
              ((0, 5), lambda: Bishop(team="White", name=f"white_bishop_2")),
              ((0, 4), lambda: Queen(team="White", name=f"white_queen")),
              ((0, 3), lambda: King(team="White", name=f"white_king")),
              ((6, 0), lambda: Pawn(team="Black", name=f"black_pawn_1")),
              ((6, 1), lambda: Pawn(team="Black", name=f"black_pawn_2")),
              ((6, 2), lambda: Pawn(team="Black", name=f"black_pawn_3")),
              ((6, 3), lambda: Pawn(team="Black", name=f"black_pawn_4")),
              ((6, 4), lambda: Pawn(team="Black", name=f"black_pawn_5")),
              ((6, 5), lambda: Pawn(team="Black", name=f"black_pawn_6")),
              ((6, 6), lambda: Pawn(team="Black", name=f"black_pawn_7")),
              ((6, 7), lambda: Pawn(team="Black", name=f"black_pawn_8")),
              ((7, 0), lambda: Rook(team="Black", name=f"black_rook_1")),
              ((7, 7), lambda: Rook(team="Black", name=f"black_rook_2")),
              ((7, 1), lambda: Knight(team="Black", name=f"black_knight_1")),
              ((7, 6), lambda: Knight(team="Black", name=f"black_knight_2")),
              ((7, 2), lambda: Bishop(team="Black", name=f"black_bishop_1")),
              ((7, 5), lambda: Bishop(team="Black", name=f"black_bishop_2")),
              ((7, 4), lambda: Queen(team="Black", name=f"black_queen")),
              ((7, 3), lambda: King(team="Black", name=f"black_king")),
              ]
}

RCC = {
        "players": ["White", "Black"],
        "players_orientations": {"White": "s", "Black": "n"},  # TODO unify above?
        "board_height": 8,
        "board_width": 8,
        "square_height": 8,
        "square_width": 16,
        "die_roll_function": lambda turn_n: 1 if not turn_n else random.randint(1, 6),
        "deck": lambda: Deck(list(ALL_CARDS.values())),
        "initial_positions": [
              ((1, 0), lambda: Pawn(team="White", name=f"white_pawn_1")),
              ((1, 1), lambda: Pawn(team="White", name=f"white_pawn_2")),
              ((1, 2), lambda: Pawn(team="White", name=f"white_pawn_3")),
              ((1, 3), lambda: Pawn(team="White", name=f"white_pawn_4")),
              ((1, 4), lambda: Pawn(team="White", name=f"white_pawn_5")),
              ((1, 5), lambda: Pawn(team="White", name=f"white_pawn_6")),
              ((1, 6), lambda: Pawn(team="White", name=f"white_pawn_7")),
              ((1, 7), lambda: Pawn(team="White", name=f"white_pawn_8")),
              ((0, 0), lambda: Rook(team="White", name=f"white_rook_1")),
              ((0, 7), lambda: Rook(team="White", name=f"white_rook_2")),
              ((0, 1), lambda: Knight(team="White", name=f"white_knight_1")),
              ((0, 6), lambda: Knight(team="White", name=f"white_knight_2")),
              ((0, 2), lambda: Bishop(team="White", name=f"white_bishop_1")),
              ((0, 5), lambda: Bishop(team="White", name=f"white_bishop_2")),
              ((0, 4), lambda: Queen(team="White", name=f"white_queen")),
              ((0, 3), lambda: King(team="White", name=f"white_king")),
              ((6, 0), lambda: Pawn(team="Black", name=f"black_pawn_1")),
              ((6, 1), lambda: Pawn(team="Black", name=f"black_pawn_2")),
              ((6, 2), lambda: Pawn(team="Black", name=f"black_pawn_3")),
              ((6, 3), lambda: Pawn(team="Black", name=f"black_pawn_4")),
              ((6, 4), lambda: Pawn(team="Black", name=f"black_pawn_5")),
              ((6, 5), lambda: Pawn(team="Black", name=f"black_pawn_6")),
              ((6, 6), lambda: Pawn(team="Black", name=f"black_pawn_7")),
              ((6, 7), lambda: Pawn(team="Black", name=f"black_pawn_8")),
              ((7, 0), lambda: Rook(team="Black", name=f"black_rook_1")),
              ((7, 7), lambda: Rook(team="Black", name=f"black_rook_2")),
              ((7, 1), lambda: Knight(team="Black", name=f"black_knight_1")),
              ((7, 6), lambda: Knight(team="Black", name=f"black_knight_2")),
              ((7, 2), lambda: Bishop(team="Black", name=f"black_bishop_1")),
              ((7, 5), lambda: Bishop(team="Black", name=f"black_bishop_2")),
              ((7, 4), lambda: Queen(team="Black", name=f"black_queen")),
              ((7, 3), lambda: King(team="Black", name=f"black_king")),
              ]
}


TEST_GAME_CONFIG = {
        "players": ["White", "Black"],
        "players_orientations": {"White": "s", "Black": "n"},  # TODO unify above?
        "board_height": 8,
        "board_width": 8,
        "square_height": 8,
        "square_width": 16,
        "die_roll_function": lambda turn_n: 1 if not turn_n else random.randint(1, 16),
        "deck": lambda: Deck(TEST_DECK, shuffle=False),
        "initial_positions": [
              ((1, 0), lambda: Pawn(team="White", name=f"white_pawn_1")),
              ((1, 1), lambda: Pawn(team="White", name=f"white_pawn_2")),
              ((1, 2), lambda: Pawn(team="White", name=f"white_pawn_3")),
              ((1, 3), lambda: Pawn(team="White", name=f"white_pawn_4")),
              ((2, 4), lambda: Pawn(team="White", name=f"white_pawn_5")),
              ((3, 5), lambda: Pawn(team="White", name=f"white_pawn_6")),
              ((1, 6), lambda: Pawn(team="White", name=f"white_pawn_7")),
              ((4, 7), lambda: Pawn(team="White", name=f"white_pawn_8")),
              ((0, 0), lambda: Rook(team="White", name=f"white_rook_1")),
              ((0, 7), lambda: Rook(team="White", name=f"white_rook_2")),
              ((4, 4), lambda: Knight(team="White", name=f"white_knight_1")),
              ((0, 6), lambda: Knight(team="White", name=f"white_knight_2")),
              ((0, 2), lambda: Bishop(team="White", name=f"white_bishop_1")),
              ((0, 5), lambda: Bishop(team="White", name=f"white_bishop_2")),
              ((6, 4), lambda: Queen(team="White", name=f"white_queen")),
              ((0, 3), lambda: King(team="White", name=f"white_king")),
              ((6, 0), lambda: Pawn(team="Black", name=f"black_pawn_1")),
              ((6, 1), lambda: Pawn(team="Black", name=f"black_pawn_2")),
              ((6, 2), lambda: Pawn(team="Black", name=f"black_pawn_3")),
              ((5, 3), lambda: Pawn(team="Black", name=f"black_pawn_4")),
              ((5, 4), lambda: Pawn(team="Black", name=f"black_pawn_5")),
              ((4, 5), lambda: Pawn(team="Black", name=f"black_pawn_6")),
              ((6, 6), lambda: Pawn(team="Black", name=f"black_pawn_7")),
              ((6, 7), lambda: Pawn(team="Black", name=f"black_pawn_8")),
              ((4, 0), lambda: Rook(team="Black", name=f"black_rook_1")),
              ((7, 7), lambda: Rook(team="Black", name=f"black_rook_2")),
              ((1, 4), lambda: Knight(team="Black", name=f"black_knight_1")),
              ((7, 6), lambda: Knight(team="Black", name=f"black_knight_2")),
              ((7, 2), lambda: Bishop(team="Black", name=f"black_bishop_1")),
              ((7, 5), lambda: Bishop(team="Black", name=f"black_bishop_2")),
              ((7, 4), lambda: Queen(team="Black", name=f"black_queen")),
              ((7, 3), lambda: King(team="Black", name=f"black_king")),
              ((2, 6), lambda: ZamboniPiece(team="Zamboni", name=f"Zambonus")),
              ((2, 2), lambda: SwapperPiece(team="Swapper", name=f"swapper")),
              # ((3, 1), lambda: RabbitPiece(team="Black", name=f"rabbit")),
              # ((4, 1), lambda: RabbitPiece(team="autonomous", name=f"rabbit")),
              # ((5, 1), lambda: RabbitPiece(team="white", name=f"rabbit")),
        ]
}

validate_config(STANDARD_CHESS)
validate_config(RCC)
validate_config(TEST_GAME_CONFIG)
