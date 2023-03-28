from game_library import STANDARD_CHESS, TEST_GAME_CONFIG
from graphics import colorize
from game import Game
from animation import INTRO_VIDEO

def main():
  G = Game(TEST_GAME_CONFIG)
  INTRO_VIDEO.play()
  unused = input()
  # G = Game(STANDARD_CHESS)
  G.play_game_interactive()

main()
