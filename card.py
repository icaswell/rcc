import random
from graphics import Image, colorize
import piece
import board
from piece import ALL_MOVING_STYLES
import asset_library as assets
from constants import *
from commands import COMMAND_ACTIONS, user_choose_square, user_choose_list_item
from name_registry import get_unique_name
from typing import List


class Deck():
  def __init__(self, cards):
    if not isinstance(cards, list):
      raise ValueError("Cards must be a list of Cards")
    self.cards = cards

  def draw_card(self, turn_number):
    available_cards = self.cards
    if not turn_number:
      available_cards = [c for c in self.cards if c.can_be_drawn_first_turn]
    if not available_cards:
      return None
    card = random.choice(available_cards)
    self.cards.remove(card)
    return card


class Card():
  text = """Pls fill in the text field"""
  can_be_drawn_first_turn = True
  def __init__(self, game, name="uninintialized", is_persistent=False):
    """This also functions as the card draw action. Namely, the __init__ 
    method is the place to do anything to the game that happens when this card is drawn!
    """
    self.message = ""
    self.name = name
    self.is_active = True if is_persistent else False
    self.i_was_drawn_on_whose_turn = game.whose_turn
    self.img = Image(width=32, height=24)
    self.img.set_color("teal_highlight")
    self.img.print_in_string_nicely(self.name.replace("Card", ""), (3, 4))
    self.img.print_in_string_nicely(self.text, (5, 4))

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

  def action_after_piece_moves(self, game, piece_that_moved: piece.Piece, taken_pieces: List[piece.Piece]) -> None:
    """A few cards may use this, like Riastrad."""
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
    super().__init__(game=game, name=get_unique_name("Zamboni"), is_persistent=True)
    squares_and_orientations = [("d4", "e"),  ("d5", "n"),  ("e4", "s"),  ("e5", "w")]
    birthsquare_name, self.orientation = random.choice(squares_and_orientations)
    self.message = f"A Zamboni has generated on square {birthsquare_name}!!!!"
    birthsquare = game.board.square_from_a1_coordinates(birthsquare_name)

    self.zamboni = piece.ZamboniPiece(team="Elijah", name="Zamboni")
    squashed_pieces = birthsquare.occupants
    for squashed in squashed_pieces:
      game.mark_piece_as_dead_and_remove_from_board(squashed)
    birthsquare.add_occupant(self.zamboni)

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
    next_square = cur_square.get_square_from_directions(moving_piece=self.zamboni, directions=[self.orientation])

    if DEV_MODE:
      print(f"moving from {cur_square.name} to {next_square.name}")

    # If the zamboni has passed off the end of the board:
    if not next_square:
      self.is_active=False
      return
    else:
      game.animate_render()
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
  can_be_drawn_first_turn = False
  def __init__(self, game):
    super().__init__(game=game, name="Back to the Basics", is_persistent=False)
    for card in game.active_cards:
      card.when_leaves_play(game)
    game.active_cards = []

    self.message =  "You are back to the basics! There are no random cards in play!"

class Landslide(Card):
  text = """All Pawns, Knights and Bishops move as far to their owner’s left as they can, until they hit an edge or another piece."""
  can_be_drawn_first_turn = False
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

      game.board.highlight_square(ray[-1], color="teal_highlight")
      n_slides += 1
    return n_slides

