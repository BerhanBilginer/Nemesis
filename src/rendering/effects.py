"""Visual effects for background animations"""
import random
import math
import curses

class StarField:
    def __init__(self, count=220, seed=42):
        self.count = count
        random.seed(seed)
        self.stars = []
    
    def rebuild(self, h, w):
        self.stars = []
        chars = ['.', '·', '•', '∙']
        for _ in range(self.count):
            y = random.randint(0, max(0, h - 1))
            x = random.randint(0, max(0, w - 1))
            sp = random.uniform(0.05, 0.4)
            ch = random.choice(chars)
            self.stars.append([y, x, sp, ch, random.random() * 2 * math.pi])
    
    def draw(self, stdscr, h, w, t, attr_dim, attr_bold):
        for y, x, spd, ch, ph in self.stars:
            dy = math.sin(t * spd + ph) * 0.1
            dx = math.cos(t * spd + ph) * 0.2
            yy = int(max(0, min(h - 1, y + dy)))
            xx = int(max(0, min(w - 1, x + dx)))
            a = attr_dim if (int((t * 2 + ph * 3) % 3) != 0) else attr_bold
            try:
                stdscr.addstr(yy, xx, ch, a)
            except curses.error:
                pass

class MatrixRain:
    def __init__(self, density=0.08, seed=123):
        random.seed(seed)
        self.density = density
        self.columns = []
    
    def rebuild(self, h, w):
        self.columns = []
        for x in range(w):
            if random.random() < self.density:
                L = random.randint(4, max(5, h // 2))
                head = random.randint(-h, 0)
                self.columns.append({
                    'x': x,
                    'len': L,
                    'head': head,
                    'spd': random.uniform(0.3, 1.2)
                })
    
    def draw(self, stdscr, h, w, t, attr_dim, attr_bold):
        for col in self.columns:
            col['head'] += col['spd']
            head = int(col['head'])
            for i in range(col['len']):
                y = head - i
                if 0 <= y < h:
                    ch = random.choice("0123456789abcdefghijklmnopqrstuvwxyz")
                    attr = attr_bold if i == 0 else attr_dim
                    try:
                        stdscr.addstr(y, col['x'], ch, attr)
                    except curses.error:
                        pass
            if head - col['len'] > h:
                col['head'] = random.randint(-h, 0)
                col['len'] = random.randint(4, max(5, h // 2))
                col['spd'] = random.uniform(0.3, 1.2)

class Snow:
    def __init__(self, flakes=180):
        self.flakes = flakes
        self.s = []
    
    def rebuild(self, h, w):
        self.s = [[random.randint(-h, 0), random.randint(0, w - 1), 
                   random.uniform(0.1, 0.6)] for _ in range(self.flakes)]
    
    def draw(self, stdscr, h, w, t, attr_dim, attr_bold):
        for fl in self.s:
            fl[0] += fl[2]
            y = int(fl[0])
            x = int(fl[1] + math.sin(t * 0.8 + fl[1] * 0.1))
            if y >= h:
                fl[0] = random.randint(-h // 2, 0)
            if 0 <= y < h and 0 <= x < w:
                try:
                    stdscr.addstr(y, x, '*', attr_dim)
                except curses.error:
                    pass

class Rain:
    def __init__(self, drops=220):
        self.drops = drops
        self.d = []
    
    def rebuild(self, h, w):
        self.d = [[random.randint(-h, 0), random.randint(0, w - 1), 
                   random.uniform(0.6, 1.4)] for _ in range(self.drops)]
    
    def draw(self, stdscr, h, w, t, attr_dim, attr_bold):
        for dr in self.d:
            dr[0] += dr[2]
            y = int(dr[0])
            x = dr[1]
            if y >= h:
                dr[0] = random.randint(-h // 3, 0)
            if 0 <= y < h and 0 <= x < w:
                try:
                    stdscr.addstr(y, x, '|', attr_dim)
                except curses.error:
                    pass

class Bubbles:
    def __init__(self, count=120):
        self.count = count
        self.b = []
    
    def rebuild(self, h, w):
        self.b = [[random.randint(0, h - 1), random.randint(0, w - 1), 
                   random.uniform(0.05, 0.25)] for _ in range(self.count)]
    
    def draw(self, stdscr, h, w, t, attr_dim, attr_bold):
        for bb in self.b:
            bb[0] -= bb[2]
            y = int(bb[0])
            x = int(bb[1] + math.sin(t * 0.8 + bb[1] * 0.05))
            if y < 0:
                bb[0] = h - 1
            if 0 <= y < h and 0 <= x < w:
                try:
                    stdscr.addstr(y, x, 'o', attr_dim)
                except curses.error:
                    pass

class Noise:
    def draw(self, stdscr, h, w, t, attr_dim, attr_bold):
        for _ in range((h * w) // 200):
            y = random.randint(0, h - 1)
            x = random.randint(0, w - 1)
            try:
                stdscr.addstr(y, x, '.', attr_dim)
            except curses.error:
                pass

BG_EFFECTS = {
    "stars": StarField,
    "darkstars": StarField,
    "matrix": MatrixRain,
    "snow": Snow,
    "rain": Rain,
    "bubbles": Bubbles,
    "noise": Noise
}
