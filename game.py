import random
import traceback
from time import sleep
import sys, os

from board import Board
from piece import Piece
from graphics import Image, wrap_collapse, vertical_collapse, colorize
import commands

BREAK = "break"

class Player():
    color = "" 
    display_name = ""
    
    special_stuff = {}  # e.g. Seeds of Self Doubt, quantum credits

class Action():
    # purely for informaiton passing to cards
    action_type = "" # move if the piece moved, ability if not ot something
    from_square = ""
    to_square = ""
    moving_player = ""
    pieces_taken = ""

class Turn():
    # can_the_turn_be_ended = "" # enum of ["cannot_be_ended", "can_be_ended", "must_be_ended"]
    # actions_still_available_this_turn = []
    def update_available_actions(self, last_action):
        pass
        # after you do anything, call this
    # do upkeep?
    # Keep track of the things that pieces allow a player to do, including how many moves thy get per turn

    summary_of_this_turn_to_send_to_cards = []  # ordered summary of the moves made, pieces taken, etc.

class Game(): pass
class Game():
    def __init__(self, game_config):
      random.seed(42)
      self.game_config = game_config
      self.all_cards = []
      self.turn_order = ["White",  "Black"]  # Ibrahim is the "player" corresponding to white's pkeep
      # self.turn_order = ["Ibrahim", "White", "Elijah",  "Black"]  # Ibrahim is the "player" corresponding to white's pkeep
      # self.upkeep_players = ["Ibrahim", "Elijah"]
      self.human_players = ["White", "Black"]  # TODO replace these with much more fun names
      self.living_pieces =    {}
      self.dead_pieces =      {}
      self.etherized_pieces = {}
      for player in self.human_players: # + self.upkeep_players:
        self.living_pieces[player] = []
        self.dead_pieces[player] = []
        self.etherized_pieces[player] = []

      self.turn_number = 0
      self.whose_turn = "White"
      self.selected_pieces = []
      self.selection_message = "There are no selected pieces."
      self._cur_available_piece_moves = None

      self.board = Board(game_config)
      for player in self.human_players:
          self.living_pieces[player] =  []
      for piece_name, piece in self.board.piece_map.items():
          self.living_pieces[piece.team].append(piece)

      # maps turn number to stuff about the board. Ideally, everything can be written to a json....
      self.command_history = [[]]

      # rendering stuff
      self.graveyard_width = game_config["square_width"] * 4 + 2 # aka it can fit four pieces, plus two pixels for good luck

    # def reconstitute_from_turn_history(turn_history: list) -> Game:
    #     copy = Game(self.game_config)
    #     for turn_i, turn_actions in enumerate(turn_history):
    #         copy.perform_upkeep()
    #         for action in turn_actions:
    #           copy.take_action_from_action_description(action)
    #         copy.turn_end_actions()
    #     return copy
    # 
    # def take_action_from_action_description(self: action):

        
    def select_random_move(self, take_prob):
        movable_pieces_to_moves = []
        for piece in self.living_pieces[self.whose_turn]:
            moves = piece.get_possible_moves()
            if moves.taking or moves.nontaking:
              movable_pieces_to_moves.append((piece, moves))
        if not movable_pieces_to_moves:
            raise ValueError("No pieces can be moved!")
        piece, moves = random.choice(movable_pieces_to_moves)
        if (moves.taking and random.random() < take_prob) or not moves.nontaking:
            return piece, random.choice(moves.taking)

        # perform bookkeeping
        self._select_piece(piece, continue_existing_selection=False)
        return piece, random.choice(moves.nontaking)

    def take_nonsense_turn(self, n_secs_wait, take_prob):
       moving_piece, end_square = self.select_random_move(take_prob)
       self._cur_available_piece_moves = self.board.highlight_and_get_piece_moves(moving_piece)
       self.render()
       sleep(n_secs_wait)
       self.move_piece(moving_piece, end_square)
       self.render()
       sleep(n_secs_wait)

       self.turn_end_actions()

    def turn_end_actions(self):
        new_turn_idx = self.turn_order.index(self.whose_turn) + 1
        self.whose_turn = self.turn_order[new_turn_idx%len(self.turn_order)]
        self.turn_number += 1

    def play_nonsense_game(self):
        n_turns = 10
        n_secs_wait = 0.05
        take_prob = 0.8
        while True:
            if self.turn_number > n_turns : break
            self.take_nonsense_turn(n_secs_wait, take_prob)

    def get_turn_info_img(self):
        rows = [f"turn number: {self.turn_number}", f"Whose turn:  {self.whose_turn}"]
        max_len = max(len(s) for s in rows)
        rows = [r.ljust(max_len, " ") for r in rows]
        return Image(from_string="\n".join(rows), color="blue")


    def get_graveyard_img(self):
        graveyard_images = []
        for player in self.human_players: #  + self.upkeep_players:
          if not self.dead_pieces[player]: continue
          graveyard_img = Image(height=2, width=self.graveyard_width, color="green_highlight")
          graveyard_img.print_in_string(f"  {player}'s Graveyard")
          graveyard_row = []
          for dead_piece in self.dead_pieces[player]:
              dead_piece_img = dead_piece.img
              dead_piece_img.print_in_string(dead_piece.name)
              graveyard_row.append(dead_piece_img)
          row_img = wrap_collapse(graveyard_row, self.graveyard_width, height_buf=1)
          graveyard_img.drop_in_image(row_img, "bottom_left")
          graveyard_images.append(graveyard_img)
        return vertical_collapse(graveyard_images)
        # return wrap_collapse(graveyard_images, self.graveyard_width)

    def render(self):
      # get board image
      # get graveyard images
      # get player specific boxes
      # get cards
      # put together!

      board_img = self.board.get_image()
      graveyard_img = self.get_graveyard_img()
      turn_info_img = self.get_turn_info_img()

      side_bar_img = Image(height=1, width=0) # TODO make 0-height work!!
      if graveyard_img:
        side_bar_img.drop_in_image(graveyard_img, "bottom_left")
    
      side_bar_img.drop_in_image(turn_info_img, "bottom_left", height_buf = 2)

      board_img.drop_in_image(side_bar_img, "right_top", width_buf=3)
      empty_top_bit_to_hide_past_board = Image(height=20, width=0)  # the width will be expanded after the dropping
      empty_top_bit_to_hide_past_board.drop_in_image(board_img, "bottom_left")

      messages_to_print = [self.selection_message]
      messages_img = Image(from_string="\n".join(messages_to_print))
      empty_top_bit_to_hide_past_board.drop_in_image(messages_img, "bottom_left")


      printstring = empty_top_bit_to_hide_past_board.rasterize()
      printstring += "\n" +  self.command_prompt()
      print(printstring, end="")

    def command_prompt(self):
      return colorize("enter command ('help' for help): ", 'green')

    def perform_upkeep(self):
        pass

    def move_piece(self, piece, end_square):
      """Note: this method moves the piece and updates living and dead pieces.
      It does NOT call the turn_end method."""
      if piece.team != self.whose_turn:
        raise ValueError(f"You ({self.whose_turn}) can't move a piece belonging to {piece.team}!")
      dead_pieces = self.board.move_piece(piece, end_square)
      for piece in dead_pieces:
          self.dead_pieces[piece.team].append(piece)
          self.living_pieces[piece.team].remove(piece)


    def move_selected_piece(self, selected_move_id):
        """
        """
        if len(self.selected_pieces) != 1:
            raise ValueError("Moving when multiple pieces selected is Not Implemented!")
        if not self._cur_available_piece_moves:
            raise ValueError(f"There are no available moves (but in a bad way like there is a programmatic error")
        if selected_move_id not in self._cur_available_piece_moves.id_to_move:
            raise ValueError(f"Move option {selected_move_id} does not exist")

        end_square = self._cur_available_piece_moves.id_to_move[selected_move_id]
        self.move_piece(self.selected_pieces[0], end_square)
        self._deselect_all()

        # _cur_available_piece_moves is basically a way for move_selected_piece() and _select_piece_interactive to communicate
        self._cur_available_piece_moves = None
        self.turn_end_actions()  # TODO move this out of here and into a take_turn method!
       
      
    def _deselect_all(self) -> None:
       self.selected_pieces = []
       self.board.dehighlight_all()
       self.selection_message = f"No selected_pieces."

 
    def _select_piece(self, piece: Piece, continue_existing_selection: bool) -> None:
       """This method takes care of the internal bookkeepping for selecting pieces, including the selection message.
       """
       if not continue_existing_selection:
         self.selected_pieces = []

       self.selected_pieces.append(piece)

       piece_names = ', '.join([piece_i.name for piece_i in self.selected_pieces])
       square_names = ', '.join([piece_i.square_this_is_on.name for piece_i in self.selected_pieces])
       self.selection_message = f"Selected piece: {piece_names} on square {square_names}"

    def select_piece_interactive(self, square_name):
        """TODO: can only select one square at a time
        TODO: where is the dehighlighting happening?
        The reason this method is called "interactive" is that if you select and there are multiple pieces on the square, it will prompt you to choose.
        """
        square = self.board.square_from_a1_coordinates(square_name)
        occupants = square.occupants
        if not occupants:
            self.selection_message = f"Selected square ({square_name}) has no occupants"
        elif len(occupants) == 1:
            piece = occupants[0]
            self._select_piece(piece, continue_existing_selection=False)
            # _cur_available_piece_moves is basically a way for move_selected_piece() and _select_piece_interactive to communicate
            self._cur_available_piece_moves = self.board.highlight_and_get_piece_moves(piece)
        else:
            raise ValueError("Not Implemented!")

    def move_top_piece(self, start_square, end_square):
      """For debugging/testing.
      """
      dead_pieces = self.board.move_top_piece(start_square, end_square)
      for piece in dead_pieces:
          self.dead_pieces[piece.team].append(piece)

    def take_action_from_command(self, input_cmd:str) -> str:
       cmd, args, kwargs = commands.parse_command(input_cmd)
       if cmd == "v":
           pass # view
       elif cmd == "q":
           return BREAK
       elif cmd == "m":  # move selected
           assert len(args) ==  1 and len(args[0]) <= 2  # this assert should go as soon as there are more interesting moves that pieces can do!
           square_name = args[0]
           self.move_selected_piece(square_name)
       elif cmd == "s":
           assert len(args) ==  1 and len(args[0]) == 2
           square_name = args[0]
           self.select_piece_interactive(square_name)
       elif cmd == "h":
           commands.print_help()
       else:
           raise ValueError("Something is very wrong")

        
    def play_game_interactive(self):
      self.render()
      while True:
          try:
            line = input(colorize("enter command ('help' for help): ", 'green')).strip()
            self.command_history.append(line)
            action_result = self.take_action_from_command(line)
            if action_result == BREAK: break
            self.render()
          except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"OOPS! {e} (exception from {fname}, line {exc_tb.tb_lineno}).\n{self.command_prompt()}", end="")
            print(traceback.format_exc())
            # print(exc_tb)



