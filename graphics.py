import os, sys

from name_registry import register_name, random_string

COLORS = {
  "underline": 4,
  "flashing": 5,
  "black": 30,
  "red": 31,
  "green": 32,
  "yellow": 33,
  "blue": 34,
  "pink": 35,
  "teal": 36,
  "grey": 37,
  "white_highlight": 7,
  "black_highlight": 40,
  "red_highlight": 41,
  "green_highlight": 42,
  "yellow_highlight": 43,
  "blue_highlight": 44,
  "pink_highlight": 45,
  "teal_highlight": 46,
  "grey_highlight": 47,
}
COLOR_END =  "\033[0m"

def get_color_tags(color):
  if color == "none": return ('', '')
  if color not in COLORS:
      raise ValueError(f"Unknown color '{color}'")
  color_i = COLORS[color]
  return f"\033[{color_i}m",  "\033[0m"

def colorize(s: str, color: str) -> str:
  start, stop = get_color_tags(color)
  return f"{start}{s}{stop}"


class Pixel():
    def __init__(self, val = " ", color: str = None, color_end:bool = False):
        # self.val = val
        # pre_tags = []
        # post_tags = []
        if color and color != "none":
          if color not in COLORS:
            raise ValueError(f"Unknown color '{color}'")
          color_i = COLORS[color]
          self.pre_tags.append(f"\033[{color_i}m")
        if color_end:
            self.post_tags.append(COLOR_END)

    def surface(self):
      """Get the surface form of the pixel"""
      return ''.join(self.pre_tags) + self.val + ''.join(self.post_tags)




