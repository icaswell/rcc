import os, sys
from typing import List

from name_registry import register_name, register_unique_name, random_string

# echo -e "\033[38;5;208mpeach\033[0;00m"
# This will output a pleasing sort of peach colored text.
# 
# Taking apart this command: \033[38;5;208m
# 
# The \033 is the escape code. The [38; directs command to the foreground. If you want to change the background color instead, use [48; instead. The 5; is just a piece of the sequence that changes color. And the most important part, 208m, selects the actual color.
# 
# There are 3 sets of colors that can be found in the 256 color sequence for this escape. The first set is the basic "candy" color set, or values 0-15. Then there is a cube of distributed colors, from 16-231. Lastly there is a detailed grayscale set from 232-255.
# 
# You can find a table with all of these values here: http://bitmote.com/index.php?post/2012/11/19/Using-ANSI-Color-Codes-to-Colorize-Your-Bash-Prompt-on-Linux#256%20(8-bit)%20Colors

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

DEBUG_COLORS_TO_NAMES = {f"\033[{v}m":"+" + k.replace("highlight", "h") for k, v in COLORS.items()}
DEBUG_COLORS_TO_NAMES[COLOR_END] = "END"
DEBUG_COLORS_TO_NAMES[""] = ""

def get_color_tags(color: str):
  if color == "none": return ('', '')
  return get_color_open_tag(color), COLOR_END

def get_color_open_tag(color: str):
  if color == "none": return ''
  if color not in COLORS:
      raise ValueError(f"Unknown color '{color}'")
  color_i = COLORS[color]
  return f"\033[{color_i}m"

def colorize(s: str, color: str) -> str:
  """Color the given string"""
  start, stop = get_color_tags(color)
  return f"{start}{s}{stop}"


class Pixel(): pass  # forward declaration
class Pixel():
    def __init__(self, val:str=" ", color:str=""):
        self.val = val
        self.set_color(color)

    def debug_string(self):
        s = f"{self.val}"
        return f"{DEBUG_COLORS_TO_NAMES[self.color_open_tag]} {s}"
        
    def surface(self) -> str:
      """Get the surface form of the pixel"""
      # TODO raise error if printed length is not 1 .. but how to get printed length ?
      color_close_tag = COLOR_END if self.color_open_tag else ""
      return f"{self.color_open_tag}{self.val}{color_close_tag}"

    def set_value(self, val:str) -> None: 
        self.val = val

    def set_color(self, color:str) -> None: 
        """What happens if there are multiple open tags?
        We just ignore the earlier ones. but this is bad news in general.
        """
        if color:
          self.color_open_tag = get_color_open_tag(color)
        else:
          self.color_open_tag = ""

    def copy(self) -> Pixel:
      ret = Pixel()
      ret.val = self.val
      ret.color_open_tag = self.color_open_tag
      return ret
        
    def stack_on_pixel(self, other_pixel: Pixel) -> None:
      """If other_pixel is on top of this pixel, what does the pixel look like?
      Treats colored pixels as opaque.
      """

      if other_pixel.color_open_tag == "":
          if other_pixel.val == " ":
              # fully transparent pixel
              return
          else:
              # new pixel keeps botom pixel's color but top pixel's value
              self.val = other_pixel.val
      else:
        # we are stacking on a colored pixel; it is fully opaque.
        self.val = other_pixel.val
        self.color_open_tag =  other_pixel.color_open_tag
      


