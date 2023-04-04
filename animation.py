"""This is a fast, simple, and hacky class. For anything more complex, use graphics.Image() or rewriter this module.
"""
from time import sleep
from graphics import colorize

def pprint(s):
    print(f"len(s)={len(s)}")
    for row in s:
        print(f'{len(row)} {row}')

class Animation():
    def __init__(self, height=64, width=128, color="green"):
        self.color = color
        self.height = height
        self.width = width
        self.top_border = '\n'*16 + '-'*self.width + "\n"
        self.bottom_border = '-'*self.width + "\n"
        self.frames = []
        self.add_clear_frame()

    def add_clear_frame(self):
        self.frames.append([' '*self.width for _ in range(self.height)])

    def crop_frame_to_size(self, frame:list, upper_left_row=0, upper_left_col=0):
       return self.crop_frame(frame, top_crop=upper_left_row, bottom_crop=upper_left_row + self.height, left_crop=upper_left_col, right_crop=upper_left_col + self.width)

    def crop_frame(self, frame:list, top_crop=0, bottom_crop=1000, left_crop=0, right_crop=1000):
       """Also pads out to desired size"""
       cropped = frame[top_crop:bottom_crop]
       # pad height back to the correct size
       cropped += [" "*self.width for _ in range(self.height - len(cropped))]
       # Want each row to have at least width self.width
       cropped = [row + " "*(self.width + right_crop - len(row)) for row in cropped]
       cropped = [line[left_crop:right_crop] for line in cropped]
       # pad number of columns
       return cropped

    def drop_in_frame(self, bottom_frame, top_frame) -> str:
       if len(bottom_frame) != len(top_frame):
           bottom_h =  [len(r) for r in bottom_frame]
           top_h =  [len(r) for r in top_frame]
           raise ValueError(f"len(bottom_frame)={len(bottom_frame)} (h={bottom_h}); len(top_frame)={len(top_frame)} (h={top_h})")
       out_frame = []
       for row_i, row in enumerate(bottom_frame):
           out_row = ''
           for col_j, ch in enumerate(top_frame[row_i]):
               if ch.strip():
                   out_row += ch
               else:
                   out_row += bottom_frame[row_i][col_j]
           out_frame.append(out_row)
       return out_frame

    def play(self, n_secs=0.08, top_crop=0, bottom_crop=0, left_crop=0, right_crop=0):
        # cropped_frames = [colorize(self.crop_frame(frame), self.color) for frame in self.frames]
        for frame in self.frames:
            payload = self.top_border + '|\n'.join(frame) + "|\n" + self.bottom_border
            print(colorize(payload, self.color), end="")
            sleep(n_secs)

    def add_ltr_scrolling_entrance(self, s, n_frames, row_offset, speed=2):
        raw_frame = s.split("\n")
        max_width = max([len(row) for row in raw_frame])
        full_width = self.width  + max_width
        for row_i in range(len(raw_frame)):
          # pad it so each line has length self.width  + max_width
          # put self.width " "'s to the right
          extra_pixels_to_add = full_width - len(raw_frame[row_i])
          raw_frame[row_i] += " " * extra_pixels_to_add
        # offset the image down by putting more rows on top
        raw_frame = [' '*full_width for _ in range(row_offset)] + raw_frame
        # add extra rows on bottom if needed to have height self.height
        raw_frame += [' '*full_width for _ in range(self.height - len(raw_frame))]
        cur_frame = raw_frame
        last_old_frame= self.frames[-1]
        for i in range(n_frames):
           # shift rows over
           for row_i in range(len(cur_frame)):
               cur_frame[row_i]  = " " + cur_frame[row_i][0:-1]
           if i%speed and i != n_frames - 1: continue
           cropped = self.crop_frame_to_size(cur_frame, upper_left_col=max_width)
           cropped = self.drop_in_frame(bottom_frame=last_old_frame, top_frame=cropped)
           self.frames.append(cropped)


    def add_ttb_scrolling_entrance(self, s, n_frames, speed=1):
        raw_frame = s.split("\n")
        orig_len = len(raw_frame)
        raw_frame += [' '*self.width for _ in range(self.height)]
        cur_frame = raw_frame
        last_old_frame= self.frames[-1]
        for i in range(n_frames):
           # remove last row; add empty first row
           cur_frame = [" "*self.width] + cur_frame[0:-1] 
           if i%speed and i != n_frames - 1: continue
           cropped = self.crop_frame_to_size(cur_frame, upper_left_row=orig_len)
           cropped = self.drop_in_frame(bottom_frame=last_old_frame, top_frame=cropped)
           self.frames.append(cropped)
    def extend_final_frame(self, n_times):
        self.frames += [self.frames[-1].copy() for _ in range(n_times)]


