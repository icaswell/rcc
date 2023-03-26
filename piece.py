from graphics import Image
from name_registry import register_name
from asset_library import STANDARD_PIECES, OTHER_PIECES
from constants import *


class Piece(): pass
class PieceMoves():
    """This class is essentially a glorified dict + function decorator.
    There are three ways to initialize this:
      1. give it all_moves, and it will figure out which are taking or nontaking
      2. explicitly give it taking and nontaking moves. This is good for cases like PAwns that move and take differently
      3. initialize empty object with (square is None and piece is None)

    It stores what moves a given Piece can make. The actual logic for finding the takable moves happens in the piece's get_possible_moves function/
    """
    def __init__(self, square, piece, all_moves=None, taking_moves=None, nontaking_moves=None):
        if square is None and piece is None:
            self.taking = []
            self.nontaking = []
        elif all_moves is not None:
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

def GetImmobileMoves(piece:Piece) -> PieceMoves:
    return PieceMoves(None, None)

def pawn_taking_directions(pawn):
   directions = "n ne e se s sw w nw".split() 
   orientation_idx = directions.index(pawn.orientation)
   diag_1 = directions[(orientation_idx + 1)%len(directions)]
   diag_2 = directions[(orientation_idx - 1)%len(directions)]
   return [[diag_1], [diag_2]]

def pawn_is_valid_nontaking_move(pawn, square):
    """Can this pawn make a nontaking move to this square?
    """
    if not square: return False
    if not square.takable_occupants(pawn) and not square.untakable_occupants(pawn):
       return True
    return False


def GetPawnMoves(piece:Piece) -> PieceMoves:
    nontaking_moves = []
    in_front = piece.square_this_is_on.get_square_from_directions(piece, [piece.orientation])
    if pawn_is_valid_nontaking_move(piece, in_front):
        nontaking_moves.append(in_front)
    if not piece.has_moved and nontaking_moves:
      in_front = piece.square_this_is_on.get_square_from_directions(piece, [piece.orientation, piece.orientation])
      if pawn_is_valid_nontaking_move(piece, in_front):
          nontaking_moves.append(in_front)

    taking_moves = piece.square_this_is_on.get_squares_from_directions_list(piece, pawn_taking_directions(piece))
    taking_moves = [square for square in taking_moves if (square.takable_occupants(piece) and not square.untakable_occupants(piece))]  # TODO

    return PieceMoves(square=piece.square_this_is_on, piece=piece, taking_moves=taking_moves, nontaking_moves=nontaking_moves)

def GetKnightMoves(piece:Piece) -> PieceMoves:
  directions = [["n", "nw"], ["n", "ne"], ["e", "ne"], ["e", "se"], ["s", "se"], ["s", "sw"], ["w", "sw"], ["w", "nw"]]
  all_moves = piece.square_this_is_on.get_squares_from_directions_list(piece, directions, "jumping") 
  return PieceMoves(piece=piece, square=piece.square_this_is_on, all_moves=all_moves)

def GetBishopMoves(piece:Piece) -> PieceMoves:
  all_moves = piece.square_this_is_on.get_diagonal_rays(piece) 
  return PieceMoves(piece=piece, square=piece.square_this_is_on, all_moves=all_moves)

def GetRookMoves(piece:Piece) -> PieceMoves:
  all_moves = piece.square_this_is_on.get_orthogonal_rays(piece) 
  return PieceMoves(piece=piece, square=piece.square_this_is_on, all_moves=all_moves)

def GetQueenMoves(piece:Piece) -> PieceMoves:
  all_moves = piece.square_this_is_on.get_orthogonal_rays(piece) 
  all_moves += piece.square_this_is_on.get_diagonal_rays(piece) 
  return PieceMoves(piece=piece, square=piece.square_this_is_on, all_moves=all_moves)

def GetKingMoves(piece:Piece) -> PieceMoves:
  directions = [["n"],["ne"],["e"],["se"],["s"],["sw"],["w"], ["nw"]]
  all_moves = piece.square_this_is_on.get_squares_from_directions_list(piece, directions) 
  return PieceMoves(piece=piece, square=piece.square_this_is_on, all_moves=all_moves)

def GetCamelMoves(piece:Piece) -> PieceMoves:
    directions = [["n", "n", "nw"], ["n", "n", "ne"], ["e", "e", "ne"], ["e", "e", "se"], ["s", "s", "se"], ["s", "s", "sw"], ["w", "w", "sw"], ["w", "w", "nw"]]
    all_moves = piece.square_this_is_on.get_squares_from_directions_list(piece, directions, "jumping") 
    return PieceMoves(piece=piece, square=piece.square_this_is_on, all_moves=all_moves)


ALL_MOVING_STYLES = {
        "immobile": GetImmobileMoves,
        "pawn": GetPawnMoves,
        "knight": GetKnightMoves,
        "bishop": GetBishopMoves,
        "rook": GetRookMoves,
        "queen": GetQueenMoves,
        "king": GetKingMoves,
        "camel": GetCamelMoves,
        }

class Piece():

    # special_stuff = {}  # any special enchantments or attributes
    # e.g. that it has the one ring, or is a successor, or riastrad, guzunder


    def __init__(self, team, piece_type, name, moves_as = None, interaction_type: InteractionType = InteractionType.TAKING, img:Image=None):
        if img:
            self.img = img
        else:
            self.img = Image(STANDARD_PIECES[piece_type][team], color="none", name=f"{name}_img")
        register_name(name)
        self.name = name
        self.type = piece_type
        self.moves_as = moves_as if moves_as else piece_type
        self.interaction_type = interaction_type 
        self.team = team
        self.has_moved = False
        self.square_this_is_on = None

    def __repr__(self):
        return f"{self.name} ({self.team}'s {self.type})"
    def __str__(self):
        return self.__repr__()


    def can_be_taken_by(self, piece: Piece) -> bool:
        """Can self be taken by piece?"""
        return piece.team != self.team

    def tangibility_wrt_incomer(self, piece: Piece) -> str:
        """How tangible is Self to the incoming piece?
        returns one of the enum of ["intangible", "unpassthroughable", "unpassintoable"]
        the default method is the one that works for all standard pieces and some nonstandard pieces.
        """
        if not self.can_be_taken_by(piece):
            return "unpassintoable"
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

    def get_possible_moves(self) -> PieceMoves:
        return ALL_MOVING_STYLES[self.moves_as](self)


class Pawn(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="pawn")
        self.orientation = "n" if team == "Black" else "s"


class Knight(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="knight")


class Camel(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="camel")


class Bishop(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="bishop")


class Rook(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="rook")


class Queen(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="queen")


class King(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="king")


class ZamboniPiece(Piece):
    def __init__(self, team, name):
        img = Image(OTHER_PIECES["zamboni"], color="none", name=f"{name}_img")
        super().__init__(team=team, name=name, piece_type="zamboni", moves_as="king", interaction_type=InteractionType.PUSHING, img=img)

    def can_be_taken_by(self, piece: Piece) -> bool:
        """Zamboni cannot be taken!! haha!"""
        return False


class SwapperPiece(Piece):
    def __init__(self, team, name):
        img = Image(OTHER_PIECES["swapper"], color="none", name=f"{name}_img")
        super().__init__(team=team, name=name, piece_type="swapper", moves_as="king", interaction_type=InteractionType.SWAPPING, img=img)