# BAHAHA this is a forward-declaration so that I can use type annotations!
class Image(): pass
class Image():
    def __init__(self, from_string=None, height=None, width=None, name=None, color="none"):
        assert (from_string is not None) != (height or width)

        if width and not height:
          raise ValueError("No can do 0-height images (yet)")

        if name:
            self.name = name
            register_name(self.name)
        else:
            self.name = register_unique_name("img")


        self.layers = []
        self.layer_unique_ids = []

        if from_string:
          self.height = None
          self.width = None
          self.add_layer_from_string(from_string, layer_name=f"{self.name}_base")
        else:
          self.height = height
          self.width = width
          self.add_transparency(layer_name=f"{self.name}_base")

        self.set_color(color)
        self.flattened = None
        self.image_has_changed_since_flattening = False

    def add_transparency(self, layer_name:str=None) -> None:
          new_pixels = [[Pixel() for i in range(self.width)] for j in range(self.height)]
          self.layers.append(new_pixels)
          if not layer_name:
              layer_name = register_unique_name("transparency")
          self.layer_unique_ids.append(layer_name)
        
    def get_top_visible_pixel(self, i:int, j:int) -> Pixel:
        # traverse the layers from top to bottom
        ret = Pixel()
        for layer in self.layers:
            ret.stack_on_pixel(layer[i][j])
        return ret

    # def pop_layer(self, layer_id = None):
    #     pass

    def expand_canvas(self, new_height: int, new_width: int) -> None:
        if new_height < self.height and new_width < self.width:
            return # nothing need be done. Image is already big enough.

        new_height = max(self.height, new_height)
        new_width = max(self.width, new_width)

        for layer_i, layer in enumerate(self.layers):
          # expand height
          n_new_cols = new_width - self.width
          n_new_rows = new_height - self.height

          # Add new cols to existing rows
          for row_i in range(len(layer)):
            new_cols = [Pixel() for _ in range(n_new_cols)]
            self.layers[layer_i][row_i] += new_cols

          # expand height by adding entirely new rows
          new_rows = [[Pixel() for new_col_i in range(new_width)] for new_row_i in range(n_new_rows)]
          self.layers[layer_i] += new_rows

        self.height = new_height
        self.width = new_width


    def print_debug(self) -> None:
        print(f"Image '{self.name}' has  {len(self.layers)} layers and shape (h={self.height}, w={self.width})")
        for i, layer in enumerate(self.layers):
          print(f"\tlayer {i} (ID={self.layer_unique_ids[i]}): (h={len(layer)}, w={len(layer[i])})")
          for row in layer:
            for pixel in row: 
              print(pixel.debug_string(), end=" | ")
            print()
    def debug_print(self) -> None:
        self.print_debug()

    def flatten(self) -> List[List[str]]:
        """Return a flattened copy of this image.
        """
        # Re-cache if the image has changed
        # Note that this is likely to be a source of bugs...
        # TODO change updating self.image_has_changed_since_flattening
        # to be a function decorator
        if self.image_has_changed_since_flattening or not self.flattened:
          out_pixels = self._copy_layer(self.layers[-1])
          for row_i in range(self.height):
              for col_j in range(self.width):
                  out_pixels[row_i][col_j] = self.get_top_visible_pixel(row_i, col_j)
          self.flattened = out_pixels
          self.image_has_changed_since_flattening = False

        return self.flattened

    def check_image_dimensions(self) -> None:
        # a debug method
        for layer_i, layer in enumerate(self.layers):
          if len(layer) != self.height:
              raise ValueError(f"Image {img.name} has height {self.height}, but layer {self.layer_unique_ids[layer_i]} (#{layer_i}) has length {len(layer)}")
          for row_i, row in enumerate(layer):
            if len(row) != self.width:
                  raise ValueError(f"Image {img.name} has width {self.width}, but row #{row_i} in layer {self.layer_unique_ids[layer_i]} (#{layer_i}) has length {len(row)}")

    #==========================================================
    #==========================================================
    # Methods that modify how the image looks
    # And thus update the cached flattened image
    # except _get_pixel, which is internal only, and drop_in_image, which calls drop_in_image_by_coordinates


    def _set_pixel(self, row_i:int, col_j:int, pixel_val:str, layer_i:int=-1, color:str=None) -> None:
        self.layers[layer_i][row_i][col_j].set_value(pixel_val)
        if color:
            self.layers[layer_i][row_i][col_j].set_color(color)
      

    def print_in_string(self, s:str, location:str="lower_right", color:str=None) -> None:
        """Make a new transparent layer and print a string on it.
        """
        n_rows_this_message_will_span = len(s) // self.width
        n_cols_in_last_row = len(s) % self.width
        if location == "lower_right":
            row_offset = (self.height - 1) - n_rows_this_message_will_span 
            col_offset = (self.width) - n_cols_in_last_row
        elif location == "upper_left":
          row_offset = 0
          col_offset = 0
        else:
          raise ValueError("Not Implemented")

        self.add_transparency()
        for row_i in range(self.height):
            for col_j in range(self.width):
                string_idx = col_j + row_i*self.width
                if string_idx >= len(s): break
                self._set_pixel(row_i + row_offset, col_j + col_offset, s[string_idx], color=color)
        self.image_has_changed_since_flattening = True


    def drop_in_image_by_coordinates(self, image: Image, upper_left_row: int, upper_left_col: int) -> None:
       assert upper_left_row >= 0 and upper_left_col >= 0
       new_height = upper_left_row + image.height
       new_width = upper_left_col + image.width
       self.expand_canvas(new_height=new_height, new_width=new_width)

       new_pixels = image.flatten()
       for row_i in range(image.height):
           for col_j in range(image.width):
               new_pixel = new_pixels[row_i][col_j]
               self.layers[-1][row_i + upper_left_row][col_j + upper_left_col].stack_on_pixel(new_pixel)
       self.image_has_changed_since_flattening = True

    def drop_in_image(self, image: Image, location:str, height_buf:int=0, width_buf:int=0) -> None:
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
 
    def stack_on_image(self, image: Image) -> None:
        #  sort of like "over_append"
        self.layers += self._copy_layers(image.layers)
        self.layer_unique_ids += image.layer_unique_ids.copy()
        # TODO: currently, uou can stack on images of different sizes, and the behavior is unclear; consider fixing, e.g.:
        # if occupant.img.width != width: raise ValueError(f"Cannot stack {occupant.name}'s image of width {occupant.img.width} into square {self.name} of width {width}")
        # if occupant.img.height != height: raise ValueError(f"Cannot stack {occupant.name}'s image of height {occupant.img.height} into square {self.name} of height {height}")
        self.image_has_changed_since_flattening = True

    def r_append(self, other_image:Image) -> None:
        # append to right
        # WARNING this method flattens all the images together and only keeps the top layer!
        # doesn't deal with layers. Therefore, only for printing.
        if self.height != other_image.height:
            raise ValueError(f"Image '{self.name}' of height {self.height} can't r_append '{other_image.name}' of height {other_image.height}")

        pixels = self.flatten()
        other_img_pixels = other_image.flatten()
        for row_i in range(self.height):
            pixels[row_i] = pixels[row_i] + other_img_pixels[row_i]
        self.layers = [pixels]
        self.width += other_image.width
        self.image_has_changed_since_flattening = True

    def u_append(self, other_image:Image) -> None:
        # append under
        # WARNING this method flattens all the images together and only keeps the top layer!
        # So it should only be used for rendering.
        pixels = self.flatten()
        if self.width != other_image.width:
            raise ValueError(f"Can't concatenate image {self.name} with shape (h={self.height}, w={self.width}) with image {other_image.name} with shape (h={other_image.height}, w={other_image.width})")
        pixels += other_image.flatten()
        self.layers = [pixels]
        self.height += other_image.height
        self.image_has_changed_since_flattening = True

    def set_color(self, color:str) -> None:
        if not self.width: return
        pixels = self.layers[-1]
        for row_i in range(self.height):
          for col_j in range(self.width):
            pixels[row_i][col_j].set_color(color)
        self.image_has_changed_since_flattening = True


    def add_layer_from_string(self, s:str, layer_name=None) -> None:
        rows = [row for row in s.split("\n") if row]

        if not self.height or not self.width:
          self.height = len(rows)
          self.width = len(rows[0])
        else:
            if self.height != len(rows):
                raise ValueError(f"cannot insert a string with {len(rows)} rows into an image with height {self.height}")
            if self.width != len(rows[0]):
                raise ValueError(f"cannot insert a string with {len(rows[0])} columnss into an image with width {self.width}")

        string_pixels = []
        for row_i in range(self.height):
            string_pixels.append([])
            if len(rows[row_i]) != self.width:
                raise ValueError(f"row {row_i} of image {self.name} has length {len(rows[row_i])}, but self.width={self.width}")
            for col_j in range(self.width):
                string_pixels[row_i].append(Pixel(rows[row_i][col_j: col_j+1]))
        self.layers.append(string_pixels)
        if not layer_name:
            layer_name = register_unique_name("img_from_string")
        self.layer_unique_ids.append(layer_name)
        self.image_has_changed_since_flattening = True


    def set_all_pixels_to_value(self, v:str) -> None:
        # TODO consider deprecating
        pixels = self.layers[-1]
        for row_i in range(self.height):
            for col_j in range(self.width):
                pixels[row_i][col_j].set_value(v)
        self.image_has_changed_since_flattening = True

    #==========================================================
    #==========================================================
    # other

    def rasterize(self) -> str:
        pixels = self.flatten()
        printstring = ""
        for row_i in range(self.height):
            for col_j in range(self.width):
                printstring += pixels[row_i][col_j].surface()
            printstring += "\n"
        return printstring

    def render(self) -> None:
        printstring = self.rasterize()
        print(printstring)

    def _copy_row(self, row: list) -> list:
        return [pixel.copy() for pixel in row]

    def _copy_layer(self, layer: list) -> list:
        return [self._copy_row(row) for row in layer]

    def _copy_layers(self, layers: list) -> list:
        return [self._copy_layer(layer) for layer in layers]

    def copy(self, name=None, color=None) -> Image:
        if not name: 
            name = f"{self.name}_copy_{random_string()}"
        new_image = Image(width=self.width, height=self.height, name=name)
        new_image.layers = self._copy_layers(self.layers)
        if color:
            new_image.set_color(color)
        return new_image






def wrap_collapse(images: list, width: int, height_buf:int = 0) -> Image:
    """wrap a list of images into one image:
    Input: [a, b, c, d, e, f, g]
    Output image:
     a b c 
     d e f 
     g 
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


