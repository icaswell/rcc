import random
from graphics import Image
import piece
from piece import ALL_MOVING_STYLES
from constants import *

class Deck():
    def __init__(self, cards, shuffle=True):
        if not isinstance(cards, list):
            raise ValueError("Cards must be a list of Cards")
        self.cards = cards
        if shuffle:
          random.shuffle(cards)

    def draw_card(self):
        if not self.cards:
            return None
        return self.cards.pop(0)


class Card():
    # is]_active = True

    text = """Pls fill in the text field"""
    def __init__(self, game, name="uninintialized", is_persistent=False):

        """This also functions as the card draw action. Namely, the __init__ 
        method is the place to do anything to the game that happens when this card is drawn!
        """
        self.message = ""
        self.name = name
        self.is_persistent = is_persistent
        # text = ""

        self.img = Image(width=32, height=24)
        self.img.set_color("teal_highlight")
        self.img.print_in_string(self.name.replace("Card", ""), (3, 4))
        self.img.print_in_string(self.text, (5, 4))


    def __str__(self):
        return self.name

    def get_message(self) -> str:
        return self.message

    def upkeep_action(self, game):
        # e.g. advance plague
        pass

    def update_from_turn_results(self, turn_summary):
        # e.g. for A King is for Glory, update number of King takes and check for win
        pass

    def when_leaves_play(self, name) -> None:
        """"Cleanup" or "deconstructor: actions for a persistent card to take when this cards leaves play.
        TBH this is almost entirely for Back to the Basics."""
        pass

class ZamboniCard(Card):
    text = """Place a Zamboni on a center square at random.  The Zamboni moves one space per turn during your upkeep in a clockwise spiral around the board, pushing all pieces it hits. The Zamboni acts as a piece that cannot be taken.
If it ever reaches the end of the spiral, it exits the board and leaves play.
"""
    def __init__(self, game):
        super().__init__(game=game, name="ZamboniCard", is_persistent=True)
        squares_and_orientations = [("d4", "e"),  ("d5", "n"),  ("e4", "s"),  ("e5", "w")]
        birthsquare_name, self.orientation = random.choice(squares_and_orientations)
        self.message = f"A Zamboni has generated on square {birthsquare_name}!!!!"
        birthsquare = game.board.square_from_a1_coordinates(birthsquare_name)
        self.i_move_on_whose_upkeep = game.whose_turn

        self.zamboni = piece.ZamboniPiece(team="Elijah", name="Zamboni")
        squashed_pieces = birthsquare.occupants
        for squashed in squashed_pieces:
            game.mark_piece_as_dead_and_remove_from_board(squashed)
        birthsquare.occupants = [self.zamboni]
        self.zamboni.square_this_is_on = birthsquare

        # variables for trackign movement
        self.how_many_turns_have_i_traveled_straight = 0
        self.how_long_is_this_straightaway = 1
        self.whichth_straightaway = 0 # 0 or 1


    def upkeep_action(self, game) -> None:
        """TODO: bug when it runs into something that can't take. Not only does it not push it...it vanishes.
        """
        if game.whose_turn != self.i_move_on_whose_upkeep:
            return
        cur_square = self.zamboni.square_this_is_on
        next_square = cur_square.get_square_from_directions(piece=self.zamboni, directions=[self.orientation])

        if DEV_MODE:
          print(f"moving from {cur_square.name} to {next_square.name}")

        # If the zamboni has passed off the end of the board:
        if not next_square:
            game.active_cards.remove(self) # the card is no longer active
            self.zamboni.square_this_is_on.occupants.remove(self.zamboni)
        else:
            game.move_piece(self.zamboni, next_square, enforce_whose_turn_it_is=False)

        self.how_many_turns_have_i_traveled_straight += 1
        if self.how_many_turns_have_i_traveled_straight == self.how_long_is_this_straightaway:
            self.orientation = game.board.rotate_direction_clockwise(self.orientation, 2)
            self.how_many_turns_have_i_traveled_straight = 0
            if self.whichth_straightaway == 0:
                self.whichth_straightaway = 1
            else:
                self.whichth_straightaway = 0
                self.how_long_is_this_straightaway += 1

    def get_message(self) -> str:
        """Only give a message on the first turn it is drawn
        """
        msg = self.message
        self.msg = None
        return msg
    
    def when_leaves_play(self, game) -> None:
        self.zamboni.square_this_is_on.remove_occupant(self.zamboni)


class BackToTheBasics(Card):
    text = """Remove all cards from play that alter the rules of the game. This includes the removal of all nonstandard pieces."""
    def __init__(self, game):
        super().__init__(game=game, name="Back to the Basics", is_persistent=False)
        
        for card in game.active_cards:
            card.when_leaves_play(game)
        game.active_cards = []

    def get_message(self) -> str:
        return "You are back to the basics! There are no random cards in play!"

