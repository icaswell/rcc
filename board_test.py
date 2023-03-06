from board import Board

SEC="#" + "="*79 + "\n"

print(f"{SEC}Testing Board Creation")
board = Board(square_height=8, grid_width=8, border_width=1)
board.render()
print(f"{SEC}Moving a pawn")
board.remove_piece_from_square("square_16", "white_pawn_6")
board.add_piece_to_square("square_36", "white_pawn_6")
board.select_square("square_36")
board.render()

# TODO select squares on edges and corners
