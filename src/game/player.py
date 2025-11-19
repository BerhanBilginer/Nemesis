"""Player entity and controls"""
import curses

class Player:
    def __init__(self, h, w):
        self.h, self.w = h, w
        self.x = w // 2
        self.y = h - 5
        self.speed = 2
        self.ship = [
            "  ▲  ",
            " ███ ", 
            "█████",
            " █ █ "
        ]
        self.width = 5
        self.height = 4
        
    def move_left(self):
        self.x = max(2, self.x - self.speed)
        
    def move_right(self):
        self.x = min(self.w - self.width - 2, self.x + self.speed)
        
    def get_center(self):
        return self.x + self.width // 2, self.y
        
    def draw(self, stdscr, attr):
        for i, line in enumerate(self.ship):
            try:
                stdscr.addstr(self.y + i, self.x, line, attr)
            except curses.error:
                pass
                
    def get_hitbox(self):
        """Returns list of occupied coordinates for collision detection"""
        return [(self.x + dx, self.y + dy) 
                for dy in range(self.height) 
                for dx in range(self.width) 
                if self.ship[dy][dx] != ' ']
