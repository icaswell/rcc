import random
import traceback
from time import sleep
import sys, os
from typing import List, Set, Dict

from board import Board, Square
from piece import Piece
from graphics import Image, wrap_collapse, vertical_collapse, colorize
import commands
from constants import *


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
      
      self.game_config = game_config
      self.all_cards = []
      self.turn_order = game_config["players"]
      self.human_players = game_config["players"]
      # self.turn_order = ["Ibrahim", "White", "Elijah",  "Black"]  # Ibrahim is the "player" corresponding to white's pkeep
      # self.upkeep_players = ["Ibrahim", "Elijah"]
      self.living_pieces =    {}
      self.dead_pieces =      {}
      self.etherized_pieces = {}
      for player in self.human_players: # + self.upkeep_players:
        self.living_pieces[player] = []
        self.dead_pieces[player] = []
        self.etherized_pieces[player] = []

      self.turn_number = 0
      self.whose_turn = "White"
      self.selected_square = None
      self.selected_pieces = []
      self.selection_message = "There are no selected pieces."
      self._cur_available_piece_moves = None

      self.board = Board(game_config)
      for player in self.human_players:
          self.living_pieces[player] =  []
      for piece_name, piece in self.board.piece_map.items():
          self.living_pieces[piece.team].append(piece)
      # this is where the cursor reappears if you move the cursor when there has been no slection
      self.backup_selected_square = self.board.square_from_a1_coordinates("D4") # this will fail if the board is smaller than 4x4...but...

      # maps turn number to stuff about the board. Ideally, everything can be written to a json....
      seed = random.randint(0, 1000000)
      random.seed(seed)
      self.command_history = [f"set_random_seed {seed}"]


      # rendering stuff
      self.graveyard_width = game_config["square_width"] * 4 + 2 # aka it can fit four pieces, plus two pixels for good luck

    def execute_commands(self, cmd_history: List[str], display:bool=False) -> None:
        for cmd in cmd_history:
           self.take_action_from_command(cmd)
           if display:
               sleep(0.3)
               self.render()
    
    def highlight_current_piece_moves(self) -> None:
        piece_moves = self._cur_available_piece_moves
        if not piece_moves: return
        self.board.highlighted_squares.update({square.name:PIECE_MOVE_SELECT_COLOR for square in piece_moves.nontaking})
        self.board.highlighted_squares.update({square.name:PIECE_TAKABLE_SELECT_COLOR for square in piece_moves.taking})
        for move_id, square in piece_moves.id_to_move.items():
            self.board.square_annotations[square.name].append(move_id)
        
    def select_random_move(self, take_prob):
        movable_pieces_to_moves = []
        for piece in self.living_pieces[self.whose_turn]:
            moves = piece.get_possible_moves()
            if moves.taking or moves.nontaking:
              movable_pieces_to_moves.append((piece, moves))
        if not movable_pieces_to_moves:
            raise ValueError("No pieces can be moved!")

        piece, moves = random.choice(movable_pieces_to_moves)
        move_to_id = {move:i for i, move in moves.id_to_move.items()}
        if (moves.taking and random.random() < take_prob) or not moves.nontaking:
            move = random.choice(moves.taking)
            return piece, move, move_to_id[move]

        # perform bookkeeping
        # self._select_piece(piece, continue_existing_selection=False)

        move = random.choice(moves.nontaking)
        return piece, move, move_to_id[move]

    def take_nonsense_turn(self, n_secs_wait, take_prob):
       moving_piece, end_square, move_i = self.select_random_move(take_prob)
       self._cur_available_piece_moves = moving_piece.get_possible_moves()

      
       command = f"s {moving_piece.square_this_is_on.name}"  # hack alert! this assumes that the name of the square is an alphanumeric format (or select doesn't work from name)
       self.take_action_from_command(command)

       self.render()
       sleep(n_secs_wait)
 
       command = f"m {move_i}"
       self.take_action_from_command(command)

       self.render()
       sleep(n_secs_wait)


    def turn_end_actions(self):
        new_turn_idx = self.turn_order.index(self.whose_turn) + 1
        self.whose_turn = self.turn_order[new_turn_idx%len(self.turn_order)]
        self.turn_number += 1

    def play_nonsense_game(self, n_turns=15, n_secs_wait = 0.05, take_prob = 0.8):
        # TODO decompose so that this can call execute_command!!
        # Also make sure that handles turn end actions etc.
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
        img =  vertical_collapse(graveyard_images)
        return img if img else Image(height=1, width=0)
        # return wrap_collapse(graveyard_images, self.graveyard_width)

    def render(self):
      # get board image
      # get graveyard images
      # get player specific boxes
      # get cards
      # put together!

      self.board.dehighlight_all()
      if self.selected_square:
        self.board.highlight_square(self.selected_square)
      self.highlight_current_piece_moves()

      n_empty_rows_above = 20
      sidebar_width_buf = 3

      messages_to_print = [self.selection_message]
      messages_img = Image(from_string="\n".join(messages_to_print))

      board_img = self.board.get_image()
      graveyard_img = self.get_graveyard_img()
      turn_info_img = self.get_turn_info_img()
      game_image = Image(height=board_img.height + turn_info_img.height + n_empty_rows_above + 2, width=board_img.width + graveyard_img.width + sidebar_width_buf)

      # side_bar_img = Image(height=1, width=0) # TODO make 0-height work!!
      # if graveyard_img:
          # side_bar_img.drop_in_image(graveyard_img, "bottom_left")
      game_image.drop_in_image_by_coordinates(graveyard_img, upper_left_row=n_empty_rows_above, upper_left_col=board_img.width + sidebar_width_buf)
    
      game_image.drop_in_image_by_coordinates(turn_info_img, upper_left_row=graveyard_img.height + 2 + n_empty_rows_above, upper_left_col=board_img.width + sidebar_width_buf)
      game_image.drop_in_image_by_coordinates(board_img, upper_left_row=n_empty_rows_above, upper_left_col=0)
      game_image.drop_in_image_by_coordinates(turn_info_img, upper_left_row=n_empty_rows_above + board_img.height, upper_left_col=0)
      # side_bar_img.drop_in_image(turn_info_img, "bottom_left", height_buf = 2)

      # board_img.drop_in_image(side_bar_img, "right_top", width_buf=3)
      # empty_top_bit_to_hide_past_board = Image(height=10, width=0)  # the width will be expanded after the dropping
      # empty_top_bit_to_hide_past_board.drop_in_image(board_img, "bottom_left")

      # empty_top_bit_to_hide_past_board.drop_in_image(messages_img, "bottom_left")


      # printstring = empty_top_bit_to_hide_past_board.rasterize()
      printstring = game_image.rasterize()
      printstring += "\n" +  self.command_prompt()
      printstring += f"\n\033[1A"  # TODO should this be in the printstring??
      printstring += f"\033[33C"
      print(printstring, end="")

    def command_prompt(self):
      prompt_str = "enter command ('halp' for help): "
      prompt_str = colorize(prompt_str, 'green')
      # move the cursor up and to the right
      # prompt_str += f"\n\033[1A\033[{len(prompt_str)}C"
      return prompt_str

    def perform_upkeep(self):
        pass

    def move_piece(self, piece, end_square):
      """Note: this method moves the piece and updates living and dead pieces.
      It does NOT call the turn_end method."""
      if not DEV_MODE and piece.team != self.whose_turn:
        raise ValueError(f"You ({self.whose_turn}) can't move a piece belonging to {piece.team}!")
      dead_pieces = self.board.move_piece(piece, end_square)
      for piece in dead_pieces:
          self.dead_pieces[piece.team].append(piece)
          self.living_pieces[piece.team].remove(piece)


    def move_selected_piece(self, selected_move_id):
        """
        """
        if not self.selected_pieces:
            raise ValueError("No piece selected!")
        if len(self.selected_pieces) > 1:
            raise ValueError("Moving when multiple pieces selected is Not Implemented!")
        if not self._cur_available_piece_moves:
            raise ValueError(f"There are no available moves (but in a bad way like there is a programmatic error")
        if selected_move_id not in self._cur_available_piece_moves.id_to_move:
            raise ValueError(f"Move option {selected_move_id} for {self.selected_pieces[0].name} does not exist")

        end_square = self._cur_available_piece_moves.id_to_move[selected_move_id]
        self.move_piece(self.selected_pieces[0], end_square)
        self._deselect_all()

        # _cur_available_piece_moves is basically a way for move_selected_piece() and _select_piece_interactive to communicate
        self._cur_available_piece_moves = None
       
      
    def _deselect_all(self) -> None:
       self.selected_pieces = []
       self.backup_selected_square = self.selected_square
       self.selected_square = None
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

    def select_square_and_occupant_interactive(self, square_name):
        """TODO: can only select one square at a time
        TODO: where is the dehighlighting happening?
        The reason this method is called "interactive" is that if you select and there are multiple pieces on the square, it will prompt you to choose.
        """
        square = self.board.square_from_a1_coordinates(square_name)
        self.update_selected_square(square)
        occupants = square.occupants
        if not occupants:
            self.selection_message = f"Selected square ({square_name}) has no occupants"
        elif len(occupants) == 1:
            piece = occupants[0]
            self._select_piece(piece, continue_existing_selection=False)
            self._cur_available_piece_moves = piece.get_possible_moves()
        else:
            raise ValueError("Not Implemented!")

    def update_selected_square(self, square:Square) -> None:
        self.board.dehighlight_square(self.selected_square)
        self.selected_square = square

    def move_square_selection(self, cmd:str, args: List[str]) -> None:
       if not self.selected_square:
           self.selected_square = self.backup_selected_square
       assert len(args) <= 1
       if args: assert args[0].isnumeric()
       direction = {"h": "w", "j": "s", "k": "n", "l": "e"}[cmd]
       path = [direction]
       if args: path *= int(args[0])
       new_selected_square = self.selected_square.get_square_from_directions(piece=None, directions=path, stop_at_end_of_board=True)
       self.select_square_and_occupant_interactive(new_selected_square)


    def move_top_piece(self, start_square, end_square):
      """For debugging/testing.
      """
      dead_pieces = self.board.move_top_piece(start_square, end_square)
      for piece in dead_pieces:
          self.dead_pieces[piece.team].append(piece)

    def take_action_from_command(self, input_cmd:str) -> str:
       self.command_history.append(input_cmd)
       cmd, args, kwargs = commands.parse_command(input_cmd)
       end_turn = False
       if cmd == "v":
           pass # view
       elif cmd == "q":
           return BREAK
       elif cmd == "m":  # move selected
           assert len(args) ==  1 and len(args[0]) <= 2  # this assert should go as soon as there are more interesting moves that pieces can do!
           square_name = args[0]
           self.board.dehighlight_all()
           self.move_selected_piece(square_name)
           end_turn = True
       elif cmd == "g":
           assert len(args) ==  1 and len(args[0]) == 2
           square_name = args[0]
           self.board.dehighlight_all()
           self.select_square_and_occupant_interactive(square_name)
       elif cmd in {"h", "j", "k", "l"}:
          self.move_square_selection(cmd, args)
       elif cmd == "gg":
           self.move_square_selection("k", ["8"])
           self.move_square_selection("h", ["8"])
       elif cmd == "G":
           self.move_square_selection("j", ["8"])
           self.move_square_selection("l", ["8"])
       elif cmd == "set_random_seed":
           random.seed(int(args[0]))
       elif cmd == "r":
           self.render()
       elif cmd == "halp":
           commands.print_help()
       else:
           raise ValueError(f"Oops you didn't add an elif statement for command '{cmd}'")

       if end_turn: 
         self.turn_end_actions()
         self.perform_upkeep()

        
    def play_game_interactive(self):
      self.render()
      while True or False:
          try:
            line = input().strip()
            # line = input(self.command_prompt()).strip()
            self.command_history.append(line)
            action_result = self.take_action_from_command(line)
            if action_result == BREAK: break
            self.render()
          except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(f"OOPS! {e} (exception from {fname}, line {exc_tb.tb_lineno}).\n{self.command_prompt()}", end="")
            print(traceback.format_exc())
            "enter command ('halp' for help): "

            print(self.command_prompt(), end="")
            # print(exc_tb)



