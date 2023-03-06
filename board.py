from graphics import Image
from name_registry import register_name
from piece import *


ROW_OFFSET_TO_NAME = {
    (-1, 0): "n",
    (-1, 1): "ne",
    (0,  1): "e",
    (1,  1): "se",
    (1,  0): "s",
    (1, -1): "sw",
    (0, -1): "w",
    (-1, -1): "nw",
}

SELECT_COLOR = "pink_highlight"

class Square():
    # one square of the board
    highlight_color = "none"

    def __init__(self, height, width, color, name, neighbors = {}):
        self.base_img = Image(height=height, width=width, color="none", name=name + "_img")
        self.neighbors = neighbors  # a dict of offset tuple to Square object, e.g. {(-1, -1): square_xxx} aka {"nw": square_xxx}
        self.occupants = []  # list of Pieces
        self.color = color
        self.name = name
        register_name(self.name)

    def update_neighbors(self, neighbors):
        """NOTE this never removes neighbors. May need to have an extra option for some cards.
        """
        self.neighbors.update(neighbors)

    def get_image(self):
        full_img = self.base_img.copy()
        for occupant in self.occupants:
          full_img.stack_on_image(occupant.img)
        full_img.set_color(self.color)
        return full_img
    
    def set_color(self, color):
        self.color = color

    def add_occupant(self, piece):
        if not hasattr(piece, "img"):
            raise ValueError("Occupants must be renderable")
        self.occupants.append(piece)

    def remove_occupant(self, piece):
        assert self.occupants
        piece_name = piece.name if isinstance(piece, Piece) else piece
        piece_idx = -1
        for i, occupant in enumerate(self.occupants):
            if occupant.name == piece_name:
                piece_idx = i
                break
        if piece_idx == -1:
            raise ValueError(f"Cannot remove piece {piece_name} from square {self.name}, since said square only has these {len(self.occupants)} occupants: {', '.join([o.name for o in self.occupants])}.")
        return self.occupants.pop(piece_idx)


    def get_neighbor(self, direction):
        # direction can be N, NE, E, Se, S, etc.
        # return list of pointers
        # normally just 1 but e.g. those slidey things have multiple ones
        pass
    def action_when_landed_on(self, landing_piece):
        # e.g. activate boojum, teleport piece to other portal, etc.
        pass
    def action_when_vacated(self):
        pass
    def get_all_adjacent(self):
        pass
    def get_occupants(self):
        # usually returns one, but there can be coocupation...
        # TODO return a copy of this!!!
        return self.occupants
    # special_stuff = {"card name": {attributes}}  # e.g. Terraforming will store "itchy_nucleus" and "is_itchy"
    # and boojum. But maybe these are all pieces??

