from graphics import colorize
from typing import Union, List
from animation import INTRO_VIDEO, HBD_VIDEO, GAME_WIN_ANIMATION
from constants import *
import random
import time

import sys, os
import traceback

def print_help():
  print(f"""
====================================
Here are some commands you can enter!
------------------------------------
Command format:
$ command arg1 arg2 keyword_arg1=X keyword_arg2=Y -option1 -option2 

{colorize('General Commands:',     'green')}
          {colorize('halp',      'red')}: print this string.
          {colorize('r',         'red')}: refresh the screen
          {colorize('q',         'red')}: quit this game.

{colorize('Moving the selection around:',     'green')}
          {colorize('h [N]',     'red')}: move highlighted square left N squares (N defaults to 1)
          {colorize('j [N]',     'red')}: move highlighted square down N squares (N defaults to 1)
          {colorize('k [N]',     'red')}: move highlighted square up N squares (N defaults to 1)
          {colorize('l [N]',     'red')}: move highlighted square right N squares (N defaults to 1)
          {colorize('gg',        'red')}: highlight top-left square
          {colorize('G',         'red')}: highlight bottom right square
          {colorize('g XY [-k]', 'red')}: go to square XY, selecting the piece on it (alternate option -k: keep existing selection) 

{colorize('Taking your turn:',     'green')}
          {colorize('m N',      'red')}: Move the selected piece to the square indicated as N (the lower right-hand corner of every available move will show a number if the piece is selected)
          {colorize('n [K] [--s=X] [--s=Y]', 'red')}: Take a nonsense turn. Alternately, take K nonsense turns, with S seconds wait between them, and take probability T.

{colorize('Advanced/Debugging:',     'green')}
          {colorize('dev',       'red')}: toggle dev mode
          {colorize('d',         'red')}: draw a card
        """)


def user_choose_square(game, square_list:List, message:str=None) -> int:
  # game.deselect_all()
  for i, square in enumerate(square_list):
    game.board.annotate_square(square, annotation = str(i))
  game.render(clear_messages=False)
  return user_choose_list_item(square_list, message=message)

def user_choose_list_item(option_list:List, print_options:bool=False, message:str=None) -> int:
  if message:
    print(colorize(message, "teal_highlight"))
  if print_options:
    option_str = ';'.join([f'{i}. {item}' for i, item in enumerate(option_list)])
    print(colorize(f"Your options are: {option_str}", "teal_highlight"))
  choice = None
  while True:
    if len(option_list) == 1:
      choice = 0
      break
    line = input(colorize(f"Enter a number from 0 to {len(option_list) -1} to indicate which option to choose: ", color="teal_highlight")).strip()
    if not line.isnumeric():
      print(colorize("enter a numeric value", "red"))
      continue
    choice = int(line)
    if not (0 <= choice < len(option_list)):
      print(colorize(f"enter a value between 0 and {len(option_list) -1}", "red"))
      continue
    break
  return choice


def parse_command(line):
  parts = line.strip().split()
  if not parts:  # refresh
    return "r", [], {}
  cmd = parts[0]
  args = []
  kwargs = dict()
  for part in parts[1:]:
    if "=" in part: # part.startswith('--'):
      part = part.replace("--", "")
      k, v = part.split("=", 1)
      kwargs[k] = v
    elif part.startswith('-'):
      kwargs[part[1:]] = True
    else:
      args.append(part)

  # special case: vim-style inputs. assumes a single-letter command.
  if len(cmd) > 1 and not args and not kwargs:
    if cmd[0:-1].isnumeric() and cmd[-1].isalpha():
      args = [cmd[0:-1]]
      cmd = cmd[-1]
    if cmd[1:].isnumeric() and cmd[0].isalpha():
      args = [cmd[1:]]
      cmd = cmd[0]

  # semantic sugar
  if cmd in {"h", "j", "k", "l"}:
    args = [cmd] + args
    cmd = "move_cursor"

  if cmd not in COMMAND_ACTIONS:
    raise ValueError(f"unrecognized command '{line}'. Please try again.")
  return cmd, args, kwargs


def command_v(game, args, kwargs, display):
  pass # view
def command_q(game, args, kwargs, display):
  return BREAK
def command_m(game, args, kwargs, display):
  assert len(args) ==  1 and len(args[0]) <= 2  # this assert should go as soon as there are more interesting moves that pieces can do!
  square_name = args[0]
  game.board.dehighlight_all()
  game.move_selected_piece(square_name)
def command_g(game, args, kwargs, display):
  assert len(args) ==  1 and len(args[0]) == 2
  square_name = args[0]
  game.board.dehighlight_all()
  game.select_square_and_occupant(square_name)
def command_move_cursor(game, args, kwargs, display):
  game.move_square_selection(args[0], args[1:])
def command_gg(game, args, kwargs, display):
  game.move_square_selection("k", ["8"])
  game.move_square_selection("h", ["8"])
def command_G(game, args, kwargs, display):
  game.move_square_selection("j", ["8"])
  game.move_square_selection("l", ["8"])
def command_set_random_seed(game, args, kwargs, display):
  random.seed(int(args[0]))
def command_retro(game, args, kwargs, display):
  COLOR_SCHEME.update(RETRO_COLOR_SCHEME)
def command_r(game, args, kwargs, display):
  game.render()
