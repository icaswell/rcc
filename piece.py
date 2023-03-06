from graphics import Image
from name_registry import register_name
from graphics_library import STANDARD_PIECES

class Piece():
    unique_id = ""
    piece_type = ""
    team = ""  # white, black, etc.
    mover = ""  # white, Ibraheem, Ibhraheem, etc
    alive = True

    special_stuff = {}  # any special enchantments or attributes
    # e.g. that it has the one ring, or is a successor, or riastrad, guzunder

    def __init__(self, color, piece_type, name):
        self.img = Image(STANDARD_PIECES[piece_type][color], color=none, name=name)
        register_name(name)
        self.name = name
        self.type = piece_type

    def when_lands_on():
        # what happens when it lands on something else
        # usually: nothing
        # (the when_landed_on method handles being taken)
        pass
    def when_landed_on():
        # usually: mark itself as dead
        pass
    def get_possible_taking_moves():
        pass
    def get_possible_moves():
        """Returns a list of tuples of (Square, i), where Square is a Square object and i is a numeric ID.
        """
        pass
    def choose_autonomous_move():
        pass # only for autonomous pieces
    def get_squares_this_is_on():
        # usually one, but can be multiple, like with one ring
        pass

class Pawn(Piece):
    def __init__(self, color, name):
        self.type = "pawn"
        self.img = Image(STANDARD_PIECES[self.type][color], color="none", name=name + "_img")
        register_name(name)
        self.name = name

class Knight(Piece):
    def __init__(self, color, name):
        self.type = "knight"
        self.img = Image(STANDARD_PIECES[self.type][color], color="none", name=name + "_img")
        register_name(name)
        self.name = name

class Bishop(Piece):
    def __init__(self, color, name):
        self.type = "bishop"
        self.img = Image(STANDARD_PIECES[self.type][color], color="none", name=name + "_img")
        register_name(name)
        self.name = name

class Rook(Piece):
    def __init__(self, color, name):
        self.type = "rook"
        self.img = Image(STANDARD_PIECES[self.type][color], color="none", name=name + "_img")
        register_name(name)
        self.name = name

class Queen(Piece):
    def __init__(self, color, name):
        self.type = "queen"
        self.img = Image(STANDARD_PIECES[self.type][color], color="none", name=name + "_img")
        register_name(name)
        self.name = name

class King(Piece):
    def __init__(self, color, name):
        self.type = "king"
        self.img = Image(STANDARD_PIECES[self.type][color], color="none", name=name + "_img")
        register_name(name)
        self.name = name

# ALL_PIECES = {
#       "pawn": Pawn,
#       "knight": Knight,
#       "bishop": Bishop,
#       "rook": Rook,
#       "queen": Queen,
#       "king": King,
# }