class FlippedClassroom(Card):
  text = """Rotate board 180º. Continue playing. (Each player still controls the same pieces.)"""
  can_be_drawn_first_turn = False
  def __init__(self, game):
    super().__init__(game=game, name="Flipped Classroom", is_persistent=False)
    self.message = "You haven't switched teams... but the board has flipped!"

    # I don't think  this is right:
    # for p in game.human_players:
    #   p.home_row = abs(p.home_row - n_rows + 1)
    #   p.orientation = game.board.rotate_direction_clockwise(p.orientation, 4) 

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
#     can_be_drawn_first_turn = False
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
      game.board.highlight_square(piece.square_this_is_on, color="teal_highlight")

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
    piece_type_a, piece_type_b = random.sample(["pawn", "knight", "bishop", "rook", "queen", "king"], k=2)
    for piece in game.board.get_pieces(types=[piece_type_a]):
      game.board.highlight_square(piece.square_this_is_on, color="teal_highlight")
      piece.moves_as =  piece_type_b # # ALL_MOVING_STYLES[piece_type_b]
      piece.type = piece_type_b
    for piece in game.board.get_pieces(types=[piece_type_b]):
      game.board.highlight_square(piece.square_this_is_on, color="teal_highlight")
      piece.moves_as =  piece_type_a
      piece.type = piece_type_a
    self.piece_type_b = piece_type_b
    self.piece_type_a = piece_type_a
    game.animate_render(n_secs_post_wait=1)

    self.message = f"Ach noo! all your {piece_type_a}s move as {piece_type_b}s, and vice versa!"


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
    game.select_square_and_occupant(self.coyote.square_this_is_on)
    game.animate_render()

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
    game.select_square_and_occupant(self.coyote.square_this_is_on)
    game.animate_render()
    game.move_piece(self.coyote, move, enforce_whose_turn_it_is=False)

class Plague(Card):
  # I am sorry dear reader, this card is not implemented very cleanly.
  # one also need be careful to see whether the counters are implemented correctly.
  text = """Randomly select one of your pieces to come down with a highly infectious and deadly disease. On the third turn after being infected*, an infected piece first infects all pieces orthogonal to it. After it passes on the infection, roll a die to see whether it recovers from the plague, keeps the plague, or passes away. All three have equal probability. 
"""
  def __init__(self, game):
    super().__init__(game=game, name="Plague", is_persistent=True)
    self.messages = []
    pieces = game.board.get_pieces(team=game.whose_turn.team)
    infected_piece = random.choice(pieces)
    self.give_plague(infected_piece, None)

  def when_leaves_play(self, game):
    self.active = False
    for piece in game.board.get_pieces():
      if "plague_state" in piece.special_stuff:
        del piece.special_stuff["plague_state"]

  def give_plague(self, infected_piece, infecting_piece):
    stage = 0
    if infecting_piece and infecting_piece.team != infected_piece.team:
      stage = -1
    infected_piece.special_stuff["plague_state"] = stage
    self.messages.append(f"{infected_piece} got the plague!")
    infected_piece.extra_images["plague"] = Image(from_string=assets.PLAGUE_STAGES[0])

  def advance_plague(self, piece):
    if "plague_state" not in piece.special_stuff: return
    piece.special_stuff["plague_state"] += 1
    piece.extra_images["plague"] = Image(from_string=assets.PLAGUE_STAGES[piece.special_stuff["plague_state"]])

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
          potential_cols -= {col_j}
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


def rabbit_domesticate_cmd(game, args, kwargs, display):
  """This method is public bc it needs to be put in COMMANDS"""
  game.deselect_all()
  domesticatable_rabbits = set()
  for my_piece in game.board.get_pieces(team=game.whose_turn.team):
    for orthogonal_neighbor_square in my_piece.square_this_is_on.get_orthogonal_squares(my_piece):
      for occ in orthogonal_neighbor_square.occupants:
        if occ.type == "rabbit" and occ.team != game.whose_turn.team:
          domesticatable_rabbits.add(occ)
  domesticatable_rabbits = list(domesticatable_rabbits)
  for i, rabbit in enumerate(domesticatable_rabbits):
    game.board.highlight_square(rabbit.square_this_is_on, color="teal_highlight")
    game.board.annotate_square(rabbit.square_this_is_on, annotation = str(i))
  DEV_PRINT(f"You can domesticate these rabbits: {domesticatable_rabbits}")
  
  if not domesticatable_rabbits:
    DEV_PRINT("THERE ARE NO RABBITS ORTHOGONALLY ADJACENT TO YOUR PIECES SO YOU CAN'T DOMESTICATE")
    return

  # game.render(clear_messages=False)
  # while True:
  #   if len(domesticatable_rabbits) == 1:
  #     choice = 0
  #     break
  #   line = input(f"Enter a number from 0 to {len(domesticatable_rabbits) -1} to indicate which rabbit you want to domesticate:").strip()
  #   if not line.isnumeric():
  #     print(colorize("enter a numeric value", "red"))
  #     continue
  #   choice = int(line)
  #   if not (0 <= choice < len(domesticatable_rabbits)):
  #     print(colorize("enter a value between 0 and {len(domesticatable_rabbits) -1}", "red"))
  #     continue
  #   break
  domesticatable_rabbits_squares = [r.square_this_is_on for r in domesticatable_rabbits]
  rabbit_to_domesticate_i = user_choose_square(game, domesticatable_rabbits_squares)
  rabbit_to_domesticate = domesticatable_rabbits[rabbit_to_domesticate_i]
  game.change_piece_team(rabbit_to_domesticate, game.whose_turn.team)
  # It counts as a move
  game.incorporate_action_and_check_for_end_of_turn("m")



