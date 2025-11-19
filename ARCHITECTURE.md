# 🏗️ Nemesis Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                        │
│                     (Curses Terminal)                        │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────┐
│                      Game Engine                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Game Loop • State Management • Event Handling      │   │
│  └─────────────────────────────────────────────────────┘   │
└───┬────────────────┬────────────────┬───────────────────────┘
    │                │                │
┌───▼─────┐    ┌────▼────┐    ┌─────▼──────┐
│  Game   │    │ Render  │    │    AI      │
│ Entities│    │ System  │    │  System    │
└────┬────┘    └────┬────┘    └─────┬──────┘
     │              │               │
┌────▼─────────┐ ┌─▼──────────┐ ┌──▼────────────┐
│ • Player     │ │ • Themes   │ │ • RL Agent    │
│ • Enemy      │ │ • Effects  │ │ • Patterns    │
│ • Boss       │ │ • UI       │ │ • Behavior    │
│ • Bullets    │ │            │ │   Tracker     │
│ • Collision  │ │            │ │               │
└──────────────┘ └────────────┘ └───────┬───────┘
                                        │
                                ┌───────▼────────┐
                                │  Data Storage  │
                                │  • Sessions    │
                                │  • Models      │
                                └────────────────┘
```

## Module Breakdown

### 1. Game Module (`src/game/`)

#### **game_engine.py**
- **Purpose**: Main game loop and orchestration
- **Responsibilities**:
  - Input handling
  - Game state management
  - Entity updates
  - Collision detection
  - Score/wave tracking
  - AI integration
- **Key Methods**:
  - `run()`: Main game loop
  - `_draw_ui()`: HUD rendering
  - `_show_game_over()`: End screen

#### **player.py**
- **Purpose**: Player ship entity
- **State**:
  - Position (x, y)
  - Movement speed
  - Sprite representation
- **Methods**:
  - `move_left()`, `move_right()`: Movement
  - `get_center()`: Get firing position
  - `get_hitbox()`: Collision detection
  - `draw()`: Render sprite

#### **enemy.py**
- **Purpose**: Regular enemy entities
- **Types**:
  - **Fighter**: Balanced stats, horizontal movement
  - **Bomber**: High health, slow, heavy fire
  - **Interceptor**: Fast, low health
  - **Ground Turret**: Stationary, high health
- **State**:
  - Position, health, movement pattern
  - Damage indicator
- **Behavior**:
  - Movement patterns (horizontal, stationary)
  - Shooting probability
  - Damage feedback

#### **boss.py**
- **Purpose**: AI-powered adaptive boss
- **Features**:
  - Reinforcement learning integration
  - Pattern analysis integration
  - Adaptive behavior modes
  - Health management
  - Special attacks
- **AI Integration**:
  ```python
  # Boss uses RL agent to choose actions
  action = self.rl_agent.choose_action(game_state)
  
  # Rewards/penalties update learning
  reward = calculate_reward(event)
  self.rl_agent.update(reward, new_state)
  ```

#### **projectiles.py**
- **Bullet**: Player projectiles (move up)
- **EnemyBullet**: Enemy projectiles (move down)

#### **collision.py**
- `check_collision()`: Entity-entity collision
- `check_bullet_collision()`: Bullet-enemy collision

### 2. Rendering Module (`src/rendering/`)

#### **themes.py**
- **Purpose**: Color scheme management
- **Themes**: neo, retro, mono, matrix, sunset, dark
- **Function**: `init_colors()` sets up curses color pairs

#### **effects.py**
- **Background Effects**:
  - `StarField`: Animated stars with drift
  - `MatrixRain`: Matrix-style falling characters
  - `Snow`: Falling snowflakes
  - `Rain`: Vertical rain
  - `Bubbles`: Rising bubbles
  - `Noise`: Static noise
- **Common Interface**:
  - `rebuild(h, w)`: Regenerate for screen size
  - `draw(stdscr, h, w, t, attr_dim, attr_bold)`: Render effect

### 3. AI Module (`src/ai/`)

#### **behavior_tracker.py**
- **Purpose**: Log all player actions
- **Tracked Data**:
  - Movement actions (left/right)
  - Shooting events
  - Hit events
  - Death events
  - Position history (time series)
- **Output**: JSON session files
- **Data Structure**:
  ```json
  {
    "session_id": "20250119_223045",
    "actions": [
      {"timestamp": 0.123, "type": "move_left", "data": {"x": 35}},
      {"timestamp": 0.456, "type": "shoot", "data": {"x": 40, "y": 50}}
    ],
    "stats": {
      "total_shots": 150,
      "total_hits": 87,
      "accuracy": 0.58
    }
  }
  ```

#### **pattern_analyzer.py**
- **Purpose**: Unsupervised learning for pattern recognition
- **Analysis Types**:

**Movement Patterns**:
```python
{
  "left_preference": 0.45,  # 45% left, 55% right
  "avg_move_interval": 0.3,  # Moves every 0.3s
  "mobility": 12.5  # Position variance
}
```

**Shooting Patterns**:
```python
{
  "accuracy": 0.65,
  "shots_per_second": 2.5,
  "burst_shooter": True,  # High variance in intervals
  "avg_shot_interval": 0.4
}
```

**Positioning**:
```python
{
  "avg_position": 40,  # Center of screen is 40
  "preferred_x_range": (30, 50),  # 25th-75th percentile
  "mobility": 8.3  # Standard deviation
}
```

- **Methods**:
  - `analyze_movement_patterns()`
  - `analyze_shooting_patterns()`
  - `analyze_positioning()`
  - `get_player_profile()`: Generate complete profile
  - `predict_next_action()`: Predict likely next move

#### **rl_agent.py**
- **Purpose**: Q-Learning agent for boss behavior
- **Algorithm**: Q-Learning (Temporal Difference Learning)

**State Space**:
```python
state = (
  relative_position,  # "left", "center", "right"
  distance_category,  # "close", "medium", "far"
  player_pattern      # "aggressive", "defensive", "balanced"
)
```

**Action Space**:
- `move_left`, `move_right`
- `shoot`, `shoot_burst`
- `defensive`, `aggressive`

**Q-Learning Update**:
```python
Q(s, a) ← Q(s, a) + α[r + γ·max Q(s', a') - Q(s, a)]
```
Where:
- α = learning rate (0.1)
- γ = discount factor (0.95)
- r = reward

**Reward Function**:
```python
rewards = {
  "hit_player": +10,
  "got_hit": -5,
  "missed": -2,
  "survived": +1
}
```

**Exploration Strategy**:
- Epsilon-greedy (ε = 0.2)
- Decays over time: ε ← ε × 0.995

### 4. Data Flow

#### Training Loop
```
1. Player plays game
   ↓
