
class Player():
  def __init__(self, team:str, orientation:str, home_row:int) -> None:
    self.team = team
    self.orientation = orientation
    self.home_row = home_row

  def __repr__(self):
    return self.team


