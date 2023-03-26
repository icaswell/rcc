from game import Game
from game_library import *
from name_registry import reset_name_registry
import time
from typing import List
from card import ALL_CARDS

SEC = "#" + "="*79 + "\n"

tests_to_run = {"unit_tests", "landslide+flipped"}

def test_cards(card_names:List[str]) -> None:
  reset_name_registry()
  G = Game(TEST_GAME_CONFIG)
  G.render()
  commands = [f"ds {card_name}" for card_name in card_names]
  G.execute_commands(commands, display=True)
  # move the cursor around
  G.execute_commands("j l k h 4j 6k 11h".split(), display=False)
  # play a nonsense game for 12 moves
  G.execute_commands(["n 12"], display=False)
  G.render()

#===============================================================================
# Unit tests
if "unit_tests" in tests_to_run:
  for card_name in ALL_CARDS:
    print(f"{SEC}Test {card_name}")
    test_cards([card_name])


#===============================================================================
# integration tests
if "landslide+flipped" in tests_to_run:
  print(f"{SEC}Test Landslide + Flipped Classroom")
  test_cards(["Landslide", "FlippedClassroom"])