class Rabbit(Card):
  text = """Place a rabbit under your control anywhere on your side of the board such that it cannot take on its first move.  The rabbit moves by hopping two spaces orthogonally.

During your upkeep, for each rabbit in play (whether they belong to you or not), roll a die.  If it comes up 1 or 2, the owner of that rabbit adds another rabbit on an unoccupied square of their choosing  orthogonally adjacent to that rabbit, under their control.  If it comes up a 6, that rabbit becomes autonomous.

As a turn, a player may domesticate any rabbit adjacent to one of their pieces.  The domesticated rabbit is now under that player’s control.

"""
  can_be_drawn_first_turn = False
  def __init__(self, game):
    super().__init__(game=game, name="Rabbit", is_persistent=True)
    rabbit = piece.RabbitPiece(team="Autonomous", name="Rabbitus")
    birthsquare = game.board.get_random_square(must_be_unoccupied=True, piece_that_cannot_take_from_here=rabbit)
    if birthsquare is None:
      self.active=False
      self.messages = [f"There was nowhere for a Rabbit to generate, so this card was skipped!"]
      return
    birthsquare.add_occupant(rabbit)
    # TODO actually you can chose where to place the rabbit!
    self.messages = [f"A Wild Rabbit has appeared on {birthsquare}!"]

    COMMAND_ACTIONS["domesticate"] = rabbit_domesticate_cmd
    COMMAND_ACTIONS["dom"] = rabbit_domesticate_cmd

  def when_leaves_play(self, game):
    self.active = False
    for rabbit in game.board.get_pieces(types=["rabbit"]):
      rabbit.square_this_is_on.remove_occupant(rabbit)
    del COMMAND_ACTIONS["domesticate"] 
    del COMMAND_ACTIONS["dom"] 


  def generate_offspring(self, game, parent):
    neighbors = parent.square_this_is_on.get_squares_from_directions_list(parent, directions_list=[["n"], ["e"], ["s"], ["w"]])
    unoccupied_neighbors = [neigh for neigh in neighbors if not neigh.occupants]
    if not unoccupied_neighbors:
      self.messages.append(f"{parent} could not generate offspring because there is no available square")
      return
    birthsquare = random.choice(unoccupied_neighbors)
    assert birthsquare is not None

    offspring = piece.RabbitPiece(team=parent.team, name="Rabbitus")
    birthsquare.add_occupant(offspring)
    game.board.highlight_square(birthsquare, color="teal_highlight")
    self.messages.append(f"{parent} had offspring {offspring} on square {birthsquare}")
    game.animate_render()

  def upkeep_action(self, game) -> None:
    if game.whose_turn != self.i_was_drawn_on_whose_turn:
      return
    for rabbit in game.board.get_pieces(types=["rabbit"]):
      if not rabbit.alive:  # it probably got taken by another rabbit earlier this iteration
        continue
      # Slecting the rabbit is for visual porpoises
      DEV_PRINT(f"  Upkeep for {rabbit.name}")
      die_roll = random.randint(1, 6)
      if die_roll == 6 and rabbit.team  != "Autonomous":
        DEV_PRINT(f"  Went autonomous!!")
        game.living_pieces[rabbit.team].remove(rabbit)
        game.change_piece_team(rabbit, "Autonomous")
        game.animate_render()
      if die_roll in {1, 2}:
        self.generate_offspring(game, rabbit)
        DEV_PRINT(f"  Had Offspring!")

      # in classic RCC, only autonomous rabbits moved.
      # But i decided to change this!!
      # if rabbit.team == "Autonomous":
      game.select_square_and_occupant(rabbit.square_this_is_on)
      game.animate_render()
      moves = rabbit.get_possible_moves()
      if moves:
        move = random.choice(list(moves.id_to_move.values()))
        game.move_piece(rabbit, move, enforce_whose_turn_it_is=False)
        game.animate_render()

  def get_message(self) -> str:
    msg = "; ".join(self.messages + ["Remember you can domesticate a rabbit with the command 'dom[esticate]'!"])
    self.messages = []
    return msg


