from game_library import STANDARD_CHESS, RCC, TEST_GAME_CONFIG
from graphics import colorize
from game import Game
from animation import INTRO_VIDEO, HBD_VIDEO
from constants import DEV_MODE

def main():
  global DEV_MODE
  if False:  # Dev mode
    DEV_MODE.append('gg')
    G = Game(TEST_GAME_CONFIG)
  else:  # Normal mode
    DEV_MODE = []
    DEV_MODE.append('gg')
    INTRO_VIDEO.play(); unused = input()
    HBD_VIDEO.play()
    G = Game(RCC)
  G.play_game_interactive()

main()