class Board():

    def __init__(self, square_height=8, grid_width=8, border_width=1):
        # Create the squares and color them
        self.piece_map = {} # map of piece name to Piece
        self.square_map = {} # map of square name to Square
        self.board_grid = [] # list of lists of the same Squares
        self.selected_squares = set()
        self.square_height = square_height
        self.square_width = 2*square_height  # terminal characters have a dimansion of 2x1
        self.col_names_to_idx = {a:i for i, a in enumerate('abcdefgh')}
        self.idx_to_col_names = {i:a for a, i in self.col_names_to_idx.items()}

        for i in range(grid_width):
            self.board_grid.append([])
            for j in range(grid_width):
                if (i+j)%2: 
                  sq_color ="black_highlight"
                else:
                  sq_color ="white_highlight"
                # sq_color = "none"
                square = Square(width=self.square_width, height=self.square_height, name=f"square_{i}{j}", color=sq_color)
                self.board_grid[i].append(square)
                self.square_map[square.name] = square
        # add in all the squares' neighbors
        for row_i in range(grid_width):
            for col_j in range(grid_width):
                self.add_square_neighbors(row_i, col_j)
        for j in range(grid_width):
            self.add_new_piece(Pawn(color="white", name=f"white_pawn_{j}"), 1, j)
            self.add_new_piece(Pawn(color="black", name=f"black_pawn_{j}"), 6, j)

        self.add_new_piece(Rook(color="white", name=f"white_rook_1"), 0, 0)
        self.add_new_piece(Rook(color="white", name=f"white_rook_2"), 0, 7)
        self.add_new_piece(Rook(color="black", name=f"black_rook_1"), 7, 0)
        self.add_new_piece(Rook(color="black", name=f"black_rook_2"), 7, 7)

        self.add_new_piece(Knight(color="white", name=f"white_knight_1"), 0, 1)
        self.add_new_piece(Knight(color="white", name=f"white_knight_2"), 0, 6)
        self.add_new_piece(Knight(color="black", name=f"black_knight_1"), 7, 1)
        self.add_new_piece(Knight(color="black", name=f"black_knight_2"), 7, 6)

        self.add_new_piece(Bishop(color="white", name=f"white_bishop_1"), 0, 2)
        self.add_new_piece(Bishop(color="white", name=f"white_bishop_2"), 0, 5)
        self.add_new_piece(Bishop(color="black", name=f"black_bishop_1"), 7, 2)
        self.add_new_piece(Bishop(color="black", name=f"black_bishop_2"), 7, 5)

        self.add_new_piece(Queen(color="white", name=f"white_queen_1"), 0, 4)
        self.add_new_piece(Queen(color="black", name=f"black_queen_2"), 7, 4)

        self.add_new_piece(King(color="white", name=f"white_king_1"), 0, 3)
        self.add_new_piece(King(color="black", name=f"black_king_2"), 7, 3)

        # add the pretty edges of the board
        # self.left_border = Image(height=self.square_height*grid_width + 2*border_width, width=2*border_width, name="left_border", color="red_highlight") 
        vertical_border_img = "  \n"
        horizontal_border_img = ""
        for i in range(grid_width):
            vert_chunk = [f"  \n"] * self.square_height
            vert_chunk[self.square_height // 2] = f" {i + 1}\n"
            vertical_border_img += ''.join(vert_chunk)
            horiz_chunk = [" "]* self.square_width
            horiz_chunk[self.square_width//2] = self.idx_to_col_names[i].upper()
            horizontal_border_img += ''.join(horiz_chunk)
            # vertical_border_img += f"{i + 1}\n"* self.square_height
            # horizontal_border_img += f"{self.idx_to_col_names[i].upper()}"* self.square_width
        vertical_border_img += "  "

        self.left_border = Image(from_string=vertical_border_img, name="left_border", color="red_highlight")
        self.right_border = self.left_border.copy(name="right_border")
        # self.top_border = Image(height=border_width, width=self.square_width*grid_width, name="top_border", color="red_highlight")  
        self.top_border = Image(from_string=horizontal_border_img, name="top_border", color="red_highlight")  
        self.bottom_border = self.top_border.copy(name="bottom_border")

    def coordinate_is_on_grid(self, row_i, col_j):
        # assumes a convex board
        if row_i < 0 or row_i >=len(self.board_grid):
            return False
        if col_j < 0 or col_j >=len(self.board_grid[0]):
            return False
        return True


    def add_square_neighbors(self, row_i, col_j):
        """To be used during board setup"""
        square = self.board_grid[row_i][col_j]
        for adjacent_row in [row_i - 1, row_i + 1]:
          for adjacent_col in [col_j - 1, col_j + 1]:
              if not self.coordinate_is_on_grid(row_i=adjacent_row, col_j=adjacent_col):
                  continue
              square.neighbors[(adjacent_row, adjacent_col)] = self.board_grid[adjacent_row][adjacent_col]


    def get_pieces_on_square(self, square):
        # for landslide, e.g., order type is LTR or some such
        square = self.square_from_a1_coordinates(square)
        return square.get_occupants()

    def get_all_pieces_in_order(self, order_type):
        # for landslide, e.g., order type is LTR or some such
        pass

    def render(self):
        # flipped classroom overrides this somehow
        rows = []
        for i in range(len(self.board_grid)):
            # final_row_image = Image(height=self.square_height, width=0) # self.board_grid[i][0].get_image().copy()
            final_row_image = self.board_grid[i][0].get_image().copy()
            for j in range(len(self.board_grid[i])):
                if not j: continue
                square = self.board_grid[i][j]
                square_img = square.get_image()
                if self.is_selected(square):
                    square_img.set_color(SELECT_COLOR)
                final_row_image.r_append(square_img)
            rows.append(final_row_image)
        for row in rows[1:]:
            rows[0].u_append(row)
 
        # add borders
        half_bordered = self.top_border.copy()
        half_bordered.u_append(rows[0])
        half_bordered.u_append(self.bottom_border)
        full_bordered = self.left_border.copy()
        full_bordered.r_append(half_bordered)
        full_bordered.r_append(self.right_border)

        full_bordered.render()


    def move_piece(self, piece, start_square, end_square):
        start_square = self.square_from_a1_coordinates(start_square)
        end_square = self.square_from_a1_coordinates(end_square)
        if piece not in start_square.occupants:  # TODO should probably be a contains() method 
            raise ValueError(f"Piece '{piece.name}' is not on square '{start_square.name}'")
        # raise all sorts of errors if it can't go to the target square, or if either square doesn't exist, etc.
        # TODO all the when_lands methods etc.
        start_square.remove_occupant(piece)
        end_square.add_occupant(piece)


    def is_selected(self, square_name):
        if isinstance(square_name, Square):
            square_name = square_name.name
        return square_name in self.selected_squares

    def deselect_all(self):
        self.selected_squares = set()

    def square_from_a1_coordinates(self, a1_coord):
        if isinstance(a1_coord, Square): return a1_coord
        assert len(a1_coord) == 2
        a, b = a1_coord[0], a1_coord[1]
        row = a
        col = b
        if a.isalpha():
            row = b
            col = a
        if not col.isalpha():
            raise ValueError(f"Got row ID '{row}' and col ID '{col}', but col ID is not all alpha characters.")
        if not row.isnumeric():
            raise ValueError(f"Got row ID '{row}' and col ID '{col}', but row ID is not numeric.")
        col_idx = self.col_names_to_idx[col.lower()]
        row_idx = int(row) - 1
        return self.board_grid[row_idx][col_idx]


    def select_square(self, square_name, continue_existing_selection=False):
        """
        continue_existing_selection: if True, don't deselect existing selected peices.
        """
        if not square_name:
            raise ValueError("Cannot select square with empty input")
        if not continue_existing_selection:
            self.deselect_all()
        if isinstance(square_name, Square):
            square_name = {square_name.name}
        elif isinstance(square_name, str):
            square_name = {square_name}
        self.selected_squares |= set(square_name)

    def add_new_piece(self, piece, row, col):
       self.board_grid[row][col].add_occupant(piece)
       self.piece_map[piece.name] = piece

    def add_piece_to_square(self, square_name, piece_name):
        square = self.square_map[square_name]
        piece = self.piece_map[piece_name]
        square.add_occupant(piece)

    def remove_piece_from_square(self, square_name, piece_name):
        square = self.square_map[square_name]
        square.remove_occupant(piece_name)


    def push(self, square, direction):
        # push all pieces in some direction, activating the relevant on/off actions if needed
        pass

    def get_possible_moves(self, piece):
        pass