class Landslide(Card):
    text = """All Pawns, Knights and Bishops move as far to their owner’s left as they can, until they hit an edge or another piece."""
    def __init__(self, game):
        super().__init__(game=game, name="Landslide", is_persistent=False)
        self.message =  f"There was a landslide!! "

        # ASSUMES THAT BLACK IS ON THE BOTTOM AND WHITE ON TOP

        eligible_pieces = game.board.get_pieces(types=["pawn", "knight", "bishop"], team="Black", reverse_rows=False)
        direction = "w"
        self.message += f"{self.slide_pieces(game, eligible_pieces, direction)} Black pieces and "
        
        eligible_pieces = game.board.get_pieces(types=["pawn", "knight", "bishop"], team="White", reverse_rows=True)
        direction = "e"
        self.message += f"{self.slide_pieces(game, eligible_pieces, direction)} White pieces slipped to the left!"

    def slide_pieces(self, game, eligible_pieces, direction):
        n_slides = 0
        for piece in eligible_pieces:
            ray = piece.square_this_is_on.get_squares_in_ray(direction=direction, moving_piece=piece, only_nontaking=True)
            if not ray: continue
            game.move_piece(piece, ray[-1], enforce_whose_turn_it_is=False)
            
            game.board.highlight_square(ray[-1], color="yellow_highlight")
            n_slides += 1
        return n_slides

    def get_message(self) -> str:
        return self.message
        

class FlippedClassroom(Card):
    text = """Rotate board 180º. Continue playing. (Each player still controls the same pieces.)"""
    def __init__(self, game):
        super().__init__(game=game, name="Flipped Classroom", is_persistent=False)
        self.message = "You haven't switched teams... but the board has flipped!"
        
        # Reverse the grid
        game.board.board_grid = game.board.board_grid[::-1]

        # Reverse the grid indices
        new_row_names_to_idx = game.board.row_names_to_idx.copy()
        n_rows = len(game.board.row_names_to_idx)  # likely: 8
        for row_name, idx in game.board.row_names_to_idx.items():
            # row name is what humans call it (1-indexed), whereas indices are 0-indexed.
            # row_name ranges from e.g. 1 to 8
            # these items are e.g. "5: 4"
            new_row_names_to_idx[n_rows - row_name + 1] = idx
        game.board.row_names_to_idx = new_row_names_to_idx


# class TheMeek(Card):
#     text = """TODO"""
#     def __init__(self, game):
#         super().__init__(game=game, name="The Meek shall inherit the World", is_persistent=False)
#         self.message = ""
#         num_rows = len(game.board.board_grid)


class EpiscopiVagantes(Card):
    text = "Henceforward, Bishops may no longer take or be taken. Instead, what would normally have resulted in taking a Bishop (or being taken by one) now results in swapping places of the two pieces in question."
    def __init__(self, game):
        super().__init__(game=game, name="Episcopi Vagantes", is_persistent=True)
        self.message = "Bahaha! Your bishops can no longer take or be taken; they just swap places with the other piece!!!!!!"
        for piece in game.board.get_pieces(types=['bishop']):
            piece.interaction_type = InteractionType.SWAPPING
   
    def when_leaves_play(self, game):
        for piece in game.board.get_pieces(types=['bishop']):
            piece.interaction_type = InteractionType.TAKING


class IdentityCrisis(Card):
    text = """Roll two dice. The pieces that correspond to those numbers switch moving capabilities and roles. If the same number is rolled on both die, reroll:

1 = Pawns
2 = Knights
3 = Bishops
4 = Rooks
5 = Queen
6 = King

Concessions
Each player must have at least one of each of the two types of pieces. If this is not the case, reroll. If a 6 is rolled, the all of the new piece(s) that move as the King must be captured for the game to end, and if the original King is captured, the game continues.

"""
    def __init__(self, game):
        """IMPLEMENTATION DECISION: This also changes the type of the piece. This exegesis is from iterpretation of the clause about kings.
        MAJOR TODO: may not handle game end condition in the case of Kings.
        """
        super().__init__(game=game, name="Identity Crisis", is_persistent=True)
        piece_type_a, piece_type_b = random.choices(["pawn", "knight", "bishop", "rook", "queen", "king"], k=2)
        for piece in game.board.get_pieces(types=[piece_type_a]):
            piece.moves_as =  piece_type_b # # ALL_MOVING_STYLES[piece_type_b]
            piece.type = piece_type_b
        for piece in game.board.get_pieces(types=[piece_type_b]):
            piece.moves_as =  piece_type_a
            piece.type = piece_type_a
        self.piece_type_b = piece_type_b
        self.piece_type_a = piece_type_a

        self.message = f"Ach noo! all your {piece_type_a} move as {piece_type_b}, and vise versa!"
       
   
    def when_leaves_play(self, game):
        for piece in game.board.get_pieces(types=[self.piece_type_a]):
            piece.moves_as =  self.piece_type_a
            piece.type = self.piece_type_a
        for piece in game.board.get_pieces(types=[self.piece_type_b]):
            piece.moves_as =  self.piece_type_b
            piece.type = self.piece_type_b


ALL_CARDS = {
    "Zamboni": ZamboniCard,
    "Landslide": Landslide,
    "BackToTheBasics": BackToTheBasics,
    "FlippedClassroom": FlippedClassroom,
    "EpiscopiVagantes": EpiscopiVagantes,
    "Crisis": IdentityCrisis,
}

TEST_DECK = [IdentityCrisis, BackToTheBasics, EpiscopiVagantes, FlippedClassroom, Landslide, ZamboniCard, BackToTheBasics]
