from graphics import Image
# from graphics_library import img_lib
import graphics_library as img_lib

SEC="#" + "="*79 + "\n"
#=================================================================
print(f"{SEC}Testing empty canvas render")
img = Image(height=5, width=10)
img.render()

#=================================================================
print(f"{SEC}Testing highlighted canvas render")
img = Image(height=5, width=10)
img.set_color("red_highlight")
img.render()


#=================================================================
print(f"{SEC}Testing highlighted width-1 canvas render")
img = Image(height=5, width=1)
img.set_color("red_highlight")
img.render()

#=================================================================
print(f"{SEC}Testing highlighted height-1 canvas render")
img = Image(height=1, width=10)
img.set_color("red_highlight")
img.render()

#=================================================================
print(f"{SEC}Testing 0-width canvas render")
img = Image(height=5, width=0)
img.render()

#=================================================================
print(f"{SEC}Testing render on image")
img = Image(from_string=img_lib.pawn_b_8p)
img.render()

#=================================================================
print(f"{SEC}Testing render on image with highlight")
img = Image(from_string=img_lib.pawn_b_8p)
img.set_color("red_highlight")
img.render()

#=================================================================
print(f"{SEC}Testing r_append")
img = Image(from_string=img_lib.pawn_b_8p)
imgb = Image(from_string=img_lib.pawn_w_8p)
img.r_append(imgb)
img.render()

#=================================================================
print(f"{SEC}Testing u_append")
img = Image(from_string=img_lib.pawn_b_8p)
imgb = Image(from_string=img_lib.pawn_w_8p)
img.u_append(imgb)
img.render()

#=================================================================
print(f"{SEC}Testing stacking")
img = Image(from_string=img_lib.pawn_b_8p)
crown = Image(from_string=img_lib.crown_8p)
crown.stack_on_image(img)
crown.render()

#=================================================================
print(f"{SEC}Testing stacking and r_append (same N layers)")
img = Image(from_string=img_lib.pawn_b_8p)
imgb = Image(from_string=img_lib.pawn_w_8p)
crown = Image(from_string=img_lib.crown_8p)
img.stack_on_image(crown)
imgb.stack_on_image(crown)
img.r_append(imgb)
img.render()

#=================================================================
print(f"{SEC}Testing stacking and r_append (different N layers)")
img = Image(from_string=img_lib.pawn_b_8p)
imgb = Image(from_string=img_lib.pawn_w_8p)
crown = Image(from_string=img_lib.crown_8p)
img.stack_on_image(crown)
img.r_append(imgb)
img.render()

#=================================================================
print(f"{SEC}Testing stacking and r_append (different N layers, reverse)")
img = Image(from_string=img_lib.pawn_b_8p)
imgb = Image(from_string=img_lib.pawn_w_8p)
crown = Image(from_string=img_lib.crown_8p)
imgb.stack_on_image(crown)
img.r_append(imgb)
img.render()

#=================================================================
print(f"{SEC}Testing stacking and colored bottom layer")
img = Image(from_string=img_lib.pawn_b_8p)
crown = Image(from_string=img_lib.crown_8p)
img.set_color("blue_highlight")
img.stack_on_image(crown)
img.render()

#=================================================================
print(f"{SEC}Testing stacking and colored top layer")
img = Image(from_string=img_lib.pawn_b_8p)
crown = Image(from_string=img_lib.crown_8p)
crown.set_color("yellow_highlight")
img.stack_on_image(crown)
img.render()

#=================================================================
print(f"{SEC}Testing stacking and colored both layers")
img = Image(from_string=img_lib.pawn_b_8p)
crown = Image(from_string=img_lib.crown_8p)
crown.set_color("yellow_highlight")
img.set_color("blue_highlight")
img.stack_on_image(crown)
img.render()



#=================================================================
print(f"{SEC}Testing render on images' edges, coloring and uncoloring")
img = Image(from_string=
"12345678\n"
"12345678\n"
"12345678\n"
"12345678"
, color="teal_highlight")
img.render()
img.set_color("red_highlight")
img.render()
img.set_color("none")
img.render()
img.set_color("blue_highlight")
img.render()


#=================================================================
print(f"{SEC}Testing r_append and u_append together")
rowa = Image(from_string=img_lib.pawn_b_8p)
rowa2 = Image(from_string=img_lib.pawn_w_8p)
rowa.r_append(rowa2)
rowb = Image(from_string=img_lib.pawn_w_8p)
rowb2 = Image(from_string=img_lib.pawn_b_8p)
rowb.r_append(rowb2)
rowa.u_append(rowb)
rowa.render()

#=================================================================
print(f"{SEC}Testing r_append and u_append with colors and layers")
crown = Image(from_string=img_lib.crown_8p)
rowa = Image(from_string=img_lib.pawn_b_8p)
rowa.set_color("white_highlight")
rowa.stack_on_image(crown)
rowa2 = Image(from_string=img_lib.pawn_w_8p)
rowa2.stack_on_image(crown)
rowa.r_append(rowa2)
rowb = Image(from_string=img_lib.pawn_w_8p)
rowb.stack_on_image(crown)
rowb2 = Image(from_string=img_lib.pawn_b_8p)
rowb2.set_color("white_highlight")
rowb2.stack_on_image(crown)
rowb.r_append(rowb2)
rowa.u_append(rowb)
rowa.render()


#=================================================================
print(f"{SEC}Testing resizing canvas and dropping in images by coordinate (one layer)")
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



#=================================================================
print(f"{SEC}Testing resizing canvas and dropping in images by location name (one layer)")
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


colors = ["red", "green", "teal_highlight", "flashing", "blue", "pink", "teal", "grey", "white_highlight", "black_highlight", "red_highlight", "green_highlight", "yellow_highlight", "blue_highlight", "pink_highlight", "teal_highlight", "grey_highlight"][::-1]
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



