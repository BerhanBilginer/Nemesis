"""Enemy entities"""
import random
import curses

class Enemy:
    def __init__(self, x, y, enemy_type="fighter"):
        self.x, self.y = x, y
        self.enemy_type = enemy_type
        self.last_shot = 0
        self.original_x = x
        self.time = 0
        self.damaged = False
        
        if enemy_type == "fighter":
            self.sprite = [" ▼ ", "███", " █ "]
            self.width, self.height = 3, 3
            self.speed = 0.3
            self.shoot_chance = 0.012
            self.move_pattern = "horizontal"
            self.max_health = 3
            self.health = self.max_health
            self.direction = random.choice([-1, 1])
            
        elif enemy_type == "bomber":
            self.sprite = ["  ▼  ", " ███ ", "█████", " ███ "]
            self.width, self.height = 5, 4
            self.speed = 0.2
            self.shoot_chance = 0.020
            self.move_pattern = "horizontal"
            self.max_health = 8
            self.health = self.max_health
            self.direction = random.choice([-1, 1])
            
        elif enemy_type == "interceptor":
            self.sprite = ["▼", "█", "█"]
            self.width, self.height = 1, 3
            self.speed = 0.5
            self.shoot_chance = 0.008
            self.move_pattern = "horizontal"
            self.max_health = 2
            self.health = self.max_health
            self.direction = random.choice([-1, 1])
            
        elif enemy_type == "ground_turret":
            self.sprite = ["░▓░", "███", "▀▀▀"]
            self.width, self.height = 3, 3
            self.speed = 0
            self.shoot_chance = 0.018
            self.move_pattern = "stationary"
            self.max_health = 10
            self.health = self.max_health
            self.direction = 0
            
    def take_damage(self):
        """Apply damage and return True if destroyed"""
        self.health -= 1
        self.damaged = True
        return self.health <= 0
        
    def update(self):
        """Update enemy position and state"""
        self.time += 0.1
        self.damaged = False
        
        if self.move_pattern == "horizontal":
            self.x += self.speed * self.direction
            
            if self.x <= 2:
                self.direction = 1
            elif self.x >= 80 - self.width:
                self.direction = -1
                
        elif self.move_pattern == "stationary":
            pass
            
    def should_shoot(self):
        """Determine if enemy should shoot this frame"""
        return random.random() < self.shoot_chance
        
    def is_offscreen(self, h, w):
        """Check if enemy is offscreen (currently always False)"""
        return False
        
    def draw(self, stdscr, attr):
        """Draw enemy with damage indication"""
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
        """Get center coordinates of enemy"""
        return int(self.x + self.width // 2), int(self.y + self.height // 2)
        
    def get_hitbox(self):
        """Get hitbox coordinates for collision detection"""
        return [(int(self.x) + dx, int(self.y) + dy) 
                for dy in range(self.height) 
                for dx in range(self.width)]
