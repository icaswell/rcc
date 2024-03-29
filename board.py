import random
from typing import List

from graphics import Image
from name_registry import register_name
import piece


from constants import *

class Square(): pass  # forward declatation for typecheck lol
class Square():
  def __init__(self, height:int, width:int, color:str, name:str) -> None:
    self.base_img = Image(height=height, width=width, color="transparent", name=name + "_img")
    self.neighbors = {}  # a dict of direction name to Square object, e.g. {"nw": square_xxx}
    self.occupants = []  # list of piece.Pieces
    self.color = color
    self.name = name
    register_name(self.name)

  def __repr__(self):
    occ_string = f" (occs: {[occ.name for occ in self.occupants]})"
    if not self.occupants:
      occ_string = ""
    return self.name + occ_string
  def __str__(self):
    return self.__repr__()  # meow

  def update_neighbors(self, neighbors: dict) -> None:
    """NOTE this never removes neighbors. May need to have an extra option for some cards.
    """
    self.neighbors.update(neighbors)
    to_pop = [k for k, v in neighbors.items() if v is None]
    for p in to_pop:
      self.neighbors.pop(p)

  def get_image(self) -> Image:
    full_img = self.base_img.copy()
    width, height = full_img.width, full_img.height
    for occupant in self.occupants:
      occupant_img = occupant.get_image()
      if occupant_img.width != width: raise ValueError(f"Cannot stack {occupant.name}'s image of width {occupant.img.width} into square {self.name} of width {width}")
      if occupant_img.height != height: raise ValueError(f"Cannot stack {occupant.name}'s image of height {occupant.img.height} into square {self.name} of height {height}")
      full_img.stack_on_image(occupant_img)
      if DEV_MODE:
        full_img.print_in_string(occupant.name)

    full_img.set_color(self.color)
    if DEV_MODE:
      full_img.print_in_string(self.name, location=(0,0))
    return full_img

  def set_color(self, color: str) -> None:
    self.color = color

  def add_occupant(self, new_piece:piece.Piece) -> None:
    if not hasattr(new_piece, "img"):
      raise ValueError("Occupants must be renderable")
    self.occupants.append(new_piece)
    new_piece.square_this_is_on = self

  def remove_occupant(self, removed_piece:piece.Piece) -> piece.Piece:
    if not self.occupants:
      raise ValueError(f"Square {self.name} does not have any occupants!")
    piece_name = removed_piece.name if isinstance(removed_piece, piece.Piece) else removed_piece
    # this rigamarole instead of just occupants.remove is ebcasuse we are handling string inputs as well
    piece_idx = -1
    for i, occupant in enumerate(self.occupants):
      if occupant.name == piece_name:
        piece_idx = i
        break
    if piece_idx == -1:
      raise ValueError(f"Cannot remove piece {piece_name} from square {self.name}, since said square only has these {len(self.occupants)} occupants: {', '.join([o.name for o in self.occupants])}.")
    popped_piece = self.occupants.pop(piece_idx)
    popped_piece.square_this_is_on = None
    DEV_PRINT(f"----removed {popped_piece.name} from {self.name}")
    return popped_piece

  def transfer_piece_here(self, new_piece:piece.Piece) -> piece.Piece:
    if new_piece in self.occupants:
      raise ValueError(f"OOPS! {piece} already on {self}")
    old_square = new_piece.square_this_is_on
    old_square.remove_occupant(new_piece)
    self.add_occupant(new_piece)

  def add_debug_layer(self) -> None:
    debug_string = f"{self.name.replace('square_', 's')}:"
    for direction, square in self.neighbors.items():
      debug_string += f"{direction}:{square.name.replace('square_', 's')};"
    for occupant in self.occupants:
      debug_string += f"occ:{occupant.name}; "
    self.base_img.print_in_string(debug_string)

  def takable_occupants(self, moving_piece:piece.Piece) -> list:
    """Returns list of the occupants that can be taken by piece.
    """
    return  [occ for occ in self.occupants if occ.can_be_taken_by(moving_piece)]

  def untakable_occupants(self, moving_piece:piece.Piece) -> list:
    """Returns list of the occupants that cannot be taken by piece.
    """
    return  [occ for occ in self.occupants if not occ.can_be_taken_by(moving_piece)]

  def relative_tangibility(self, moving_piece:piece.Piece) -> str:
    """How can this square be moved through by this piece?
    In classic chess, this is synonymous with whether it has an occupant.
    In RCC, there are pieces and objects that can be moved through.
    returns: enum in ["intangible", "unpassthroughable", "unpassintoable"]
    """
    tangibilities = {occ.tangibility_wrt_incomer(moving_piece) for occ in self.occupants}
    if "unpassintoable" in tangibilities: return "unpassintoable"
    if "unpassthroughable" in tangibilities: return "unpassthroughable"
    return "intangible"
    # TODO make these constants


  def get_squares_in_ray(self, direction: str, moving_piece: piece.Piece, only_nontaking:str=False) -> list:
    """E.g. get all the squares that a bishop could reach in one direction.
    Include the last square, aka the piece that will be taken.

    AHAH note: "only_nontaking" has some pathological edge cases. Namely, it means that a piece can't landslide into a cat bus or something.
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
      if only_nontaking and cur_square_tangibility == "unpassthroughable": break
      reachable_squares.append(cur_square)
      if direction not in cur_square.neighbors: break
      if cur_square_tangibility == "unpassthroughable": break
      # TODO for board wrapping this will have to be clever
      # should be as simple as checking that square is not already seen
      if ctr >= 10: raise ValueError("Your board is bigger than 10 squares??")
    return reachable_squares

  def get_orthogonal_squares(self, moving_piece: piece.Piece) -> list:
    return self.get_squares_from_directions_list(piece=moving_piece, directions_list=[["n"], ["e"], ["s"], ["w"]])

  def get_orthogonal_rays(self, moving_piece: piece.Piece) -> list:
    return [square for direction in ["n", "e", "s", "w"] for square in self.get_squares_in_ray(direction, moving_piece)]

  def get_diagonal_rays(self, moving_piece: piece.Piece) -> list:
    return [square for direction in ["ne", "se", "sw", "nw"] for square in self.get_squares_in_ray(direction, moving_piece)]

  def get_squares_from_directions_list(self, moving_piece:piece.Piece, directions_list: list, mode:str="normal") -> list:
    if mode not in MODES_OF_MOVEMENT:
      raise ValueError(f"mode {mode} is not supported; only {MODES_OF_MOVEMENT} are available.")
    if not isinstance(directions_list, list) or not directions_list:
      raise ValueError("get_squares_from_directions_list needs a nonempty list, like [['n'], ['s']]")
    if not isinstance(directions_list[0], list):
      raise ValueError("get_squares_from_directions_list needs a nonempty list, like [['n'], ['s']]")
    reachable_squares = []
    for directions_i in directions_list:
      reachable_square = self.get_square_from_directions(moving_piece, directions_i, mode)
      if reachable_square:
        reachable_squares.append(reachable_square)
    return reachable_squares


  def get_square_from_directions(self, moving_piece:piece.Piece, directions:list, mode="normal", stop_at_end_of_board=False) -> Square:
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
      cur_square_tangibility = cur_square.relative_tangibility(moving_piece) if moving_piece else "transparent"
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

  def is_adjacent_to(self, other_sq:Square):
    if isinstance(other_sq, piece.Piece): other_sq = other_sq.square_this_is_on
    # Assumes that this is a symmetric operation
    return other_sq in self.neighbors.values()

  def get_adjacent_occupants(self):
    return [occ for square in self.neighbors.values() for occ in square.occupants]

  def get_neighbor(self, direction:str) -> Square:
    # direction can be N, NE, E, Se, S, etc.
    # return list of pointers
    # normally just 1 but e.g. those slidey things have multiple ones
    return self.neighbors.get(direction, None)

  def get_occupants(self) -> list:
    # usually returns one, but there can be coocupation...
    # TODO return a copy of this!!!
    return self.occupants
    # special_stuff = {"card name": {attributes}}  # e.g. Terraforming will store "itchy_nucleus" and "is_itchy"
    # and boojum. But maybe these are all pieces??

class Board():
  def __init__(self, game_config:dict) -> None:
     # self.piece_map = {} # map of piece name to piece.Piece
     self.square_map = {} # map of square name to Square
     self.board_grid = [] # list of lists of the same Squares
     # self.selected_squares = {}  # set of squares that are "selected"...use  unclear.
     self.highlighted_squares = {}  # map of square names to their highlight colors
     # map of square names to anything that is printed on those squares.
     # These are specifically temporary annotations and they are cleared whenever things are
     # deselected. For more permanent things, a piece will be placed on the board.
     self.square_annotations = {}
     self.square_height = game_config["square_height"]
     self.square_width = game_config["square_width"] 
     self.board_height = game_config["board_height"]
     self.board_width = game_config["board_width"] 
     # This all may seem a bit extra for a simple indexing...but remember that the board can be rotated around!
     self.col_names_to_idx = {a:i for i, a in enumerate('abcdefgh')}
     self.row_names_to_idx = {i+1:i for i in range(self.board_height)}
     idx_to_col_names = {i:a for a, i in self.col_names_to_idx.items()}
     idx_to_row_names = {i:a for a, i in self.row_names_to_idx.items()}

     # Initialize all the Square objects
     for row_i in range(game_config["board_height"]):
       self.board_grid.append([])
       for col_j in range(game_config["board_width"]):
         if (row_i + col_j)%2: 
           sq_color = COLOR_SCHEME["BLACK_SQUARE_COLOR"]
         else:
           sq_color = COLOR_SCHEME["WHITE_SQUARE_COLOR"]
         alpha_name = f"{idx_to_col_names[col_j]}{idx_to_row_names[row_i]}"
         square = Square(width=self.square_width, height=self.square_height, name=alpha_name, color=sq_color)
         self.board_grid[row_i].append(square)
         self.square_map[square.name] = square
         self.square_annotations[square.name] = []

     # add in all the squares' neighbors
     for row_i in range(game_config["board_height"]):
       for col_j in range(game_config["board_width"]):
         self.add_square_neighbors(row_i, col_j)

     # Add in all the pieces
     for (piece_row, piece_col), piece_generator in game_config["initial_positions"]:
       piece = piece_generator()
       self.add_new_piece(piece, piece_row, piece_col)

     self.make_border_images()


  def make_border_images(self):
    # add the pretty edges of the board
    # this could be done in a simpler way with the newer graphics methods
    idx_to_col_names = {i:a for a, i in self.col_names_to_idx.items()}
    idx_to_row_names = {i:a for a, i in self.row_names_to_idx.items()}
    v_border_width = 2
    h_border_width = 1
    v_border_block = " "*v_border_width + "\n"
    vertical_border_img = v_border_block*h_border_width
    for i in range(self.board_height):
      vert_chunk = [v_border_block] * self.square_height
      vert_chunk[self.square_height // 2] = f" {i + 1}\n"
      vertical_border_img += ''.join(vert_chunk)
    vertical_border_img += v_border_block[0:-1]  # remove newline

    horizontal_border_img = v_border_block[0:-1]
    for i in range(self.board_width):
      horiz_chunk = [" "]* self.square_width
      horiz_chunk[self.square_width//2] = idx_to_col_names[i].upper()
      horizontal_border_img += ''.join(horiz_chunk)

    self.left_border = Image(from_string=vertical_border_img, color=COLOR_SCHEME["BORDER_COLOR"])
    self.right_border = self.left_border.copy()
    self.top_border = Image(from_string=horizontal_border_img, color=COLOR_SCHEME["BORDER_COLOR"])  
    self.bottom_border = self.top_border.copy()

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
    row_offset_to_name = {
        (-1, 0): "n",
        (-1, 1): "ne",
        (0,  1): "e",
        (1,  1): "se",
        (1,  0): "s",
        (1, -1): "sw",
        (0, -1): "w",
        (-1, -1): "nw",
        }
    square = self.board_grid[row_i][col_j]
    for row_offset in [-1, 0, 1]:
      for col_offset in [-1, 0, 1]: 
        if row_offset == 0 and col_offset == 0: continue
        adjacent_row = row_i + row_offset
        adjacent_col = col_j + col_offset
        if not self._coordinate_is_on_grid(row_i=adjacent_row, col_j=adjacent_col):
          continue
        direction_name = row_offset_to_name[(row_offset, col_offset)]
        # TODO did I correctly add a pointer here? or is there now a duplicate of this square here?
        square.neighbors[direction_name] = self.board_grid[adjacent_row][adjacent_col]


  def get_pieces_on_square(self, square:Square) -> list:
    square = self.square_from_a1_coordinates(square)
    return square.get_occupants()

  def can_take_from_here(self, square:Square, moving_piece:piece.Piece) -> bool:
    """can piece make any taking move fromthis square?
    """
    true_square = moving_piece.square_this_is_on
    moving_piece.square_this_is_on = square # put it here temporarily to see where it can go
    moves_if_it_were_here = moving_piece.get_possible_moves()
    moving_piece.square_this_is_on = true_square # put it back on its true square
    return len(moves_if_it_were_here.taking) != 0

  def get_random_square(self, must_be_unoccupied:bool=False, piece_that_cannot_take_from_here:piece.Piece=None) -> Square:
    """
    Args:
      piece_that_cannot_take_from_here: if not None, don't select any square that would allow this piece to take.
    """
    possible_squares = []
    for row in self.board_grid:
      for square in row:
        if must_be_unoccupied and square.occupants:
          continue
        if piece_that_cannot_take_from_here is not None and  self.can_take_from_here(square, piece_that_cannot_take_from_here):
          continue
        possible_squares.append(square)
    DEV_PRINT(possible_squares)
    return random.choice(possible_squares) if possible_squares else None
    # row_i = random.randint(0, self.board_height - 1)
    # col_j = random.randint(0, self.board_width - 1)
    # return self.board_grid[row_i][col_j]

  def get_pieces(self, types:List[str]=None, team:str=None, adjacent_to:Square=None, reverse_rows:bool=False) -> List[piece.Piece]:
    if types and any(c.isupper() for c in "".join(types)):  # canot wait to replace this with enum!
      raise ValueError(f"piece types are always lowercase; got {types}")
    if team and team.islower():
      raise ValueError(f"Team names are always uppercase; got {team}")
    ret = []

    def selection_fn(occ:piece.Piece) -> bool:
      if types and occ.type not in types: return False
      if team and occ.team != team: return False
      if adjacent_to and not occ.square_this_is_on.is_adjacent_to(adjacent_to): return False
      return True

    rows = self.board_grid
    if reverse_rows:
      rows = self.board_grid[::-1]

    for row in rows:
      for square in row:
        ret += [occ for occ in square.occupants if selection_fn(occ)]
    return ret


  def get_squares(self, rows:List[int], unoccupied:bool=False):
    candidates = []
    for row_i, row in enumerate(self.board_grid):
      if row_i not in rows: continue
      for col_j, sq in enumerate(row):
        if unoccupied and sq.occupants: continue
        candidates.append(sq)
    return candidates


  def render(self) -> None:
    board_img = self.get_image()
    board_img.render()

  def get_image(self) -> Image:
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
          square_img.print_in_string(annotation, color=COLOR_SCHEME["ANNOTATE_COLOR"], location="lower_right")
        row_x  = row_i*self.square_height + self.top_border.height
        col_x = col_j*self.square_width + self.left_border.width
        board_image.drop_in_image_by_coordinates(square_img, upper_left_row=row_x, upper_left_col=col_x)

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

  def move_piece(self, moving_piece:piece.Piece, end_square:Square) -> list:
    if moving_piece.interaction_type == InteractionType.SWAPPING or any([occ.interaction_type == InteractionType.SWAPPING for occ in end_square.occupants]):
      return self.swap_pieces(moving_piece, end_square)  
    elif moving_piece.interaction_type == InteractionType.TAKING: 
      return self.move_piece_proper(moving_piece, end_square)
    elif moving_piece.interaction_type == InteractionType.PUSHING:
      return self.push_from_piece(moving_piece, end_square)
    else:
      assert False

  def move_piece_proper(self, moving_piece:piece.Piece, end_square:Square) -> list:
    """Returns a list of dead pieces after this move.
    This does NOT ensure that the piece actually CAN move to this square!
    That is the responsibility of the caller.

    possible future TODO: option of what to do with the pieces it lands on (maybe not kill them?)
    """
    assert end_square is not None
    start_square = moving_piece.square_this_is_on
    end_square = self.square_from_a1_coordinates(end_square)
    if moving_piece not in start_square.occupants:  # TODO should probably be a contains() method 
      raise ValueError(f"piece.Piece '{piece.name}' is not on square '{start_square.name}'")
    # TODO raise all sorts of errors if it can't go to the target square, or if either square doesn't exist, etc.

    #=========================================================
    # The piece leaves its start square....
    moving_piece.action_when_vacates(start_square) # activate anything that the piece does when it leaves a square (usually nothing)
    # start_square.action_when_vacated(piece)

    # Handle taking. (etherization is different.)
    pieces_landed_on = []
    for occupant in end_square.occupants:
      pieces_landed_on.append(occupant)
    # for dead_piece in pieces_landed_on:
    #     end_square.occupants.remove(dead_piece)

    end_square.transfer_piece_here(moving_piece)

    #=========================================================
    # And lands on the next square.
    moving_piece.action_when_lands_on(end_square) # activate anything that the piece does when it lands on a square (usually nothing)

    #=========================================================
    # some checks to make sure we have programmed this right...
    for occupant in start_square.occupants:
      if occupant.square_this_is_on != start_square:
        raise ValueError(f"Square {start_square.name} has {occupant.name} as an occupant, but that occupant has its current square as {occupant.square_this_is_on.name if occupant.square_this_is_on else 'None'}.")
    for occupant in end_square.occupants:
      if occupant.square_this_is_on != end_square:
        raise ValueError(f"Square {end_square.name} has {occupant.name} as an occupant, but that occupant has its current square as {occupant.square_this_is_on.name if occupant.square_this_is_on else 'None'}.")
    assert moving_piece.square_this_is_on is not None
    return pieces_landed_on


  def rotate_direction_clockwise(self, direction:str, n_ticks:int):
    """get the direction that is rotated N ticks from this one.
    e.g. 1 tick clockwise from North is Nort-East; 2 ticks is East.
    """
    directions_in_clockwise_order = "n ne e se s sw w nw".split()
    if direction not in directions_in_clockwise_order:
      raise ValueError(f"WTF is this direction: {direction}? It should be 'n' for North, etc.")
    d_i = directions_in_clockwise_order.index(direction)
    return directions_in_clockwise_order[(d_i + n_ticks)%len(directions_in_clockwise_order)]

  def direction_between_neighbor_squares(self, square_a:Square, square_b:Square) -> str:
    for direction, neighbor in square_a.neighbors.items():
      if neighbor == square_b:
        return direction
    raise ValueError("Squares {square_a} and {square_b} are not neighbors")


  def push_from_piece(self, pushing_piece:piece.Piece, landing_square:Square) -> List[piece.Piece]:
    direction = self.direction_between_neighbor_squares(pushing_piece.square_this_is_on, landing_square)
    taken_pieces = self.push(landing_square, direction)
    self.move_piece_proper(pushing_piece, landing_square)
    return taken_pieces

  def swap_pieces(self, swapping_piece: piece.Piece, landing_square: Square) -> List[piece.Piece]:
    # First add all the occupants of the landing square onto piece's square,
    # then move piece to the landing square.
    for occ in landing_square.occupants:
      swapping_piece.square_this_is_on.transfer_piece_here(occ)
    return self.move_piece_proper(swapping_piece, landing_square)        

  def push(self, first_pushed_square, direction) -> List[piece.Piece]:
    """
    # push all pieces in some direction, activating the relevant on/off actions if needed
    returns taken pieces
    """
    # TODO I have somehow inverted this loop and it can all be done more simply
    # without this first iteration outside
    cur_square = first_pushed_square
    occupants_in_limbo = first_pushed_square.occupants
    if not occupants_in_limbo: return []
    while True:
      # TODO this will need to change if we on;y want some types of occupants pushed
      next_square = cur_square.get_neighbor(direction)
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
      # next_square.occupants = occupants_in_limbo
      for occ in occupants_in_limbo:
        next_square.transfer_piece_here(occ)
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
    self.deannotate_all()

  def deannotate_all(self) -> None:
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
    row_idx = self.row_names_to_idx[int(row)]
    if row_idx >= len(self.board_grid) or col_idx >= len(self.board_grid[row_idx]):
      raise ValueError(f"Square {a1_coord} (row={row_idx}, col={col_idx}) is impossible bruh")
    return self.board_grid[row_idx][col_idx]

  def get_piece_moves_from_square(self, square:Square) -> piece.PieceMoves:
    square = self.square_from_a1_coordinates(square)
    if not square.occupants: return
    if len(square.occupants) > 1:
      raise ValueError("Square must have one or fewer occupants for this method")
    return square.occupants[0].get_possible_moves()

  def annotate_square(self, square:Square, annotation:str) -> None:
    self.square_annotations[square.name].append(annotation)
  def highlight_square(self, square:Square, color:str=COLOR_SCHEME["SELECT_COLOR"]) -> None:
    self.highlighted_squares.update({square.name:color})

  def dehighlight_square(self, square:Square) -> None:
    if not square: return
    if square.name not in self.highlighted_squares:
      return
    del self.highlighted_squares[square.name]

  # def get_piece_moves(self, piece:piece.Piece) -> piece.PieceMoves:
  #     if not piece:
  #         raise ValueError("Empty piece given as input")
  #     # self.dehighlight_all()
  #     
  #     piece_moves = piece.get_possible_moves()
  #     # for i, square in enumerate(piece_moves):
  #     # self.highlighted_squares.update({square.name:COLOR_SCHEME["PIECE_MOVE_SELECT_COLOR"] for square in piece_moves.nontaking})
  #     # self.highlighted_squares.update({square.name:COLOR_SCHEME["PIECE_TAKABLE_SELECT_COLOR"] for square in piece_moves.taking})
  #     # self.highlighted_squares.update({piece.square_this_is_on.name:COLOR_SCHEME["SELECT_COLOR"]})
  #     # for move_id, square in piece_moves.id_to_move.items():
  #     #     self.square_annotations[square.name].append(move_id)
  #     return piece_moves

  def add_new_piece(self, new_piece:piece.Piece, row:int, col:int) -> None:
    new_piece.action_when_lands_on(self.board_grid[row][col])
    self.board_grid[row][col].add_occupant(new_piece)
    # self.piece_map[piece.name] = piece

  def add_piece_to_square(self, square_name:str, piece_name:str) -> None:
    square = self.square_map[square_name]
    # piece = self.piece_map[piece_name]
    square.add_occupant(piece)

  def remove_piece_from_square(self, square_name:str, piece_name:str) -> None:
    square = self.square_map[square_name]
    square.remove_occupant(piece_name)

# TODO ensure when placing a piece that it can only be in one place?

