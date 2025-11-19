"""Projectile entities (bullets)"""
import curses

class Bullet:
    """Player's bullet"""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.char = "|"
        
    def update(self):
        self.y -= 1
        
    def is_offscreen(self):
        return self.y < 0
        
    def draw(self, stdscr, attr):
        try:
            stdscr.addstr(self.y, self.x, self.char, attr)
        except curses.error:
            pass

class EnemyBullet:
    """Enemy's bullet"""
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.char = "●"
        self.speed = 1
        
    def update(self):
        self.y += self.speed
        
    def is_offscreen(self, h):
        return self.y >= h
        
    def draw(self, stdscr, attr):
        try:
            stdscr.addstr(self.y, self.x, self.char, attr)
        except curses.error:
            pass
