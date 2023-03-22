from graphics import colorize


def parse_command(line):
    parts = line.strip().split()
    if not parts:  # refresh
        return "r", [], {}
    cmd = parts[0]
    args = []
    kwargs = dict()
    for part in parts[1:]:
        if part.startswith('--'):
            k, v = part[2:].split("=", 1)
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

    if cmd not in COMMAND_ACTIONS:
      raise ValueError(f"unrecognized command '{line}'. Please try again.")
    return cmd, args, kwargs


# Augh this should somehow be decoubled from game.py
COMMAND_ACTIONS = {"halp", "q", "g", "m", "h", "j", "k", 
                   "l", "gg", "G", "r", "set_random_seed"}

def print_help():
    print(f"""
====================================
Here are some commands you can enter!
------------------------------------
    General format:
      $ command -option1 -option2 --keyword_argument=
          {colorize('halp',      'red')}: print this string.
          {colorize('g XY [-k]', 'red')}: go to square XY, selecting the piece on it (alternate option -k: keep existing selection) 
          {colorize('m XY',      'red')}: Move the selected piece to square XY
          {colorize('r',         'red')}: refresh
          {colorize('q',         'red')}: quit this game.
          {colorize('h n',       'red')}: move highlighted square left n squares (n defaults to 1)
          {colorize('j n',       'red')}: move highlighted square down n squares (n defaults to 1)
          {colorize('k n',       'red')}: move highlighted square up n squares (n defaults to 1)
          {colorize('l n',       'red')}: move highlighted square right n squares (n defaults to 1)
          {colorize('gg',        'red')}: highlight top-left square
          {colorize('G',         'red')}: highlight bottom right square
""")