def command_n(game, args, kwargs, display):
  n_nonsense_turns = int(args[0]) if args else 1
  n_secs_wait = 0.0 if "s" not in kwargs else float(kwargs["s"])
  take_prob =   0.5 if "t" not in kwargs else float(kwargs["t"])
  for _ in range(n_nonsense_turns):
    take_nonsense_turn(game, n_secs_wait=n_secs_wait, take_prob=take_prob, display=display)
    # HAHAHA this option actually means that this very method (take_action_from_command)
    # will be called twice! because of this we don't end the turn at the higher level in the stack.
def command_d(game, args, kwargs, display):
  game.draw_card()
def command_ds(game, args, kwargs, display):
  assert len(args) == 1
  game.draw_specific_card(args[0])
def command_dev(game, args, kwargs, display):
  global DEV_MODE
  if DEV_MODE:
    DEV_MODE.pop()
  else:
    DEV_MODE.append("heehee")
  game.selection_message = f"Set DEV_MODE to {DEV_MODE != []}"
def command_halp(game, args, kwargs, display):
  print_help()
  return NORENDER

COMMAND_ACTIONS = {
    "v": command_v,
    "q": command_q,
    "m": command_m,
    "g": command_g,
    "move_cursor": command_move_cursor,
    "gg": command_gg,
    "G": command_G,
    "set_random_seed": command_set_random_seed,
    "retro": command_retro,
    "r": command_r,
    "n": command_n,
    "d": command_d,
    "ds": command_ds,
    "dev": command_dev,
    "halp": command_halp,
}



def take_action_from_command(game, input_cmd:str, display:str=False) -> Union[str, None]:
  """
  Args:
    input_cmd: a string like "2j" for the command. If it starts with '#', it is
               treated as a comment and ignored
    display: whether to render the board. NOTE: not all commands will render anyways.
             But if you don't pass in display=True, nothing will render.
             The entire point of `display` is for execute_commands -- so when you 
             reload a game you can choose to display the moves. CONSIDER DEPRECATING

  """
  game.command_history.append(input_cmd)
  DEV_PRINT(game.command_history)
  if input_cmd.startswith("#"):
    return None  # this was a comment
  cmd, args, kwargs = parse_command(input_cmd)
  cmd_fn = COMMAND_ACTIONS[cmd]
  return cmd_fn(game, args, kwargs, display)


def play_game_interactive(game, intro_video=True):
  if intro_video:
    INTRO_VIDEO.play(); unused = input()
    HBD_VIDEO.play()

  game.draw_card()
  game.render()

  while True or False:
    try:
      winner = game.check_for_winner()
      if winner is not None:
        GAME_WIN_ANIMATION(winner).play()
        break
      line = input().strip()
      # line = input(game.command_prompt()).strip()
      game.command_history.append(line)
      action_result = take_action_from_command(game, line)
      if action_result == BREAK: break
      if action_result == NORENDER: continue
      game.render()
    except Exception as e:
      exc_type, exc_obj, exc_tb = sys.exc_info()
      fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
      print(f"OOPS! {e} (exception from {fname}, line {exc_tb.tb_lineno})")
      print_help()
      print(f"{game.command_prompt()}", end="")
      if True or DEV_MODE:
        print(traceback.format_exc())
        print(colorize("Command history: ", "red"), end="")
        print(game.command_history)
        # print(exc_tb)
  game.render()



def execute_commands(game, cmd_history: List[str], display:bool=False) -> None:
  for cmd in cmd_history:
    take_action_from_command(game, cmd, display=display)
    if display:
      time.sleep(0.3)
      game.render()

def select_random_move(game, take_prob):
  movable_pieces_to_moves = []
  for piece in game.living_pieces[game.whose_turn.team]:
    moves = piece.get_possible_moves()
    if moves.taking or moves.nontaking:
      movable_pieces_to_moves.append((piece, moves))
  if not movable_pieces_to_moves:
    raise ValueError("No pieces can be moved!")
  DEV_PRINT("Selecting random move.")
  DEV_PRINT(f"It is {game.whose_turn}'s turn. Choosing from amongst these pieces: {movable_pieces_to_moves}")

  piece, moves = random.choice(movable_pieces_to_moves)
  move_to_id = {move:i for i, move in moves.id_to_move.items()}
  if (moves.taking and random.random() < take_prob) or not moves.nontaking:
    move = random.choice(moves.taking)
    return piece, move, move_to_id[move]

  # perform bookkeeping
  # game._select_piece(piece, continue_existing_selection=False)

  move = random.choice(moves.nontaking)
  return piece, move, move_to_id[move]

def take_nonsense_turn(game, n_secs_wait, take_prob, display=True):
  moving_piece, end_square, move_i = select_random_move(game, take_prob)
  DEV_PRINT(f"Selected {moving_piece} to move to {end_square}.")
  game._cur_available_piece_moves = moving_piece.get_possible_moves()

  command = f"g {moving_piece.square_this_is_on.name}"  # hack alert! this assumes that the name of the square is an alphanumeric format (or select doesn't work from name)
  take_action_from_command(game, command)

  if display:
    game.render()
    time.sleep(n_secs_wait)

  command = f"m {move_i}"
  take_action_from_command(game, command)

  if display:
    game.render()
    time.sleep(n_secs_wait)


def play_nonsense_game(game, n_turns=15, n_secs_wait = 0.05, take_prob = 0.8):
  # TODO decompose so that this can call execute_command!!
  # Also make sure that handles turn end actions etc.
  while True:
    if game.turn_number > n_turns : break
    game.take_nonsense_turn(n_secs_wait, take_prob)



