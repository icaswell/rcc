from game import Game
from game_library import *
from name_registry import reset_name_registry
import time

SEC = "#" + "="*79 + "\n"
SEC = f"\n{SEC}{SEC}"
G = Game(STANDARD_CHESS)
G.render()

SHOULD_I_DO_TESTS = True
# SHOULD_I_DO_TESTS = False

if SHOULD_I_DO_TESTS:
  print(f"{SEC}Moving various")
  G.move_top_piece("b1", "c4") # w knight
  G.move_top_piece("c4", "b5") # w knight
  G.move_top_piece("e7", "e5")
  G.move_top_piece("d7", "d6")
  G.move_top_piece("h8", "f5")
  G.move_top_piece("e2", "e4")
  G.move_top_piece("e1", "f3")
  G.move_top_piece("c1", "c5")  # w bishop
  G.move_top_piece("a8", "h8")
  G.move_top_piece("d2", "d4")  # W pawn
  G.move_top_piece("b2", "b6")  # W pawn
  G.render()


# if SHOULD_I_DO_TESTS:
#   print(f"{SEC}Select moves")
#   G.board.highlight_piece_moves_from_square("c5")  # the bishop on the side
#   G.render()
#   G.board.highlight_piece_moves_from_square("f5")  # Rook
#   G.render()
#   G.board.highlight_piece_moves_from_square("g7")  # Pawn that hasn't moved
#   G.render()
#   G.board.highlight_piece_moves_from_square("d4")  # Pawn that has already moved
#   G.render()
#   G.board.highlight_piece_moves_from_square("b6")  # pawn that can take but not move
#   G.render()
#   G.board.highlight_piece_moves_from_square("g8")  # Knight that can move but not take
#   G.render()
#   G.board.highlight_piece_moves_from_square("b5")  # Knight that can move and take
#   G.render()
#   G.board.highlight_piece_moves_from_square("f3")  # Queen that can move and take
#   G.render()
#   G.board.highlight_piece_moves_from_square("d1")  # King
#   G.render()

if SHOULD_I_DO_TESTS:
  print(f"{SEC}Take")
  G.move_top_piece("c5", "d6")  # w bishop takes black pawn
  G.render()
  G.move_top_piece("d6", "e7")  # w bishop moves
  G.move_top_piece("e8", "e7")  # Queen takes
  G.move_top_piece("a2", "a3")  # w p moves
  G.move_top_piece("e7", "a3")  # b queen moves
  G.render()


if SHOULD_I_DO_TESTS:
  print(f"{SEC}Nonsense Game")
  reset_name_registry()
  G = Game(STANDARD_CHESS)
  G.render()
  G.play_nonsense_game()
  
