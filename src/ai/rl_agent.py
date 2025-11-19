"""Reinforcement Learning agent for adaptive boss behavior"""
import numpy as np
import json
from pathlib import Path

class BossRLAgent:
    """
    Q-Learning based agent that learns to counter player strategies.
    The boss adapts its behavior based on player patterns.
    """
    
    def __init__(self, model_dir="models/saved_models"):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Q-table: state -> action -> value
        self.q_table = {}
        
        # Hyperparameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.epsilon = 0.2  # Exploration rate
        
        # Action space for boss
        self.actions = [
            "move_left",
            "move_right",
            "shoot",
            "shoot_burst",
            "defensive",
            "aggressive"
        ]
        
        self.current_state = None
        self.last_action = None
        
    def get_state_key(self, game_state):
        """
        Convert game state to a hashable state key
        
        Args:
            game_state: dict with player_x, boss_x, player_health, boss_health, etc.
        """
        # Discretize continuous values
        player_zone = int(game_state.get("player_x", 0) / 10)  # 0-7 zones
        boss_zone = int(game_state.get("boss_x", 0) / 10)
        
        relative_pos = "left" if player_zone < boss_zone else "right" if player_zone > boss_zone else "center"
        
        distance = abs(player_zone - boss_zone)
        distance_category = "close" if distance <= 2 else "medium" if distance <= 4 else "far"
        
        player_pattern = game_state.get("player_pattern", "balanced")  # from PatternAnalyzer
        
        return (relative_pos, distance_category, player_pattern)
        
    def get_q_value(self, state_key, action):
        """Get Q-value for state-action pair"""
        if state_key not in self.q_table:
            self.q_table[state_key] = {a: 0.0 for a in self.actions}
        return self.q_table[state_key].get(action, 0.0)
        
    def choose_action(self, game_state):
        """
        Choose action using epsilon-greedy policy
        
        Args:
            game_state: Current game state
            
        Returns:
            str: Selected action
        """
        state_key = self.get_state_key(game_state)
        self.current_state = state_key
        
        # Epsilon-greedy exploration
        if np.random.random() < self.epsilon:
            # Explore: random action
            action = np.random.choice(self.actions)
        else:
            # Exploit: best known action
            if state_key not in self.q_table:
                self.q_table[state_key] = {a: 0.0 for a in self.actions}
                
            action = max(self.actions, key=lambda a: self.get_q_value(state_key, a))
            
        self.last_action = action
        return action
        
    def update(self, reward, next_game_state):
        """
        Update Q-table based on reward
        
        Args:
            reward: Reward received for last action
            next_game_state: New game state after action
        """
        if self.current_state is None or self.last_action is None:
            return
            
        next_state_key = self.get_state_key(next_game_state)
        
        # Q-learning update
        current_q = self.get_q_value(self.current_state, self.last_action)
        
        # Max Q-value for next state
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {a: 0.0 for a in self.actions}
        max_next_q = max(self.q_table[next_state_key].values())
        
        # Q-learning formula
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        self.q_table[self.current_state][self.last_action] = new_q
        
    def calculate_reward(self, event_type, game_state):
        """
        Calculate reward based on game events
        
        Args:
            event_type: 'hit_player', 'missed', 'got_hit', 'player_dodged'
            game_state: Current game state
            
        Returns:
            float: Reward value
        """
        rewards = {
            "hit_player": 10.0,      # Successfully hit player
            "missed": -2.0,          # Missed shot
            "got_hit": -5.0,         # Boss got hit
            "player_dodged": -1.0,   # Player dodged attack
            "survived": 1.0          # Boss survived a turn
        }
        
        return rewards.get(event_type, 0.0)
        
    def save_model(self, filename="boss_model.json"):
        """Save Q-table to file"""
        filepath = self.model_dir / filename
        
        # Convert tuple keys to strings for JSON serialization
        serializable_q_table = {
            str(k): v for k, v in self.q_table.items()
        }
        
        model_data = {
            "q_table": serializable_q_table,
            "learning_rate": self.learning_rate,
            "discount_factor": self.discount_factor,
            "epsilon": self.epsilon
        }
        
        with open(filepath, 'w') as f:
            json.dump(model_data, f, indent=2)
            
        return filepath
        
    def load_model(self, filename="boss_model.json"):
        """Load Q-table from file"""
        filepath = self.model_dir / filename
        
        if not filepath.exists():
            return False
            
        with open(filepath, 'r') as f:
            model_data = json.load(f)
            
        # Convert string keys back to tuples
        self.q_table = {
            eval(k): v for k, v in model_data["q_table"].items()
        }
        
        self.learning_rate = model_data.get("learning_rate", self.learning_rate)
        self.discount_factor = model_data.get("discount_factor", self.discount_factor)
        self.epsilon = model_data.get("epsilon", self.epsilon)
        
        return True
        
    def decay_epsilon(self, decay_rate=0.995):
        """Decay exploration rate over time"""
        self.epsilon = max(0.05, self.epsilon * decay_rate)