class Image():
    def __init__(self, from_string=None, height=None, width=None, name=None, color=None):
        assert (from_string is not None) != (height or width)

        if width and not height:
          raise ValueError("No can do 0-height images (yet)")

        if name:
            self.name = name
        else:
            self.name = "unnamed_" + random_string()
        register_name(self.name)


        self.layers = []
        self.layer_unique_ids = []
        self.empty_pixel = " "

        if from_string:
          self.add_layer_from_string(from_string, layer_name=f"{self.name}_base")
        else:
          self.height = height
          self.width = width
          self.add_transparency(layer_name=f"{self.name}_base")

        self.color = "none"
        if color:
            self.set_color(color)

    def add_transparency(self, layer_name=None):
          pixels = [[self.empty_pixel]* self.width for _ in range(self.height)]
          self.layers.append(pixels)
          if not layer_name:
              layer_name = "transparency" 
              # TODO random string
              # TODO register name
          self.layer_unique_ids.append(layer_name)
        

    def pop_layer(self, layer_id = None):
        pass

    def expand_canvas(self, new_height, new_width):
        if new_height < self.height and new_width < self.width:
            return # nothing need be done. Image is already big enough.
            # raise ValueError(f"Cannot expand image {self.name} with size (h={self.height}, w={self.width}) to new size (h={new_height}, w={new_width}); new size must be greater in at least one dimension.")

        new_height = max(self.height, new_height)
        new_width = max(self.width, new_width)

        current_color = self.color
        self.set_color("none")

        for layer_i, layer in enumerate(self.layers):
          # expand height
          n_new_cols = new_width - self.width
          n_new_rows = new_height - self.height

          # Add new cols to existing rows
          for row_i in range(len(layer)):
            new_cols = [' ']*n_new_cols
            self.layers[layer_i][row_i] += new_cols

          # expand height by adding entirely new rows
          new_rows = [[' ']*new_width for new_row_i in range(n_new_rows)]
          self.layers[layer_i] += new_rows

        self.height = new_height
        self.width = new_width
        self.set_color(current_color)


    def print_debug(self):
        print(f"Image '{self.name}' has {len(self.layers)} layers and shape (h={self.height}, w={self.width})")
        for i, layer in enumerate(self.layers):
          print(f"\tlayer {i} (ID={self.layer_unique_ids[i]}): (h={len(layer)}, w={len(layer[i])})")
          for row in layer:
            print("\t\t", row)


    def set_pixel(self, row_i, col_j, pixel_val, layer_i=-1, preserve_color=True):
        # possible todo: raise error if pixel val doesn't have a printed length of 1
        old_pixel = self.layers[layer_i][row_i][col_j]
        if preserve_color and len(old_pixel) > 1:
          print([old_pixel])
          open_tag, pixel, close_tag = re.match("(\033\[[^m]*m)?(.*)(\033\[0m)?", old_pixel).groups()
          open_tag = '' if not open_tag else open_tag
          close_tag = '' if not close_tag else close_tag
          pixel_val = f"{open_tag}{pixel_val}{close_tag}"
        self.layers[layer_i][row_i][col_j] = pixel_val


    def print_in_string(self, s):
        """Make a new transparent layer and print a string on it.
        """
        self.add_transparency()
        for row_i in range(self.height):
            for col_j in range(self.width):
                string_idx = col_j + row_i*self.width
                if string_idx >= len(s): break
                self.set_pixel(row_i, col_j, s[string_idx])



    def drop_in_image_by_coordinates(self, image, upper_left_row, upper_left_col):
       assert upper_left_row >= 0 and upper_left_col >= 0
       new_height = upper_left_row + image.height
       new_width = upper_left_col + image.width
       self.expand_canvas(new_height=new_height, new_width=new_width)
       current_color = self.color
       self.set_color("none")

       new_pixels = image.pixels()
       for row_i in range(image.height):
           for col_j in range(image.width):
               new_pixel = new_pixels[row_i][col_j]
               self.layers[-1][row_i + upper_left_row][col_j + upper_left_col] = new_pixel
       self.set_color(current_color)
       self.fix_nested_colors(self.layers[-1])

    def drop_in_image(self, image, location, height_buf=0, width_buf=0):
        # location can be:
        #   tuple of coordinates
        #   A string equalling "right_top" or "bottom_left"
        # height_buf, row_buf are the offests from this location in the height and width dimensions, resp. TODO rename to right_buf, bottom_buf?

        # 
        # xxxxxx   oo   <-- location=right_top, width_buf=3
        # xxxxxx   oo
        # xxxxxx
        # oo            <---location=bottom_left
        # oo
        if isinstance(location, tuple):
            assert (height_buf, width_buf) == (0, 0)
            upper_left_row, upper_left_col = location
        elif location == "right_top":
            upper_left_row = height_buf
            upper_left_col = self.width + width_buf
        elif location == "bottom_left":
            upper_left_row = self.height + height_buf
            upper_left_col = width_buf
        else:
           raise ValueError(f"location {location} for drop_in_image is not supported!")
        if upper_left_row < 0 or upper_left_col < 0:
            raise ValueError(f"derop_in_image with location={location}, height_buf={height_buf}, width_buf={width_buf} causes one of the following to be negative: upper_left_col={upper_left_col}, upper_left_row={upper_left_row}")

        self.drop_in_image_by_coordinates(image, upper_left_row, upper_left_col)
       
    def get_top_visible_pixel(self, i, j):
        # traverse the layers from top to bottom
        for layer in self.layers[::-1]:
            if layer[i][j] != self.empty_pixel:
                return layer[i][j]
        return self.empty_pixel

    def pixels(self):
        # TODO handle stacked colors
        out_pixels = self.layers[-1]
        for row_i in range(self.height):
            for col_j in range(self.width):
                out_pixels[row_i][col_j] = self.get_top_visible_pixel(row_i, col_j)
        self.fix_nested_colors(out_pixels)
        return out_pixels

    def stack_on_image(self, image):
        #  sort of like "over_append"
        self.layers += self.copy_layers(image.layers)
        self.layer_unique_ids += image.layer_unique_ids.copy()

    def r_append(self, other_image):
        # append to right
        # WARNING this method flattens all the images together and only keeps the top layer!
        pixels = self.pixels()
        # doesn't deal with layers. Therefore, only for printing.
        if self.height != other_image.height:
            raise ValueError(f"Image '{self.name}' of height {self.height} can't r_append '{other_image.name}' of height {other_image.height}")
        other_img_pixels = other_image.pixels()
        for row_i in range(self.height):
            pixels[row_i] = pixels[row_i] + other_img_pixels[row_i]
        self.layers = [pixels]
        self.width += other_image.width

    def u_append(self, other_image):
        # append under
        # WARNING this method flattens all the images together and only keeps the top layer!
        # So it should only be used for rendering.
        pixels = self.pixels()
        if self.width != other_image.width:
            raise ValueError(f"Can't concatenate image {self.name} with shape (h={self.height}, w={self.width}) with image {other_image.name} with shape (h={other_image.height}, w={other_image.width})")
        pixels += other_image.pixels()
        self.layers = [pixels]
        self.height += other_image.height


    def fix_nested_colors(self, pixels):
        # to be called after any layer merging
        # say "R(" opens red, "G(" opens Green, ")" closes any color:
        #
        # Normal nesting
        # in:  ['R( ', ' ', 'G( ', ' ', ' )',   ' ', ' )']
        # out: ['R( ', ' ', 'G( ', ' ', ' )R(', ' ', ' )']
        # 
        # Missing last tag
        # in:  ['R( ', ' ', 'G( ', ' ', ' )',   ' ', ' ']
        # out: ['R( ', ' ', 'G( ', ' ', ' )R(', ' ', ' )']
        # 
        # double tag
        # in:  ['R( ', ' ', 'G(Y( ', ' )',   ' )',   ' ', ' )']
        # out: ['R( ', ' ', 'G(Y( ', ' )G(', ' )R(', ' ', ' )']
        # 
        # don't mess up on partially correct colors
        # in:  ['R( ', ' ', 'G(Y( ', ' )',   ' )R('  ' ', ' )']
        # out: ['R( ', ' ', 'G(Y( ', ' )G(', ' )R(', ' ', ' )']
        # 
        # Extra last tag
        # in:  [' ', ' ', 'G( ', ' ', ' )', ' ', ' )']
        # out: [' ', ' ', 'G( ', ' ', ' )', ' ', ' ']
        # TODO implement
        pass

    def set_color(self, color):
        self.color = color
        if color == "none": return

        self.uncolor()
        pixels = self.layers[-1]
        open_tag, close_tag = get_color_tags(color)
        for row_i in range(self.height):
            pixels[row_i][0] = open_tag + pixels[row_i][0]
            pixels[row_i][-1] =  pixels[row_i][-1] + close_tag

    def uncolor(self):
        pixels = self.layers[-1]
        for row_i in range(self.height):
            # Technically these if statements are unneccesary
          if len(pixels[row_i][0]) != 1:
              pixels[row_i][0] = pixels[row_i][0][-1]
          if len(pixels[row_i][-1]) != 1:
              pixels[row_i][-1] = pixels[row_i][-1][0]
        self.color = "none"

    def check_image_dimensions(self):
        # a debug method
        for layer_i, layer in enumerate(self.layers):
          if len(layer) != self.height:
              raise ValueError(f"Image {img.name} has height {self.height}, but layer {self.layer_unique_ids[layer_i]} (#{layer_i}) has length {len(layer)}")
          for row_i, row in enumerate(layer):
            if len(row) != self.width:
                  raise ValueError(f"Image {img.name} has width {self.width}, but row #{row_i} in layer {self.layer_unique_ids[layer_i]} (#{layer_i}) has length {len(row)}")
            for pixel_i, pixel in enumerate(row):
                pixel_len = len(pixel)
                # color end tag: 4
                # color begin tag: 4 - 6 (TODO check)
                if pixel_len not in {1, 5, 6, 7, 9, 10, 11}:
                    raise ValueError(f"In Image {img.name}, pixel {pixel_i} '{pixel}' in row #{row_i} in layer {self.layer_unique_ids[layer_i]} (#{layer_i}) has length {pixel_len}, but pixels must be of length in {1, 5, 6, 7, 9, 10, 11}")


    def add_layer_from_string(self, s, layer_name=None):
        rows = [row for row in s.split("\n") if row]
        self.height = len(rows)
        self.width = len(rows[0])

        string_pixels = []
        for row_i in range(self.height):
            string_pixels.append([])
            if len(rows[row_i]) != self.width:
                raise ValueError(f"row {row_i} of image {self.name} has length {len(rows[row_i])}, but self.width={self.width}")
            for col_j in range(self.width):
                string_pixels[row_i].append(rows[row_i][col_j: col_j+1])
        self.layers.append(string_pixels)
        if not layer_name:
            # TODO register and random
            layer_name = "from_string"
        self.layer_unique_ids.append(layer_name)


    def set_all_pixels_to_value(self, v):
        pixels = self.layers[-1]
        for row_i in range(self.height):
            for col_j in range(self.width):
                pixels[row_i][col_j] = v

    def render(self):
        pixels = self.pixels()
        printstring = ""
        for row_i in range(self.height):
            for col_j in range(self.width):
                printstring += pixels[row_i][col_j]
            printstring += "\n"
        # fo = os.fdopen(sys.stdout.fileno(), 'w', 1000000)
        # fo.write(printstring)
        # fo.close()
        print(printstring)

    def copy_layers(self, layers):
        return [[row.copy() for row in layer] for layer in layers]

    def copy(self, name=None, color=None):
        if not name: 
            name = self.name + "_copy"
        new_image = Image(width=self.width, height=self.height, name=name)
        new_image.layers = self.copy_layers(self.layers)
        if color:
            new_image.set_color(color)
        return new_image






