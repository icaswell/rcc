"""Each config is a separate type of game!
"""

from piece import *
STANDARD_CHESS = {
        "board_height": 8,
        "board_width": 8,
        "card_draw_probability": lambda turn_n: 0,
        "initial_positions": {
            "White": {
              (1, 0): Pawn(team="White", name=f"white_pawn_1"), 
              (1, 1): Pawn(team="White", name=f"white_pawn_2"), 
              (1, 2): Pawn(team="White", name=f"white_pawn_3"), 
              (1, 3): Pawn(team="White", name=f"white_pawn_4"), 
              (1, 4): Pawn(team="White", name=f"white_pawn_5"), 
              (1, 5): Pawn(team="White", name=f"white_pawn_6"), 
              (1, 6): Pawn(team="White", name=f"white_pawn_7"), 
              (1, 7): Pawn(team="White", name=f"white_pawn_8"), 
              (0, 0): Rook(team="White", name=f"white_rook_1"), 
              (0, 7): Rook(team="White", name=f"white_rook_2"), 
              (0, 1): Knight(team="White", name=f"white_knight_1"), 
              (0, 6): Knight(team="White", name=f"white_knight_2"), 
              (0, 2): Bishop(team="White", name=f"white_bishop_1"), 
              (0, 5): Bishop(team="White", name=f"white_bishop_2"), 
              (0, 4): Queen(team="White", name=f"white_queen"), 
              (0, 3): King(team="White", name=f"white_king"), 
            },
            "Black": {
              (6, 0): Pawn(team="Black", name=f"black_pawn_1"), 
              (6, 1): Pawn(team="Black", name=f"black_pawn_2"), 
              (6, 2): Pawn(team="Black", name=f"black_pawn_3"), 
              (6, 3): Pawn(team="Black", name=f"black_pawn_4"), 
              (6, 4): Pawn(team="Black", name=f"black_pawn_5"), 
              (6, 5): Pawn(team="Black", name=f"black_pawn_6"), 
              (6, 6): Pawn(team="Black", name=f"black_pawn_7"), 
              (6, 7): Pawn(team="Black", name=f"black_pawn_8"), 
              (7, 0): Rook(team="Black", name=f"black_rook_1"), 
              (7, 7): Rook(team="Black", name=f"black_rook_2"), 
              (7, 1): Knight(team="Black", name=f"black_knight_1"), 
              (7, 6): Knight(team="Black", name=f"black_knight_2"), 
              (7, 2): Bishop(team="Black", name=f"black_bishop_1"), 
              (7, 5): Bishop(team="Black", name=f"black_bishop_2"), 
              (7, 4): Queen(team="Black", name=f"black_queen"), 
              (7, 3): King(team="Black", name=f"black_king"), 
            }
        }
}


# TODO config validator here
