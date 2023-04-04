import random
from graphics import Image
import piece
import board
from piece import ALL_MOVING_STYLES
from asset_library import PLAGUE_STAGES
from constants import *
from name_registry import get_unique_name

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

    text = """Pls fill in the text field"""
    def __init__(self, game, name="uninintialized", is_persistent=False):

        """This also functions as the card draw action. Namely, the __init__ 
        method is the place to do anything to the game that happens when this card is drawn!
        """
        self.message = ""
        self.name = name
        # self.is_persistent = is_persistent
        self.is_active = True if is_persistent else False
        self.i_was_drawn_on_whose_turn = game.whose_turn
        # text = ""

        self.img = Image(width=32, height=24)
        self.img.set_color("teal_highlight")
        self.img.print_in_string(self.name.replace("Card", ""), (3, 4))
        self.img.print_in_string(self.text, (5, 4))


    def __str__(self):
        return self.name

    def get_message(self) -> str:
        msg = self.message
        self.message = None
        return msg

    def upkeep_action(self, game):
        # e.g. advance plague
        pass

    def update_from_turn_results(self, turn_summary):
        # e.g. for A King is for Glory, update number of King takes and check for win
        pass

    def when_leaves_play(self, name) -> None:
        """"Cleanup" or "deconstructor: actions for a persistent card to take when this cards leaves play.
        TBH this is almost entirely for Back to the Basics."""
        self.is_active = False

class ZamboniCard(Card):
    text = """Place a Zamboni on a center square at random.  The Zamboni moves one space per turn during your upkeep in a clockwise spiral around the board, pushing all pieces it hits. The Zamboni acts as a piece that cannot be taken.
If it ever reaches the end of the spiral, it exits the board and leaves play.
"""
    def __init__(self, game):
        super().__init__(game=game, name="Zamboni", is_persistent=True)
        squares_and_orientations = [("d4", "e"),  ("d5", "n"),  ("e4", "s"),  ("e5", "w")]
        birthsquare_name, self.orientation = random.choice(squares_and_orientations)
        self.message = f"A Zamboni has generated on square {birthsquare_name}!!!!"
        birthsquare = game.board.square_from_a1_coordinates(birthsquare_name)

        self.zamboni = piece.ZamboniPiece(team="Elijah", name="Zamboni")
        squashed_pieces = birthsquare.occupants
        for squashed in squashed_pieces:
            game.mark_piece_as_dead_and_remove_from_board(squashed)
        birthsquare.add_occupant(self.zamboni)
        # birthsquare.occupants = [self.zamboni]
        # self.zamboni.square_this_is_on = birthsquare

        # variables for tracking movement
        self.how_many_turns_have_i_traveled_straight = 0
        self.how_long_is_this_straightaway = 1
        self.whichth_straightaway = 0 # 0 or 1
   
    def when_leaves_play(self, game):
        self.is_active = False
        game.mark_piece_as_dead_and_remove_from_board(self.zamboni)

    def upkeep_action(self, game) -> None:
        """TODO: bug when it runs into something that can't take. Not only does it not push it...it vanishes.
        """
        if game.whose_turn != self.i_was_drawn_on_whose_turn:
            return
        cur_square = self.zamboni.square_this_is_on
        next_square = cur_square.get_square_from_directions(piece=self.zamboni, directions=[self.orientation])

        if DEV_MODE:
          print(f"moving from {cur_square.name} to {next_square.name}")

        # If the zamboni has passed off the end of the board:
        if not next_square:
            self.is_active=False
            return
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


class BackToTheBasics(Card):
    text = """Remove all cards from play that alter the rules of the game. This includes the removal of all nonstandard pieces."""
    def __init__(self, game):
        super().__init__(game=game, name="Back to the Basics", is_persistent=False)
        
        for card in game.active_cards:
            card.when_leaves_play(game)
        game.active_cards = []

        self.message =  "You are back to the basics! There are no random cards in play!"

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
        self.is_active=False
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

        self.message = f"Ach noo! all your {piece_type_a} move as {piece_type_b}, and vice versa!"
       
   
    def when_leaves_play(self, game):
        self.is_active=False
        for piece in game.board.get_pieces(types=[self.piece_type_a]):
            piece.moves_as =  self.piece_type_a
            piece.type = self.piece_type_a
        for piece in game.board.get_pieces(types=[self.piece_type_b]):
            piece.moves_as =  self.piece_type_b
            piece.type = self.piece_type_b

