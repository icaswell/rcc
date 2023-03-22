from game_library import STANDARD_CHESS, TEST_GAME_CONFIG
from game import Game

def main():
  G = Game(TEST_GAME_CONFIG)
  # G = Game(STANDARD_CHESS)
  G.play_game_interactive()

main()
