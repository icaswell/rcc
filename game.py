from collections import defaultdict
import random
import time
from typing import List, Set, Dict, Union
import random

from board import Board, Square
from card import ALL_CARDS, Card
from constants import *
from graphics import Image, wrap_collapse, vertical_collapse, colorize
from piece import Piece, PieceMoves
from asset_library import DICE_FACES, IMAGE_STRINGS
from name_registry import get_unique_name
import commands

class Game(): pass
class Game():
  def __init__(self, game_config):
    self.game_config = game_config
    self.board = Board(game_config)
    self.all_cards = []
    self.human_players = game_config["players"]
    self.king_deaths = {player.team:0 for player in self.human_players}
    self.living_pieces =    defaultdict(list)
    self.dead_pieces =      defaultdict(list)
    for piece in self.board.get_pieces():
      self.living_pieces[piece.team].append(piece)
    # this is where the cursor reappears if you move the cursor when there has been no slection
    self.backup_selected_square = self.board.square_from_a1_coordinates("D4") # this will fail if the board is smaller than 4x4...but...


    self.die_roll = 1
    self.die_roll_fn = game_config["die_roll_function"]
    self.deck = game_config["deck"]()
    self.active_cards = []
    # self.past_cards = []

    self.turn_number = 0
    self.whose_turn = self.human_players[0]
    self.selected_square = None
    self.selected_pieces = []
    self.messages_this_turn = ["There are no selected pieces."]
    self._cur_available_piece_moves = None
    self.available_actions_per_turn = ["m"]  # default: can do one Move ("m")
    self.available_actions_this_turn = self.available_actions_per_turn.copy()


    # HISTORY AND REPRODUCIBILITY
    # maps turn number to stuff about the board. Ideally, everything can be written to a json....
    seed = random.randint(0, 1000000)
    random.seed(seed)
    self.command_history = [f"set_random_seed {seed}"]

    # rendering stuff
    self.graveyard_width = game_config["square_width"] * 4 + 2 # aka it can fit four pieces, plus two pixels for good luck

  def check_for_winner(self):
    # Obviously this has to change
    if self.king_deaths["White"] > 0: return "Black"
    if self.king_deaths["Black"] > 0: return "White"
    return None

  def incorporate_action_and_check_for_end_of_turn(self, action):
    if not self.available_actions_this_turn:
      raise ValueError(f"Action {action} is not possible this turn, as there are no more available actions this turn.")
    if action not in self.available_actions_this_turn:
      raise ValueError(f"Action {action} is not possible this turn; you can only do {self.available_actions_this_turn}")
    self.available_actions_this_turn.remove(action)

    if not self.available_actions_this_turn:
      # Aha! you have no more actions so the turn ends!
      # Let's do the turn-ending things.
      # Note: self.available_actions_this_turn is re-filled in the upkeep.
      new_turn_idx = self.human_players.index(self.whose_turn) + 1
      self.whose_turn = self.human_players[new_turn_idx%len(self.human_players)]
      self.turn_number += 1
      self.perform_upkeep()
      self.roll_for_card()

  def roll_for_card(self):
    self.die_roll = self.die_roll_fn(self.turn_number)
    self.messages_this_turn.append(f"You rolled a {self.die_roll}!")
    if self.die_roll == 1 and not DEV_MODE:
      card = self.draw_card()

  def perform_upkeep(self):
    to_pop = []
    DEV_PRINT(f"starting upkeep")
    for card in self.active_cards:
      DEV_PRINT(f"doing upkeep for {card}")
      card.upkeep_action(self)
      card_message = card.get_message()
      if card_message:
        self.messages_this_turn.append(card_message)
      if not card.is_active:
        card.when_leaves_play(self)
        to_pop.append(card)
    for card in to_pop:
      DEV_PRINT(f"Removing inactive card {card}")
      self.active_cards.remove(card)
    self.available_actions_this_turn = self.available_actions_per_turn.copy()
    DEV_PRINT(f"Finished upkeep!")


  def get_turn_info_img(self):
    rows = [f"turn number: {self.turn_number}", f"Whose turn:  {self.whose_turn}"]
    max_len = max(len(s) for s in rows)
    rows = [r.ljust(max_len, " ") for r in rows]
    color="blue_highlight" if self.whose_turn.team == "Black" else "teal_highlight"

    img = Image(from_string="\n".join(rows), color=color)
    img.drop_in_image(Image(from_string=DICE_FACES[self.die_roll]), location=(0, img.width + 2))
    return img
    # Below: stack die over turn info
    # die_img = Image(from_string=DICE_FACES[self.die_roll])
    # die_img.drop_in_image(Image(from_string="\n".join(rows), color=color), location="bottom_left", height_buf=1)
    # return die_img


  def get_card_row_img(self):
    n_cards = len(self.active_cards)
    if not n_cards:
      return Image(height=1, width=0)
    board_width = self.board.board_width * self.board.square_width
    card_display_width = board_width + self.graveyard_width
    return wrap_collapse([card.img for card in self.active_cards], width=card_display_width, width_buf=1)


  def get_graveyard_img(self):
    graveyard_images = []
    for team, cur_dead_pieces in self.dead_pieces.items():
      team = "Elijah" if team == "Autonomous" else team  # just for fun
      if not cur_dead_pieces: continue
      graveyard_width = self.graveyard_width
      # graveyard_width = min(self.graveyard_width, self.board.square_width*len(self.dead_pieces[player]))
      graveyard_img = Image(height=2, width=graveyard_width, color=COLOR_SCHEME["GRAVEYARD_HEADER_COLOR"])
      graveyard_img.print_in_string(f"  {team}'s Graveyard")
      graveyard_row = []
      for dead_piece in cur_dead_pieces:
        dead_piece_img = dead_piece.get_image()
        dead_piece_img.print_in_string(dead_piece.name)
        graveyard_row.append(dead_piece_img)
      row_img = wrap_collapse(graveyard_row, self.graveyard_width, height_buf=1)
      graveyard_img.drop_in_image(row_img, "bottom_left")
      graveyard_images.append(graveyard_img)
    img =  vertical_collapse(graveyard_images)
    return img if img else Image(height=1, width=0)
    # return wrap_collapse(graveyard_images, self.graveyard_width)

  def get_messages_img(self, clear_messages=True):
    # messages below board: 
    # messages_img_width = self.board.board_width*self.board.square_width
    # messages below graveyard: 
    messages_img_width = self.graveyard_width
    def height_of_message(m):
      return (len(m)//messages_img_width + 1)
    self.messages_this_turn = [f"{m}" for m in self.messages_this_turn]
    n_message_lines = sum([height_of_message(m) for m in self.messages_this_turn])
    # TODO the +2 is a horrible hack to try to compensate for image wrapping
    # it wil fail in some situations
    messages_img = Image(height=max(4, n_message_lines) + 2, width=messages_img_width)

    top_delineator = "-"*(messages_img_width - 5)
    messages_img.print_in_string_nicely(top_delineator, location=(0,0))

    row_i = 1
    rand_colors = "underline flashing red green yellow blue pink teal grey".split()
    random.shuffle(rand_colors)
    for msg_i, msg in enumerate(self.messages_this_turn):
      if not msg: continue
      color = rand_colors[msg_i%len(rand_colors)]
      printed_height = messages_img.print_in_string_nicely(msg, location=(row_i, 1), color=color)
      row_i += printed_height

    # Delete all messages from this turn
    if clear_messages:
      self.messages_this_turn = []
    return messages_img

  def animate_render(self, n_secs_pre_wait:int=0.2, n_secs_post_wait:int=0.3):
    """A wrapper for self.render() that waits for a bit before and after. Mainly for animating happenings during the upkeep."""
    if not n_secs_pre_wait and not n_secs_post_wait: return
    time.sleep(n_secs_pre_wait)
    self.render(clear_messages=False)
    time.sleep(n_secs_post_wait)

  def render(self, clear_messages:bool=True):
    # get board image
    # get graveyard images
    # get player specific boxes
    # get cards
    # put together!

    # highlight the relevant squares, and then dehighlight everything.
    if self.selected_square:
      self.board.highlight_square(self.selected_square)
    self.highlight_current_piece_moves()
    board_img = self.board.get_image()
    self.board.dehighlight_all()

    n_empty_rows_above = 20
    sidebar_width_buf = 3

    messages_img = self.get_messages_img(clear_messages=clear_messages)
    graveyard_img = self.get_graveyard_img()
    turn_info_img = self.get_turn_info_img()  # includes whose team and the die roll
    card_row_img = self.get_card_row_img()
    game_img_height = board_img.height + turn_info_img.height + card_row_img.height + n_empty_rows_above + 2
    game_img_width = board_img.width + graveyard_img.width + sidebar_width_buf
    game_image = Image(height=game_img_height, width=game_img_width)

    board_start_row = card_row_img.height + n_empty_rows_above

    game_image.drop_in_image_by_coordinates(card_row_img, upper_left_row=n_empty_rows_above, upper_left_col=0)
    game_image.drop_in_image_by_coordinates(board_img, upper_left_row=board_start_row, upper_left_col=0)
    game_image.drop_in_image_by_coordinates(graveyard_img, upper_left_row=board_start_row, upper_left_col=board_img.width + sidebar_width_buf)
    game_image.drop_in_image_by_coordinates(messages_img, upper_left_row=board_start_row + graveyard_img.height + 2, upper_left_col=board_img.width + sidebar_width_buf)
    # game_image.drop_in_image_by_coordinates(messages_img, upper_left_row=board_start_row + board_img.height, upper_left_col=0)

    # side_bar_img.drop_in_image(turn_info_img, "bottom_left", height_buf = 2)
    # game_image.drop_in_image_by_coordinates(turn_info_img, upper_left_row=board_start_row + board_img.height - turn_info_img.height, upper_left_col=board_img.width)
    game_image.drop_in_image_by_coordinates(turn_info_img, upper_left_row=board_start_row + board_img.height, upper_left_col=0)

    # board_img.drop_in_image(side_bar_img, "right_top", width_buf=3)
    # empty_top_bit_to_hide_past_board = Image(height=10, width=0)  # the width will be expanded after the dropping
    # empty_top_bit_to_hide_past_board.drop_in_image(board_img, "bottom_left")

    # empty_top_bit_to_hide_past_board.drop_in_image(messages_img, "bottom_left")


    # printstring = empty_top_bit_to_hide_past_board.rasterize()
    printstring =  game_image.rasterize()
    printstring += "\n" +  self.command_prompt()
    printstring += f"\n\033[1A"  # Move cursor up
    printstring += f"\033[33C"
    print(printstring, end="")
    if DEV_MODE: print()
    for player in self.human_players:
      DEV_PRINT(f"Living pieces for player {player}: {self.living_pieces[player.team]}")

  def command_prompt(self):
    prompt_str = "enter command ('halp' for help): "
    prompt_str = colorize(prompt_str, COLOR_SCHEME["MESSAGE_COLOR"])
    # move the cursor up and to the right
    # prompt_str += f"\n\033[1A\033[{len(prompt_str)}C"
    return prompt_str

  def players_starting_with_me(self):
    """Return the list of players, but cycled such atht eh current player is first in the list.
    This is used by several cards."""
    cur_turn_idx = self.human_players.index(self.whose_turn)
    return self.human_players[cur_turn_idx%len(self.human_players):] + self.human_players[0:cur_turn_idx%len(self.human_players)]

  def mark_piece_as_dead_and_remove_from_board(self, dead_piece):
    dead_piece.action_when_dies(self)
    self.command_history.append(f"# died: {dead_piece.name}")
    if dead_piece in self.dead_pieces[dead_piece.team]:
      raise ValueError(f"While marking {dead_piece} as dead, we noticed that it was already in self.dead_pieces: {self.dead_pieces}")
    self.dead_pieces[dead_piece.team].append(dead_piece)
    if dead_piece.team in self.living_pieces:
      self.living_pieces[dead_piece.team].remove(dead_piece)
      if dead_piece in self.living_pieces[dead_piece.team]:
        raise ValueError(f"While marking {dead_piece} as dead, we noticed that it occurred multiple times in self.living_pieces: {self.living_pieces}")
    if dead_piece in dead_piece.square_this_is_on.occupants:
      dead_piece.square_this_is_on.remove_occupant(dead_piece)

  def raise_piece_from_dead(self, revived_piece:Piece, birthsquare:Square, new_team:str=None) -> None:
    if revived_piece not in self.dead_pieces[revived_piece.team]:
      raise ValueError(f"Piece {revived_piece} was not dead!! Dead pieces: {self.dead_pieces}; living pieces: {self.living_pieces}")
    self.dead_pieces[revived_piece.team].remove(revived_piece)
    self.living_pieces[revived_piece.team].append(revived_piece)
    revived_piece.alive = True
    birthsquare.add_occupant(revived_piece)
    if new_team:
      self.change_piece_team(revived_piece, new_team)


  def change_piece_team(self, piece_to_change:Piece, team:str) -> None:
    if piece_to_change.team == team: return
    was_alive_or_dead = False
    for piece_set in [self.living_pieces, self.dead_pieces]:
      if piece_to_change.team not in piece_set:
        piece_set[piece_to_change.team] = []
      if team not in piece_set:
        piece_set[team] = []
      if piece_to_change in piece_set[piece_to_change.team]:
        was_alive_or_dead = True
        piece_set[piece_to_change.team].remove(piece_to_change)
        piece_set[team].append(piece_to_change)
    if not was_alive_or_dead:
      raise ValueError(f"Tried to change the team of {piece_to_change} from {piece_to_change.team} to {team}, but it was neither alive nor dead. Dead pieces: {self.dead_pieces}; alive pieces: {self.living_pieces}")

    if piece_to_change.type in IMAGE_STRINGS and team in IMAGE_STRINGS[piece_to_change.type]:
      piece_to_change.img = Image(IMAGE_STRINGS[piece_to_change.type][team], color="transparent", name=get_unique_name(f"{piece_to_change.name}_img"))

    piece_to_change.team = team


  def move_piece(self, moving_piece, end_square, enforce_whose_turn_it_is = True, this_was_a_human_making_this_move_and_thus_using_their_move_allowance=False, do_card_end_actions=True) -> List[Piece]:
    """Note: this method moves the piece and updates living and dead pieces.
    It does NOT call the turn_end method.

    If enforce_whose_turn_it_is, this raises an error if aomeone tries to move another's piece.
    Autonomous pieces will need to avoid this.

    Args:
      moving_piece
      end_square
      enforce_whose_turn_it_is = True
      this_was_a_human_making_this_move_and_thus_using_their_move_allowance=False
      do_card_end_actions: set to false if this is a card making this move
    """
    if DEV_MODE:
      enforce_whose_turn_it_is = False
    DEV_PRINT(f"moving {moving_piece} from {moving_piece.square_this_is_on} to {end_square}, {self.whose_turn}'s turn")
    if enforce_whose_turn_it_is and moving_piece.team != self.whose_turn.team:
      raise ValueError(f"You ({self.whose_turn}) can't move a piece belonging to {moving_piece.team}!") 
    dead_pieces = self.board.move_piece(moving_piece, end_square)
    for dead_piece in dead_pieces:
      self.command_history.append(f"# move: {moving_piece.name} took {dead_piece.name}")
      self.mark_piece_as_dead_and_remove_from_board(dead_piece)
    if do_card_end_actions:
      for card in self.active_cards:
        card.action_after_piece_moves(self, moving_piece, dead_pieces)
    if this_was_a_human_making_this_move_and_thus_using_their_move_allowance:
      self.incorporate_action_and_check_for_end_of_turn("m")
    DEV_PRINT(f"moved!")
    return dead_pieces

  def move_selected_piece(self, selected_move_id):
    if not self.selected_pieces:
      raise ValueError("No piece selected!")
    if len(self.selected_pieces) > 1:
      raise ValueError("Moving when multiple pieces selected is Not Implemented!")
    if not self._cur_available_piece_moves:
      raise ValueError(f"There are no available moves (but in a bad way like there is a programmatic error")
    if selected_move_id not in self._cur_available_piece_moves.id_to_move:
      raise ValueError(f"Move option {selected_move_id} for {self.selected_pieces[0].name} does not exist")

    end_square = self._cur_available_piece_moves.id_to_move[selected_move_id]
    self.move_piece(self.selected_pieces[0], end_square, this_was_a_human_making_this_move_and_thus_using_their_move_allowance=True)
    self.deselect_all()

    # _cur_available_piece_moves is basically a way for move_selected_piece() and _select_piece_interactive to communicate
    self._cur_available_piece_moves = None


  def deselect_all(self) -> None:
    self.selected_pieces = []
    if self.selected_square:
      self.backup_selected_square = self.selected_square
    self.selected_square = None
    self.board.dehighlight_all()
    self.messages_this_turn.append(f"No selected_pieces.")


  def _select_piece(self, piece: Piece, continue_existing_selection: bool) -> None:
    """This method takes care of the internal bookkeepping for selecting pieces, including the selection message.
    """
    if not continue_existing_selection:
      self.selected_pieces = []

    self.selected_pieces.append(piece)

    piece_names = ', '.join([piece_i.name for piece_i in self.selected_pieces])
    square_names = ', '.join([piece_i.square_this_is_on.name for piece_i in self.selected_pieces])
    self.messages_this_turn.append(f"Selected piece: {piece_names} on square {square_names}")

  def select_square_and_occupant(self, square_name:str) -> None:
    """TODO: can only select one square at a time
    Note: dehighlighting is happening in update_selected_square
    """
    square = self.board.square_from_a1_coordinates(square_name)
    DEV_PRINT(f">>> Selecting {square}")
    self.update_selected_square(square)
    occupants = square.occupants
    if not occupants:
      self._cur_available_piece_moves = PieceMoves(None, None)
      self.selection_message = f"Selected square ({square_name}) has no occupants"
    elif len(occupants) == 1:
      piece = occupants[0]
      self._select_piece(piece, continue_existing_selection=False)
      self._cur_available_piece_moves = piece.get_possible_moves()
    else:
      raise ValueError("Not Implemented!")

  def update_selected_square(self, square:Square) -> None:
    self.board.dehighlight_all()
    # self.board.dehighlight_square(self.selected_square)
    self.selected_square = square

  def move_square_selection(self, cmd:str, args: List[str]) -> None:
    if not self.selected_square:
      self.selected_square = self.backup_selected_square
    assert len(args) <= 1
    if args: assert args[0].isnumeric()
    direction = {"h": "w", "j": "s", "k": "n", "l": "e"}[cmd]
    path = [direction]
    if args: path *= int(args[0])
    new_selected_square = self.selected_square.get_square_from_directions(moving_piece=None, directions=path, stop_at_end_of_board=True)
    self.select_square_and_occupant(new_selected_square)

  def move_top_piece(self, start_square, end_square):
    """For debugging/testing."""
    dead_pieces = self.board.move_top_piece(start_square, end_square)
    for piece in dead_pieces:
      self.dead_pieces[piece.team].append(piece)

  def draw_specific_card(self, card_name: str) -> None:
    """Draw a specific card by name. This is mainly a debug/dev method, because otherwise why
    would you choose the card?
    """
    card_fn = ALL_CARDS[card_name]
    card = card_fn(self)
    self.command_history.append(f"# drew specific card {card}")
    if card.is_active:
      self.active_cards.append(card)
    card_message = card.get_message()
    if card_message:
      self.messages_this_turn.append(card_message)

  def draw_card(self) -> Card:
    card_fn = self.deck.draw_card(self.turn_number)
    if card_fn is None:
      self.messages_this_turn.append("No more cards in the deck!")
      return None

    card = card_fn(self)
    self.command_history.append(f"# drew card {card}")
    if card.is_active:
      self.active_cards.append(card)
    card_message = card.get_message()
    self.messages_this_turn.append(f"You drew {card}!")
    if card_message:
      self.messages_this_turn.append(card_message)
    return card

  def highlight_current_piece_moves(self) -> None:
    piece_moves = self._cur_available_piece_moves
    if not piece_moves: return
    self.board.highlighted_squares.update({square.name:COLOR_SCHEME["PIECE_MOVE_SELECT_COLOR"] for square in piece_moves.nontaking})
    self.board.highlighted_squares.update({square.name:COLOR_SCHEME["PIECE_TAKABLE_SELECT_COLOR"] for square in piece_moves.taking})
    for move_id, square in piece_moves.id_to_move.items():
      self.board.square_annotations[square.name].append(move_id)

