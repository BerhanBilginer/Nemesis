"""Main game engine with AI integration"""
import curses
import time
import random
from ..rendering.themes import init_colors
from ..rendering.effects import StarField, BG_EFFECTS
from ..ai.behavior_tracker import BehaviorTracker
from ..ai.pattern_analyzer import PatternAnalyzer
from .player import Player
from .enemy import Enemy
from .boss import Boss
from .projectiles import Bullet, EnemyBullet
from .collision import check_collision, check_bullet_collision

class GameEngine:
    """Main game engine orchestrating gameplay and AI"""
    
    def __init__(self, theme="neo", use_ai=True, mode="normal"):
        self.theme = theme
        self.use_ai = use_ai
        self.mode = mode
        
        # AI components
        self.behavior_tracker = BehaviorTracker() if use_ai else None
        self.pattern_analyzer = PatternAnalyzer() if use_ai else None
        
    def run(self, stdscr):
        """Main game loop"""
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.timeout(30)
        
        attr_primary, attr_dim, attr_acc, attr_alt, attr_bg = init_colors(self.theme)
        stdscr.bkgd(' ', attr_bg)
        
        H, W = stdscr.getmaxyx()
        
        # Initialize game state
        player = Player(H, W)
        bullets = []
        enemies = []
        enemy_bullets = []
        boss = None
        
        score = 0
        lives = 5
        wave = 1
        game_speed = 0
        enemy_spawn_counter = 0
        enemies_killed_this_wave = 0
        
        # Movement tracking
        keys_pressed = {'left': False, 'right': False}
        
        # Background effects
        stars = StarField(count=min(300, H * W // 50))
        stars.rebuild(H, W)
        
        # Boss mode
        if self.mode == "boss":
            boss = Boss(W // 2 - 4, 5, use_ai=self.use_ai)
            
        # Track frame times for behavior logging
        last_position_track = time.time()
        position_track_interval = 0.1  # Track position every 100ms
        
        while lives > 0:
            game_speed += 1
            old_h, old_w = H, W
            H, W = stdscr.getmaxyx()
            
            # Handle resize
            if (H, W) != (old_h, old_w):
                player = Player(H, W)
                stars.rebuild(H, W)
                
            # Input handling
            try:
                ch = stdscr.getch()
            except:
                ch = -1
                
            if ch == ord('q') or ch == ord('Q'):
                break
            elif ch == curses.KEY_LEFT or ch == ord('a'):
                keys_pressed['left'] = True
                if self.behavior_tracker:
                    self.behavior_tracker.track_action("move_left", {"x": player.x})
            elif ch == curses.KEY_RIGHT or ch == ord('d'):
                keys_pressed['right'] = True
                if self.behavior_tracker:
                    self.behavior_tracker.track_action("move_right", {"x": player.x})
            elif ch == ord(' '):
                center_x, center_y = player.get_center()
                bullets.append(Bullet(center_x, center_y - 1))
                if self.behavior_tracker:
                    self.behavior_tracker.track_action("shoot", {"x": center_x, "y": center_y})
                    
            # Apply movement
            if keys_pressed['left']:
                player.move_left()
                keys_pressed['left'] = False
            if keys_pressed['right']:
                player.move_right()
                keys_pressed['right'] = False
                
            # Track player position periodically
            current_time = time.time()
            if self.behavior_tracker and (current_time - last_position_track) >= position_track_interval:
                self.behavior_tracker.track_position(player.x, player.y)
                last_position_track = current_time
                
            # Update bullets
            bullets = [b for b in bullets if not b.is_offscreen()]
            for bullet in bullets:
                bullet.update()
                
            # Update enemy bullets
            enemy_bullets = [b for b in enemy_bullets if not b.is_offscreen(H)]
            for bullet in enemy_bullets:
                bullet.update()
                
            # Boss mode logic
            if boss:
                boss.update(player.x, player.y, W)
                
                # Boss shooting
                if boss.should_shoot():
                    center_x, center_y = boss.get_center()
                    enemy_bullets.append(EnemyBullet(center_x, center_y + 1))
                    
                # Check player bullets hitting boss
                new_bullets = []
                for bullet in bullets:
                    hit = False
                    if check_bullet_collision(bullet, boss):
                        if boss.take_damage():
                            # Boss defeated!
                            score += 1000
                            self._show_victory(stdscr, H, W, score, attr_acc, attr_primary)
                            if self.behavior_tracker:
                                self.behavior_tracker.save_session()
                            if boss:
                                boss.save_training()
                            return
                        else:
                            score += 10
                            if self.behavior_tracker:
                                self.behavior_tracker.track_action("hit", {"target": "boss"})
                        hit = True
                    if not hit:
                        new_bullets.append(bullet)
                bullets = new_bullets
                
            else:
                # Normal mode: wave-based enemies
                max_enemies = min(8 + wave, 15)
                
                if len(enemies) < max_enemies:
                    if enemy_spawn_counter % 30 == 0:
                        x = random.randint(5, W - 8)
                        y_positions = [5, 8, 11, 14]
                        y = random.choice(y_positions)
                        
                        if wave <= 2:
                            enemy_type = random.choice(["fighter", "interceptor"])
                        else:
                            enemy_type = random.choice(["fighter", "bomber", "interceptor"])
                            
                        position_free = True
                        for existing_enemy in enemies:
                            if (abs(existing_enemy.x - x) < 6 and 
                                abs(existing_enemy.y - y) < 4):
                                position_free = False
                                break
                                
                        if position_free:
                            enemies.append(Enemy(x, y, enemy_type))
                            
                enemy_spawn_counter += 1
                
                # Update enemies
                for enemy in enemies:
                    enemy.update()
                    if enemy.should_shoot():
                        center_x, center_y = enemy.get_center()
                        enemy_bullets.append(EnemyBullet(center_x, center_y + 1))
                        
                # Check bullet collisions
                new_bullets = []
                for bullet in bullets:
                    hit = False
                    for enemy in enemies[:]:
                        if check_bullet_collision(bullet, enemy):
                            if enemy.take_damage():
                                # Enemy destroyed
                                score += {"fighter": 100, "bomber": 300, 
                                         "interceptor": 150, "ground_turret": 500}.get(enemy.enemy_type, 100)
                                
                                if self.behavior_tracker:
                                    self.behavior_tracker.track_action("hit", {"target": enemy.enemy_type})
                                
                                enemies_killed_this_wave += 1
                                enemies.remove(enemy)
                                
                                # Spawn new enemy
                                if len(enemies) < max_enemies:
                                    new_x = random.randint(5, W - 8)
                                    new_y = random.choice([5, 8, 11, 14])
                                    new_type = random.choice(["fighter", "bomber", "interceptor"])
                                    enemies.append(Enemy(new_x, new_y, new_type))
                            else:
                                score += 5
                                
                            hit = True
                            break
                    if not hit:
                        new_bullets.append(bullet)
                bullets = new_bullets
                
                # Wave progression
                if enemies_killed_this_wave >= wave * 5:
                    wave += 1
                    enemies_killed_this_wave = 0
                    
                    # Enter boss mode after wave 3
                    if wave == 4 and not boss:
                        enemies = []
                        enemy_bullets = []
                        boss = Boss(W // 2 - 4, 5, use_ai=self.use_ai)
                        
            # Check player collisions
            for enemy in enemies[:]:
                if check_collision(player, enemy):
                    lives -= 1
                    enemies.remove(enemy)
                    if self.behavior_tracker:
                        self.behavior_tracker.track_action("death", {"cause": "enemy_collision"})
                    self._flash_screen(stdscr)
                    break
                    
            if boss and check_collision(player, boss):
                lives -= 1
                if self.behavior_tracker:
                    self.behavior_tracker.track_action("death", {"cause": "boss_collision"})
                self._flash_screen(stdscr)
                    
            for bullet in enemy_bullets[:]:
                if check_collision(player, bullet):
                    lives -= 1
                    enemy_bullets.remove(bullet)
                    if self.behavior_tracker:
                        self.behavior_tracker.track_action("death", {"cause": "bullet"})
                    self._flash_screen(stdscr)
                    break
                    
            # Draw everything
            stdscr.erase()
            
            # Background
            stars.draw(stdscr, H, W, time.time(), attr_dim, attr_primary)
            
            # Game objects
            player.draw(stdscr, attr_primary)
            
            for bullet in bullets:
                bullet.draw(stdscr, attr_acc)
                
            for bullet in enemy_bullets:
                bullet.draw(stdscr, curses.color_pair(3) | curses.A_BOLD)
                
            if boss:
                boss.draw(stdscr, attr_primary)
            else:
                for enemy in enemies:
                    enemy.draw(stdscr, attr_alt)
                    
            # UI
            self._draw_ui(stdscr, H, W, score, lives, wave, boss, 
                         len(enemies), len(enemy_bullets), attr_primary, attr_acc, attr_dim)
                         
            stdscr.refresh()
            time.sleep(0.03)
            
        # Game over
        self._show_game_over(stdscr, H, W, score, attr_acc, attr_primary, attr_dim)
        
        # Save session data
        if self.behavior_tracker:
            filepath = self.behavior_tracker.save_session()
            print(f"\n📊 Session data saved: {filepath}")
            
        # Save boss training
        if boss:
            boss.save_training()
            print("🧠 Boss training saved!")
            
    def _draw_ui(self, stdscr, H, W, score, lives, wave, boss, enemy_count, bullet_count, 
                 attr_primary, attr_acc, attr_dim):
        """Draw game UI"""
        score_text = f"SKOR: {score}"
        lives_text = f"♥ CAN: {lives}"
        
        if boss:
            wave_text = f"BOSS: {boss.health}/{boss.max_health} HP"
        else:
            wave_text = f"WAVE: {wave}"
            
        controls = "←→ hareket  SPACE ateş  Q çık"
        
        try:
            stdscr.addstr(0, 2, score_text, attr_primary)
            stdscr.addstr(0, 15, wave_text, attr_acc if boss else attr_primary)
            stdscr.addstr(0, W - len(lives_text) - 2, lives_text, attr_primary)
            
            if H > 5:
                stdscr.addstr(H - 1, max(0, (W - len(controls)) // 2), controls, attr_dim)
        except curses.error:
            pass
            
    def _flash_screen(self, stdscr):
        """Flash screen on hit"""
        for _ in range(3):
            stdscr.clear()
            stdscr.refresh()
            time.sleep(0.05)
            
    def _show_game_over(self, stdscr, H, W, score, attr_acc, attr_primary, attr_dim):
        """Show game over screen"""
        for _ in range(20):
            stdscr.clear()
            game_over = "OYUN BİTTİ!"
            final_score = f"TOPLAM SKOR: {score}"
            restart_msg = "Q: Çık"
            
            try:
                stdscr.addstr(H // 2 - 1, (W - len(game_over)) // 2, game_over, attr_acc)
                stdscr.addstr(H // 2, (W - len(final_score)) // 2, final_score, attr_primary)
                stdscr.addstr(H // 2 + 2, (W - len(restart_msg)) // 2, restart_msg, attr_dim)
            except curses.error:
                pass
                
            stdscr.refresh()
            time.sleep(0.1)
            
        stdscr.timeout(-1)
        while True:
            try:
                ch = stdscr.getch()
            except:
                continue
            if ch == ord('q') or ch == ord('Q'):
                break
                
    def _show_victory(self, stdscr, H, W, score, attr_acc, attr_primary):
        """Show victory screen"""
        for _ in range(30):
            stdscr.clear()
            victory = "🎉 KAZANDIN! 🎉"
            final_score = f"TOPLAM SKOR: {score}"
            msg = "Boss'u yendin!"
            
            try:
                stdscr.addstr(H // 2 - 2, (W - len(victory)) // 2, victory, attr_acc)
                stdscr.addstr(H // 2, (W - len(msg)) // 2, msg, attr_primary)
                stdscr.addstr(H // 2 + 1, (W - len(final_score)) // 2, final_score, attr_primary)
            except curses.error:
                pass
                
            stdscr.refresh()
            time.sleep(0.1)
