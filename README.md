# Enhanced Flappy Bird Game - Player Edition

A beautiful, enhanced Flappy Bird game implemented in Python using Pygame with stunning graphics, smooth gameplay, three difficulty levels, and a complete player system with statistics tracking.

## ✨ Enhanced Features

### Visual Enhancements
- **Animated Bird**: Wing flapping animation, rotation based on velocity, and colorful sprite with trail effects
- **Gradient Backgrounds**: Beautiful sky gradients with parallax scrolling clouds
- **3D Pipe Effects**: Gradient pipes with highlights and shadows for realistic depth
- **Particle Effects**: Explosion particles on crash and celebration particles on scoring
- **Screen Shake**: Dynamic camera shake effects during crashes
- **Textured Ground**: Multi-layered ground with realistic textures

### Four Difficulty Levels
- **Level 1 (EASY)**: Large pipe gaps (200px), gentle jumps (-6.5), slower pipes (speed 2)
- **Level 2 (MEDIUM)**: Smaller gaps (160px), same gentle jumps, faster pipes (speed 2.5)
- **Level 3 (HARD)**: Small gaps (160px), higher jumps (-8), faster pipes (speed 2.5)
- **Level 4 (FANTASTIC)**: Dark theme, switches between Flappy Bird and Geometry Dash modes every 10 points!

### Gameplay Improvements
- **Level Selection Screen**: Choose your preferred difficulty before playing
- **Level-Specific High Scores**: Track best scores for each difficulty level
- **Progressive Difficulty**: Pipe spacing gradually decreases as your score increases within each level
- **Smoother Controls**: More responsive jump mechanics with level-appropriate physics

### Audio & Feedback
- **Enhanced Sound Effects**: Musical jump sounds, success chimes for scoring, dramatic game over tones
- **Score Animation**: Animated score display with color changes when scoring
- **Visual Feedback**: Particle effects and screen shake provide immediate feedback

### Player System & UI
- **Home Page**: Welcome screen with player statistics and leaderboard
- **Player Registration**: Name input system for tracking individual progress  
- **Personal Stats**: Individual high scores, games played, and total score tracking
- **Game Over Options**: Choose to restart level, select new level, or return home
- **Data Persistence**: Player data automatically saved and loaded
- **Leaderboard**: Top players displayed on home page

## Visual Features

The enhanced game features:
- **Animated Bird**: Golden bird with wing flapping, rotation effects, and particle trails
- **3D Pipes**: Green gradient pipes with realistic depth and lighting effects
- **Dynamic Sky**: Gradient background with moving clouds and parallax scrolling (dark theme for Fantastic level)
- **Textured Ground**: Multi-layered ground with realistic brown earth tones (dark theme variants)
- **Particle Systems**: Explosion effects on crashes and celebration particles when scoring
- **Screen Effects**: Camera shake, score animations, and smooth visual transitions
- **Geometry Dash Mode**: Unique cube-based gameplay with obstacles, spikes, and platforms
- **Dark Theme**: Atmospheric dark backgrounds and purple gradients for Level 4

## Requirements

- Python 3.6 or higher
- Pygame 2.5.2

## Installation

1. **Clone or Download** this project to your local machine

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
   Or install pygame directly:
   ```bash
   pip install pygame==2.5.2
   ```

## How to Run

1. Navigate to the project directory:
   ```bash
   cd Project_Flappy_Bird
   ```

2. Run the game:
   ```bash
   python flappy_bird.py
   ```

## Game Controls

### Level Selection Screen:
- **1, 2, 3, 4 Keys**: Select difficulty level (Easy, Medium, Hard, Fantastic)
- **MOUSE CLICK**: Click on desired level button
- **ESC**: Quit the game

### During Gameplay:
- **SPACEBAR** or **LEFT MOUSE CLICK**: Make the bird jump
- **ESC**: Return to home page

### Game Over Screen:
- **1 Key**: Restart current level
- **2 Key**: Go to level selection
- **3 Key**: Return to home page
- **MOUSE CLICK**: Click on desired option
- **ESC**: Return to home page

