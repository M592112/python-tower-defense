# Tower Defense - Defend Your Base!

A classic tower defense game built with Python and Pygame where you strategically place and upgrade towers to defend against waves of increasingly difficult enemies.

## Features

- **Strategic Tower Placement**: Place towers anywhere except on the enemy path
- **Tower Upgrades**: Upgrade towers up to level 3 for increased damage, range, and fire rate
- **Progressive Difficulty**: Enemies get faster and tougher with each wave
- **Resource Management**: Earn money by defeating enemies and spend wisely on towers and upgrades
- **Wave System**: Survive endless waves of enemies with increasing challenge
- **Pause Functionality**: Pause the game to plan your strategy
- **Score Tracking**: Keep track of your current score and high score

## Requirements

- Python 3.x
- Pygame library

## Installation

1. Install Python from [python.org](https://www.python.org/)
2. Install Pygame:
```bash
pip install pygame
```

## How to Run

```bash
python tower_defense.py
```

## Controls

| Action | Control |
|--------|---------|
| Place Tower | Left Click (costs $50) |
| Select Tower | Left Click on existing tower |
| Sell Tower | Right Click on tower (50% refund) |
| Upgrade Tower | Select tower + Press U (costs $30) |
| Pause/Unpause | Press P |
| Restart (Game Over) | Press R |
| Quit (Game Over) | Press Q |

## Gameplay

### Starting Resources
- **Money**: $200
- **Lives**: 20

### Objective
Prevent enemies from reaching the end of the path by strategically placing and upgrading towers. Each enemy that reaches the end costs you 1 life. The game ends when you run out of lives.

### Towers
- **Level 1** (Blue): Base damage and range
- **Level 2** (Dark Blue): +15 damage, +20 range, faster fire rate
- **Level 3** (Purple): +30 total damage, +40 total range, fastest fire rate
- **Max Level**: 3

### Enemies
- Enemies follow a predetermined path
- Each wave spawns more enemies with increased health and speed
- Defeating enemies rewards money and score points
- Enemy difficulty scales with wave number

### Strategy Tips
- Place towers at corners where enemies slow down
- Upgrade strategically - level 3 towers are powerful
- Save money for critical upgrades during tough waves
- Use the pre-wave time to build your defense
- Monitor your lives - don't let too many enemies through

## Game Mechanics

### Wave Progression
- Wave 1: 5 enemies
- Each subsequent wave: +2 enemies
- Enemy speed increases by 10% per wave
- Enemy health increases by 20% per wave

### Economy
- Starting money: $200
- Tower cost: $50
- Upgrade cost: $30 per level
- Sell refund: 50% of tower's total value
- Enemy reward: Scales with enemy health

### Scoring
- Points earned by defeating enemies
- Score = Enemy reward × 10
- High score tracked across sessions

## UI Information

The game displays:
- Current wave number
- Available money
- Remaining lives
- Current score
- High score
- Selected tower stats (level, damage, range)
- Tower placement and upgrade costs

## Technical Details

- **Window Size**: 800x600 pixels
- **Grid Size**: 40x40 pixels
- **Frame Rate**: 60 FPS
- **Tower Range**: Visual indicator shown when selected

## Credits

Built with Python and Pygame as a classic tower defense experience.

---

**Have fun defending your base!** 🏰