class Riastrad(Card):
  text = """Mark one of your pieces. Whenever this piece takes, it enters a battle rage and must take again immediately if possible, where all takes past the first one are chosen at random (choose randomly among all possible takes, with the additional option of stopping the frenzy). It may take friendly pieces. It may not take a King except for as its first take in a turn."""
  can_be_drawn_first_turn = True
  def __init__(self, game):
    super().__init__(game=game, name="Riastrad", is_persistent=True)
    eligible_pieces = game.board.get_pieces(team=game.whose_turn.team)
    eligible_squares = [p.square_this_is_on for p in eligible_pieces]
    game.deselect_all()
    piece_i = user_choose_square(game, eligible_squares)
    chosen_piece = eligible_pieces[piece_i]
    self.message = f"{chosen_piece} is marked with the warp spasm! When this piece takes, the warp spasm comes upon it. Its shanks and joints shake like a tree in the flood or a reed in the stream. Its body makes a furious twist inside its skin, so that its feet and shins switch to the rear and his heels and calves switch to the front...There is heard the loud clap of its heart against his breast like the yelp of a howling bloodhound or like a lion going among bears...it sucks one eye so deep into its head that a wild crane couldn't probe it onto its cheek out of the depths of its skull; the other eye falls out along its cheek. The Lon Laith stands out of its forehead, so that it is as long and as thick as a warrior's whetstone. As high, as thick, as strong, as steady, as long as the sail-tree of some huge prime ship is the straight spout of dark blood which arises right on high from the very ridge-pole of its crown."
    chosen_piece.special_stuff["riastrad"] = True
    chosen_piece.extra_images["plague"] = Image(from_string=assets.riastrad_img)

  def when_leaves_play(self, game):
    self.active = False
    for piece in game.board.get_pieces():
      if "riastrad" in piece.special_stuff:
        del piece.special_stuff["riastrad"]


  def action_after_piece_moves(self, game, piece_that_moved: piece.Piece, taken_pieces: List[piece.Piece]) -> None:
    if not taken_pieces: return
    if "riastrad" not in piece_that_moved.special_stuff: return
    game.animate_render()

    actual_team_of_the_piece = piece_that_moved.team
    newly_taken_pieces = []
    while True:
      # Get the moves, but first it temporarily changes team (and can therefore take its own team)
      piece_that_moved.team = "Ulster"
      moves = piece_that_moved.get_possible_moves()
      piece_that_moved.team = actual_team_of_the_piece

      moves = [sq for sq in moves.taking if not any([occ.type == "king" for occ in sq.occupants])]
      if not moves:
        break
      moves.append(None) # add a "do not move and break this cycle" option
      which_move = random.choice(moves)
      if which_move is None:
        DEV_PRINT("Rampage has stopped!")
        break
      # Select the sqare+occupants just so the viewers can see its location and choice at each time
      # game.select_square_and_occupant(piece_that_moved.square_this_is_on)
      # a hack to make sure that the piece that is rampaging is always colored red
      color_me_red = piece.PieceMoves(square=None, moving_piece=piece_that_moved, taking_moves=[which_move], nontaking_moves=[])
      game._cur_available_piece_moves = color_me_red
      newly_taken_pieces += game.move_piece(piece_that_moved, which_move, enforce_whose_turn_it_is=False, do_card_end_actions=False)
      game.animate_render()
    if newly_taken_pieces:
      taken_pieces += newly_taken_pieces
      taken_pieces_str = ', '.join([str(p) for p in taken_pieces[0:-1]]) + f" and {taken_pieces[-1]}"
      self.message = f"When the wasp spasm had cleared, {piece_that_moved} looked around it at the slain, counting among their number {taken_pieces_str}"
    else:
      self.message = f"{piece_that_moved} was feeling very chill today and did not enter the warp spasm"



