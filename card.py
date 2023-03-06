class Card():
    name = ""
    text = ""
    is_active = True

    def card_draw_action(self, player):
        # e.g. Act of humility place pieces
        pass

    def upkeep_action(self, player):
        # e.g. advance plague
        pass

    def update_from_turn_results(self, turn_summary):
        # e.g. for A King is for Glory, update number of King takes and check for win
        pass
