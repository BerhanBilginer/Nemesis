#!/usr/bin/env python3
import argparse, curses, time, math, re, random, shutil, subprocess

BIG_DIGITS = {
    '0': [" ██████ ","██    ██","██    ██","██    ██"," ██████ "],
    '1': ["   ██   ","  ███   ","   ██   ","   ██   "," ██████ "],
    '2': [" ██████ ","██    ██","    ███ ","  ███   ","████████"],
    '3': [" ██████ ","     ██ ","  █████ ","     ██ "," ██████ "],
    '4': ["██   ██ ","██   ██ ","████████","     ██ ","     ██ "],
    '5': ["████████","██      ","███████ ","     ██ ","██████  "],
    '6': [" ██████ ","██      ","███████ ","██    ██"," ██████ "],
    '7': ["████████","     ██ ","    ██  ","   ██   ","   ██   "],
    '8': [" ██████ ","██    ██"," ██████ ","██    ██"," ██████ "],
    '9': [" ██████ ","██    ██"," ███████","     ██ "," █████  "],
    ':': ["   "," ██","   "," ██","   "],
}

THEMES = {
    "neo": (curses.COLOR_CYAN, curses.COLOR_BLUE, curses.COLOR_MAGENTA, curses.COLOR_WHITE),
    "retro": (curses.COLOR_YELLOW, curses.COLOR_GREEN, curses.COLOR_RED, curses.COLOR_WHITE),
    "mono": (curses.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_WHITE),
    "matrix": (curses.COLOR_GREEN, curses.COLOR_BLACK, curses.COLOR_GREEN, curses.COLOR_WHITE),
    "sunset": (curses.COLOR_MAGENTA, curses.COLOR_RED, curses.COLOR_YELLOW, curses.COLOR_WHITE),
    "dark": (curses.COLOR_WHITE, curses.COLOR_BLUE, curses.COLOR_WHITE, curses.COLOR_BLACK),
}

BG_LIST = ["stars","darkstars","matrix","snow","rain","bubbles","noise"]

def parse_duration(text: str) -> int:
    text = text.strip().lower()
    if re.match(r"^\d+$", text): return int(text)
    if re.match(r"^\d+:\d{2}$", text):
        m, s = text.split(":"); return int(m)*60 + int(s)
    total = 0
    for amount, unit in re.findall(r"(\d+)\s*([hms])", text):
        val = int(amount)
        total += val * (3600 if unit=='h' else 60 if unit=='m' else 1)
    if total > 0: return total
    raise ValueError("Invalid duration")

def fmt_time(sec: int) -> str:
    if sec < 0: sec = 0
    m, s = divmod(sec, 60); return f"{m:02d}:{s:02d}"

def have_cbonsai(): return shutil.which("cbonsai") is not None
def show_bonsai():
    try:
        if have_cbonsai(): subprocess.run(["cbonsai","-l","-t","0.06","-p"], check=False)
        else: print(ASCII_BONSAI)
    except Exception: print(ASCII_BONSAI)

def notify(title, body):
    try: subprocess.run(["notify-send", title, body], check=False)
    except Exception: pass

def beep(do=True):
    if not do: return
    try: subprocess.run(["spd-say","Timer complete"], check=False)
    except Exception: pass
    print("\a", end="", flush=True)