INTRO_VIDEO = Animation()
INTRO_VIDEO.add_ttb_scrolling_entrance("""
            ____                  __                   ______            _                ________
           / __ \____ _____  ____/ /___  ____ ___     / ____/___  ____  (_)___  ____ _   / ____/ /_  ___  __________
          / /_/ / __ `/ __ \/ __  / __ \/ __ `__ \   / /   / __ \/ __ \/ / __ \/ __ `/  / /   / __ \/ _ \/ ___/ ___/
         / _, _/ /_/ / / / / /_/ / /_/ / / / / / /  / /___/ /_/ / /_/ / / / / / /_/ /  / /___/ / / /  __(__  |__  )
        /_/ |_|\__,_/_/ /_/\__,_/\____/_/ /_/ /_/   \____/\____/ .___/_/_/ /_/\__, /   \____/_/ /_/\___/____/____/
                                                              /_/            /____/
""", 28)

INTRO_VIDEO.add_ltr_scrolling_entrance("""
 ,-.      ___                  ______                 _ __                             _ __  __ _
/,-.\    ( /                  (  /                   ( /  )                            /(__)(__)/
||  |     / (   __,  __,  _,    /_   _  _  ,___ _     /--<  __,  _ _ _   __,  _ _     /   /   // 
\`-'/   _/_/_)_(_/(_(_/(_(__  _// (_(/_/ |/ (_)/ (_  /   \_(_/(_/ / / /_(_/(_/ / /_  /   /   //  
 `-'                                                                                             
                                                                                           

                                """, n_frames=124, row_offset=58, speed=14)
INTRO_VIDEO.extend_final_frame(10)
INTRO_VIDEO.add_clear_frame()


INTRO_VIDEO.add_ttb_scrolling_entrance("""
                      
                       _ _|               |                       |   _)                     
                         |   __ \    __|  __|   __|  |   |   __|  __|  |   _ \   __ \    __| 
                         |   |   | \__ \  |    |     |   |  (     |    |  (   |  |   | \__ \ 
                       ___| _|  _| ____/ \__| _|    \__,_| \___| \__| _| \___/  _|  _| ____/ 
                                                                          

                                 """, n_frames=11, speed=1)
INTRO_VIDEO.add_ttb_scrolling_entrance("""
               _  _          _           _                _ _   _      _  _      _   _  __  _    
         ___  | \| |__ ___ _(_)__ _ __ _| |_ ___  __ __ _(_) |_| |_   | || |  _ | | | |/ / | |   
        |___| | .` / _` \ V / / _` / _` |  _/ -_) \ V  V / |  _| ' \  | __ | | || | | ' <  | |__ 
              |_|\_\__,_|\_/|_\__, \__,_|\__\___|  \_/\_/|_|\__|_||_| |_||_|  \__/  |_|\_\ |____|
                              |___/                                                              """, n_frames=19, speed=3)
INTRO_VIDEO.add_ttb_scrolling_entrance("""
               __  __                       _        _          _        _                     _ _   _            
         ___  |  \/  |_____ _____   ___ ___| |___ __| |_ ___ __| |  _ __(_)___ __ ___  __ __ _(_) |_| |_    _ __  
        |___| | |\/| / _ \ V / -_) (_-</ -_) / -_) _|  _/ -_) _` | | '_ \ / -_) _/ -_) \ V  V / |  _| ' \  | '  \ 
              |_|  |_\___/\_/\___| /__/\___|_\___\__|\__\___\__,_| | .__/_\___\__\___|  \_/\_/|_|\__|_||_| |_|_|_|
                                                                   |_|                                            """, n_frames=25, speed=3)
    
