from graphics import Image
from name_registry import register_name
from piece import Piece, PieceMoves
from typing import List

from constants import *


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

class Square(): pass  # forward declatation for typecheck lol
class Square():
    # one square of the board
    highlight_color = "none"

    def __init__(self, height:int, width:int, color:str, name:str) -> None:
        self.base_img = Image(height=height, width=width, color="none", name=name + "_img")
        self.neighbors = {}  # a dict of direction name to Square object, e.g. {"nw": square_xxx}
        self.occupants = []  # list of Pieces
        self.color = color
        self.name = name
        register_name(self.name)

    def update_neighbors(self, neighbors: list) -> None:
        """NOTE this never removes neighbors. May need to have an extra option for some cards.
        """
        self.neighbors.update(neighbors)

    def get_image(self) -> Image:
        full_img = self.base_img.copy()
        width, height = full_img.width, full_img.height
        for occupant in self.occupants:
          if occupant.img.width != width: raise ValueError(f"Cannot stack {occupant.name}'s image of width {occupant.img.width} into square {self.name} of width {width}")
          if occupant.img.height != height: raise ValueError(f"Cannot stack {occupant.name}'s image of height {occupant.img.height} into square {self.name} of height {height}")
          full_img.stack_on_image(occupant.img)
        full_img.set_color(self.color)
        return full_img
    
    def set_color(self, color: str) -> None:
        self.color = color

    def add_occupant(self, piece:Piece) -> None:
        if not hasattr(piece, "img"):
            raise ValueError("Occupants must be renderable")
        self.occupants.append(piece)

    def remove_occupant(self, piece:Piece) -> Piece:
        if not  self.occupants:
            raise ValueError(f"Square {self.name} does nto have any occupants!")
        piece_name = piece.name if isinstance(piece, Piece) else piece
        piece_idx = -1
        for i, occupant in enumerate(self.occupants):
            if occupant.name == piece_name:
                piece_idx = i
                break
        if piece_idx == -1:
            raise ValueError(f"Cannot remove piece {piece_name} from square {self.name}, since said square only has these {len(self.occupants)} occupants: {', '.join([o.name for o in self.occupants])}.")
        return self.occupants.pop(piece_idx)

    def add_debug_layer(self) -> None:
        debug_string = f"{self.name.replace('square_', 's')}:"
        for direction, square in self.neighbors.items():
            debug_string += f"{direction}:{square.name.replace('square_', 's')};"
        for occupant in self.occupants:
            debug_string += f"occ:{occupant.name}; "
        self.base_img.print_in_string(debug_string)

    def takable_occupants(self, piece:Piece) -> list:
        """Returns list of the occupants that can be taken by piece.
        """
        return  [occ for occ in self.occupants if occ.can_be_taken_by(piece)]

    def untakable_occupants(self, piece:Piece) -> list:
        """Returns list of the occupants that cannot be taken by piece.
        """
        return  [occ for occ in self.occupants if not occ.can_be_taken_by(piece)]

    def relative_tangibility(self, piece:Piece) -> str:
        """How can this square be moved through by this piece?
        In classic chess, this is synonymous with whether it has an occupant.
        In RCC, there are pieces and objects that can be moved through.
        returns: enum in ["intangible", "unpassthroughable", "unpassintoable"]
        """
        tangibilities = {occ.relative_tangibility(piece) for occ in self.occupants}
        if "unpassintoable" in tangibilities: return "unpassintoable"
        if "unpassthroughable" in tangibilities: return "unpassthroughable"
        return "intangible"
        # TODO make these constants


    def get_squares_in_ray(self, direction: str, moving_piece: Piece) -> list:
        """E.g. get all the pieces that a bishop could reach in one direction.
        Include the last square, aka the piece that will be taken.
        """
        reachable_squares = []
        if direction not in self.neighbors: return []
        ctr = 0
        cur_square = self
        while True:
            ctr +=1
            cur_square = cur_square.neighbors[direction]
            cur_square_tangibility = cur_square.relative_tangibility(moving_piece)
            if cur_square_tangibility == "unpassintoable": break
            reachable_squares.append(cur_square)
            if direction not in cur_square.neighbors: break
            if cur_square_tangibility == "unpassthroughable": break
            # TODO for board wrapping this will have to be clever
            # should be as simple as checking that square is not already seen
            if ctr >= 10: raise ValueError("Your board is bigger than 10 squares??")
        return reachable_squares

    def get_orthogonal_rays(self, moving_piece: Piece) -> list:
        return [square for direction in ["n", "e", "s", "w"] for square in self.get_squares_in_ray(direction, moving_piece)]

    def get_diagonal_rays(self, moving_piece: Piece) -> list:
        return [square for direction in ["ne", "se", "sw", "nw"] for square in self.get_squares_in_ray(direction, moving_piece)]

    def get_squares_from_directions_list(self, piece:Piece, directions_list: list, mode:str="normal") -> list:
        if mode not in MODES_OF_MOVEMENT:
            raise ValueError(f"mode {mode} is not supported; only {MODES_OF_MOVEMENT} are available.")
        if not isinstance(directions_list, list) or not directions_list:
            raise ValueError("get_squares_from_directions_list needs a nonempty list, like [['n'], ['s']]")
        if not isinstance(directions_list[0], list):
            raise ValueError("get_squares_from_directions_list needs a nonempty list, like [['n'], ['s']]")
        reachable_squares = []
        for directions_i in directions_list:
            reachable_square = self.get_square_from_directions(piece, directions_i, mode)
            if reachable_square:
              reachable_squares.append(reachable_square)
        return reachable_squares


    def get_square_from_directions(self, piece:Piece, directions:list, mode="normal", stop_at_end_of_board=False) -> Square:
        """Returns the final square you reach, or None if you can't reach a square given those directions.
        returns None if none exists

        Args:
          piece: the piece that is moving
          directions: a list of directions like ["n", "nw", "e"], moves (e.g. North, Northwest, East)
          mode: one of MODES_OF_MOVEMENT; eg. "jumping" for a Knight and "normal" otherwise.
          stop_at_end_of_board: if the directions run off the edge of the board, return None if stop_at_end_of_board==False, or the square on th edge of the board elsewise.
        """
        if mode not in MODES_OF_MOVEMENT:
            raise ValueError(f"mode {mode} is not supported; only {MODES_OF_MOVEMENT} are available.")
        if not isinstance(directions, list) or not directions:
            raise ValueError("get_square_from_directions needs a nonempty list, like ['n', 's']")
        if not isinstance(directions[0], str):
            raise ValueError("get_square_from_directions needs a nonempty list, like ['n', 's']")
        cur_square = self
        for i, direction in enumerate(directions):
            next_square = cur_square.neighbors.get(direction, None)
            if next_square is None:
                return cur_square if stop_at_end_of_board else None
            cur_square = next_square
            cur_square_tangibility = cur_square.relative_tangibility(piece) if piece else "transparent"
            if cur_square_tangibility == "unpassintoable":
                # unpassintoable: e.g. what happens if this square has a piece on your same team?
                if mode == "normal":
                    return None
                elif mode == "jumping":
                    if i == len(directions) - 1: return None
                else:
                    raise ValueError("wtf?")
            elif cur_square_tangibility == "unpassthroughable":
                # unpassthroughable: e.g. what happens if you can take a piece on this square?
                if mode == "normal":
                    return cur_square if i == len(directions) - 1 else None
                elif mode == "jumping":
                    pass
                else:
                    raise ValueError("wtf?")
        return cur_square


    def get_neighbor(self, direction):
        # direction can be N, NE, E, Se, S, etc.
        # return list of pointers
        # normally just 1 but e.g. those slidey things have multiple ones
        pass
    def action_when_landed_on(self, landing_piece:Piece) -> None:
        # e.g. activate boojum, teleport piece to other portal, etc.
        pass
    def action_when_vacated(self, piece:Piece) -> None:
        pass
    # def get_all_adjacent(self):
    #     pass
    def get_occupants(self) -> list:
        # usually returns one, but there can be coocupation...
        # TODO return a copy of this!!!
        return self.occupants
    # special_stuff = {"card name": {attributes}}  # e.g. Terraforming will store "itchy_nucleus" and "is_itchy"
    # and boojum. But maybe these are all pieces??