def center_coords(H,W,h,w): return max((H-h)//2,0), max((W-w)//2,0)

def draw_big_time(stdscr, text, attr):
    rows=5; lines=[""]*rows
    for ch in text:
        glyph = BIG_DIGITS.get(ch, BIG_DIGITS['0']); pad="  "
        for r in range(rows): lines[r]+=glyph[r]+pad
    box_h=rows; box_w=max(len(l) for l in lines)
    H,W = stdscr.getmaxyx(); y0,x0 = center_coords(H,W,box_h,box_w)
    for i,l in enumerate(lines):
        try: stdscr.addstr(y0+i, x0, l, attr)
        except curses.error: pass
    return (y0,x0,box_h,box_w)

def draw_progress(stdscr, frac, y, w, attr_dim, attr_bold):
    frac=max(0.0,min(1.0,frac)); width=max(w-6,10)
    try: stdscr.addstr(y,2,"["+ " "*width +"]", attr_dim)
    except curses.error: return
    pos=int(frac*(width-1))
    for dx,attr in [(-1,attr_dim),(0,attr_bold),(1,attr_dim)]:
        p=max(0,min(width-1,pos+dx))
        try: stdscr.addstr(y,3+p,"█",attr)
        except curses.error: pass

class StarField:
    def __init__(self,count=220,seed=42):
        self.count=count; random.seed(seed); self.stars=[]
    def rebuild(self,h,w):
        self.stars=[]; chars=['.','·','•','∙']
        for _ in range(self.count):
            y=random.randint(0,max(0,h-1)); x=random.randint(0,max(0,w-1))
            sp=random.uniform(0.05,0.4); ch=random.choice(chars)
            self.stars.append([y,x,sp,ch,random.random()*2*math.pi])
    def draw(self,stdscr,h,w,t,attr_dim,attr_bold):
        for y,x,spd,ch,ph in self.stars:
            dy=math.sin(t*spd+ph)*0.1; dx=math.cos(t*spd+ph)*0.2
            yy=int(max(0,min(h-1,y+dy))); xx=int(max(0,min(w-1,x+dx)))
            a=attr_dim if (int((t*2+ph*3)%3)!=0) else attr_bold
            try: stdscr.addstr(yy,xx,ch,a)
            except curses.error: pass

class MatrixRain:
    def __init__(self,density=0.08,seed=123):
        random.seed(seed); self.density=density; self.columns=[]
    def rebuild(self,h,w):
        self.columns=[]
        for x in range(w):
            if random.random()<self.density:
                L=random.randint(4,max(5,h//2)); head=random.randint(-h,0)
                self.columns.append({'x':x,'len':L,'head':head,'spd':random.uniform(0.3,1.2)})
    def draw(self,stdscr,h,w,t,attr_dim,attr_bold):
        for col in self.columns:
            col['head']+=col['spd']; head=int(col['head'])
            for i in range(col['len']):
                y=head-i
                if 0<=y<h:
                    ch=random.choice("0123456789abcdefghijklmnopqrstuvwxyz")
                    attr=attr_bold if i==0 else attr_dim
                    try: stdscr.addstr(y,col['x'],ch,attr)
                    except curses.error: pass
            if head-col['len']>h:
                col['head']=random.randint(-h,0); col['len']=random.randint(4,max(5,h//2)); col['spd']=random.uniform(0.3,1.2)

class Snow:
    def __init__(self,flakes=180): self.flakes=flakes; self.s=[]
    def rebuild(self,h,w): self.s=[[random.randint(-h,0),random.randint(0,w-1),random.uniform(0.1,0.6)] for _ in range(self.flakes)]
    def draw(self,stdscr,h,w,t,attr_dim,attr_bold):
        for fl in self.s:
            fl[0]+=fl[2]
            y=int(fl[0]); x=int(fl[1]+math.sin(t*0.8+fl[1]*0.1))
            if y>=h: fl[0]=random.randint(-h//2,0)
            if 0<=y<h and 0<=x<w:
                try: stdscr.addstr(y,x,'*',attr_dim)
                except curses.error: pass

class Rain:
    def __init__(self,drops=220): self.drops=drops; self.d=[]
    def rebuild(self,h,w): self.d=[[random.randint(-h,0),random.randint(0,w-1),random.uniform(0.6,1.4)] for _ in range(self.drops)]
    def draw(self,stdscr,h,w,t,attr_dim,attr_bold):
        for dr in self.d:
            dr[0]+=dr[2]; y=int(dr[0]); x=dr[1]
            if y>=h: dr[0]=random.randint(-h//3,0)
            if 0<=y<h and 0<=x<w:
                try: stdscr.addstr(y,x,'|',attr_dim)
                except curses.error: pass

class Bubbles:
    def __init__(self,count=120): self.count=count; self.b=[]
    def rebuild(self,h,w): self.b=[[random.randint(0,h-1),random.randint(0,w-1),random.uniform(0.05,0.25)] for _ in range(self.count)]
    def draw(self,stdscr,h,w,t,attr_dim,attr_bold):
        for bb in self.b:
            bb[0]-=bb[2]
            y=int(bb[0]); x=int(bb[1]+math.sin(t*0.8+bb[1]*0.05))
            if y<0: bb[0]=h-1
            if 0<=y<h and 0<=x<w:
                try: stdscr.addstr(y,x,'o',attr_dim)
                except curses.error: pass

class Noise:
    def draw(self,stdscr,h,w,t,attr_dim,attr_bold):
        for _ in range((h*w)//200):
            y=random.randint(0,h-1); x=random.randint(0,w-1)
            try: stdscr.addstr(y,x,'.',attr_dim)
            except curses.error: pass


def init_colors(theme_name):
    try:
        curses.start_color(); curses.use_default_colors()
    except curses.error: pass
    
    # Define dark gray/blue background color
    # Using black as base for a very dark background
    bg_color = curses.COLOR_BLACK
    
    fg_primary, fg_dim, acc1, acc2 = THEMES.get(theme_name, list(THEMES.values())[0])
    curses.init_pair(1, fg_primary, bg_color)
    curses.init_pair(2, fg_dim, bg_color)
    curses.init_pair(3, acc1, bg_color)
    curses.init_pair(4, acc2, bg_color)
    curses.init_pair(5, fg_primary, bg_color)   # for dark fg on colored bg
    curses.init_pair(6, -1, bg_color)  # default fg with colored bg
    curses.init_pair(7, curses.COLOR_BLACK, bg_color)  # black text on colored bg
    return (curses.color_pair(1)|curses.A_BOLD,
            curses.color_pair(2)|curses.A_DIM,
            curses.color_pair(3)|curses.A_BOLD,
            curses.color_pair(4),
            curses.color_pair(6))

def button(stdscr,y,x,label,attr_box,attr_text):
    w=len(label)+4
    try:
        stdscr.addstr(y,x,"┌"+"─"*(w-2)+"┐",attr_box)
        stdscr.addstr(y+1,x,"│ "+label+" │",attr_box)
        stdscr.addstr(y+1,x+2,label,attr_text)
        stdscr.addstr(y+2,x,"└"+"─"*(w-2)+"┘",attr_box)
    except curses.error: pass
    return (y,x,y+2,x+w-1)

def inside(rect,my,mx):
    y1,x1,y2,x2=rect; return y1<=my<=y2 and x1<=mx<=x2

def app(stdscr,total_seconds,title="FancyTimer",do_notify=True,do_beep_flag=True,bg="stars",theme="neo"):
    curses.curs_set(0); stdscr.nodelay(True); stdscr.timeout(50); curses.mousemask(curses.ALL_MOUSE_EVENTS)
    start_total=total_seconds; start_time=time.time(); paused=False; pause_acc=0.0; pause_start=0.0
    attr_primary,attr_dim,attr_acc,attr_alt,attr_bg = init_colors(theme)

    # Set background color once to avoid flickering
    stdscr.bkgd(' ', attr_bg)

    stars=StarField(); matrix=MatrixRain(); snow=Snow(); rain=Rain(); bubbles=Bubbles(); noise=Noise()
    last_size=(-1,-1)

    while True:
        now=time.time()
        if paused:
            # When paused, freeze elapsed time at the pause point
            elapsed = pause_start - start_time - pause_acc
        else:
            # When running, calculate elapsed time normally
            elapsed = now - start_time - pause_acc
        
        remaining=max(0,int(round(total_seconds-elapsed)))
        frac=(total_seconds-elapsed)/max(total_seconds,0.00001); frac=max(0.0,min(1.0,frac))

        # Use erase instead of clear to reduce flicker
        stdscr.erase()
        H,W=stdscr.getmaxyx()

        if (H,W)!=last_size:
            stars.rebuild(H,W); matrix.rebuild(H,W); snow.rebuild(H,W); rain.rebuild(H,W); bubbles.rebuild(H,W)
            last_size=(H,W)

        if bg=="stars":
            stars.draw(stdscr,H,W,now,attr_dim,attr_primary)
        elif bg=="darkstars":
            old=stars.count; stars.count=max(80,old//2); stars.rebuild(H,W)
            stars.draw(stdscr,H,W,now,attr_dim,attr_dim); stars.count=old
        elif bg=="matrix": matrix.draw(stdscr,H,W,now,attr_dim,attr_primary)
        elif bg=="snow":   snow.draw(stdscr,H,W,now,attr_dim,attr_primary)
        elif bg=="rain":   rain.draw(stdscr,H,W,now,attr_dim,attr_primary)
        elif bg=="bubbles":bubbles.draw(stdscr,H,W,now,attr_dim,attr_primary)
        elif bg=="noise":  noise.draw(stdscr,H,W,now,attr_dim,attr_primary)

        header=f"{title}  •  Space/P pause  R reset  +/- ±60s  S +5m  T theme  B bg  Q quit"
        try: stdscr.addstr(1, max(2,(W-len(header))//2), header, attr_dim)
        except curses.error: pass

        y0,x0,bh,bw = draw_big_time(stdscr, fmt_time(remaining), attr_primary)
        bounce=(math.sin(now*2.0)+1.0)/2.0
        draw_progress(stdscr, bounce if paused else 1.0-frac, y0+bh+2, W, attr_dim, attr_acc)

        btn_y=max(3,y0-6); bx=4; rects={}
        rects["start"]=button(stdscr,btn_y,bx,"Start" if paused else "Pause",attr_alt,attr_primary); bx+=len("Start")+8
        rects["reset"]=button(stdscr,btn_y,bx,"Reset",attr_alt,attr_primary); bx+=len("Reset")+8
        rects["plus"]= button(stdscr,btn_y,bx,"+1m",attr_alt,attr_primary); bx+=len("+1m")+8
        rects["minus"]=button(stdscr,btn_y,bx,"-1m",attr_alt,attr_primary); bx+=len("-1m")+8
        rects["theme"]=button(stdscr,btn_y,bx,"Theme",attr_alt,attr_primary); bx+=len("Theme")+8
        rects["bg"]=   button(stdscr,btn_y,bx,"BG",attr_alt,attr_primary); bx+=len("BG")+8

        status="PAUSED" if paused else "RUNNING"
        footer=f"{status} • Remaining: {fmt_time(remaining)} • Total: {fmt_time(start_total)} • Theme: {theme} • BG: {bg}"
        try: stdscr.addstr(H-2, max(2,(W-len(footer))//2), footer, attr_dim)
        except curses.error: pass

        stdscr.refresh()

        try: ch=stdscr.getch()
        except Exception: ch=-1

        if ch==curses.KEY_MOUSE:
            try:
                _,mx,my,_,bstate=curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED:
                    if inside(rects["start"],my,mx):
                        if paused: 
                            pause_acc += time.time()-pause_start
                            paused=False
                        else: 
                            pause_start=time.time()
                            paused=True
                    elif inside(rects["reset"],my,mx):
                        start_time=time.time(); pause_acc=0.0; paused=False; total_seconds=start_total
                    elif inside(rects["plus"],my,mx):
                        total_seconds += 60; start_total += 60
                    elif inside(rects["minus"],my,mx):
                        total_seconds=max(0,total_seconds-60); start_total=max(0,start_total-60)
                    elif inside(rects["theme"],my,mx):
                        names=list(THEMES.keys()); i=names.index(theme); theme=names[(i+1)%len(names)]
                        attr_primary,attr_dim,attr_acc,attr_alt,attr_bg = init_colors(theme)
                    elif inside(rects["bg"],my,mx):
                        i=BG_LIST.index(bg) if bg in BG_LIST else 0; bg=BG_LIST[(i+1)%len(BG_LIST)]
            except Exception:
                pass
        elif ch in (ord('q'),ord('Q')): break
        elif ch in (ord('p'),ord('P'),ord(' ')):
            if not paused: 
                pause_start=time.time()
                paused=True
            else: 
                pause_acc += time.time()-pause_start
                paused=False
        elif ch == ord('+'):
            total_seconds += 60; start_total += 60
        elif ch == ord('-'):
            total_seconds=max(0,total_seconds-60); start_total=max(0,start_total-60)
        elif ch in (ord('r'),ord('R')):
            start_time=time.time(); pause_acc=0.0; paused=False; total_seconds=start_total
        elif ch in (ord('t'),ord('T')):
            names=list(THEMES.keys()); i=names.index(theme); theme=names[(i+1)%len(names)]
            attr_primary,attr_dim,attr_acc,attr_alt,attr_bg = init_colors(theme)
        elif ch in (ord('b'),ord('B')):
            i=BG_LIST.index(bg) if bg in BG_LIST else 0; bg=BG_LIST[(i+1)%len(BG_LIST)]
        elif ch in (ord('s'),ord('S')):
            total_seconds += 300; start_total += 300

        if not paused and remaining<=0:
            for _ in range(16):
                stdscr.clear()
                _=draw_big_time(stdscr,"00:00",attr_acc)
                msg="DONE • Press Q to exit"
                try: stdscr.addstr(H-2, max(2,(W-len(msg))//2), msg, attr_primary)
                except curses.error: pass
                stdscr.refresh(); time.sleep(0.05)
            if do_notify: notify(title,"Timer complete")
            beep(do_beep_flag); break
    return True

def main():
    parser=argparse.ArgumentParser(description="Full-screen themed, interactive animated timer")
    parser.add_argument("duration", help="Duration: 900 | 15m | 15:00 | 1h5m30s")
    parser.add_argument("--title", default="FancyTimer")
    parser.add_argument("--no-notify", action="store_true")
    parser.add_argument("--no-beep", action="store_true")
    parser.add_argument("--bg", choices=BG_LIST, default="stars")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="neo")
    parser.add_argument("--no-bonsai", action="store_true")
    args=parser.parse_args()

    total=parse_duration(args.duration)
    curses.wrapper(app, total, args.title, not args.no_notify, not args.no_beep, args.bg, args.theme)
    if not args.no_bonsai:
        print("\\n(Bonsai break)\\n"); show_bonsai()

# ============== UÇAK SAVAŞ OYUNU ==============

class Player:
    def __init__(self, h, w):
        self.h, self.w = h, w
        self.x = w // 2
        self.y = h - 5
        self.speed = 2  # Hareket hızı
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
        # Çarpışma için koordinatlar
        return [(self.x + dx, self.y + dy) 
                for dy in range(self.height) 
                for dx in range(self.width) 
                if self.ship[dy][dx] != ' ']

class Bullet:
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

class Enemy:
    def __init__(self, x, y, enemy_type="fighter"):
        self.x, self.y = x, y
        self.enemy_type = enemy_type
        self.last_shot = 0
        self.original_x = x
        self.time = 0
        self.damaged = False
        
        if enemy_type == "fighter":  # Küçük uçak - sağ sola hareket
            self.sprite = [
                " ▼ ",
                "███",
                " █ "
            ]
            self.width, self.height = 3, 3
            self.speed = 0.3  # Çok daha yavaş
            self.shoot_chance = 0.012
            self.move_pattern = "horizontal"
            self.max_health = 3
            self.health = self.max_health
            self.direction = random.choice([-1, 1])  # Sağ veya sol yön
            
        elif enemy_type == "bomber":  # Büyük uçak - yavaş sağ sola
            self.sprite = [
                "  ▼  ",
                " ███ ",
                "█████",
                " ███ "
            ]
            self.width, self.height = 5, 4
            self.speed = 0.2  # En yavaş
            self.shoot_chance = 0.020
            self.move_pattern = "horizontal"
            self.max_health = 8
            self.health = self.max_health
            self.direction = random.choice([-1, 1])
            
        elif enemy_type == "interceptor":  # Hızlı uçak - orta hızda
            self.sprite = [
                "▼",
                "█",
                "█"
            ]
            self.width, self.height = 1, 3
            self.speed = 0.5  # Orta hız
            self.shoot_chance = 0.008
            self.move_pattern = "horizontal"
            self.max_health = 2
            self.health = self.max_health
            self.direction = random.choice([-1, 1])
            
        elif enemy_type == "ground_turret":  # Sabit hedef
            self.sprite = [
                "░▓░",
                "███",
                "▀▀▀"
            ]
            self.width, self.height = 3, 3
            self.speed = 0
            self.shoot_chance = 0.018
            self.move_pattern = "stationary"
            self.max_health = 10
            self.health = self.max_health
            self.direction = 0
            
    def take_damage(self):
        self.health -= 1
        self.damaged = True
        return self.health <= 0
        
    def update(self):
        self.time += 0.1
        self.damaged = False  # Reset damage indicator
        
        if self.move_pattern == "horizontal":
            # Sadece sağ-sola hareket, ekran kenarına çarparsa yön değiştir
            self.x += self.speed * self.direction
            
            # Ekran kenarı kontrolü
            if self.x <= 2:
                self.direction = 1  # Sağa döndür
            elif self.x >= 80 - self.width:  # Genel terminal genişliği
                self.direction = -1  # Sola döndür
                
        elif self.move_pattern == "stationary":
            pass  # Hareket etmez
            
    def should_shoot(self):
        return random.random() < self.shoot_chance
        
    def is_offscreen(self, h, w):
        # Düşmanlar artık ekrandan çıkmıyor, sadece sabit pozisyonda sağ-sola hareket ediyorlar
        return False
        
    def draw(self, stdscr, attr):
        # Can azaldıkça kırmızı yanıp sönüyor
        if self.damaged:
            attr = curses.color_pair(3) | curses.A_REVERSE
        elif self.health <= self.max_health // 2:
            attr = curses.color_pair(3) | curses.A_BOLD
            
        for i, line in enumerate(self.sprite):
            try:
                stdscr.addstr(int(self.y) + i, int(self.x), line, attr)
            except curses.error:
                pass
                
    def get_center(self):
        return int(self.x + self.width // 2), int(self.y + self.height // 2)
        
    def get_hitbox(self):
        return [(int(self.x) + dx, int(self.y) + dy) 
                for dy in range(self.height) 
                for dx in range(self.width)]

def check_collision(obj1, obj2):
    # Basit çarpışma kontrolü
    if hasattr(obj1, 'get_hitbox'):
        # Player için detaylı hitbox
        for px, py in obj1.get_hitbox():
            if int(px) == int(obj2.x) and int(py) == int(obj2.y):
                return True
    else:
        # Basit nokta çarpışması
        return abs(int(obj1.x) - int(obj2.x)) <= 1 and abs(int(obj1.y) - int(obj2.y)) <= 1
    return False
    
def check_bullet_collision(bullet, enemy):
    # Düşmanın sprite alanı içinde çarpışma kontrolü
    bx, by = int(bullet.x), int(bullet.y)
    ex, ey = int(enemy.x), int(enemy.y)
    
    return (ex <= bx < ex + enemy.width and 
            ey <= by < ey + enemy.height)

def space_game(stdscr, theme="neo"):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(30)  # Daha hızlı oyun
    
    attr_primary, attr_dim, attr_acc, attr_alt, attr_bg = init_colors(theme)
    stdscr.bkgd(' ', attr_bg)
    
    H, W = stdscr.getmaxyx()
    player = Player(H, W)
    bullets = []
    enemies = []
    enemy_bullets = []
    score = 0
    lives = 5  # Daha zor olacağı için daha fazla can
    game_speed = 0
    enemy_spawn_counter = 0
    wave = 1
    enemies_killed_this_wave = 0
    
    # Continuous movement tracking
    keys_pressed = {'left': False, 'right': False}
    
    # Background effects - terminal boyutuna uygun
    stars = StarField(count=min(300, H*W//50))
    stars.rebuild(H, W)
    
    while lives > 0:
        game_speed += 1
        old_h, old_w = H, W
        H, W = stdscr.getmaxyx()
        
        # Dinamik boyut değişimi
        if (H, W) != (old_h, old_w):
            player = Player(H, W)
            stars.rebuild(H, W)
        
        # Input handling - Sürekli hareket için
        try:
            ch = stdscr.getch()
        except:
            ch = -1
            
        if ch == ord('q') or ch == ord('Q'):
            break
        elif ch == curses.KEY_LEFT or ch == ord('a'):
            keys_pressed['left'] = True
        elif ch == curses.KEY_RIGHT or ch == ord('d'):
            keys_pressed['right'] = True
        elif ch == ord(' '):
            # Uçağın merkezinden ateş et
            center_x, center_y = player.get_center()
            bullets.append(Bullet(center_x, center_y - 1))
            
        # Sürekli hareket uygula
        if keys_pressed['left']:
            player.move_left()
            keys_pressed['left'] = False  # Tek frame için
        if keys_pressed['right']:
            player.move_right()
            keys_pressed['right'] = False
            
        # Update bullets
        bullets = [b for b in bullets if not b.is_offscreen()]
        for bullet in bullets:
            bullet.update()
            
        # Update enemy bullets
        enemy_bullets = [b for b in enemy_bullets if not b.is_offscreen(H)]
        for bullet in enemy_bullets:
            bullet.update()
            
        # Sabit düşman sayısını koruma sistemi
        max_enemies = min(8 + wave, 15)  # Wave'e göre maksimum düşman
        
        # Düşman sayısı azsa yeni spawn et
        if len(enemies) < max_enemies:
            if enemy_spawn_counter % 30 == 0:  # Her 30 frame'de kontrol
                x = random.randint(5, W - 8)
                
                # Farklı yüksekliklerde spawn
                y_positions = [5, 8, 11, 14]  # Sabit yükseklik seviyeleri
                y = random.choice(y_positions)
                
                # Düşman çeşitliliği wave'e göre
                if wave <= 2:
                    enemy_type = random.choice(["fighter", "interceptor"])
                elif wave <= 4:
                    enemy_type = random.choice(["fighter", "bomber", "interceptor"])
                else:
                    enemy_type = random.choice(["fighter", "bomber", "interceptor"])
                    
                # Aynı pozisyonda düşman var mı kontrol et
                position_free = True
                for existing_enemy in enemies:
                    if (abs(existing_enemy.x - x) < 6 and 
                        abs(existing_enemy.y - y) < 4):
                        position_free = False
                        break
                        
                if position_free:
                    enemies.append(Enemy(x, y, enemy_type))
                
        # Sabit hedefler spawn - daha seyrek
        ground_turrets = [e for e in enemies if e.enemy_type == "ground_turret"]
        if len(ground_turrets) < 2 and enemy_spawn_counter % 300 == 0 and wave >= 2:
            # Yerdeki toplar
            x = random.randint(8, W - 12)
            y = H - 8  # Zemine yakın
            enemies.append(Enemy(x, y, "ground_turret"))
                
        enemy_spawn_counter += 1
        
        # Update enemies ve ateş etme
        # Artık düşmanlar ekrandan çıkmıyor
        for enemy in enemies:
            enemy.update()
            # Düşman ateşi - merkezden ateş ediyor
            if enemy.should_shoot():
                center_x, center_y = enemy.get_center()
                enemy_bullets.append(EnemyBullet(center_x, center_y + 1))
            
        # Check player bullet-enemy collisions - Can sistemi ile
        new_bullets = []
        
        for bullet in bullets:
            hit = False
            for enemy in enemies[:]:
                if check_bullet_collision(bullet, enemy):
                    # Düşman hasar alıyor
                    if enemy.take_damage():
                        # Düşman öldü - puan ver ve patlama efekti
                        if enemy.enemy_type == "fighter":
                            score += 100
                        elif enemy.enemy_type == "bomber":
                            score += 300
                        elif enemy.enemy_type == "interceptor":
                            score += 150
                        elif enemy.enemy_type == "ground_turret":
                            score += 500
                        
                        # Patlama efekti göster
                        explosion_x, explosion_y = enemy.get_center()
                        for _ in range(3):
                            try:
                                stdscr.addstr(explosion_y, explosion_x - 1, "***", curses.color_pair(3) | curses.A_BOLD)
                                stdscr.refresh()
                                time.sleep(0.02)
                            except:
                                pass
                        
                        enemies_killed_this_wave += 1
                        enemies.remove(enemy)
                        
                        # Hemen yeni düşman spawn et (eğer maksimum sayıya ulaşmadıysa)
                        if len(enemies) < max_enemies:
                            new_x = random.randint(5, W - 8)
                            new_y = random.choice([5, 8, 11, 14])
                            new_type = random.choice(["fighter", "bomber", "interceptor"])
                            enemies.append(Enemy(new_x, new_y, new_type))
                    else:
                        # Sadece hasar aldı - 5 puan
                        score += 5
                        
                    hit = True
                    break
            if not hit:
                new_bullets.append(bullet)
                
        bullets = new_bullets
        
        # Wave ilerlemesi
        if enemies_killed_this_wave >= wave * 5:
            wave += 1
            enemies_killed_this_wave = 0
        
        # Check player-enemy collisions
        for enemy in enemies[:]:
            if check_collision(player, enemy):
                lives -= 1
                enemies.remove(enemy)
                # Flash effect
                for _ in range(3):
                    stdscr.clear()
                    stdscr.refresh()
                    time.sleep(0.05)
                break
                
        # Check player-enemy bullet collisions  
        for bullet in enemy_bullets[:]:
            if check_collision(player, bullet):
                lives -= 1
                enemy_bullets.remove(bullet)
                # Flash effect
                for _ in range(3):
                    stdscr.clear()
                    stdscr.refresh()
                    time.sleep(0.05)
                break
                
        # Draw everything
        stdscr.erase()
        
        # Background stars
        stars.draw(stdscr, H, W, time.time(), attr_dim, attr_primary)
        
        # Draw game objects
        player.draw(stdscr, attr_primary)
        
        # Player bullets (mavi)
        for bullet in bullets:
            bullet.draw(stdscr, attr_acc)
            
        # Enemy bullets (kırmızı)
        for bullet in enemy_bullets:
            bullet.draw(stdscr, curses.color_pair(3) | curses.A_BOLD)
            
        # Enemies - türe göre renklendir
        for enemy in enemies:
            if enemy.enemy_type == "fighter":
                enemy.draw(stdscr, attr_alt)
            elif enemy.enemy_type == "bomber":
                enemy.draw(stdscr, curses.color_pair(1) | curses.A_BOLD)
            elif enemy.enemy_type == "interceptor":
                enemy.draw(stdscr, curses.color_pair(3) | curses.A_BOLD)
            elif enemy.enemy_type == "ground_turret":
                enemy.draw(stdscr, curses.color_pair(2) | curses.A_REVERSE)
            
        # Draw UI - Daha detaylı
        score_text = f"SKOR: {score}"
        lives_text = f"♥ CAN: {lives}"
        wave_text = f"WAVE: {wave}"
        enemies_text = f"DÜŞMANLAR: {len(enemies)} | MİN: {len(enemy_bullets)}"
        controls = "←→ hareket  SPACE ateş  Q çık"
        
        try:
            # Üst bar
            stdscr.addstr(0, 2, score_text, attr_primary)
            stdscr.addstr(0, 15, wave_text, attr_acc)
            stdscr.addstr(0, W - len(lives_text) - 2, lives_text, attr_primary)
            
            # Alt bar
            if H > 5:
                stdscr.addstr(H - 2, 2, enemies_text, attr_dim)
                stdscr.addstr(H - 1, max(0, (W - len(controls)) // 2), controls, attr_dim)
        except curses.error:
            pass
            
        # Draw borders - daha görsel
        try:
            # Yan çizgiler
            for y in range(1, H-1):
                stdscr.addstr(y, 0, "│", attr_dim)
                stdscr.addstr(y, W - 1, "│", attr_dim)
            
            # Köşeler ve üst/alt
            stdscr.addstr(0, 0, "┌", attr_dim)
            stdscr.addstr(0, W-1, "┐", attr_dim)
            stdscr.addstr(H-1, 0, "└", attr_dim) 
            stdscr.addstr(H-1, W-1, "┘", attr_dim)
            
            for x in range(1, W-1):
                stdscr.addstr(0, x, "─", attr_dim)
                stdscr.addstr(H-1, x, "─", attr_dim)
                
        except curses.error:
            pass
            
        stdscr.refresh()
        time.sleep(0.03)  # Daha akıcı oyun
        
    # Game Over screen
    for _ in range(20):
        stdscr.clear()
        game_over = "OYUN BİTTİ!"
        final_score = f"TOPLAM SKOR: {score}"
        restart_msg = "R: Tekrar  Q: Çık"
        
        try:
            stdscr.addstr(H//2 - 1, (W - len(game_over))//2, game_over, attr_acc)
            stdscr.addstr(H//2, (W - len(final_score))//2, final_score, attr_primary)
            stdscr.addstr(H//2 + 2, (W - len(restart_msg))//2, restart_msg, attr_dim)
        except curses.error:
            pass
            
        stdscr.refresh()
        time.sleep(0.1)
        
    # Wait for input
    while True:
        try:
            ch = stdscr.getch()
        except:
            continue
            
        if ch == ord('q') or ch == ord('Q'):
            break
        elif ch == ord('r') or ch == ord('R'):
            curses.wrapper(space_game, theme)
            break

def main():
    parser = argparse.ArgumentParser(description="Uzay savaşçı oyunu")
    parser.add_argument("--theme", choices=list(THEMES.keys()), default="neo")
    args = parser.parse_args()

    curses.wrapper(space_game, args.theme)

if __name__=="__main__": main()