INTRO_VIDEO.add_ttb_scrolling_entrance("""
               _____                 _ _         _      _    __           _        _      
         ___  |_   _|  _ _ __  ___  ( ) |_  __ _| |_ __( )  / _|___ _ _  | |_  ___| |_ __ 
        |___|   | || || | '_ \/ -_) |/| ' \/ _` | | '_ \/  |  _/ _ \ '_| | ' \/ -_) | '_ \\
                |_| \_, | .__/\___|   |_||_\__,_|_| .__/   |_| \___/_|   |_||_\___|_| .__/
                    |__/|_|                       |_|                               |_|   """, n_frames=31, speed=3)
    
INTRO_VIDEO.add_ttb_scrolling_entrance("""
                 _           _   __  __        _     ___                     _            _   _              
         ___    /_\  _ _  __| | |  \/  |___ __| |_  |_ _|_ __  _ __  ___ _ _| |_ __ _ _ _| |_| |_  _         
        |___|  / _ \| ' \/ _` | | |\/| / _ (_-<  _|  | || '  \| '_ \/ _ \ '_|  _/ _` | ' \  _| | || |_ _ _ _ 
              /_/ \_\_||_\__,_| |_|  |_\___/__/\__| |___|_|_|_| .__/\___/_|  \__\__,_|_||_\__|_|\_, (_|_|_|_)
                                                              |_|                               |__/         """, n_frames=37, speed=3)


INTRO_VIDEO.add_ttb_scrolling_entrance("""
                    
                              ...                                                 ..     ..   
                           xH88"`~ .x8X                                          888B.  888B. 
                         :8888   .f"8888Hf        u.    .d``                    48888E 48888E 
                        :8888>  X8L  ^""`   ...ue888b   @8Ne.   .u        .u    '8888' '8888' 
                        X8888  X888h        888R Y888r  %8888:u@88N    ud8888.   Y88F   Y88F  
                        88888  !88888.      888R I888>   `888I  888. :888'8888.  '88    '88   
                        88888   %88888      888R I888>    888I  888I d888 '88%"   8F     8F   
                        88888 '> `8888>     888R I888>    888I  888I 8888.+"      4      4    
                        `8888L %  ?888   ! u8888cJ888   uW888L  888' 8888L        .      .    
                         `8888  `-*""   /   "*888*P"   '*88888Nu88P  '8888c. .+  u8N.   u8N.  
                           "888.      :"      'Y"      ~ '88888F`     "88888%   "*88%  "*88%  
                             `""***~"`                    888 ^         "YP'      ""     ""   
                                                          *8E                                 
                                                          '8>                                 
                                                           "                                  
                                 """, n_frames=58, speed=3)

INTRO_VIDEO.add_ltr_scrolling_entrance("""
 _ __                 ______
( /  )               (  /          _/_         _/_                 _/_o
 /--'_   _  (   (      /--   _ _   /  _  _     /  __   _, __ _ _   / ,  _ _   , , _
/   / (_(/_/_)_/_)_  (/____// / /_(__(/_/ (_  (__(_)  (__(_)/ / /_(__(_/ / /_(_/_(/_ o  o  o

                                                                                     """, n_frames=125, speed=30, row_offset=58)








HBD_VIDEO = Animation()

