class Player():
    color = "" 
    display_name = ""
    
    special_stuff = {}  # e.g. Seeds of Self Doubt, quantum credits

class Move():
    # purely for informaiton passing to cards
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

    all_cards = []
    turn_order = ["Ibrahim", "White", "Elijah",  "Black"]  # Ibrahim is the "player" corresponding to white's pkeep
    upkeep_players = ["Ibrahim", "Elijah"]
    human_players = ["White", "Black"]
    turn = 0
    living_pieces = []
    dead_pieces = []
    etherized_pieces = []

    def perform_upkeep():
        pass
