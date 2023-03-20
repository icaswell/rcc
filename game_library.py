"""Each config is a separate type of game!
"""

from piece import *

def validate_config(config):
    required_keys = ["board_height", "board_width", "card_draw_probability", "square_height", "square_width"]
    for key in required_keys:
        if key not in config:
            raise ValueError(f"config missing {key}")
    assert callable(config["card_draw_probability"])
    players = []
    for player, positions in config["initial_positions"].items():
        if player in players:
            raise ValueError(f"Duplicate player {player}")
        players.append(player)
        for (row, col), piece_generator in positions.items():
            assert 0 <= row < config["board_height"]
            assert 0 <= col < config["board_width"]
            assert callable(piece_generator)

STANDARD_CHESS = {
        "board_height": 8,
        "board_width": 8,
        "square_height": 8,
        "square_width": 16,
        "card_draw_probability": lambda turn_n: 0,
        "initial_positions": {
            "White": {
              (1, 0): lambda: Pawn(team="White", name=f"white_pawn_1"), 
              (1, 1): lambda: Pawn(team="White", name=f"white_pawn_2"), 
              (1, 2): lambda: Pawn(team="White", name=f"white_pawn_3"), 
              (1, 3): lambda: Pawn(team="White", name=f"white_pawn_4"), 
              (1, 4): lambda: Pawn(team="White", name=f"white_pawn_5"), 
              (1, 5): lambda: Pawn(team="White", name=f"white_pawn_6"), 
              (1, 6): lambda: Pawn(team="White", name=f"white_pawn_7"), 
              (1, 7): lambda: Pawn(team="White", name=f"white_pawn_8"), 
              (0, 0): lambda: Rook(team="White", name=f"white_rook_1"), 
              (0, 7): lambda: Rook(team="White", name=f"white_rook_2"), 
              (0, 1): lambda: Knight(team="White", name=f"white_knight_1"), 
              (0, 6): lambda: Knight(team="White", name=f"white_knight_2"), 
              (0, 2): lambda: Bishop(team="White", name=f"white_bishop_1"), 
              (0, 5): lambda: Bishop(team="White", name=f"white_bishop_2"), 
              (0, 4): lambda: Queen(team="White", name=f"white_queen"), 
              (0, 3): lambda: King(team="White", name=f"white_king"), 
            },
            "Black": {
              (6, 0): lambda: Pawn(team="Black", name=f"black_pawn_1"), 
              (6, 1): lambda: Pawn(team="Black", name=f"black_pawn_2"), 
              (6, 2): lambda: Pawn(team="Black", name=f"black_pawn_3"), 
              (6, 3): lambda: Pawn(team="Black", name=f"black_pawn_4"), 
              (6, 4): lambda: Pawn(team="Black", name=f"black_pawn_5"), 
              (6, 5): lambda: Pawn(team="Black", name=f"black_pawn_6"), 
              (6, 6): lambda: Pawn(team="Black", name=f"black_pawn_7"), 
              (6, 7): lambda: Pawn(team="Black", name=f"black_pawn_8"), 
              (7, 0): lambda: Rook(team="Black", name=f"black_rook_1"), 
              (7, 7): lambda: Rook(team="Black", name=f"black_rook_2"), 
              (7, 1): lambda: Knight(team="Black", name=f"black_knight_1"), 
              (7, 6): lambda: Knight(team="Black", name=f"black_knight_2"), 
              (7, 2): lambda: Bishop(team="Black", name=f"black_bishop_1"), 
              (7, 5): lambda: Bishop(team="Black", name=f"black_bishop_2"), 
              (7, 4): lambda: Queen(team="Black", name=f"black_queen"), 
              (7, 3): lambda: King(team="Black", name=f"black_king"), 
            }
        }
}

validate_config(STANDARD_CHESS)
