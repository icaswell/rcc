from graphics import Image, vertical_collapse, horizontal_collapse, wrap_collapse
# from graphics_library import img_lib
# currently failing:
# test 21dropping a teal_highlight square at bottom_left, width_buf=0, height_buf=0

FROM_TEST_NUMBER = 0
TO_TEST_NUMBER = 180
CUR_TEST_NUMBER = 0


pawn_w_2p =(
" △ \n"
" ░ ")
pawn_b_2p =(
" ▲ \n"
" █ ")
crown_2p =(
"- -\n"
"   ")

crown_8p =(
"     /╚◭╝\      \n"
"  ═══╣---╠═══   \n"
"  \◄◄-----►►/   \n"
"                \n"
"                \n"
"                \n"
"                \n"
"                ")

pawn_w_8p=(
"       _        \n"
"      / \       \n"
"     /   \      \n"
"     \   /      \n"
"      | |       \n"
"     /   \      \n"
"     |___|      \n"
"                ")

pawn_b_8p=(
"       _        \n"
"      /▇\       \n"
"     /▇▇▇\      \n"
"     \▇▇▇/      \n"
"      |▇|       \n"
"     /▇▇▇\      \n"
"     |▇▇▇|      \n"
"                ")

SEC="#" + "="*79 + "\n"

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing empty canvas render")
  img = Image(height=5, width=10)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing highlighted canvas render")
  img = Image(height=5, width=10)
  img.set_color("red_highlight")
  img.render()
  
CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing highlighted width-1 canvas render")
  img = Image(height=5, width=1)
  img.set_color("red_highlight")
  img.render()
  
CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing highlighted height-1 canvas render")
  img = Image(height=1, width=10)
  img.set_color("red_highlight")
  img.render()
  
CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing 0-width canvas render")
  img = Image(height=5, width=0)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing render on image")
  img = Image(from_string=pawn_b_8p)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing render on image with highlight")
  img = Image(from_string=pawn_b_8p)
  img.set_color("blue_highlight")
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing r_append")
  img = Image(from_string=pawn_b_8p)
  imgb = Image(from_string=pawn_w_8p)
  img.r_append(imgb)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing u_append")
  img = Image(from_string=pawn_b_8p)
  imgb = Image(from_string=pawn_w_8p)
  img.u_append(imgb)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing stacking")
  img = Image(from_string=pawn_b_8p)
  crown = Image(from_string=crown_8p)
  crown.stack_on_image(img)
  crown.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing stacking and r_append (same N layers)")
  img = Image(from_string=pawn_b_8p)
  imgb = Image(from_string=pawn_w_8p)
  crown = Image(from_string=crown_8p)
  img.stack_on_image(crown)
  imgb.stack_on_image(crown)
  img.r_append(imgb)
  img.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing stacking and r_append (different N layers)")
  img = Image(from_string=pawn_b_8p)
  imgb = Image(from_string=pawn_w_8p)
  crown = Image(from_string=crown_8p)
  img.stack_on_image(crown)
  img.r_append(imgb)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing stacking and r_append (different N layers, reverse)")
  img = Image(from_string=pawn_b_8p)
  imgb = Image(from_string=pawn_w_8p)
  crown = Image(from_string=crown_8p)
  imgb.stack_on_image(crown)
  img.r_append(imgb)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing stacking uncolored crown on colored pawn")
  img = Image(from_string=pawn_b_8p)
  crown = Image(from_string=crown_8p)
  img.set_color("blue_highlight")
  img.stack_on_image(crown)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing stacking colored crown on uncolored bottom layer")
  print("(opaque color should mask imag underneath)")
  img = Image(from_string=pawn_b_8p)
  crown = Image(from_string=crown_8p)
  crown.set_color("yellow_highlight")
  img.stack_on_image(crown)
  img.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing render on images' edges, coloring and uncoloring")
  img = Image(from_string=
  "12345678\n"
  "12345678\n"
  "12345678\n"
  "12345678"
  , color="teal_highlight")
  
  print("Should be teal highlight:")
  img.render()
  
  print("Should be red highlight:")
  img.set_color("red_highlight")
  img.render()
  
  print("Should be no highlight:")
  img.set_color("none")
  img.render()

  print("Should be blue highlight:")
  img.set_color("blue_highlight")
  img.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing r_append and u_append together")
  rowa = Image(from_string=pawn_b_8p)
  rowa2 = Image(from_string=pawn_w_8p)
  rowa.r_append(rowa2)
  rowb = Image(from_string=pawn_w_8p)
  rowb2 = Image(from_string=pawn_b_8p)
  rowb.r_append(rowb2)
  rowa.u_append(rowb)
  rowa.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing r_append and u_append with colors and layers (small)")
  crown = Image(from_string=crown_2p)
  rowa = Image(from_string=pawn_b_2p)
  rowa.set_color("white_highlight")
  rowa.stack_on_image(crown)
  rowa2 = Image(from_string=pawn_w_2p)
  rowa.set_color("black_highlight")
  rowa2.stack_on_image(crown)
  rowa.r_append(rowa2)
  rowa.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing r_append and u_append with colors and layers")
  crown = Image(from_string=crown_8p)
  rowa = Image(from_string=pawn_b_8p)
  rowa.set_color("white_highlight")
  rowa.stack_on_image(crown)
  rowa2 = Image(from_string=pawn_w_8p)
  rowa2.stack_on_image(crown)
  rowa.r_append(rowa2)
  rowb = Image(from_string=pawn_w_8p)
  rowb.stack_on_image(crown)
  rowb2 = Image(from_string=pawn_b_8p)
  rowb2.set_color("white_highlight")
  rowb2.stack_on_image(crown)
  rowb.r_append(rowb2)
  rowa.u_append(rowb)
  rowa.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing resizing canvas and dropping in images by coordinate (one layer)")
  img = Image(from_string=
  "12345678\n"
  "12345678\n"
  "12345678\n"
  "12345678"
  , color="none")
  print("here is the base image:")
  img.render()
  
  to_drop = Image(from_string=
  "1234\n"
  "1234"
  , color="green_highlight")
  print("\nhere is the image to drop:")
  to_drop.render()
  
  drop_row, drop_col = 0, 1
  print(f"\ndropping at ({drop_row}, {drop_col}):") 
  img.drop_in_image(to_drop, location=(drop_row, drop_col))
  print('-'*80)
  img.render()
  print('-'*80)
  
  drop_row, drop_col = 1, 12
  print(f"\ndropping at ({drop_row}, {drop_col}):") 
  img.drop_in_image(to_drop, location=(drop_row, drop_col))
  print('-'*80)
  img.render()
  print('-'*80)
  
  drop_row, drop_col = 7, 4
  print(f"\ndropping at ({drop_row}, {drop_col}):") 
  img.drop_in_image(to_drop, location=(drop_row, drop_col))
  print('-'*80)
  img.render()
  print('-'*80)



CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing resizing canvas and dropping in images by location name (one layer)")
  img = Image(from_string=
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]\n"
  "[xxxxxxxxxxxxxxxxxx]"
  , color="none")
  print("here is the base image:")
  img.render()
  
  
  colors = ["white_highlight", "green", "teal_highlight", "flashing", "blue", "pink", "teal", "grey", "white_highlight", "black_highlight", "red_highlight", "green_highlight", "yellow_highlight", "blue_highlight", "pink_highlight", "teal_highlight", "grey_highlight"][::-1]
  cur_color=colors.pop()
  
  to_drop = Image(from_string=
  "OOO\n"
  "OOO"
  , color=cur_color)
  print("\nhere is the image to drop:")
  to_drop.render()
  
  
  drop_location="right_top"
  width_buf, height_buf = 0 , 0
  print(f"\ndropping a {cur_color} square at {drop_location}, width_buf={width_buf}, height_buf={height_buf}")
  img.drop_in_image(to_drop, location=drop_location, width_buf=width_buf, height_buf=height_buf)
  print('-'*80)
  img.render()
  print('-'*80)
  
  drop_location="right_top"
  width_buf, height_buf = -5 , 6
  cur_color=colors.pop()
  to_drop.set_color(cur_color)
  print(f"\ndropping a {cur_color} square at {drop_location}, width_buf={width_buf}, height_buf={height_buf}")
  img.drop_in_image(to_drop, location=drop_location, width_buf=width_buf, height_buf=height_buf)
  print('-'*80)
  img.render()
  print('-'*80)
  
  drop_location="bottom_left"
  width_buf, height_buf = 0 , 0
  cur_color=colors.pop()
  to_drop.set_color(cur_color)
  print(f"\ndropping a {cur_color} square at {drop_location}, width_buf={width_buf}, height_buf={height_buf}")
  img.drop_in_image(to_drop, location=drop_location, width_buf=width_buf, height_buf=height_buf)
  print('-'*80)
  img.render()
  print('-'*80)
  
  drop_location="bottom_left"
  width_buf, height_buf = 0 , -6
  cur_color=colors.pop()
  to_drop.set_color(cur_color)
  print(f"\ndropping a {cur_color} square at {drop_location}, width_buf={width_buf}, height_buf={height_buf}")
  img.drop_in_image(to_drop, location=drop_location, width_buf=width_buf, height_buf=height_buf)
  print('-'*80)
  img.render()
  print('-'*80)
  
  drop_location="bottom_left"
  width_buf, height_buf = 56 , 5
  cur_color=colors.pop()
  to_drop.set_color(cur_color)
  print(f"\ndropping a {cur_color} square at {drop_location}, width_buf={width_buf}, height_buf={height_buf}")
  img.drop_in_image(to_drop, location=drop_location, width_buf=width_buf, height_buf=height_buf)
  print('-'*80)
  img.render()
  print('-'*80)
  


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Placing small image underneath:")
  smol_teal_img = Image(from_string=
  "01\n"
  "01"
  , color="teal_highlight")
  
  smol_red_img = Image(from_string=
  "ab\n"
  "ab"
  , color="red_highlight")
  
  img = smol_teal_img.copy()
 
  print("Base image:")
  img.render()

  print(f"\ndropping red square at bottom_left, width_buf=0, height_buf=-1")
  img.drop_in_image(smol_red_img, location="bottom_left", width_buf=0, height_buf=-1)
  img.render()
 
  print(f"\ndropping red square at (2, 1)")
  img.drop_in_image_by_coordinates(smol_red_img, upper_left_row=2, upper_left_col=1)
  img.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing nested coloring tiny:")
  small_teal_img = Image(from_string=
  "0123\n"
  "0123\n"
  "0123"
  , color="teal_highlight")
  
  smol_red_img = Image(from_string=
  "ab"
  , color="red_highlight")

  img = small_teal_img.copy()
  print("Base image:")
  img.render()
  
  print("Drop red in middle:")
  img.drop_in_image_by_coordinates(smol_red_img, upper_left_row=1, upper_left_col=1)
  img.render()
 

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing nested coloring:")
  big_teal_img = Image(from_string=
  "0123456789\n"
  "0123456789\n"
  "0123456789\n"
  "0123456789\n"
  "0123456789\n"
  "0123456789\n"
  "0123456789"
  , color="teal_highlight")
  
  medium_red_img = Image(from_string=
  "abcde\n"
  "abcde\n"
  "abcde\n"
  "abcde\n"
  , color="red_highlight")
  
  medium_green_img = Image(from_string=
  "ghjkl\n"
  "ghjkl\n"
  "ghjkl\n"
  "ghjkl\n"
  , color="green_highlight")
  
  small_blue_img = Image(from_string=
  "--\n"
  "--\n"
  , color="blue_highlight")

  
  img = big_teal_img.copy()
  print("Base image:")
  img.render()
  
  print("Drop red in middle:")
  img.drop_in_image_by_coordinates(medium_red_img, upper_left_row=1, upper_left_col=2)
  img.render()
  
  print("Drop blue in middle of that:")
  img.drop_in_image_by_coordinates(small_blue_img, upper_left_row=2, upper_left_col=4)
  img.render()
  
  print("Drop green directly over red, hiding blue:")
  img.drop_in_image_by_coordinates(medium_green_img, upper_left_row=1, upper_left_col=2)
  img.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing overlapping coloring, smaller:")
  
  big_teal_img_small = Image(from_string=
  "012\n"
  "012\n"
  "012\n"
  "012"
  , color="teal_highlight")
  
  medium_red_img_small = Image(from_string=
  "ab\n"
  "ab"
  , color="red_highlight")
  
  small_blue_img_small = Image(from_string=
  "--"
  , color="blue_highlight")

  img = big_teal_img_small.copy()
  print("Base image(small):")
  img.render()
  
  print("Drop red overlapping on the right (small):")
  img.drop_in_image_by_coordinates(medium_red_img_small, upper_left_row=1, upper_left_col=2)
  img.render()
  
  print("Drop blue overlapping further right (small):")
  print("This fails because you have to keep track of were the edge of the other image was.")
  img.drop_in_image_by_coordinates(small_blue_img_small, upper_left_row=1, upper_left_col=3)
  img.render()

CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing overlapping coloring:")
  
  img = big_teal_img.copy()
  print("Base image:")
  img.render()
  
  print("Drop red overlapping on the right:")
  img.drop_in_image_by_coordinates(medium_red_img, upper_left_row=1, upper_left_col=8)
  img.render()
  
  print("Drop blue overlapping further right:")
  print("This fails because you have to keep track of were the edge of the other image was.")
  img.drop_in_image_by_coordinates(small_blue_img, upper_left_row=2, upper_left_col=12)
  img.render()
  
  print("Drop blue in middle of teal-red boundary:")
  img.drop_in_image_by_coordinates(small_blue_img, upper_left_row=4, upper_left_col=9)
  img.render()


CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  print(f"{SEC}# TEST {CUR_TEST_NUMBER}: Testing color edges")
  
  img = big_teal_img.copy()
  print("Base image:")
  img.render()
  
  print("Put red image aligned with the lefthand side:")
  img.drop_in_image_by_coordinates(medium_red_img, upper_left_row=0, upper_left_col=0)
  img.render()
  
  print("Put blue image aligned with the lefthand side with vertical overlap:")
  img.drop_in_image_by_coordinates(small_blue_img, upper_left_row=2, upper_left_col=0)
  img.render()



  
CUR_TEST_NUMBER += 1
if FROM_TEST_NUMBER <= CUR_TEST_NUMBER <= TO_TEST_NUMBER:
  images_to_wrap = [
          Image(from_string="012\n012\n012", color="green_highlight"),
          Image(from_string="012\n012\n012\n012", color="teal_highlight"),
          Image(height=4, width=0),
          Image(from_string="ab\nab", color="red_highlight"),
          Image(from_string="----", color="blue_highlight"),
          Image(from_string="qwerty\nqwerty", color="grey_highlight"),
          Image(from_string="•", color="yellow_highlight"),
          Image(from_string="012\n012\n012\n012", color="pink_highlight")
          ]
  
  print("Here are the eight images we'll be testing with:")
  for i, img in enumerate(images_to_wrap):
      print(f"\nImage {i}:")
      print('-'*80)
      img.render()
      print('-'*80)
  
  
  print("Horizontal collapse the first four images:")
  print(horizontal_collapse(images_to_wrap[0:4]).rasterize())
  print("And the next four:")
  print(horizontal_collapse(images_to_wrap[4:8]).rasterize())
  
  print("Vertical collapse the first four images:")
  print(vertical_collapse(images_to_wrap[0:4]).rasterize())
  print("And the next four:")
  print(vertical_collapse(images_to_wrap[4:8]).rasterize())
  print("And the next four, but this time with a vertical height buffer of 1:")
  print(vertical_collapse(images_to_wrap[4:8], height_buf=1).rasterize())
  print("And the next four, but this time with a vertical height buffer of -1. This will obscure some images entirely:")
  print(vertical_collapse(images_to_wrap[4:8], height_buf=-1).rasterize())
  
  width=45; height_buf=0
  print(f"Now wrap-collapse everything, with width={width}, height_buf={height_buf}:")
  wrap_collapse(images=images_to_wrap, width=width, height_buf=height_buf).render()
  
  
  width=20; height_buf=0
  print(f"Now wrap-collapse everything, with width={width}, height_buf={height_buf}:")
  wrap_collapse(images=images_to_wrap, width=width, height_buf=height_buf).render()
  
  
  width=8; height_buf=0
  print(f"Now wrap-collapse everything, with width={width}, height_buf={height_buf}:")
  wrap_collapse(images=images_to_wrap, width=width, height_buf=height_buf).render()
  
  
  width=8; height_buf=-1
  print(f"Now wrap-collapse everything, with width={width}, height_buf={height_buf}:")
  wrap_collapse(images=images_to_wrap, width=width, height_buf=height_buf).render()