class Coyote(Card):
    text = """Place Coyote on any square in the board.  Roll to determine whether Coyote moves as a Knight, a Bishop, a Rook, or a Queen. Coyote moves autonomously during your upkeep. Coyote cannot take or be taken.  When either of these events would occur, instead swap Coyote with the relevant piece.

Each move Coyote makes must be as far as possible--for instance, if Coyote moves as a Rook, each turn Coyote chooses between the options Left, Right, Forward, Back and No Move, and goes as far in that direction as possible - either hitting an edge or swapping places with a piece."""
    def __init__(self, game):
        super().__init__(game=game, name="Coyote", is_persistent=True)
        self.coyote = piece.CoyotePiece(team="Coyotus", name="Coyotus")

        birthsquare = game.board.get_random_square()
        self.message = f"Coyote (moving as a {self.coyote.moves_as}) has generated on square {birthsquare}!!"
        for occ in birthsquare.occupants:
            game.mark_piece_as_dead_and_remove_from_board(occ)
        birthsquare.add_occupant(self.coyote)
        # birthsquare.occupants = [self.coyote]
        # self.coyote.square_this_is_on = birthsquare
   
    def when_leaves_play(self, game):
        game.mark_piece_as_dead_and_remove_from_board(self.coyote)
        self.active = False

    def upkeep_action(self, game) -> None:
        if game.whose_turn != self.i_was_drawn_on_whose_turn:
            return
        if not self.coyote.alive:
            self.is_active=False
            return

        moves = self.coyote.get_possible_moves()
        move = random.choice(list(moves.id_to_move.values()))

        DEV_PRINT(f"moving from {self.coyote.square_this_is_on} to {move}")
        game.move_piece(self.coyote, move, enforce_whose_turn_it_is=False)

class Plague(Card):
    # I am sorry dear reader, this card is not implemented very cleanly.
    # one also need be careful to see whether the counters are implemented correctly.
    text = """Randomly select one of your pieces to come down with a highly infectious and deadly disease. On the third turn after being infected*, an infected piece first infects all pieces orthogonal to it. After it passes on the infection, roll a die to see whether it recovers from the plague, keeps the plague, or passes away. All three have equal probability. 
"""
    def __init__(self, game):
        super().__init__(game=game, name="Plague", is_persistent=True)
        self.messages = []
        pieces = game.board.get_pieces(team=game.whose_turn)
        infected_piece = random.choice(pieces)
        self.give_plague(infected_piece, None)
   
    def when_leaves_play(self, game):
        self.active = False
        for piece in game.board.get_pieces():
            del piece.special_stuff["plague_state"]

    def give_plague(self, infected_piece, infecting_piece):
        stage = 0
        if infecting_piece and infecting_piece.team != infected_piece.team:
            stage = -1
        infected_piece.special_stuff["plague_state"] = stage
        self.messages.append(f"{infected_piece} got the plague!")
        infected_piece.extra_images["plague"] = Image(from_string=PLAGUE_STAGES[0])

    def advance_plague(self, piece):
        if "plague_state" not in piece.special_stuff: return
        piece.special_stuff["plague_state"] += 1
        piece.extra_images["plague"] = Image(from_string=PLAGUE_STAGES[piece.special_stuff["plague_state"]])

    def upkeep_action(self, game) -> None:
        # plague state is defined such that its owner has two full teams before the fatal upkeep.
        self.message = ""
        at_least_one_piece_is_infected = False
        for piece in game.board.get_pieces():
            if "plague_state" not in piece.special_stuff: continue
            at_least_one_piece_is_infected = True
            self.advance_plague(piece)
            self.messages.append(f"{piece}'s plague advanced to stage {piece.special_stuff['plague_state']}!")
            if piece.special_stuff["plague_state"] == 4:
                for adjacent_piece in piece.square_this_is_on.get_adjacent_occupants():
                  self.give_plague(infected_piece=adjacent_piece, infecting_piece=piece)
                prognosis = random.choice([0, 1, 2])
                if prognosis == 0:  # recovery!
                    del piece.special_stuff["plague_state"]
                    del piece.extra_images["plague"]
                    self.messages.append(f"{piece} recovered!")
                elif prognosis == 0:  # stays sick!
                    self.give_plague(infected_piece, None)
                    self.messages.append(f"{piece} still has plague!!")
                else:  # dies!
                    game.mark_piece_as_dead_and_remove_from_board(piece)
                    self.messages.append(f"{piece} died!")
        if not at_least_one_piece_is_infected:
            self.messages.append("WOW YOU BEAT THE PANDEMIC!!!!")
            self.is_active = False

    def get_message(self) -> str:
        msg = "; ".join(self.messages)
        self.messages = []
        return msg