class Board():

    def __init__(self, game_config:dict) -> None:
        # Create the squares and color them
        self.piece_map = {} # map of piece name to Piece
        self.square_map = {} # map of square name to Square
        self.board_grid = [] # list of lists of the same Squares
        # self.selected_squares = {}  # set of squares that are "selected"...use  unclear.
        self.highlighted_squares = {}  # map of squares to their highlight colors
        # map of square names to anything that is printed on those squares.
        # These are specifically temporary annotations and they are cleared whenever things are
        # deselected. For more permanent things, a piece will be placed on the board.
        self.square_annotations = {}
        self.square_height = game_config["square_height"]
        self.square_width = game_config["square_width"] 
        self.board_height = game_config["board_height"]
        self.board_width = game_config["board_width"] 
        self.col_names_to_idx = {a:i for i, a in enumerate('abcdefgh')}
        self.idx_to_col_names = {i:a for a, i in self.col_names_to_idx.items()}

        # Initialize all the Square objects
        for row_i in range(game_config["board_height"]):
            self.board_grid.append([])
            for col_j in range(game_config["board_width"]):
                if (row_i + col_j)%2: 
                  sq_color ="black_highlight"
                else:
                  sq_color ="white_highlight"
                # sq_color = "none"
                alpha_name = f"{self.idx_to_col_names[col_j]}{row_i + 1}"
                square = Square(width=self.square_width, height=self.square_height, name=alpha_name, color=sq_color)
                self.board_grid[row_i].append(square)
                self.square_map[square.name] = square
                self.square_annotations[square.name] = []

        # add in all the squares' neighbors
        for row_i in range(game_config["board_height"]):
            for col_j in range(game_config["board_width"]):
                self.add_square_neighbors(row_i, col_j)

        # Add in all the pieces
        for unused_team, positions_and_pieces in game_config["initial_positions"].items(): 
          for (piece_row, piece_col), piece_generator in positions_and_pieces.items():
              piece = piece_generator()
              self.add_new_piece(piece, piece_row, piece_col)


        # add the pretty edges of the board
        # this could be done in a simpler way with the newer graphics methods
        v_border_width = 2
        h_border_width = 1
        v_border_block = " "*v_border_width + "\n"
        vertical_border_img = v_border_block*h_border_width
        for i in range(game_config["board_height"]):
            vert_chunk = [v_border_block] * self.square_height
            vert_chunk[self.square_height // 2] = f" {i + 1}\n"
            vertical_border_img += ''.join(vert_chunk)
        vertical_border_img += v_border_block[0:-1]  # remove newline

        horizontal_border_img = v_border_block[0:-1]
        for i in range(game_config["board_width"]):
            horiz_chunk = [" "]* self.square_width
            horiz_chunk[self.square_width//2] = self.idx_to_col_names[i].upper()
            horizontal_border_img += ''.join(horiz_chunk)

        self.left_border = Image(from_string=vertical_border_img, name="left_border", color="red_highlight")
        self.right_border = self.left_border.copy(name="right_border")
        self.top_border = Image(from_string=horizontal_border_img, name="top_border", color="red_highlight")  
        self.bottom_border = self.top_border.copy(name="bottom_border")

    def add_debug_layer(self) -> None:
        for name, square in self.square_map.items():
            square.add_debug_layer()

    def _coordinate_is_on_grid(self, row_i:int, col_j:int) -> bool:
        # assumes a convex board
        if row_i < 0 or row_i >= len(self.board_grid):
            return False
        if col_j < 0 or col_j >=len(self.board_grid[0]):
            return False
        return True


    def add_square_neighbors(self, row_i:int, col_j:int) -> None:
        """To be used during board setup"""
        square = self.board_grid[row_i][col_j]
        for row_offset in [-1, 0, 1]:
          for col_offset in [-1, 0, 1]: 
              if row_offset == 0 and col_offset == 0: continue
              adjacent_row = row_i + row_offset
              adjacent_col = col_j + col_offset
              if not self._coordinate_is_on_grid(row_i=adjacent_row, col_j=adjacent_col):
                  continue
              direction_name = ROW_OFFSET_TO_NAME[(row_offset, col_offset)]
              # TODO did I correctly add a pointer here? or is there now a duplicate of this square here?
              square.neighbors[direction_name] = self.board_grid[adjacent_row][adjacent_col]



    def get_pieces_on_square(self, square:Square) -> list:
        # for landslide, e.g., order type is LTR or some such
        square = self.square_from_a1_coordinates(square)
        return square.get_occupants()

    # def get_all_pieces_in_order(self, order_type):
    #     # for landslide, e.g., order type is LTR or some such
    #     pass

    def render(self) -> None:
        board_img = self.get_image()
        board_img.render()

    def get_image(self) -> Image:
        # flipped classroom overrides this somehow
        # rows = []
        total_width = self.square_width*self.board_width + 2*self.left_border.width
        total_height = self.square_height*self.board_height + 2*self.top_border.height
        
        board_image = Image(width=self.square_width*self.board_width, height=self.square_height*self.board_height)
        for row_i in range(self.board_height):
            # final_row_image = Image(height=self.square_height, width=0) # self.board_grid[i][0].get_image().copy()
            for col_j in range(self.board_width):
                square = self.board_grid[row_i][col_j]
                square_img = square.get_image()
                if square.name in self.highlighted_squares:
                    square_img.set_color(self.highlighted_squares[square.name])
                if square.name in self.square_annotations:
                    annotation = ';'.join(self.square_annotations[square.name])
                    square_img.print_in_string(annotation, color=ANNOTATE_COLOR, location="lower_right")
                # final_row_image.drop_in_image(square_img, location="right_top")
                row_x  = row_i*self.square_height + self.top_border.height
                col_x = col_j*self.square_width + self.left_border.width
                board_image.drop_in_image_by_coordinates(square_img, upper_left_row=row_x, upper_left_col=col_x)
            # rows.append(final_row_image)
        # for row in rows[1:]:
        #     rows[0].drop_in_image(row, location="bottom_left")
 
        # add borders
        board_image.drop_in_image_by_coordinates(self.left_border, upper_left_row=0, upper_left_col=0)
        board_image.drop_in_image_by_coordinates(self.top_border , upper_left_row=0, upper_left_col=0)
        board_image.drop_in_image_by_coordinates(self.left_border, upper_left_row=0, upper_left_col=self.board_width*self.square_width + self.left_border.width)
        board_image.drop_in_image_by_coordinates(self.top_border, upper_left_row=self.board_height*self.square_height + self.top_border.height, upper_left_col=0)
        # half_bordered = self.top_border.copy()
        # # half_bordered.drop_in_image(rows[0], location="bottom_left")
        # half_bordered.drop_in_image(board_image, location="bottom_left")
        # half_bordered.drop_in_image(self.bottom_border, location="bottom_left")
        # full_bordered = self.left_border.copy()
        # full_bordered.drop_in_image(half_bordered, location="right_top")
        # full_bordered.drop_in_image(self.right_border, location="right_top")

        return board_image

    def move_top_piece(self, start_square:Square, end_square:Square) -> list:
        """Returns a list of dead pieces after this move.
        """
        return self.move_piece(self.get_pieces_on_square(start_square)[0], end_square)

    def move_piece(self, piece:Piece, end_square:Square) -> list:
        if piece.taking_method == "normal":
            return self.move_piece_proper(piece, end_square)
        elif piece.taking_method == "pushing":
            return self.push_from_piece(piece, end_square)
        else:
            assert False

    def move_piece_proper(self, piece:Piece, end_square:Square) -> list:
        """Returns a list of dead pieces after this move.
        This does NOT ensure that the piece actually CAN move to this square!
        That is the responsibility of the caller.

        possible future TODO: option of what to do with the pieces it lands on (maybe not kill them?)
        """
        start_square = piece.square_this_is_on
        end_square = self.square_from_a1_coordinates(end_square)
        if piece not in start_square.occupants:  # TODO should probably be a contains() method 
            raise ValueError(f"Piece '{piece.name}' is not on square '{start_square.name}'")
        # TODO raise all sorts of errors if it can't go to the target square, or if either square doesn't exist, etc.

        #=========================================================
        # The piece leaves its start square....
        piece.action_when_vacates(end_square) # activate anything that the piece does when it leaves a square (usually nothing)
        start_square.remove_occupant(piece)
        start_square.action_when_vacated(piece)

        #=========================================================
        # And lands on the next square.
        piece.action_when_lands_on(end_square) # activate anything that the piece does when it lands on a square (usually nothing)
        end_square.action_when_landed_on(piece)

        # Handle taking. (etherization is different.)
        pieces_to_remove_from_square = []
        for occupant in end_square.occupants:
            occupant.action_when_landed_on(piece)
            if not occupant.alive:
                pieces_to_remove_from_square.append(occupant)
        for dead_piece in pieces_to_remove_from_square:
            end_square.occupants.remove(dead_piece)
        
        end_square.add_occupant(piece)

        #=========================================================
        # some checks to make sure we have programmed this right...
        for occupant in start_square.occupants:
            if occupant.square_this_is_on != start_square:
                raise ValueError(f"Square {start_square.name} has {occupant.name} as an occupant, but that occupant has its current square as {occupant.square_this_is_on.name if occupant.square_this_is_on else 'None'}.")
        for occupant in end_square.occupants:
            if occupant.square_this_is_on != end_square:
                raise ValueError(f"Square {end_square.name} has {occupant.name} as an occupant, but that occupant has its current square as {occupant.square_this_is_on.name if occupant.square_this_is_on else 'None'}.")
        return pieces_to_remove_from_square


    def direction_between_neighbor_squares(self, square_a:Square, square_b:Square) -> str:
        for direction, neighbor in square_a.neighbors.items():
            if neighbor == square_b:
                return direction
        raise ValueError("Squares {square_a} and {square_b} are not neighbors")


    def push_from_piece(self, piece:Piece, landing_square:Square) -> List[Piece]:
        direction = self.direction_between_neighbor_squares(piece.square_this_is_on, landing_square)
        taken_pieces = self.push(landing_square, direction)
        self.move_piece_proper(piece, landing_square)
        return taken_pieces

    def push(self, first_pushed_square, direction) -> List[Piece]:
        """
        # push all pieces in some direction, activating the relevant on/off actions if needed
        returns taken pieces
        """
        cur_square = first_pushed_square
        occupants_in_limbo = first_pushed_square.occupants
        cur_square.occupants = []
        while True:
            # TODO this will need to change if we on;y want some types of occupants pushed
            next_square = cur_square.neighbors.get(direction, None)
            if next_square is None:
                # You have pushed off the edge of the board and these pieces die!!
                # Design decision: this is death and not the ether.
                for occ in occupants_in_limbo:
                    occ.alive = False
                return occupants_in_limbo

            next_square_was_empty = not next_square.occupants
            occupants_in_limbo_tmp = next_square.occupants
            # take the occupants off the square
            # NOT doing the following: if you are pushed you don't get to activate your moving abilities.
            # for occ in occupants_in_limbo:
            #   occ.action_when_vacates(next_square)
            next_square.occupants = occupants_in_limbo
            occupants_in_limbo = occupants_in_limbo_tmp
            if next_square_was_empty:
                break
            else:
               cur_square = next_square

        return []


    def dehighlight_all(self) -> None:
        """TODO: "highlights" and "annotations" should be more unified in name, because they are the same sort of thing.
        """
        self.highlighted_squares = {}
        for square_name in self.square_annotations:
            self.square_annotations[square_name] = []

    def square_from_a1_coordinates(self, a1_coord:str) -> Square:
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


    def get_piece_moves_from_square(self, square:Square) -> PieceMoves:
        square = self.square_from_a1_coordinates(square)
        if not square.occupants: return
        if len(square.occupants) > 1:
            raise ValueError("Square must have one or fewer occupants for this method")
        return square.occupants[0].get_possible_moves()

    def highlight_square(self, square:Square, color:str=SELECT_COLOR) -> None:
        self.highlighted_squares.update({square.name:color})

    def dehighlight_square(self, square:Square) -> None:
        if not square: return
        if square.name not in self.highlighted_squares:
          return
          # this is actually not an error:
          #     raise ValueError(f"{square.name} is not highlighted. Only highlighted squares are {[s.name for s in self.highlighted_squares]}")
        del self.highlighted_squares[square.name]

    # def get_piece_moves(self, piece:Piece) -> PieceMoves:
    #     if not piece:
    #         raise ValueError("Empty piece given as input")
    #     # self.dehighlight_all()
    #     
    #     piece_moves = piece.get_possible_moves()
    #     # for i, square in enumerate(piece_moves):
    #     # self.highlighted_squares.update({square.name:PIECE_MOVE_SELECT_COLOR for square in piece_moves.nontaking})
    #     # self.highlighted_squares.update({square.name:PIECE_TAKABLE_SELECT_COLOR for square in piece_moves.taking})
    #     # self.highlighted_squares.update({piece.square_this_is_on.name:SELECT_COLOR})
    #     # for move_id, square in piece_moves.id_to_move.items():
    #     #     self.square_annotations[square.name].append(move_id)
    #     return piece_moves

    def add_new_piece(self, piece:Piece, row:int, col:int) -> None:
       piece.action_when_lands_on(self.board_grid[row][col])
       self.board_grid[row][col].add_occupant(piece)
       self.piece_map[piece.name] = piece

    def add_piece_to_square(self, square_name:str, piece_name:str) -> None:
        square = self.square_map[square_name]
        piece = self.piece_map[piece_name]
        square.add_occupant(piece)

    def remove_piece_from_square(self, square_name:str, piece_name:str) -> None:
        square = self.square_map[square_name]
        square.remove_occupant(piece_name)
# TODO ensure when placing a piece that it can only be in one place?
