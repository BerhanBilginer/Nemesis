# 🎮 NEMESIS - AI-Powered Adaptive Boss Battle

An intelligent space shooter where the boss **learns from your playstyle** and adapts its strategy using reinforcement learning and pattern analysis.

## 🧠 Core Concept

The boss enemy uses:
- **Reinforcement Learning (Q-Learning)** to optimize its strategy against you
- **Unsupervised Learning** to identify your movement patterns, shooting habits, and positioning preferences
- **Adaptive Difficulty** that evolves based on your skill level

The more you play, the smarter the boss becomes. Can you defeat your own nemesis?

## 🏗️ Project Structure

```
Nemesis/
├── src/
│   ├── game/              # Game entities and logic
│   │   ├── player.py      # Player ship
│   │   ├── enemy.py       # Regular enemies
│   │   ├── boss.py        # AI-powered boss
│   │   ├── projectiles.py # Bullets
│   │   └── collision.py   # Collision detection
│   ├── rendering/         # Visual effects
│   │   ├── themes.py      # Color themes
│   │   └── effects.py     # Background effects
│   ├── ai/                # AI/ML modules
│   │   ├── behavior_tracker.py    # Player behavior logging
│   │   ├── pattern_analyzer.py    # Pattern recognition (unsupervised)
│   │   └── rl_agent.py            # Q-Learning agent
│   └── utils/             # Utility functions
├── models/                # Saved AI models
├── data/                  # Player behavior data
├── config/                # Configuration files
└── tests/                 # Test suite

```

## 🚀 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Nemesis.git
cd Nemesis

# Install dependencies
pip install -r requirements.txt
```

## 🎯 Usage

```bash
# Run the game
python src/main.py

# Or with specific theme
python src/main.py --theme matrix

# Disable AI (classic mode)
python src/main.py --no-ai
```

## 🎮 Controls

- **←/→ or A/D**: Move left/right
- **SPACE**: Shoot
- **Q**: Quit

## 🤖 AI System

### Behavior Tracking
The game tracks:
- Movement patterns (left/right preference, reaction times)
- Shooting behavior (accuracy, burst vs sustained fire)
- Positioning (preferred zones, mobility)

### Pattern Analysis
Using unsupervised learning to identify:
- Play style classification (aggressive, defensive, balanced)
- Common movement sequences
- Predictable behavior patterns

### Reinforcement Learning
The boss uses Q-Learning to:
- Choose optimal actions based on game state
- Learn which strategies work best against your style
- Adapt difficulty dynamically

## 📊 Data & Privacy

All player data is stored **locally** in `data/player_data/`. No data is sent to external servers.

To clear your data:
```bash
rm -rf data/player_data/*
rm -rf models/saved_models/*
```

## 🛠️ Development

### Adding New AI Features

1. **Behavior Tracking**: Modify `src/ai/behavior_tracker.py`
2. **Pattern Analysis**: Extend `src/ai/pattern_analyzer.py`
3. **RL Agent**: Update `src/ai/rl_agent.py`

### Running Tests

```bash
pytest tests/
```

## 📈 Future Enhancements

- [ ] Deep Q-Networks (DQN) for more complex boss behavior
- [ ] Multi-agent learning (multiple bosses that share knowledge)
- [ ] Transfer learning between different player profiles
- [ ] Neural network for pattern prediction
- [ ] Online learning with real-time adaptation
- [ ] Boss personality types based on cluster analysis

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## 🎓 Technical Details

### Reinforcement Learning
- **Algorithm**: Q-Learning
- **State Space**: Player position, boss position, health, detected patterns
- **Action Space**: Move left/right, shoot, defensive/aggressive modes
- **Reward Function**: Hit player (+), get hit (-), survive (+)

### Pattern Recognition
- **Features**: Movement frequency, shooting intervals, position variance
- **Clustering**: K-means for play style identification
- **Sequence Analysis**: Markov chains for action prediction

---

*"The only way to win is to learn faster than your enemy learns from you."*