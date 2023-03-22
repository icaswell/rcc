from graphics import Image
from name_registry import register_name
from asset_library import STANDARD_PIECES, OTHER_PIECES

class PieceMoves():
    """This class is essentially a glorified dict + function decorator.

    It stores what moves a given Piece can make. The actual logic for dinding the takable moves happens in the piece's get_possible_moves function/
    """
    def __init__(self, square, piece, all_moves=None, taking_moves=None, nontaking_moves=None):
        # print(square, piece, all_moves, taking_moves, nontaking_moves)
        if all_moves is not None:
            if (taking_moves is not None) or (nontaking_moves is not None):
                raise ValueError("If all_moves is specified, neither of taking_moves or nontaking_moves can be")
            self.taking    =    [square for square in all_moves if square.takable_occupants(piece)]
            self.nontaking = [square for square in all_moves if not square.takable_occupants(piece)]
        else:
            if (taking_moves is None) or (nontaking_moves is None):
                raise ValueError("If all_moves is not specified, both of taking_moves and nontaking_moves must be")
            self.taking    = taking_moves
            self.nontaking = nontaking_moves

        self.id_to_move = {str(i): square_i for i, square_i in enumerate(self.taking + self.nontaking)}

    def __str__(self):
        move_to_id = {move:i for i, move in self.id_to_move.items()}
        taking = "; ".join([f"{move_to_id[sq]}:{sq.name}" for sq in self.taking])
        nontaking = "; ".join([f"{move_to_id[sq]}:{sq.name}" for sq in self.nontaking])
        return f"taking: {taking}  || nontaking: {nontaking}"

class Piece(): pass
class Piece():
    # piece attributes
    unique_id = ""
    piece_type = ""
    team = ""  # white, black, etc.
    mover = ""  # white, Ibraheem, Ibhraheem, etc
    alive = True
    has_moved = False
    square_this_is_on = None
    taking_method = "normal"  # TODO should be an enum; oen of "normal", "pushing", "swapping"

    special_stuff = {}  # any special enchantments or attributes
    # e.g. that it has the one ring, or is a successor, or riastrad, guzunder


    def __init__(self, team, piece_type, name, img:Image=None):
        if img:
            self.img = img
        else:
            self.img = Image(STANDARD_PIECES[piece_type][team], color="none", name=f"{name}_img")
        register_name(name)
        self.name = name
        self.type = piece_type
        self.team = team
        self.has_moved = False

    def can_be_taken_by(self, piece: Piece) -> bool:
        """Can self be taken by piece?"""
        return piece.team != self.team

    def relative_tangibility(self, piece: Piece) -> str:
        """
        returns one of the enum of ["intangible", "unpassthroughable", "unpassintoable"]
        the default method is the one that works for all standard pieces and some nonstandard pieces.
        """
        if piece.team == self.team: return "unpassintoable"
        return "unpassthroughable"

    def action_when_vacates(self, square) -> None:
        # what happens when it leaves a particular square
        # usually: nothing
        # the board handles taking it out of the square's occupants list
        self.square_this_is_on = square
        self.has_moved = True


    def action_when_lands_on(self, square) -> None:
        # what happens when it lands on something else
        # usually: nothing
        # (the action_when_landed_on method handles being taken)
        self.square_this_is_on = square

    def action_when_landed_on(self, piece_landing_on_me: Piece) -> None:
        # usually: mark itself as dead
        # the Square class takes care of removing the body from the square it was on.
        self.alive = False

    def get_possible_moves(self, square) -> PieceMoves:
        raise ValueError("Not Implemented!")
    # def choose_autonomous_move(self, square):
    #     pass # only for autonomous pieces
    # def get_squares_this_is_on(self, square):
    #     # usually one, but can be multiple, like with one ring
    #     return self.square_this_is_on