## Gameplay

1. **Level Selection**: Choose from four difficulty levels on the main screen
2. **Bird Physics**: The bird automatically falls due to gravity (consistent across all levels)
3. **Controls**: Click or press spacebar to make the bird jump upward (or make the cube jump in Geometry Dash mode)
4. **Objective**: Navigate through the gaps between green pipes (or avoid obstacles in Geometry Dash mode)
5. **Scoring**: Each pipe you pass through increases your score by 1
6. **Difficulty Differences**:
   - **Easy**: Large gaps (200px), gentle jumps (-6.5), slower pipes (speed 2)
   - **Medium**: Smaller gaps (160px), same gentle jumps, faster pipes (speed 2.5)  
   - **Hard**: Small gaps (160px), higher jumps (-8), faster pipes (speed 2.5)
   - **Fantastic**: Dark theme, switches between Flappy Bird and Geometry Dash modes every 10 points!
7. **Game Over**: Avoid hitting pipes, ground, ceiling, or obstacles
8. **Restart Options**: Press spacebar/click to restart, or ESC to change levels

## Game Mechanics

- **Four Difficulty Levels**: Easy, Medium, Hard, and Fantastic with distinct characteristics
- **Level-Specific Physics**: Jump strength and pipe speeds vary by level
- **Dual Game Modes**: Fantastic level switches between Flappy Bird and Geometry Dash every 10 points
- **Adaptive Pipe Gaps**: Different gap sizes for each difficulty level
- **Progressive Difficulty**: Pipe spacing gradually decreases as score increases within each level
- **Enhanced Collision**: Slightly smaller hitbox for more forgiving collision detection
- **Visual Feedback**: Particle effects, screen shake, and animations provide immediate feedback
- **Level-Based High Scores**: Separate score tracking for each difficulty level
- **Dark Theme**: Atmospheric visuals for the Fantastic level
- **Flexible Navigation**: Easy level switching via ESC key during gameplay

## Code Structure

- **`Bird` class**: Enhanced with wing animation, rotation effects, trail particles, and detailed sprite rendering
- **`Pipe` class**: Improved with gradient effects, 3D lighting, shadows, and highlights
- **`GeometryDashCube` class**: Cube character for Geometry Dash mode with rotation and trail effects
- **`GeometryDashObstacle` class**: Various obstacles (spikes, blocks, platforms) for Geometry Dash mode
- **`Cloud` class**: Manages parallax scrolling cloud effects with transparency
- **`Particle` class**: Handles explosion and celebration particle systems
- **`SoundGenerator` class**: Creates enhanced musical sound effects with envelopes and harmonies
- **`Game` class**: Comprehensive game management with dual-mode support, visual effects, and state handling

## Customization

You can easily modify the game by changing constants at the top of `flappy_bird.py`:

- `SCREEN_WIDTH/HEIGHT`: Change game window size (currently 500x700 for enhanced experience)
- `GRAVITY`: Adjust how fast the bird falls
- `JUMP_STRENGTH`: Modify jump power  
- `PIPE_SPEED`: Change how fast pipes move
- `PIPE_GAP`: Adjust the gap size between pipes
- `FPS`: Change game frame rate## Troubleshooting

**Sound Issues**: If you encounter sound problems, the game will automatically disable sound and continue running without audio.

**Performance Issues**: If the game runs slowly, try:
- Closing other applications
- Reducing the FPS constant
- Checking if your system meets the requirements

**Import Errors**: Make sure pygame is properly installed:
```bash
pip install --upgrade pygame
```

## Future Enhancements

Potential improvements you could add:
- High score system with file persistence
- Different bird characters or skins
- Power-ups and special abilities
- Background parallax scrolling
- Animated sprites instead of simple shapes
- Multiple difficulty levels
- Particle effects for collisions

## License

This project is open source and available under the MIT License.

## Contributing

Feel free to fork this project and submit pull requests for any improvements!

---

**Enjoy playing Flappy Bird!** 🐦