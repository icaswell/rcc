from board import Board
from game_library import *


tests_to_run = {"move_various", "select_moves", "take"}

SEC="#" + "="*79 + "\n"

print(f"{SEC}Testing Board Creation")
board = Board(STANDARD_CHESS)
board.render()


if "move_various" in tests_to_run:
  print(f"{SEC}Moving various")
  def move_top_piece(a, b):
    board.move_piece(board.get_pieces_on_square(a)[0], b)
  
  move_top_piece("b1", "c4") # w knight
  move_top_piece("c4", "b5") # w knight
  move_top_piece("e7", "e5")
  move_top_piece("d7", "d6")
  move_top_piece("h8", "f5")
  move_top_piece("e2", "e4")
  move_top_piece("e1", "f3")
  move_top_piece("c1", "c5")  # w bishop
  move_top_piece("a8", "h8")
  move_top_piece("d2", "d4")  # W pawn
  move_top_piece("b2", "b6")  # W pawn
  
  board.render()


if "select" in tests_to_run:
    print(f"{SEC}Select moves")
    board.highlight_piece_moves_from_square("c5")  # the bishop on the side
    board.render()
    board.highlight_piece_moves_from_square("f5")  # Rook
    board.render()
    board.highlight_piece_moves_from_square("g7")  # Pawn that hasn't moved
    board.render()
    board.highlight_piece_moves_from_square("d4")  # Pawn that has already moved
    board.render()
    board.highlight_piece_moves_from_square("b6")  # pawn that can take but not move
    board.render()
    board.highlight_piece_moves_from_square("g8")  # Knight that can move but not take
    board.render()
    board.highlight_piece_moves_from_square("b5")  # Knight that can move and take
    board.render()
    board.highlight_piece_moves_from_square("f3")  # Queen that can move and take
    board.render()
    board.highlight_piece_moves_from_square("d1")  # King
    board.render()

if "take" in tests_to_run:
  print(f"{SEC}Take")
  move_top_piece("c5", "d6")  # w bishop takes black pawn
  board.render()
  move_top_piece("d6", "e7")  # w bishop takes black pawn
  board.render()