HBD_VIDEO.add_ttb_scrolling_entrance("""
                                .xHL                                                   ..                          
                             .-`8888hxxx~                 .d``          .d``          @L                           
                          .H8X  `%888*"            u      @8Ne.   .u    @8Ne.   .u   9888i   .dL                   
                          888X     ..x..        us888u.   %8888:u@88N   %8888:u@88N  `Y888k:*888.                  
                         '8888k .x8888888x   .@88 "8888"   `888I  888.   `888I  888.   888E  888I                  
                          ?8888X    "88888X  9888  9888     888I  888I    888I  888I   888E  888I                  
                           ?8888X    '88888> 9888  9888     888I  888I    888I  888I   888E  888I                  
                        H8H %8888     `8888> 9888  9888   uW888L  888'  uW888L  888'   888E  888I                  
                       '888> 888"      8888  9888  9888  '*88888Nu88P  '*88888Nu88P   x888N><888'                  
                        "8` .8" ..     88*   "888*""888" ~ '88888F`    ~ '88888F`      "88"  888                   
                           `  x8888h. d*"     ^Y"   ^Y'     888 ^         888 ^              88F                   
                             !""*888%~                      *8E           *8E               98"                    
                             !   `"  .                      '8>           '8>             ./"                      
                             '-....:~                        "             "             ~`                        
                   ...     ..         .                      s                   ..                                
                .=*8888x <"?88h.     @88>                   :8      .uef^"     dF                       ..         
               X>  '8888H> '8888     %8P      .u    .      .88    :d88E       '88bu.                   @L          
              '88h. `8888   8888      .     .d88B :@8c    :888ooo `888E       '*88888bu         u     9888i   .dL  
              '8888 '8888    "88>   .@88u  ="8888f8888r -*8888888  888E .z8k    ^"*8888N     us888u.  `Y888k:*888. 
               `888 '8888.xH888x.  ''888E`   4888>'88"    8888     888E~?888L  beWE "888L .@88 "8888"   888E  888I 
                 X" :88*~  `*8888>   888E    4888> '      8888     888E  888E  888E  888E 9888  9888    888E  888I 
               ~"   !"`      "888>   888E    4888>        8888     888E  888E  888E  888E 9888  9888    888E  888I 
                .H8888h.      ?88    888E   .d888L .+    .8888Lu=  888E  888E  888E  888F 9888  9888    888E  888I 
               :"^"88888h.    '!     888&   ^"8888*"     ^%888*    888E  888E .888N..888  9888  9888   x888N><888' 
               ^    "88888hx.+"      R888"     "Y"         'Y"    m888N= 888>  `"888*""   "888*""888"   "88"  888  
                      ^"**""          ""                           `Y"   888      ""       ^Y"   ^Y'          88F  
                                                                        J88"                                 98"   
                                                                        @%                                 ./"     
                                                                      :"                                  ~`       
                      ..      ...                                                                 ..               
                   :~"8888x :"%888x                                                              888B.             
                  8    8888Xf  8888>                 ..    .     :                   u.    u.   48888E             
                 X88x. ?8888k  8888X        u      .888: x888  x888.        u      x@88k u@88c. '8888'             
                 '8888L'8888X  '%88X     us888u.  ~`8888~'888X`?888f`    us888u.  ^"8888""8888"  Y88F              
                  "888X 8888X:xnHH(`` .@88 "8888"   X888  888X '888>  .@88 "8888"   8888  888R   '88               
                    ?8~ 8888X X8888   9888  9888    X888  888X '888>  9888  9888    8888  888R    8F               
                  -~`   8888> X8888   9888  9888    X888  888X '888>  9888  9888    8888  888R    4                
                  :H8x  8888  X8888   9888  9888    X888  888X '888>  9888  9888    8888  888R    .                
                  8888> 888~  X8888   9888  9888   "*88%""*88" '888!` 9888  9888   "*88*" 8888"  u8N.              
                  48"` '8*~   `8888!` "888*""888"    `~    "    `"`   "888*""888"    ""   'Y"   "*88%              
                   ^-==""      `""     ^Y"   ^Y'                       ^Y"   ^Y'                  ""               
                                                                                                               
                                                                                                               
                                       """, n_frames=110, speed=3)






