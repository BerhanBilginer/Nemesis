"""Adaptive AI-powered Boss enemy"""
import random
import curses
from ..ai.rl_agent import BossRLAgent
from ..ai.pattern_analyzer import PatternAnalyzer

class Boss:
    """
    Adaptive boss that learns from player behavior using RL.
    """
    
    def __init__(self, x, y, use_ai=True):
        self.x, self.y = x, y
        self.use_ai = use_ai
        
        # Boss appearance
        self.sprite = [
            "  ╔═══╗  ",
            "  ║ ▼ ║  ",
            "╔═╩═══╩═╗",
            "║ █████ ║",
            "╠═══════╣",
            "║ ▓▓▓▓▓ ║",
            "╚═══════╝"
        ]
        self.width = 9
        self.height = 7
        
        # Boss stats
        self.max_health = 50
        self.health = self.max_health
        self.speed = 0.4
        self.direction = 1
        self.damaged = False
        
        # AI components
        self.rl_agent = BossRLAgent() if use_ai else None
        self.pattern_analyzer = PatternAnalyzer() if use_ai else None
        
        # Behavior state
        self.behavior_mode = "balanced"  # balanced, defensive, aggressive
        self.shoot_cooldown = 0
        self.special_attack_cooldown = 0
        
        # Load existing model if available
        if self.use_ai and self.rl_agent:
            loaded = self.rl_agent.load_model()
            if loaded:
                print("Boss loaded previous training!")
                
    def take_damage(self):
        """Apply damage and return True if destroyed"""
        self.health -= 1
        self.damaged = True
        
        # Notify RL agent of hit
        if self.use_ai and self.rl_agent:
            reward = self.rl_agent.calculate_reward("got_hit", self.get_state())
            self.rl_agent.update(reward, self.get_state())
            
        return self.health <= 0
        
    def get_state(self):
        """Get current boss state for AI"""
        return {
            "boss_x": self.x,
            "boss_health": self.health,
            "behavior_mode": self.behavior_mode
        }
        
    def update(self, player_x, player_y, screen_width):
        """
        Update boss position and behavior
        
        Args:
            player_x: Player X position
            player_y: Player Y position  
            screen_width: Screen width for boundary checking
        """
        self.damaged = False
        self.shoot_cooldown = max(0, self.shoot_cooldown - 1)
        self.special_attack_cooldown = max(0, self.special_attack_cooldown - 1)
        
        # AI decision making
        if self.use_ai and self.rl_agent:
            game_state = {
                "player_x": player_x,
                "boss_x": self.x,
                "player_health": 5,  # TODO: get from game
                "boss_health": self.health,
                "player_pattern": "balanced"  # TODO: get from pattern analyzer
            }
            
            action = self.rl_agent.choose_action(game_state)
            self._execute_ai_action(action, player_x, screen_width)
        else:
            # Simple behavior
            self._simple_movement(player_x, screen_width)
            
    def _execute_ai_action(self, action, player_x, screen_width):
        """Execute action chosen by AI"""
        if action == "move_left":
            self.x = max(2, self.x - self.speed)
        elif action == "move_right":
            self.x = min(screen_width - self.width - 2, self.x + self.speed)
        elif action == "aggressive":
            self.behavior_mode = "aggressive"
            self.shoot_cooldown = 0  # Ready to shoot
        elif action == "defensive":
            self.behavior_mode = "defensive"
            # Move away from player
            if player_x < self.x:
                self.x = min(screen_width - self.width - 2, self.x + self.speed * 1.5)
            else:
                self.x = max(2, self.x - self.speed * 1.5)
                
    def _simple_movement(self, player_x, screen_width):
        """Simple non-AI movement pattern"""
        # Basic horizontal movement
        self.x += self.speed * self.direction
        
        if self.x <= 2:
            self.direction = 1
        elif self.x >= screen_width - self.width - 2:
            self.direction = -1
            
    def should_shoot(self):
        """Determine if boss should shoot"""
        if self.shoot_cooldown > 0:
            return False
            
        if self.behavior_mode == "aggressive":
            chance = 0.05
        elif self.behavior_mode == "defensive":
            chance = 0.02
        else:
            chance = 0.03
            
        if random.random() < chance:
            self.shoot_cooldown = 20  # Cooldown frames
            return True
        return False
        
    def should_special_attack(self):
        """Determine if boss should use special attack"""
        if self.special_attack_cooldown > 0:
            return False
            
        # Special attack when health is low
        if self.health < self.max_health * 0.3:
            if random.random() < 0.01:
                self.special_attack_cooldown = 300  # Long cooldown
                return True
        return False
        
    def draw(self, stdscr, attr):
        """Draw boss with health indication"""
        if self.damaged:
            attr = curses.color_pair(3) | curses.A_REVERSE
        elif self.health <= self.max_health // 3:
            attr = curses.color_pair(3) | curses.A_BOLD
        elif self.health <= self.max_health // 2:
            attr = curses.color_pair(1) | curses.A_BOLD
            
        for i, line in enumerate(self.sprite):
            try:
                stdscr.addstr(int(self.y) + i, int(self.x), line, attr)
            except curses.error:
                pass
                
        # Draw health bar
        self._draw_health_bar(stdscr)
        
    def _draw_health_bar(self, stdscr):
        """Draw boss health bar"""
        bar_width = self.width
        filled = int((self.health / self.max_health) * bar_width)
        
        health_bar = "█" * filled + "░" * (bar_width - filled)
        
        try:
            stdscr.addstr(int(self.y) - 1, int(self.x), health_bar, 
                         curses.color_pair(3) if self.health < self.max_health // 2 
                         else curses.color_pair(1))
        except curses.error:
            pass
            
    def get_center(self):
        """Get center coordinates"""
        return int(self.x + self.width // 2), int(self.y + self.height // 2)
        
    def get_hitbox(self):
        """Get hitbox for collision detection"""
        return [(int(self.x) + dx, int(self.y) + dy) 
                for dy in range(self.height) 
                for dx in range(self.width)]
                
    def save_training(self):
        """Save AI training progress"""
        if self.use_ai and self.rl_agent:
            self.rl_agent.save_model()