class AKingIsForGlory(Card):
  text = """Starting this turn, if either player’s King takes two of their opponent’s pieces, that player wins the game."""
  can_be_drawn_first_turn = True
  def __init__(self, game):
    super().__init__(game=game, name="A King is for Glory, not for Long Life", is_persistent=True)
    self.king_takes_per_team = {}

  def when_leaves_play(self, game):
    self.active = False

  def action_after_piece_moves(self, game, piece_that_moved: piece.Piece, taken_pieces: List[piece.Piece]) -> None:
    if piece_that_moved.type != "king" or not  taken_pieces: return
    if piece_that_moved.team not in self.king_takes_per_team:
      self.king_takes_per_team[piece_that_moved.team] = 0
    self.king_takes_per_team[piece_that_moved.team] += 1
    self.message = f"Wae thee, for {piece_that_moved} has taken {taken_pieces}!!!"
    if self.king_takes_per_team[piece_that_moved.team] >= 2:
      game.king_deaths[piece_that_moved.team] += 1
      self.message += "  Being as that is the second such noble take, the game is hereby ended."



class TimeBandits(Card):
  text = """Take turns placing time portals on unoccupied squares on the board, starting with you.  Each player places two.  They may not be placed in the opponent’s King row or Pawn row. Any piece that lands on a Time Portal is transported to the Time Vortex. During each player’s upkeep, that player rolls a die for each of their pieces in the Time Vortex. If it comes up a one, that piece appears on one of the time portals at random.

Ramifications
Pieces can be taken while on the time portal: the taking piece will just enter the Time Vortex. Similarly, if piece A is on a time portal and piece B reënters the board on top of A from having been in the time portal, piece A is taken. Sliding pieces can slide over time portals.


“God isn't interested in technology. He cares nothing for the microchip or the silicon revolution. Look how he spends his time, forty-three species of parrots! Nipples for men!” –Evil
"""
  can_be_drawn_first_turn = True
  def __init__(self, game):
    super().__init__(game=game, name="TODO", is_persistent=True)

  def when_leaves_play(self, game):
    self.active = False

  def upkeep_action(self, game) -> None:
    if game.whose_turn != self.i_was_drawn_on_whose_turn:
      return


def necromance_cmd(game, args, kwargs, display):
  revivable_pieces = [p for dead_team in game.dead_pieces.values() for p in dead_team]
  if not revivable_pieces:
    # self.messages.append("Nothing to Revive!"_
    return
  eligible_pieces = []
  for nec in game.board.get_pieces(team=game.whose_turn.team, types=["necromancer"]):
    eligible_pieces += game.board.get_pieces(team=game.whose_turn.team, adjacent_to=nec)
  if not eligible_pieces:  # or no dead pieces
    # self.messages.append("Necromancer is not adjacent to any potential sacrifice!")
    return

  eligible_squares = [p.square_this_is_on for p in eligible_pieces]
  game.deselect_all()
  sq_i = user_choose_square(game, eligible_squares, message="You will now choose which piece to sacrifice.")

  print(colorize(f"You chose to sacrifice {eligible_pieces[sq_i]}!", "teal_highlight"))

  game.mark_piece_as_dead_and_remove_from_board(eligible_pieces[sq_i])

  game.deselect_all()
  revived_i = user_choose_list_item(revivable_pieces, print_options=True, message="You will now choose which piece to revive.")
  revived_piece = revivable_pieces[revived_i]
  print(colorize(f"You chose to revive {revived_piece}!", "teal_highlight"))

  game.raise_piece_from_dead(revived_piece, birthsquare=eligible_squares[sq_i], new_team=game.whose_turn.team)

  revived_piece.extra_images["necromancers"] = Image(from_string=assets.undead_marker_img)
  revived_piece.special_stuff["undead"] = True

  # It counts as a move
  game.incorporate_action_and_check_for_end_of_turn("m")



