from game import Game
from game_library import *
from name_registry import reset_name_registry
import time

SEC = "#" + "="*79 + "\n"

tests_to_run = {"move_and_time", "taking", "nonsense_game", "reconstitute_game"}

if "move_and_time" in tests_to_run:
  print(f"{SEC}Moving various pieces and timing the whole operation")
  G = Game(STANDARD_CHESS)
  st = time.time()
  G.render()
  G.move_top_piece("b1", "c4") # w knight
  G.render()
  G.move_top_piece("c4", "b5") # w knight
  G.render()
  G.move_top_piece("e7", "e5")
  G.render()
  G.move_top_piece("d7", "d6")
  G.render()
  G.move_top_piece("h8", "f5")
  G.render()
  G.move_top_piece("e2", "e4")
  G.render()
  G.move_top_piece("e1", "f3")
  G.render()
  G.move_top_piece("c1", "c5")  # w bishop
  G.render()
  G.move_top_piece("a8", "h8")
  G.render()
  G.move_top_piece("d2", "d4")  # W pawn
  G.render()
  G.move_top_piece("b2", "b6")  # W pawn
  G.render()
  total_time = time.time() - st
  print(f"Took {total_time} seconds ({total_time/12}s per render)")

  print(f"{SEC}Take")
  G.move_top_piece("c5", "d6")  # w bishop takes black pawn
  G.render()
  G.move_top_piece("d6", "e7")  # w bishop moves
  G.move_top_piece("e8", "e7")  # Queen takes
  G.move_top_piece("a2", "a3")  # w p moves
  G.move_top_piece("e7", "a3")  # b queen moves
  G.render()


if "nonsense_game" in tests_to_run:
  print(f"{SEC}Nonsense Game")
  reset_name_registry()
  G = Game(STANDARD_CHESS)
  G.render()
  G.play_nonsense_game()
 
if "reconstitute_game" in tests_to_run:
  print(f"{SEC}reconstitute Game")
  reset_name_registry()
  commands = G.command_history
  print(commands)
  G = Game(STANDARD_CHESS)
  G.execute_commands(commands, display=True)
