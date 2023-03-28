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
        self.top_border = '\n'*8 + '-'*self.width + "\n"
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

    def play(self, n_secs=0.1, top_crop=0, bottom_crop=0, left_crop=0, right_crop=0):
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
           if i%speed: continue
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
                                                                                           

                                """, n_frames=140, row_offset=58, speed=14)
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

                                                                                     """, n_frames=145, speed=30, row_offset=58)



