# Block Elements (U+2580 to U+259F)
# ▀ ▁ ▂ ▃ ▄ ▅ ▆ ▇ █ ▉ ▊ ▋ ▌ ▍ ▎ ▏ ▐ ░ ▒ ▓ ▔ ▕ ▖ ▗ ▘ ▙ ▚ ▛ ▜ ▝ ▞ ▟
# 
# Geometric Shapes (U+25A0 to U+25FF)
# ■ □ ▢ ▣ ▤ ▥ ▦ ▧ ▨ ▩ ▪ ▫ ▬ ▭ ▮ ▯ ▰ ▱ ▲ △ ▴ ▵ ▶ ▷ ▸ ▹ ► ▻ ▼ ▽ ▾ ▿ ◀ ◁ ◂ ◃ ◄ ◅ ◆ ◇ ◈ ◉ ◊ ○ ◌ ◍ ◎ ● ◐ ◑ ◒ ◓ ◔ ◕ ◖ ◗ ◘ ◙ ◚ ◛ ◜ ◝ ◞ ◟ ◠ ◡ ◢ ◣ ◤ ◥ ◦ ◧ ◨ ◩ ◪ ◫ ◬ ◭ ◮ ◯ ◰ ◱ ◲ ◳ ◴ ◵ ◶ ◷ ◸ ◹ ◺ ◻ ◼ ◽ ◾ ◿ 
template_8p =(
"                \n"
"                \n"
"                \n"
"                \n"
"                \n"
"                \n"
"                \n"
"                ")

crown_8p =(
"     /╚◭╝\      \n"
"  ═══╣   ╠═══   \n"
"  \◄◄     ►►/   \n"
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
pawn_b_8p="""
       _        
      /▇\       
     /▇▇▇\      
     \▇▇▇/      
      |▇|       
     /▇▇▇\      
     |▇▇▇|      
                """



knight_w_8p =(
"                \n"
"      |\_       \n"
"     /  .\_     \n"
"    |   ___)    \n"
"    |    \      \n"
"    |  =  |     \n"
"    /_____\     \n"
"   [_______]    "
)

knight_b_8p =(
"                \n"
"      ◣__       \n"
"     /▇▇◉\_     \n"
"     ▇▇▇▇▇▇)    \n"
"     ▇▇▇▇\      \n"
"     ▇▇▇▇▇      \n"
"    /▇▇▇▇▇\     \n"
"   [▇▇▇▇▇▇▇]    "
)

bishop_w_8p =(
"                \n"
"                \n"
"                \n"
" bishop_w       \n"
"                \n"
"                \n"
"                \n"
"                ")
bishop_b_8p =(
"                \n"
"                \n"
"                \n"
" bishop_b       \n"
"                \n"
"                \n"
"                \n"
"                ")

rook_w_8p =(
"                \n"
"   | T T T |    \n"
"   \       /    \n"
"    |     |     \n"
"    |     |     \n"
"   /       \    \n"
"   |_______|    \n"
"                ")
rook_b_8p =(
"                \n"
"                \n"
"                \n"
" rook_b         \n"
"                \n"
"                \n"
"                \n"
"                ")
queen_w_8p =(
"                \n"
"                \n"
"                \n"
" queen_w        \n"
"                \n"
"                \n"
"                \n"
"                ")
queen_b_8p =(
"                \n"
"                \n"
"                \n"
" queen_b        \n"
"                \n"
"                \n"
"                \n"
"                ")
king_w_8p =(
"                \n"
"                \n"
"                \n"
" king_w         \n"
"                \n"
"                \n"
"                \n"
"                ")
king_b_8p =(
"                \n"
"                \n"
"                \n"
" king_b         \n"
"                \n"
"                \n"
"                \n"
"                ")

STANDARD_PIECES = {
        "pawn": {"White": pawn_w_8p, "Black": pawn_b_8p},
        "knight": {"White": knight_w_8p, "Black": knight_b_8p},
        "bishop": {"White": bishop_w_8p, "Black": bishop_b_8p},
        "rook": {"White": rook_w_8p, "Black": rook_b_8p},
        "queen": {"White": queen_w_8p, "Black": queen_b_8p},
        "king": {"White": king_w_8p, "Black": king_b_8p},
}



