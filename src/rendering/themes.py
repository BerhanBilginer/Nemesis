"""Color themes and visual styling"""
import curses

THEMES = {
    "neo": (curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_WHITE),
    "retro": (curses.COLOR_YELLOW, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_WHITE),
    "mono": (curses.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_WHITE),
    "matrix": (curses.COLOR_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN, curses.COLOR_WHITE),
    "sunset": (curses.COLOR_MAGENTA, curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_WHITE),
    "dark": (curses.COLOR_WHITE, curses.COLOR_BLUE, curses.COLOR_WHITE, curses.COLOR_BLACK),
}

def init_colors(theme_name="neo"):
    """Initialize color pairs for the given theme"""
    try:
        curses.start_color()
        curses.use_default_colors()
    except curses.error:
        pass
    
    bg_color = curses.COLOR_BLACK
    fg_primary, fg_dim, acc1, acc2 = THEMES.get(theme_name, list(THEMES.values())[0])
    
    curses.init_pair(1, fg_primary, bg_color)
    curses.init_pair(2, fg_dim, bg_color)
    curses.init_pair(3, acc1, bg_color)
    curses.init_pair(4, acc2, bg_color)
    curses.init_pair(5, fg_primary, bg_color)
    curses.init_pair(6, -1, bg_color)
    curses.init_pair(7, curses.COLOR_BLACK, bg_color)
    
    return (
        curses.color_pair(1) | curses.A_BOLD,    # attr_primary
        curses.color_pair(2) | curses.A_DIM,     # attr_dim
        curses.color_pair(3) | curses.A_BOLD,    # attr_acc
        curses.color_pair(4),                     # attr_alt
        curses.color_pair(6)                      # attr_bg
    )
