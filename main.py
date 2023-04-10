from game_library import STANDARD_CHESS, RCC, TEST_GAME_CONFIG
from graphics import colorize
from game import Game
from constants import DEV_MODE
from commands import play_game_interactive

def main():
  global DEV_MODE
  if False:  # Dev mode
    DEV_MODE.append('gg')
    G = Game(TEST_GAME_CONFIG)
  else:  # Normal mode
    # DEV_MODE.append('gg')
    G = Game(RCC)
  play_game_interactive(G, intro_video=True)

main()