class Tesseract(Card):
    text = """Randomly choose one column that has no royal pieces on it.  Remove this column from the board. All pieces on it are removed from play, and the board now is 7 by 8 squares."""
    def __init__(self, game):
        super().__init__(game=game, name="Tesseract", is_persistent=True)
        
        potential_cols = {i for i in range(game.board.board_width)}
        for row in game.board.board_grid:
            for col_j in range(len(row)):
                if any(occ.is_royal for occ in row[col_j].occupants):
                    potential_cols == {col_j}
        self.removed_col = random.choice(list(potential_cols))

        self.removed_occs = []
        self.removed_squares = []
        for row_i in range(len(game.board.board_grid)):
            doomed_square = game.board.board_grid[row_i].pop(self.removed_col)
            self.removed_occs += doomed_square.occupants
            self._crosswire_neighbors(doomed_square)
            self.removed_squares.append(doomed_square)
        game.board.board_width -= 1
        game.board.make_border_images()

        for removed_piece in self.removed_occs:
            # the only purpose of moving these is so they can't
            # be selected in the normal way, because this would cause
            # an error if they tried to move to a square via an a1 coordinate that no longer existed.
            # This itself is only likely to be an issue because of how nonsense_turn relies on living_pieces
            team = removed_piece.team
            if team in game.living_pieces:
              game.living_pieces[team].remove(removed_piece)

        self.removed_letter = 'abcdefgh'[self.removed_col]
        for letter, idx in game.board.col_names_to_idx.items():
            if letter > self.removed_letter: 
                game.board.col_names_to_idx[letter] -= 1
        game.board.col_names_to_idx.pop(self.removed_letter)
        self.message = f"Column {self.removed_letter.upper()} was folded out of existence, leaving the following pieces unmoored in a different dimension: {self.removed_occs}"

    def _decrosswire_neighbors(self, square: board.Square):
        left_neighbor, right_neighbor = square.get_neighbor("w"), square.get_neighbor("e")
        n, s = square.get_neighbor("n"), square.get_neighbor("s")

        if left_neighbor is not None:
            left_neighbor.update_neighbors({"ne": n, "se": s, "e": square}) 
        if right_neighbor is not None:
            right_neighbor.update_neighbors({"nw": n, "sw": s, "w": square}) 


    def _crosswire_neighbors(self, square: board.Square):
        left_neighbor, right_neighbor = square.get_neighbor("w"), square.get_neighbor("e")

        if left_neighbor is not None:
            ne = square.get_neighbor("ne")
            se = square.get_neighbor("se")
            left_neighbor.update_neighbors({"ne": ne, "se": se, "e": right_neighbor}) 

        if right_neighbor is not None:
            nw = square.get_neighbor("nw")
            sw = square.get_neighbor("sw")
            right_neighbor.update_neighbors({"nw": nw, "sw": sw, "w": left_neighbor}) 

   
    def when_leaves_play(self, game):
        for letter, idx in game.board.col_names_to_idx.items():
            if letter > self.removed_letter: 
                game.board.col_names_to_idx[letter] += 1
        game.board.col_names_to_idx[self.removed_letter] = self.removed_col
        for row_i in range(len(game.board.board_grid)):
            game.board.board_grid[row_i].insert(self.removed_col, self.removed_squares[row_i])
            self._decrosswire_neighbors(self.removed_squares[row_i])
        game.board.board_width += 1
        game.board.make_border_images()
        for removed_piece in self.removed_occs:
            team = removed_piece.team
            game.living_pieces[team].append(removed_piece)

        

