from graphics import Image
from name_registry import register_name
from graphics_library import STANDARD_PIECES

class Piece():
    # piece attributes
    unique_id = ""
    piece_type = ""
    team = ""  # white, black, etc.
    mover = ""  # white, Ibraheem, Ibhraheem, etc
    alive = True
    square_this_is_on = None

    special_stuff = {}  # any special enchantments or attributes
    # e.g. that it has the one ring, or is a successor, or riastrad, guzunder


    def __init__(self, team, piece_type, name):
        self.img = Image(STANDARD_PIECES[piece_type][team], color="none", name=f"{name}_img")
        register_name(name)
        self.name = name
        self.type = piece_type
        self.team = team
        self.has_moved = False

    def can_be_taken_by(self, piece):
        """Can self be taken by piece?"""
        return piece.team != self.team

    def relative_tangibility(self, piece):
        """
        returns one of the enum of ["intangible", "unpassthroughable", "unpassintoable"]
        the default method is the one that works for all standard pieces and some nonstandard pieces.
        """
        if piece.team == self.team: return "unpassintoable"
        return "unpassthroughable"

    def action_when_vacates(self, square):
        # what happens when it leaves a particular square
        # usually: nothing
        # the board handles taking it out of the square's occupants list
        self.square_this_is_on = square
        pass


    def action_when_lands_on(self, square):
        # what happens when it lands on something else
        # usually: nothing
        # (the action_when_landed_on method handles being taken)
        self.square_this_is_on = square
        pass

    def action_when_landed_on(self, piece_landing_on_me):
        # usually: mark itself as dead
        # te Square class takes care of removing the body.
        self.alive = False
        pass
    def get_possible_taking_moves(self, square):
        pass
    def get_possible_moves(self, square):
        # default: as a king.
        # TODO: make default an error.
        return square.neighbors.values()
    def choose_autonomous_move(self, square):
        pass # only for autonomous pieces
    def get_squares_this_is_on(self, square):
        # usually one, but can be multiple, like with one ring
        return self.square_this_is_on

class Pawn(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="pawn")
        self.orientation = "n" if team == "Black" else "s"

    def taking_directions(self):
       directions = "n ne e se s sw w nw".split() 
       orientation_idx = directions.index(self.orientation)
       diag_1 = directions[(orientation_idx + 1)%len(directions)]
       diag_2 = directions[(orientation_idx - 1)%len(directions)]
       return [[diag_1], [diag_2]]


    def action_when_vacates(self, square):
        self.square_this_is_on = square
        self.has_moved = True

    def is_valid_nontaking_move(self, square):
        """Can this pawn make a nontaking move to this square?
        """
        if not square: return False
        if not square.takable_occupants(self) and not square.untakable_occupants(self):
           return True
        return False

    def get_possible_moves(self):
        nontaking_moves = []
        in_front = self.square_this_is_on.get_square_from_directions(self, [self.orientation])
        if self.is_valid_nontaking_move(in_front):
            nontaking_moves.append(in_front)
        if not self.has_moved and nontaking_moves:
          in_front = self.square_this_is_on.get_square_from_directions(self, [self.orientation, self.orientation])
          if self.is_valid_nontaking_move(in_front):
              nontaking_moves.append(in_front)

        taking_moves = self.square_this_is_on.get_squares_from_directions_list(self, self.taking_directions())
        taking_moves = [square for square in taking_moves if (square.takable_occupants(self) and not square.untakable_occupants(self))]  # TODO

        return {"taking": taking_moves, "nontaking":nontaking_moves}

class Knight(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="knight")

    def get_possible_moves(self):
        directions = [["n", "nw"], ["n", "ne"], ["e", "ne"], ["e", "se"], ["s", "se"], ["s", "sw"], ["w", "sw"], ["w", "nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions, "jumping") 
        # below can be a decorator...
        taking_moves =    [square for square in all_moves if square.takable_occupants(self)]
        nontaking_moves = [square for square in all_moves if not square.takable_occupants(self)]
        return {"taking": taking_moves, "nontaking": nontaking_moves}


class Camel(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="camel")

    def get_possible_moves(self):
        directions = [["n", "n", "nw"], ["n", "n", "ne"], ["e", "e", "ne"], ["e", "e", "se"], ["s", "s", "se"], ["s", "s", "sw"], ["w", "w", "sw"], ["w", "w", "nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions, "jumping") 
        # below can be a decorator...
        taking_moves =    [square for square in all_moves if square.takable_occupants(self)]
        nontaking_moves = [square for square in all_moves if not square.takable_occupants(self)]
        return {"taking": taking_moves, "nontaking": nontaking_moves}

class Bishop(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="bishop")

    def get_possible_moves(self):
        all_moves = self.square_this_is_on.get_diagonal_rays(self) 
        #  TODO: this is inefficient; one could call get_squares_in_ray and then just check the edges. But savings is prolly minimal.
        taking_moves =    [square for square in all_moves if square.takable_occupants(self)]
        nontaking_moves = [square for square in all_moves if not square.takable_occupants(self)]
        return {"taking": taking_moves, "nontaking":nontaking_moves}

class Rook(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="rook")

    def get_possible_moves(self):
        all_moves = self.square_this_is_on.get_orthogonal_rays(self) 
        #  TODO: this is inefficient; one could call get_squares_in_ray and then just check the edges. But savings is prolly minimal.
        taking_moves =    [square for square in all_moves if square.takable_occupants(self)]
        nontaking_moves = [square for square in all_moves if not square.takable_occupants(self)]
        return {"taking": taking_moves, "nontaking":nontaking_moves}

class Queen(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="queen")

    def get_possible_moves(self):
        all_moves = self.square_this_is_on.get_orthogonal_rays(self) 
        all_moves += self.square_this_is_on.get_diagonal_rays(self) 
        #  TODO: this is inefficient; one could call get_squares_in_ray and then just check the edges. But savings is prolly minimal.
        taking_moves =    [square for square in all_moves if square.takable_occupants(self)]
        nontaking_moves = [square for square in all_moves if not square.takable_occupants(self)]
        return {"taking": taking_moves, "nontaking":nontaking_moves}


class King(Piece):
    def __init__(self, team, name):
        super().__init__(team=team, name=name, piece_type="king")

    def get_possible_moves(self):
        directions = [["n"],["ne"],["e"],["se"],["s"],["sw"],["w"], ["nw"]]
        all_moves = self.square_this_is_on.get_squares_from_directions_list(self, directions) 
        # below can be a decorator...
        taking_moves =    [square for square in all_moves if square.takable_occupants(self)]
        nontaking_moves = [square for square in all_moves if not square.takable_occupants(self)]
        return {"taking": taking_moves, "nontaking":nontaking_moves}
# ALL_PIECES = {
#       "pawn": Pawn,
#       "knight": Knight,
#       "bishop": Bishop,
#       "rook": Rook,
#       "queen": Queen,
#       "king": King,
# }