class NeckRomancers(Card):
  text = """Each player gains control of a Necromancer, which they can place anywhere on their backmost row.  The necromancer moves as an Elephant (hopping two spaces diagonally).

As a turn, a player may sacrifice a one of their pieces adjacent to their Necromancer to revive a fallen piece on the square of the sacrificed piece. The revived piece may be any piece that was once on the board, belonging to either player. It is now under the control of the player whose Necromancer revived it.

During each player’s upkeep, they roll a die for each undead piece under their control on the board.  If it comes up a 6, that piece decomposes and leaves play.

"""
  can_be_drawn_first_turn = True
  def __init__(self, game):
    super().__init__(game=game, name="Neck Romancers", is_persistent=True)

    COMMAND_ACTIONS["necromance"] = necromance_cmd
    COMMAND_ACTIONS["nec"] = necromance_cmd
    self.messages = []

    for p in game.players_starting_with_me():
      game.deselect_all()
      eligible_squares = game.board.get_squares(rows=[p.home_row], unoccupied=False)
      sq_i = user_choose_square(game, eligible_squares)
      
      birthsquare = eligible_squares[sq_i]

      squashed_pieces = birthsquare.occupants
      for squashed in squashed_pieces:
        game.mark_piece_as_dead_and_remove_from_board(squashed)

      necromancer = piece.NecromancerPiece(team=p.team, name=f"{p.team} Necromance")
      birthsquare.add_occupant(necromancer)
      game.living_pieces[p.team].append(necromancer)

  def get_message(self) -> str:
    msg = "; ".join(self.messages + ["Remember you can raise a piece from the dead with the command 'nec[romance]'!"])
    self.messages = []
    return msg

  def _disenchant_piece(self, undead_piece:piece.Piece) -> None:
    """TODO ideally somehow this is incorporated into piece's when_dies method
    """
    if "undead" in undead_piece.special_stuff:
      del undead_piece.special_stuff["undead"]
    if "necromancers" in piece.extra_images:
      del undead_piece.extra_images["necromancers"]

  def when_leaves_play(self, game):
    # Remove undead pieces
    # remove necromancers
    self.active = False
    for piece in game.board.get_pieces():
      if "undead" in piece.special_stuff or piece.type == "necromancer":
        game.mark_piece_as_dead_and_remove_from_board(piece)
      self._disenchant_piece(piece)

  def upkeep_action(self, game) -> None:
    self.message = ""
    at_least_one_decomposition = False
    for piece in game.board.get_pieces():
      if "undead" not in piece.special_stuff: continue
      if random.randint(1, 6) != 1: continue
      at_least_one_decomposition = True
      game.board.highlight_square(piece.square_this_is_on, color="red_highlight")
      game.mark_piece_as_dead_and_remove_from_board(piece)
      del piece.special_stuff["undead"]
      self.messages.append(f"{piece} decomposed!")
    if at_least_one_decomposition:
      game.animate_render()


# class Copyme(Card):
#   text = """"""
#   can_be_drawn_first_turn = False
#   def __init__(self, game):
#     super().__init__(game=game, name="TODO", is_persistent=True)
# 
#   def when_leaves_play(self, game):
#     self.active = False
# 
#   def upkeep_action(self, game) -> None:
#     if game.whose_turn != self.i_was_drawn_on_whose_turn:
#       return

# class Copyme(Card):
#   text = """"""
#   can_be_drawn_first_turn = False
#   def __init__(self, game):
#     super().__init__(game=game, name="TODO", is_persistent=True)
# 
#   def when_leaves_play(self, game):
#     self.active = False
# 
#   def upkeep_action(self, game) -> None:
#     if game.whose_turn != self.i_was_drawn_on_whose_turn:
#       return


# the keys here are short names that are used largely for debugging when the user draws a specific card.
ALL_CARDS = {
    "zamboni": ZamboniCard,
    "landslide": Landslide,
    "basics": BackToTheBasics,
    "flipped": FlippedClassroom,
    "episcopi": EpiscopiVagantes,
    "crisis": IdentityCrisis,
    "coyote": Coyote,
    "plague": Plague,
    "tesseract": Tesseract,
    "rabbit": Rabbit,
    "riastrad": Riastrad,
    "glory": AKingIsForGlory,
    "neck": NeckRomancers,
}

TEST_DECK = [NeckRomancers, AKingIsForGlory, Riastrad, Rabbit, Plague, Coyote, Tesseract, BackToTheBasics, Plague, Coyote, IdentityCrisis, BackToTheBasics, EpiscopiVagantes, FlippedClassroom, Landslide, ZamboniCard, BackToTheBasics]