class Pawn(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="pawn")
        self.orientation = "n" if team == "Black" else "s"

    def _taking_directions(self):
       directions = "n ne e se s sw w nw".split() 
       orientation_idx = directions.index(self.orientation)
       diag_1 = directions[(orientation_idx + 1)%len(directions)]
       diag_2 = directions[(orientation_idx - 1)%len(directions)]
       return [[diag_1], [diag_2]]

    def is_valid_nontaking_move(self, square):
        """Can this pawn make a nontaking move to this square?
        """
        if not square: return False
        if not square.takable_occupants(self) and not square.untakable_occupants(self):
           return True
        return False

    def get_possible_moves(self) -> PieceMoves:
        nontaking_moves = []
        in_front = self.square_this_is_on.get_square_from_directions(self, [self.orientation])
        if self.is_valid_nontaking_move(in_front):
            nontaking_moves.append(in_front)
        if not self.has_moved and nontaking_moves:
          in_front = self.square_this_is_on.get_square_from_directions(self, [self.orientation, self.orientation])
          if self.is_valid_nontaking_move(in_front):
              nontaking_moves.append(in_front)

        taking_moves = self.square_this_is_on.get_squares_from_directions_list(self, self._taking_directions())
        taking_moves = [square for square in taking_moves if (square.takable_occupants(self) and not square.untakable_occupants(self))]  # TODO

        return PieceMoves(square=self.square_this_is_on, piece=self, taking_moves=taking_moves, nontaking_moves=nontaking_moves)

class Knight(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="knight")

    def get_possible_moves(self) -> PieceMoves:
        directions = [["n", "nw"], ["n", "ne"], ["e", "ne"], ["e", "se"], ["s", "se"], ["s", "sw"], ["w", "sw"], ["w", "nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions, "jumping") 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)


class Camel(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="camel")

    def get_possible_moves(self) -> PieceMoves:
        directions = [["n", "n", "nw"], ["n", "n", "ne"], ["e", "e", "ne"], ["e", "e", "se"], ["s", "s", "se"], ["s", "s", "sw"], ["w", "w", "sw"], ["w", "w", "nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions, "jumping") 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)

class Bishop(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="bishop")

    def get_possible_moves(self) -> PieceMoves:
        all_moves = self.square_this_is_on.get_diagonal_rays(self) 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)

class Rook(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="rook")

    def get_possible_moves(self) -> PieceMoves:
        all_moves = self.square_this_is_on.get_orthogonal_rays(self) 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)

class Queen(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="queen")

    def get_possible_moves(self) -> PieceMoves:
        all_moves = self.square_this_is_on.get_orthogonal_rays(self) 
        all_moves += self.square_this_is_on.get_diagonal_rays(self) 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)


class King(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="king")

    def get_possible_moves(self) -> PieceMoves:
        directions = [["n"],["ne"],["e"],["se"],["s"],["sw"],["w"], ["nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions) 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)




class Zamboni(Piece):
    taking_method = "pushing"
    def __init__(self, team, name):
        img = Image(OTHER_PIECES["zamboni"], color="none", name=f"{name}_img")
        super().__init__(team=team, name=name, piece_type="zamboni", img=img)

    def get_possible_moves(self) -> PieceMoves:
        directions = [["n"],["ne"],["e"],["se"],["s"],["sw"],["w"], ["nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions) 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)


class Swapper(Piece):
    def __init__(self, team, name):
        img = Image(OTHER_PIECES["swapper"], color="none", name=f"{name}_img")
        super().__init__(team=team, name=name, piece_type="swapper", img=img)

    def get_possible_moves(self) -> PieceMoves:
        directions = [["n"],["ne"],["e"],["se"],["s"],["sw"],["w"], ["nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions) 
        return PieceMoves(piece=self, square=self.square_this_is_on, all_moves=all_moves)




# ALL_PIECES = {
#       "pawn": Pawn,
#       "knight": Knight,
#       "bishop": Bishop,
#       "rook": Rook,
#       "queen": Queen,
#       "king": King,
# }
