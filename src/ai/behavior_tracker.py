"""Player behavior tracking and data collection"""
import json
import time
from datetime import datetime
from pathlib import Path

class BehaviorTracker:
    """Tracks player movements, shooting patterns, and strategies"""
    
    def __init__(self, data_dir="data/player_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_data = {
            "session_id": self.session_id,
            "start_time": time.time(),
            "actions": [],
            "stats": {
                "total_shots": 0,
                "total_moves": 0,
                "total_hits": 0,
                "total_deaths": 0,
                "position_history": []
            }
        }
        
    def track_action(self, action_type, data=None):
        """
        Track a player action
        
        Args:
            action_type: 'move_left', 'move_right', 'shoot', 'hit', 'death'
            data: Additional data about the action
        """
        timestamp = time.time() - self.session_data["start_time"]
        
        action_record = {
            "timestamp": timestamp,
            "type": action_type,
            "data": data or {}
        }
        
        self.session_data["actions"].append(action_record)
        
        # Update stats
        if action_type == "shoot":
            self.session_data["stats"]["total_shots"] += 1
        elif action_type in ["move_left", "move_right"]:
            self.session_data["stats"]["total_moves"] += 1
        elif action_type == "hit":
            self.session_data["stats"]["total_hits"] += 1
        elif action_type == "death":
            self.session_data["stats"]["total_deaths"] += 1
            
    def track_position(self, x, y, timestamp=None):
        """Track player position over time"""
        if timestamp is None:
            timestamp = time.time() - self.session_data["start_time"]
            
        self.session_data["stats"]["position_history"].append({
            "t": timestamp,
            "x": x,
            "y": y
        })
        
    def save_session(self):
        """Save session data to file"""
        filepath = self.data_dir / f"session_{self.session_id}.json"
        
        self.session_data["end_time"] = time.time()
        self.session_data["duration"] = (
            self.session_data["end_time"] - self.session_data["start_time"]
        )
        
        with open(filepath, 'w') as f:
            json.dump(self.session_data, f, indent=2)
            
        return filepath
        
    def get_stats(self):
        """Get current session statistics"""
        return self.session_data["stats"]