2. BehaviorTracker logs all actions → JSON file
   ↓
3. PatternAnalyzer reads sessions → Profile
   ↓
4. Profile fed to Boss during game
   ↓
5. Boss uses RLAgent to choose actions
   ↓
6. RLAgent receives rewards/penalties
   ↓
7. Q-table updated → Saved to disk
   ↓
8. Next game: Boss loads improved model
```

#### Real-time Adaptation
```
During Game:
  Player Action
      ↓
  BehaviorTracker.track_action()
      ↓
  (Every N frames)
      ↓
  PatternAnalyzer.get_current_tendencies()
      ↓
  Boss.update() receives pattern info
      ↓
  RLAgent.choose_action(state + patterns)
      ↓
  Boss executes action
      ↓
  Reward calculated based on outcome
      ↓
  RLAgent.update(reward) → Q-table modified
```

## File Formats

### Session Data (JSON)
```json
{
  "session_id": "20250119_223045",
  "start_time": 1705703445.123,
  "end_time": 1705703745.456,
  "duration": 300.333,
  "actions": [...],
  "stats": {
    "total_shots": 234,
    "total_moves": 567,
    "total_hits": 145,
    "total_deaths": 3,
    "position_history": [
      {"t": 0.1, "x": 40, "y": 55},
      ...
    ]
  }
}
```

### Boss Model (JSON)
```json
{
  "q_table": {
    "('left', 'close', 'aggressive')": {
      "move_right": 8.5,
      "shoot": 12.3,
      "defensive": 3.2,
      ...
    },
    ...
  },
  "learning_rate": 0.1,
  "discount_factor": 0.95,
  "epsilon": 0.15
}
```

## Performance Considerations

1. **Session Data**: Grows with gameplay time
   - Solution: Periodic cleanup of old sessions
   - Keep last 30 days by default

2. **Q-Table Size**: Grows with state-action combinations
   - Current: ~100 states × 6 actions = 600 entries
   - Memory: ~50KB typical
   - Solution: State discretization limits growth

3. **Real-time Analysis**: Pattern analysis can be expensive
   - Solution: Cache player profile, update periodically
   - Only analyze when boss spawns

## Future Enhancements

### Short-term
- [ ] More sophisticated state representation
- [ ] Additional enemy types
- [ ] Power-ups and special weapons
- [ ] Boss phases (behavior changes with health)

### Medium-term
- [ ] Deep Q-Networks (DQN) replacing Q-tables
- [ ] LSTM for sequence prediction
- [ ] Multi-boss cooperation
- [ ] Procedural level generation

### Long-term
- [ ] Transfer learning between players
- [ ] Meta-learning (learning to learn faster)
- [ ] Adversarial training
- [ ] Neural architecture search for optimal boss brain

## Testing Strategy

### Unit Tests
- Entity behavior (player, enemy movement)
- Collision detection accuracy
- AI state calculations

### Integration Tests
- Game loop stability
- AI-game engine integration
- Data persistence

### AI Tests
- Q-learning convergence
- Pattern recognition accuracy
- Reward function validation

### Performance Tests
- Frame rate stability
- Memory usage over time
- Data file growth rate

## Deployment

### Development
```bash
python src/main.py --theme neo
```

### Production
```bash
# With AI enabled (default)
python src/main.py --mode boss

# Classic mode (no AI)
python src/main.py --no-ai
```

### Data Management
```bash
# View player statistics
python scripts/analyze_sessions.py

# Clear old data
python scripts/cleanup_data.py --days 30

# Export model
python scripts/export_model.py --output boss_v1.json
```

---

**Last Updated**: 2025-01-19
**Version**: 2.0.0