def GAME_WIN_ANIMATION(team):
  VIDEO = Animation()
  if team == "White":
    VIDEO.add_ttb_scrolling_entrance("""
                                    ...    .     ...                     .         s               
                                 .~`"888x.!**h.-``888h.     .uef^"      @88>      :8               
                                dX   `8888   :X   48888>  :d88E         %8P      .88               
                               '888x  8888  X88.  '8888>  `888E          .      :888ooo      .u    
                               '88888 8888X:8888:   )?""`  888E .z8k   .@88u  -*8888888   ud8888.  
                                `8888>8888 '88888>.88h.    888E~?888L ''888E`   8888    :888'8888. 
                                  `8" 888f  `8888>X88888.  888E  888E   888E    8888    d888 '88%" 
                                 -~` '8%"     88" `88888X  888E  888E   888E    8888    8888.+"    
                                 .H888n.      XHn.  `*88!  888E  888E   888E   .8888Lu= 8888L      
                                :88888888x..x88888X.  `!   888E  888E   888&   ^%888*   '8888c. .+ 
                                f  ^%888888% `*88888nx"   m888N= 888>   R888"    'Y"     "88888%   
                                     `"**"`    `"**""      `Y"   888     ""                "YP'    
                                                                J88"                               
                                                                @%                                 
                                                              :"                                   
    """, 26, speed=2)
  elif team == "Black":
      VIDEO.add_ttb_scrolling_entrance("""
                                     ...     ..            ..                             ..      
                                 .=*8888x <"?88h.   x .d88"                        < .z@8"`      
                                X>  '8888H> '8888    5888R                          !@88E        
                               '88h. `8888   8888    '888R         u           .    '888E   u    
                               '8888 '8888    "88>    888R      us888u.   .udR88N    888E u@8NL  
                                `888 '8888.xH888x.    888R   .@88 "8888" <888'888k   888E`"88*"  
                                  X" :88*~  `*8888>   888R   9888  9888  9888 'Y"    888E .dN.   
                                ~"   !"`      "888>   888R   9888  9888  9888        888E~8888   
                                 .H8888h.      ?88    888R   9888  9888  9888        888E '888&  
                                :"^"88888h.    '!    .888B . 9888  9888  ?8888u../   888E  9888. 
                                ^    "88888hx.+"     ^*888%  "888*""888"  "8888P'  '"888*" 4888" 
                                       ^"**""          "%     ^Y"   ^Y'     "P'       ""    ""   
                                                                                                 
                                                                                                       """, 26, speed=2)
                                  
  VIDEO.add_ttb_scrolling_entrance("""
                                     ...    .     ...         .                     .x+=:.   
                                  .~`"888x.!**h.-``888h.     @88>                  z`    ^%  
                                 dX   `8888   :X   48888>    %8P      u.    u.        .   <k 
                                '888x  8888  X88.  '8888>     .     x@88k u@88c.    .@8Ned8" 
                                '88888 8888X:8888:   )?""`  .@88u  ^"8888""8888"  .@^%8888"  
                                 `8888>8888 '88888>.88h.   ''888E`   8888  888R  x88:  `)8b. 
                                   `8" 888f  `8888>X88888.   888E    8888  888R  8888N=*8888 
                                  -~` '8%"     88" `88888X   888E    8888  888R   %8"    R88 
                                  .H888n.      XHn.  `*88!   888E    8888  888R    @8Wou 9%  
                                 :88888888x..x88888X.  `!    888&   "*88*" 8888" .888888P`   
                                 f  ^%888888% `*88888nx"     R888"    ""   'Y"   `   ^"F     
                                      `"**"`    `"**""        ""                             
                                                                                             
                                                                                                        """, 44, speed=2)
                                    
  VIDEO.add_ltr_scrolling_entrance("""
              ____                  __                   ______            _                ________
             / __ \____ _____  ____/ /___  ____ ___     / ____/___  ____  (_)___  ____ _   / ____/ /_  ___  __________
            / /_/ / __ `/ __ \/ __  / __ \/ __ `__ \   / /   / __ \/ __ \/ / __ \/ __ `/  / /   / __ \/ _ \/ ___/ ___/
           / _, _/ /_/ / / / / /_/ / /_/ / / / / / /  / /___/ /_/ / /_/ / / / / / /_/ /  / /___/ / / /  __(__  |__  )
          /_/ |_|\__,_/_/ /_/\__,_/\____/_/ /_/ /_/   \____/\____/ .___/_/_/ /_/\__, /   \____/_/ /_/\___/____/____/
                                                                /_/            /____/
  """, n_frames=127, speed=20, row_offset=58)

  return VIDEO
                                                                                           