def wrap_collapse(images: list, width: int, height_buf:int = 0) -> Image:
    """wrape a list of images into one image:
    Input: [ x x x x x x x ]
    Output:
     x x x 
     x x x 
     x 
     """
    if not images: return None
    if len(images) == 1: return images[0]
    widths = [img.width for img in images]
    if any(w > width for w in widths):
        raise ValueError(f"Cannot wrap_collapse images where at least one exceeds width={width}: {widths}.")

    cur_width = 0
    row_start_indices = [0] # the NON-INCLUSIVE upper bounds of each row
    for img_i, w in enumerate(widths):
        if cur_width + w > width:
            row_start_indices.append(img_i)
            cur_width = w
        cur_width += w
    row_start_indices.append(len(widths))

    img_rows = []
    for i in range(len(row_start_indices) - 1):
        lb = row_start_indices[i]
        ub = row_start_indices[i + 1]
        img_rows.append(horizontal_collapse(images[lb:ub]))

    return vertical_collapse(img_rows, height_buf=height_buf)

def vertical_collapse(images: list, height_buf:int=0) -> Image:
    """Stack a list of images vertically into one image"""
    if not images: return None
    if len(images) == 1: return images[0]
    final_img = images[0].copy()
    for img in images[1:]:
        final_img.drop_in_image(img, "bottom_left", height_buf=height_buf)
    return final_img

def horizontal_collapse(images: list) -> Image:
    """Stack a list of images horizontally into one image"""
    if not images: return None
    if len(images) == 1: return images[0]
    final_image = Image(height=images[0].height, width=0)
    for img in images:
        final_image.drop_in_image(img, "right_top")
    return final_image


