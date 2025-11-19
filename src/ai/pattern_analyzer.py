"""Unsupervised learning for player pattern recognition"""
import json
import numpy as np
from pathlib import Path
from collections import defaultdict

class PatternAnalyzer:
    """
    Analyzes player behavior patterns using unsupervised learning techniques.
    Identifies play styles, movement patterns, and shooting habits.
    """
    
    def __init__(self, data_dir="data/player_data"):
        self.data_dir = Path(data_dir)
        self.patterns = {
            "movement": defaultdict(int),
            "shooting": defaultdict(int),
            "positioning": defaultdict(int)
        }
        
    def load_sessions(self, limit=None):
        """Load player session data from files"""
        sessions = []
        session_files = sorted(self.data_dir.glob("session_*.json"))
        
        if limit:
            session_files = session_files[-limit:]
            
        for filepath in session_files:
            with open(filepath, 'r') as f:
                sessions.append(json.load(f))
                
        return sessions
        
    def analyze_movement_patterns(self, sessions):
        """
        Analyze movement patterns:
        - Preferred directions
        - Movement frequency
        - Reaction times
        """
        patterns = {
            "left_preference": 0,
            "right_preference": 0,
            "avg_move_interval": 0,
            "preferred_zones": []  # Screen zones player prefers
        }
        
        total_moves = 0
        move_intervals = []
        
        for session in sessions:
            last_move_time = 0
            
            for action in session["actions"]:
                if action["type"] == "move_left":
                    patterns["left_preference"] += 1
                    total_moves += 1
                    move_intervals.append(action["timestamp"] - last_move_time)
                    last_move_time = action["timestamp"]
                    
                elif action["type"] == "move_right":
                    patterns["right_preference"] += 1
                    total_moves += 1
                    move_intervals.append(action["timestamp"] - last_move_time)
                    last_move_time = action["timestamp"]
                    
        if move_intervals:
            patterns["avg_move_interval"] = np.mean(move_intervals)
            
        return patterns
        
    def analyze_shooting_patterns(self, sessions):
        """
        Analyze shooting behavior:
        - Shooting frequency
        - Accuracy
        - Burst vs sustained fire
        """
        patterns = {
            "avg_shot_interval": 0,
            "accuracy": 0,
            "burst_shooter": False,
            "shots_per_second": 0
        }
        
        total_shots = 0
        total_hits = 0
        shot_intervals = []
        
        for session in sessions:
            last_shot_time = 0
            
            for action in session["actions"]:
                if action["type"] == "shoot":
                    total_shots += 1
                    if last_shot_time > 0:
                        shot_intervals.append(action["timestamp"] - last_shot_time)
                    last_shot_time = action["timestamp"]
                    
                elif action["type"] == "hit":
                    total_hits += 1
                    
        if total_shots > 0:
            patterns["accuracy"] = total_hits / total_shots
            
        if shot_intervals:
            patterns["avg_shot_interval"] = np.mean(shot_intervals)
            patterns["shots_per_second"] = 1.0 / patterns["avg_shot_interval"] if patterns["avg_shot_interval"] > 0 else 0
            
            # Burst detection: if variance is high, player shoots in bursts
            variance = np.var(shot_intervals)
            patterns["burst_shooter"] = variance > 0.5
            
        return patterns
        
    def analyze_positioning(self, sessions):
        """
        Analyze positional preferences:
        - Preferred screen zones
        - Movement range
        - Defensive vs aggressive positioning
        """
        patterns = {
            "preferred_x_range": (0, 0),
            "avg_position": 0,
            "mobility": 0  # How much player moves around
        }
        
        all_positions = []
        
        for session in sessions:
            positions = session.get("stats", {}).get("position_history", [])
            all_positions.extend([p["x"] for p in positions])
            
        if all_positions:
            patterns["avg_position"] = np.mean(all_positions)
            patterns["preferred_x_range"] = (
                np.percentile(all_positions, 25),
                np.percentile(all_positions, 75)
            )
            patterns["mobility"] = np.std(all_positions)
            
        return patterns
        
    def get_player_profile(self, recent_sessions=10):
        """
        Generate comprehensive player profile from recent sessions
        
        Returns:
            dict: Player profile with movement, shooting, and positioning patterns
        """
        sessions = self.load_sessions(limit=recent_sessions)
        
        if not sessions:
            return None
            
        profile = {
            "movement": self.analyze_movement_patterns(sessions),
            "shooting": self.analyze_shooting_patterns(sessions),
            "positioning": self.analyze_positioning(sessions),
            "total_sessions_analyzed": len(sessions)
        }
        
        return profile
        
    def predict_next_action(self, current_state):
        """
        Predict player's likely next action based on patterns
        
        Args:
            current_state: Current game state (position, time since last action, etc.)
            
        Returns:
            dict: Probabilities for each action type
        """
        # TODO: Implement with clustering or sequence prediction
        # For now, return basic probabilities
        return {
            "move_left": 0.3,
            "move_right": 0.3,
            "shoot": 0.3,
            "none": 0.1
        }