class Rabbit(Card):
    text = """Place a rabbit under your control anywhere on your side of the board such that it cannot take on its first move.  The rabbit moves by hopping two spaces orthogonally.

During your upkeep, for each rabbit in play (whether they belong to you or not), roll a die.  If it comes up 1 or 2, the owner of that rabbit adds another rabbit on an unoccupied square of their choosing  orthogonally adjacent to that rabbit, under their control.  If it comes up a 6, that rabbit becomes autonomous.

As a turn, a player may domesticate any rabbit adjacent to one of their pieces.  The domesticated rabbit is now under that player’s control.

"""
    def __init__(self, game):
        super().__init__(game=game, name="Rabbit", is_persistent=True)
        rabbit = piece.RabbitPiece(team="autonomous", name="Rabbitus")
        generation_square = game.board.get_random_square(must_be_unoccupied=True, piece_that_cannot_take_from_here=rabbit)
        generation_square.add_occupant(rabbit)
        # TODO actually you can chose where to place the rabbit!
        self.messages = [f"A Wild Rabbit has appeared on {generation_square}!"]
   
    def when_leaves_play(self, game):
        self.active = False
        for piece in game.board.get_pieces():
            if piece.type == "rabbit":
                piece.square_this_is_on.remove_occupant(piece)

    def generate_offspring(self, parent):
        neighbors = parent.square_this_is_on.get_squares_from_directions_list(parent, directions_list=[["n"], ["e"], ["s"], ["w"]])
        unoccupied_neighbors = [neigh for neigh in neighbors if not neigh.occupants]
        if not unoccupied_neighbors:
            self.messages.append(f"{parent} could not generate offspring because there is no available square")
            return
        birthsquare = random.choice(unoccupied_neighbors )

        offspring = piece.RabbitPiece(team=parent.team, name="Rabbitus")
        birthsquare.add_occupant(offspring)
        self.messages.append(f"{parent} had offspring {offspring} on square {birthsquare}")

    def upkeep_action(self, game) -> None:
        if game.whose_turn != self.i_was_drawn_on_whose_turn:
            return
        for rabbit in  game.board.get_pieces(types=["rabbit"]):
            die_roll = random.randint(1, 6)
            if die_roll == 6:
                rabbit.set_team("autonomous")
            if die_roll in {1, 2}:
                self.generate_offspring(rabbit)

            moves = rabbit.get_possible_moves()
            move = random.choice(list(moves.id_to_move.values()))

            DEV_PRINT(f"moving {rabbit} from {rabbit.square_this_is_on} to {move}")
            game.move_piece(rabbit, move, enforce_whose_turn_it_is=False)




    def get_message(self) -> str:
        msg = "; ".join(self.messages)
        self.messages = []
        return msg



ALL_CARDS = {
    "Zamboni": ZamboniCard,
    "Landslide": Landslide,
    "BackToTheBasics": BackToTheBasics,
    "FlippedClassroom": FlippedClassroom,
    "EpiscopiVagantes": EpiscopiVagantes,
    "Crisis": IdentityCrisis,
    "Coyote": Coyote,
    "Plague": Plague,
    "Tesseract": Tesseract,
    "Rabbit": Rabbit,
}

TEST_DECK = [Rabbit, Plague, Coyote, Tesseract, BackToTheBasics, Plague, Coyote, IdentityCrisis, BackToTheBasics, EpiscopiVagantes, FlippedClassroom, Landslide, ZamboniCard, BackToTheBasics]
