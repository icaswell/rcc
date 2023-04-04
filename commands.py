from graphics import colorize


def parse_command(line):
    parts = line.strip().split()
    if not parts:  # refresh
        return "r", [], {}
    cmd = parts[0]
    args = []
    kwargs = dict()
    for part in parts[1:]:
        if "=" in part: # part.startswith('--'):
            part = part.replace("--", "")
            k, v = part.split("=", 1)
            kwargs[k] = v
        elif part.startswith('-'):
            kwargs[part[1:]] = True
        else:
            args.append(part)
    # special case: vim-style inputs. assumes a single-letter command.
    if len(cmd) > 1 and not args and not kwargs:
        if cmd[0:-1].isnumeric() and cmd[-1].isalpha():
          args = [cmd[0:-1]]
          cmd = cmd[-1]
        if cmd[1:].isnumeric() and cmd[0].isalpha():
          args = [cmd[1:]]
          cmd = cmd[0]


    if cmd not in COMMAND_ACTIONS:
      raise ValueError(f"unrecognized command '{line}'. Please try again.")
    return cmd, args, kwargs


# Augh this should somehow be decoubled from game.py
COMMAND_ACTIONS = {"halp", "q", "g", "m", "h", "j", "k", 
                   "l", "gg", "G", "r", "n", "d",
                   "ds", "set_random_seed", "dev", "retro"}

def print_help():
    print(f"""
====================================
Here are some commands you can enter!
------------------------------------
Command format:
$ command arg1 arg2 keyword_arg1=X keyword_arg2=Y -option1 -option2 

{colorize('General Commands:',     'green')}
          {colorize('halp',      'red')}: print this string.
          {colorize('r',         'red')}: refresh the screen
          {colorize('q',         'red')}: quit this game.

{colorize('Moving the selection around:',     'green')}
          {colorize('h [N]',     'red')}: move highlighted square left N squares (N defaults to 1)
          {colorize('j [N]',     'red')}: move highlighted square down N squares (N defaults to 1)
          {colorize('k [N]',     'red')}: move highlighted square up N squares (N defaults to 1)
          {colorize('l [N]',     'red')}: move highlighted square right N squares (N defaults to 1)
          {colorize('gg',        'red')}: highlight top-left square
          {colorize('G',         'red')}: highlight bottom right square
          {colorize('g XY [-k]', 'red')}: go to square XY, selecting the piece on it (alternate option -k: keep existing selection) 

{colorize('Taking your turn:',     'green')}
          {colorize('m N',      'red')}: Move the selected piece to the square indicated as N (the lower right-hand corner of every available move will show a number if the piece is selected)
          {colorize('n [K] [--s=X] [--s=Y]', 'red')}: Take a nonsense turn. Alternately, take K nonsense turns, with S seconds wait between them, and take probability T.

{colorize('Advanced/Debugging:',     'green')}
          {colorize('dev',       'red')}: toggle dev mode
          {colorize('d',         'red')}: draw a card
""")



