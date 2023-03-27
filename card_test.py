from game import Game
from game_library import *
from name_registry import reset_name_registry
import time
from typing import List
from card import ALL_CARDS

SEC = "#" + "="*79 + "\n"

tests_to_run = {"unit_tests", "landslide+flipped"}

def test_cards(card_names:List[str], n_moves=12) -> None:
  reset_name_registry()
  G = Game(TEST_GAME_CONFIG)
  G.render()
  commands = [f"ds {card_name}" for card_name in card_names]
  G.execute_commands(commands, display=True)
  # play a nonsense game
  G.execute_commands([f"n {n_moves}"], display=False)
  G.render()

#===============================================================================
# Unit tests
if "unit_tests" in tests_to_run:
  for card_name in ALL_CARDS:
    print(f"{SEC}Test {card_name}")
    test_cards([card_name])

#===============================================================================
# Bunit tests
if "unit_tests" in tests_to_run:
  for card_name_a in ALL_CARDS:
    for card_name_b in ALL_CARDS:
      if card_name_a == card_name_b: continue  # rip this is bc the name registry
      print(f"{SEC}Test {card_name_a} + {card_name_b}")
      test_cards([card_name_a, card_name_b], n_moves=6)



#===============================================================================
# integration tests
if "landslide+flipped" in tests_to_run:
  print(f"{SEC}Test Landslide + Flipped Classroom")
  test_cards(["Landslide", "FlippedClassroom"])
