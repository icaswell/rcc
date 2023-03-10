import random
from time import sleep

from board import Board
from graphics import Image, wrap_collapse, vertical_collapse


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

class Game():
    def __init__(self, game_config):
      self.all_cards = []
      self.turn_order = ["White",  "Black"]  # Ibrahim is the "player" corresponding to white's pkeep
      # self.turn_order = ["Ibrahim", "White", "Elijah",  "Black"]  # Ibrahim is the "player" corresponding to white's pkeep
      # self.upkeep_players = ["Ibrahim", "Elijah"]
      self.human_players = ["White", "Black"]
      self.living_pieces =    {}
      self.dead_pieces =      {}
      self.etherized_pieces = {}
      for player in self.human_players: # + self.upkeep_players:
        self.living_pieces[player] = []
        self.dead_pieces[player] = []
        self.etherized_pieces[player] = []

      self.turn_number = 0
      self.whose_turn = "White"

      self.square_height = 8
      self.board = Board(game_config, square_height=self.square_height, border_width=1)
      for player in self.human_players:
        self.living_pieces[player] = list(game_config["initial_positions"][player].values())


      # rendering stuff
      self.graveyard_width = 16*5
      

    def select_random_move(self, take_prob):
        movable_pieces_to_moves = []
        for piece in self.living_pieces[self.whose_turn]:
            moves = piece.get_possible_moves()
            if moves["taking"] or moves["nontaking"]:
              movable_pieces_to_moves.append((piece, moves))
        if not movable_pieces_to_moves:
            raise ValueError("No pieces can be moved!")
        piece, moves = random.choice(movable_pieces_to_moves)
        if (moves["taking"] and random.random() < take_prob) or not moves["nontaking"]:
            return piece, random.choice(moves["taking"])
        return piece, random.choice(moves["nontaking"])

    def take_nonsense_turn(self, n_secs_wait, take_prob):
       moving_piece, end_square = self.select_random_move(take_prob)
       self.board.highlight_piece_moves(moving_piece)
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
        n_turns = 100
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
      empty_top_bit_to_hide_past_board.render()
      # board_img.render()

    def perform_upkeep(self):
        pass

    # Wrappers for Board methods
    def move_piece(self, piece, end_square):
      dead_pieces = self.board.move_piece(piece, end_square)
      for piece in dead_pieces:
          self.dead_pieces[piece.team].append(piece)
          self.living_pieces[piece.team].remove(piece)

    def move_top_piece(self, start_square, end_square):
      dead_pieces = self.board.move_top_piece(start_square, end_square)
      for piece in dead_pieces:
          self.dead_pieces[piece.team].append(piece)
    def highlight_piece_moves_from_square(self, square):
        self.board.highlight_piece_moves_from_square(square)
