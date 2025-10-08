import pygame
import random
import sys
import os
import math
import json
import numpy as np
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game constants
SCREEN_WIDTH = 500  # Increased from 400
SCREEN_HEIGHT = 700  # Increased from 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (135, 206, 235)  # Sky blue
YELLOW = (255, 255, 0)
RED = (255, 0, 0)

# Game physics - Level-based system
GRAVITY = 0.3  # Consistent across all levels
PIPE_WIDTH = 60

# Level configurations
LEVEL_CONFIG = {
    1: {  # Easy Level (current settings)
        'jump_strength': -6.5,
        'pipe_speed': 2,
        'pipe_gap': 200,
        'name': 'EASY',
        'color': (0, 255, 0)  # Green
    },
    2: {  # Medium Level
        'jump_strength': -6.5,
        'pipe_speed': 2.5,
        'pipe_gap': 160,
        'name': 'MEDIUM',
        'color': (255, 255, 0)  # Yellow
    },
    3: {  # Hard Level
        'jump_strength': -8,
        'pipe_speed': 2.5,
        'pipe_gap': 160,
        'name': 'HARD',
        'color': (255, 0, 0)  # Red
    },
    4: {  # Fantastic Level (Zombie Bird Shooter Mode)
        'jump_strength': -6.5,
        'pipe_speed': 2.5,
        'pipe_gap': 160,
        'name': 'FANTASTIC',
        'color': (138, 43, 226)  # Purple
    }
}

# Enhanced colors and gradients
GRADIENT_BLUE = [(135, 206, 235), (173, 216, 230), (176, 224, 230)]
GRADIENT_GREEN = [(34, 139, 34), (50, 205, 50), (144, 238, 144)]

# Dark theme colors for Fantastic level
GRADIENT_DARK = [(25, 25, 35), (35, 35, 50), (45, 45, 65)]
GRADIENT_PURPLE = [(75, 0, 130), (138, 43, 226), (148, 0, 211)]
DARK_GROUND_COLORS = [(20, 20, 30), (30, 30, 40), (40, 40, 50)]
GEO_DASH_COLORS = {
    'cube': (0, 255, 255),  # Cyan
    'obstacle': (255, 20, 147),  # Deep pink
    'ground': (64, 64, 64),  # Dark gray
    'spikes': (255, 69, 0)  # Red orange
}

BIRD_COLORS = {
    'body': (255, 215, 0),  # Gold
    'wing': (255, 140, 0),  # Dark orange
    'belly': (255, 255, 224),  # Light yellow
    'beak': (255, 165, 0),  # Orange
    'eye_outer': (255, 255, 255),  # White
    'eye_inner': (0, 0, 0)  # Black
}
CLOUD_COLOR = (255, 255, 255, 100)
GROUND_COLORS = [(139, 69, 19), (160, 82, 45), (210, 180, 140)]

class PlayerData:
    def __init__(self):
        self.save_file = "player_data.json"
        self.current_player = ""
        self.players = self.load_data()
    
    def load_data(self):
        """Load player data from file"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    # Ensure all players have level 4 data (backwards compatibility)
                    for player_name, player_data in data.items():
                        if 4 not in player_data.get('high_scores', {}):
                            player_data['high_scores'][4] = 0
                        if 4 not in player_data.get('games_played', {}):
                            player_data['games_played'][4] = 0
                    return data
            return {}
        except:
            return {}
    
    def save_data(self):
        """Save player data to file"""
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.players, f, indent=2)
        except:
            pass
    
    def set_current_player(self, name):
        """Set the current player and initialize if new"""
        self.current_player = name.strip().title()
        if self.current_player not in self.players:
            self.players[self.current_player] = {
                'high_scores': {1: 0, 2: 0, 3: 0, 4: 0},
                'games_played': {1: 0, 2: 0, 3: 0, 4: 0},
                'total_score': 0,
                'last_played': datetime.now().strftime("%Y-%m-%d %H:%M")
            }
        self.save_data()
    
    def update_score(self, level, score):
        """Update player's high score for a level"""
        if self.current_player in self.players:
            player = self.players[self.current_player]
            if score > player['high_scores'][level]:
                player['high_scores'][level] = score
            player['games_played'][level] += 1
            player['total_score'] += score
            player['last_played'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.save_data()
            return score > player['high_scores'].get(level, 0)
        return False
    
    def get_player_stats(self):
        """Get current player's statistics"""
        if self.current_player in self.players:
            # Ensure player has level 4 data (for backwards compatibility)
            player = self.players[self.current_player]
            if 4 not in player['high_scores']:
                player['high_scores'][4] = 0
            if 4 not in player['games_played']:
                player['games_played'][4] = 0
                self.save_data()
            return player
        return None
    
    def get_top_players(self, limit=5):
        """Get top players by total score"""
        sorted_players = sorted(
            self.players.items(),
            key=lambda x: x[1]['total_score'],
            reverse=True
        )
        return sorted_players[:limit]

class TextInput:
    def __init__(self, x, y, width, height, font, max_length=15):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.text = ""
        self.max_length = max_length
        self.active = True
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return self.text.strip()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < self.max_length and event.unicode.isprintable():
                self.text += event.unicode
        return None
    
    def update(self):
        self.cursor_timer += 1
        if self.cursor_timer >= 30:  # Blink cursor every 30 frames
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
    def draw(self, screen):
        # Draw input box
        pygame.draw.rect(screen, (255, 255, 255), self.rect)
        pygame.draw.rect(screen, (100, 100, 100), self.rect, 2)
        
        # Draw text
        text_surface = self.font.render(self.text, True, (0, 0, 0))
        screen.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))
        
        # Draw cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 5 + text_surface.get_width()
            cursor_y = self.rect.y + 5
            pygame.draw.line(screen, (0, 0, 0), 
                           (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + text_surface.get_height()), 2)

class SoundGenerator:
    @staticmethod
    def generate_tone(frequency, duration, sample_rate=22050, amplitude=0.5):
        """Generate a simple tone"""
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2), dtype=np.int16)
        for i in range(frames):
            wave = amplitude * math.sin(2 * math.pi * frequency * i / sample_rate)
            arr[i] = [int(wave * 32767), int(wave * 32767)]
        return pygame.sndarray.make_sound(arr)
    
    @staticmethod
    def generate_jump_sound():
        """Generate a more pleasant jump sound effect"""
        # Create a chirp-like sound
        frames = int(0.15 * 22050)
        arr = np.zeros((frames, 2), dtype=np.int16)
        for i in range(frames):
            # Rising frequency for more pleasant sound
            freq = 300 + (i / frames) * 200
            wave = 0.2 * math.sin(2 * math.pi * freq * i / 22050)
            # Add envelope for smoother sound
            envelope = max(0, 1 - (i / frames))
            arr[i] = [int(wave * envelope * 32767), int(wave * envelope * 32767)]
        return pygame.sndarray.make_sound(arr)
    
    @staticmethod
    def generate_score_sound():
        """Generate a pleasant score sound effect"""
        # Create a success chime
        frames = int(0.3 * 22050)
        arr = np.zeros((frames, 2), dtype=np.int16)
        for i in range(frames):
            # Two-tone chime
            freq1 = 523  # C5
            freq2 = 659  # E5
            wave1 = 0.15 * math.sin(2 * math.pi * freq1 * i / 22050)
            wave2 = 0.15 * math.sin(2 * math.pi * freq2 * i / 22050)
            envelope = max(0, 1 - (i / frames) ** 0.5)
            combined_wave = (wave1 + wave2) * envelope
            arr[i] = [int(combined_wave * 32767), int(combined_wave * 32767)]
        return pygame.sndarray.make_sound(arr)
    
    @staticmethod
    def generate_game_over_sound():
        """Generate a dramatic game over sound effect"""
        # Create a descending tone
        frames = int(0.8 * 22050)
        arr = np.zeros((frames, 2), dtype=np.int16)
        for i in range(frames):
            # Descending frequency
            freq = 400 - (i / frames) * 250
            wave = 0.25 * math.sin(2 * math.pi * freq * i / 22050)
            # Fade out envelope
            envelope = max(0, 1 - (i / frames) ** 0.3)
            arr[i] = [int(wave * envelope * 32767), int(wave * envelope * 32767)]
        return pygame.sndarray.make_sound(arr)
    
    @staticmethod
    def generate_shooter_gun_sound():
        """Generate a friendly laser/gun sound effect for the shooter"""
        # Create a quick laser-like sound
        frames = int(0.12 * 22050)
        arr = np.zeros((frames, 2), dtype=np.int16)
        for i in range(frames):
            # Quick descending frequency for laser effect
            freq = 1200 - (i / frames) * 800
            wave = 0.2 * math.sin(2 * math.pi * freq * i / 22050)
            # Add slight noise for texture
            noise = (random.random() - 0.5) * 0.05
            # Sharp attack and quick decay
            envelope = max(0, 1 - (i / frames) ** 0.2)
            combined = (wave + noise) * envelope
            arr[i] = [int(combined * 32767), int(combined * 32767)]
        return pygame.sndarray.make_sound(arr)

class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(0, 200)
        self.y = random.randint(50, 200)
        self.speed = random.uniform(0.3, 0.8)
        self.size = random.randint(20, 40)
        self.alpha = random.randint(80, 150)
        
    def update(self):
        self.x -= self.speed
        
    def draw(self, screen):
        # Create cloud surface with transparency
        cloud_surface = pygame.Surface((self.size * 3, self.size))
        cloud_surface.set_alpha(self.alpha)
        cloud_surface.fill(WHITE)
        
        # Draw cloud circles
        pygame.draw.circle(cloud_surface, WHITE, (self.size // 2, self.size // 2), self.size // 2)
        pygame.draw.circle(cloud_surface, WHITE, (self.size, self.size // 3), self.size // 3)
        pygame.draw.circle(cloud_surface, WHITE, (self.size * 2, self.size // 2), self.size // 2)
        pygame.draw.circle(cloud_surface, WHITE, (self.size * 2.5, self.size // 3), self.size // 4)
        
        screen.blit(cloud_surface, (self.x, self.y))
        
    def is_off_screen(self):
        return self.x + self.size * 3 < 0

class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x + random.uniform(-2, 2)
        self.velocity_y = velocity_y + random.uniform(-3, -1)
        self.life = 30
        self.max_life = 30
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity on particles
        self.life -= 1
        
    def draw(self, screen):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            particle_surface = pygame.Surface((4, 4))
            particle_surface.set_alpha(alpha)
            particle_surface.fill(self.color)
            screen.blit(particle_surface, (int(self.x), int(self.y)))
            
    def is_alive(self):
        return self.life > 0

class Bird:
    def __init__(self, jump_strength=-6.5):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.radius = 22  # Slightly larger
        self.wing_flap = 0
        self.rotation = 0
        self.trail = []  # For trail effect
        self.max_trail_length = 8
        self.jump_strength = jump_strength
        
    def jump(self):
        self.velocity = self.jump_strength
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
        # Update wing flap animation
        self.wing_flap += 0.3
        
        # Calculate rotation based on velocity (more realistic)
        self.rotation = max(-30, min(30, self.velocity * 3))
        
        # Update trail effect
        self.trail.append((int(self.x - 10), int(self.y)))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
        
    def draw(self, screen):
        # Draw trail effect
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.3)
            trail_surface = pygame.Surface((6, 6))
            trail_surface.set_alpha(alpha)
            trail_surface.fill(BIRD_COLORS['wing'])
            screen.blit(trail_surface, pos)
        
        # Calculate wing positions based on flap animation
        wing_offset = math.sin(self.wing_flap) * 3
        
        # Draw bird body (main circle with gradient effect)
        for i in range(3):
            color_intensity = 1.0 - (i * 0.15)
            body_color = tuple(int(c * color_intensity) for c in BIRD_COLORS['body'])
            pygame.draw.circle(screen, body_color, (int(self.x), int(self.y)), self.radius - i)
        
        # Draw belly (lighter circle)
        pygame.draw.circle(screen, BIRD_COLORS['belly'], 
                          (int(self.x - 3), int(self.y + 3)), self.radius - 8)
        
        # Draw wings with flapping animation
        wing_points_left = [
            (int(self.x - 15), int(self.y - 5 + wing_offset)),
            (int(self.x - 25), int(self.y - 10 + wing_offset)),
            (int(self.x - 20), int(self.y + 5 + wing_offset)),
            (int(self.x - 8), int(self.y + 2 + wing_offset))
        ]
        pygame.draw.polygon(screen, BIRD_COLORS['wing'], wing_points_left)
        
        # Draw wing details
        wing_detail_points = [
            (int(self.x - 12), int(self.y - 2 + wing_offset)),
            (int(self.x - 18), int(self.y - 5 + wing_offset)),
            (int(self.x - 15), int(self.y + 2 + wing_offset))
        ]
        pygame.draw.polygon(screen, BIRD_COLORS['body'], wing_detail_points)
        
        # Draw eye (larger and more detailed)
        eye_x, eye_y = int(self.x + 8), int(self.y - 6)
        pygame.draw.circle(screen, BIRD_COLORS['eye_outer'], (eye_x, eye_y), 6)
        pygame.draw.circle(screen, BIRD_COLORS['eye_inner'], (eye_x + 1, eye_y), 3)
        pygame.draw.circle(screen, WHITE, (eye_x + 2, eye_y - 1), 1)  # Eye shine
        
        # Draw beak (more detailed)
        beak_points = [
            (int(self.x + self.radius - 2), int(self.y - 2)),
            (int(self.x + self.radius + 12), int(self.y - 6)),
            (int(self.x + self.radius + 12), int(self.y + 2)),
            (int(self.x + self.radius - 2), int(self.y + 4))
        ]
        pygame.draw.polygon(screen, BIRD_COLORS['beak'], beak_points)
        
        # Draw beak outline
        pygame.draw.polygon(screen, (200, 100, 0), beak_points, 2)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.radius + 5, self.y - self.radius + 5, 
                          (self.radius - 5) * 2, (self.radius - 5) * 2)  # Slightly smaller hitbox

class Pipe:
    def __init__(self, x, pipe_gap=200, pipe_speed=2):
        self.x = x
        self.pipe_gap = pipe_gap
        self.pipe_speed = pipe_speed
        self.height = random.randint(120, SCREEN_HEIGHT - pipe_gap - 120)  # Better range
        self.top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        self.bottom_rect = pygame.Rect(self.x, self.height + pipe_gap, 
                                      PIPE_WIDTH, SCREEN_HEIGHT - self.height - pipe_gap - 50)  # Account for ground
        self.passed = False
        
    def update(self):
        self.x -= self.pipe_speed
        self.top_rect.x = self.x
        self.bottom_rect.x = self.x
        
    def draw_gradient_rect(self, screen, rect, colors):
        """Draw a rectangle with vertical gradient"""
        if rect.height <= 0:
            return
        for i in range(rect.height):
            color_ratio = i / rect.height
            if color_ratio < 0.3:
                # Top part - lighter
                color = colors[0]
            elif color_ratio < 0.7:
                # Middle part - medium
                color = colors[1]
            else:
                # Bottom part - darker
                color = colors[2]
            pygame.draw.line(screen, color, (rect.x, rect.y + i), (rect.x + rect.width, rect.y + i))
        
    def draw(self, screen):
        # Draw pipes with gradient effect
        self.draw_gradient_rect(screen, self.top_rect, GRADIENT_GREEN)
        self.draw_gradient_rect(screen, self.bottom_rect, GRADIENT_GREEN)
        
        # Draw pipe caps with more detail
        cap_height = 25
        top_cap_rect = pygame.Rect(self.x - 8, self.height - cap_height, PIPE_WIDTH + 16, cap_height)
        bottom_cap_rect = pygame.Rect(self.x - 8, self.height + self.pipe_gap, PIPE_WIDTH + 16, cap_height)
        
        # Draw cap gradients
        for i in range(cap_height):
            brightness = 1.0 + (i / cap_height) * 0.3
            cap_color = tuple(min(255, int(c * brightness)) for c in GRADIENT_GREEN[1])
            pygame.draw.line(screen, cap_color, 
                           (top_cap_rect.x, top_cap_rect.y + i), 
                           (top_cap_rect.x + top_cap_rect.width, top_cap_rect.y + i))
            pygame.draw.line(screen, cap_color, 
                           (bottom_cap_rect.x, bottom_cap_rect.y + i), 
                           (bottom_cap_rect.x + bottom_cap_rect.width, bottom_cap_rect.y + i))
        
        # Draw pipe highlights and shadows for 3D effect
        # Left highlight
        pygame.draw.line(screen, (100, 255, 100), (self.x + 2, 0), (self.x + 2, self.height), 3)
        pygame.draw.line(screen, (100, 255, 100), (self.x + 2, self.height + self.pipe_gap), 
                        (self.x + 2, SCREEN_HEIGHT - 50), 3)
        
        # Right shadow
        pygame.draw.line(screen, (20, 80, 20), (self.x + PIPE_WIDTH - 2, 0), 
                        (self.x + PIPE_WIDTH - 2, self.height), 2)
        pygame.draw.line(screen, (20, 80, 20), (self.x + PIPE_WIDTH - 2, self.height + self.pipe_gap), 
                        (self.x + PIPE_WIDTH - 2, SCREEN_HEIGHT - 50), 2)
    
    def collides_with(self, bird):
        bird_rect = bird.get_rect()
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bottom_rect)
    
    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

class ShooterBird:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 25
        self.velocity_y = 0
        self.speed = 4
        self.health = 3
        self.max_health = 3
        self.last_shot = 0
        self.shoot_cooldown = 200  # milliseconds
        
    def move_up(self):
        if self.y > 50:  # Top boundary
            self.y -= self.speed
            
    def move_down(self):
        if self.y < SCREEN_HEIGHT - 100:  # Bottom boundary (above ground)
            self.y += self.speed
    
    def can_shoot(self):
        import pygame
        current_time = pygame.time.get_ticks()
        return current_time - self.last_shot > self.shoot_cooldown
    
    def shoot(self):
        import pygame
        if self.can_shoot():
            self.last_shot = pygame.time.get_ticks()
            return Bullet(self.x + self.size, self.y + self.size // 2)
        return None
        
    def update(self):
        # Remove bobbing animation to prevent conflicts with movement controls
        pass
    
    def draw(self, screen):
        # Draw shooter bird with health indicator
        # Main body (enhanced bird design)
        bird_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        
        # Bird body with gradient
        for i in range(self.size):
            ratio = i / self.size
            color_r = int(255 * (1 - ratio * 0.2))
            color_g = int(215 * (1 - ratio * 0.1))
            color_b = int(0 + ratio * 100)
            pygame.draw.line(screen, (color_r, color_g, color_b), 
                           (self.x, self.y + i), (self.x + self.size, self.y + i))
        
        # Bird details
        pygame.draw.circle(screen, (255, 255, 255), (self.x + 8, self.y + 8), 3)  # Eye
        pygame.draw.circle(screen, (0, 0, 0), (self.x + 9, self.y + 8), 1)  # Pupil
        pygame.draw.polygon(screen, (255, 165, 0), 
                          [(self.x + self.size, self.y + 10), 
                           (self.x + self.size + 5, self.y + 12), 
                           (self.x + self.size, self.y + 14)])  # Beak
        
        # Health indicator
        health_bar_width = 30
        health_bar_height = 4
        health_x = self.x - 5
        health_y = self.y - 10
        
        # Background bar
        pygame.draw.rect(screen, (100, 100, 100), 
                        (health_x, health_y, health_bar_width, health_bar_height))
        
        # Health bar
        health_ratio = self.health / self.max_health
        health_color = (255, int(255 * health_ratio), 0) if health_ratio > 0.5 else (255, 0, 0)
        pygame.draw.rect(screen, health_color, 
                        (health_x, health_y, health_bar_width * health_ratio, health_bar_height))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 8
        self.size = 4
        self.active = True
        
    def update(self):
        self.x += self.speed
        # Remove bullet if it goes off screen
        if self.x > SCREEN_WIDTH:
            self.active = False
    
    def draw(self, screen):
        if self.active:
            # Draw bullet with glow effect
            pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), self.size)
            pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), self.size - 1)
    
    def get_rect(self):
        return pygame.Rect(self.x - self.size, self.y - self.size, self.size * 2, self.size * 2)

class ZombieBird:
    def __init__(self, x):
        self.x = x
        self.y = random.randint(60, SCREEN_HEIGHT - 150)
        self.size = 20
        self.speed = 2
        self.health = 2
        self.max_health = 2
        self.hit_recently = False
        self.hit_timer = 0
        
    def update(self):
        self.x -= self.speed
        
        # Reset hit effect
        if self.hit_recently:
            self.hit_timer -= 1
            if self.hit_timer <= 0:
                self.hit_recently = False
        
        # Slight vertical movement
        import time
        self.y += math.sin(time.time() * 3 + self.x * 0.01) * 0.5
    
    def take_damage(self):
        self.health -= 1
        self.hit_recently = True
        self.hit_timer = 10
        return self.health <= 0
    
    def draw(self, screen):
        # Zombie bird color (greenish with red eyes)
        zombie_color = (100, 150, 50) if not self.hit_recently else (255, 100, 100)
        
        # Main body
        bird_rect = pygame.Rect(self.x, self.y, self.size, self.size)
        pygame.draw.ellipse(screen, zombie_color, bird_rect)
        
        # Red glowing eyes
        pygame.draw.circle(screen, (255, 0, 0), (self.x + 6, self.y + 6), 2)
        pygame.draw.circle(screen, (255, 0, 0), (self.x + 14, self.y + 6), 2)
        
        # Dark beak
        pygame.draw.polygon(screen, (50, 50, 50), 
                          [(self.x + self.size, self.y + 8), 
                           (self.x + self.size + 4, self.y + 10), 
                           (self.x + self.size, self.y + 12)])
        
        # Health indicator
        if self.health < self.max_health:
            health_ratio = self.health / self.max_health
            health_color = (255, int(255 * health_ratio), 0)
            pygame.draw.rect(screen, health_color, 
                           (self.x, self.y - 5, self.size * health_ratio, 2))
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)
    
    def is_off_screen(self):
        return self.x < -self.size

# Legacy GeometryDashCube class removed - replaced with direct ShooterBird usage

# Zombie Bird Shooter replacement for GeometryDashObstacle
class ZombieBirdManager:
    def __init__(self):
        self.zombie_birds = []
        self.spawn_timer = 0
        self.spawn_interval = 120  # frames between spawns
        
    def update(self):
        # Update existing zombie birds
        for zombie in self.zombie_birds[:]:
            zombie.update()
            if zombie.is_off_screen() or zombie.health <= 0:
                self.zombie_birds.remove(zombie)
        
        # Spawn new zombie birds
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_zombie()
    
    def spawn_zombie(self):
        zombie_x = SCREEN_WIDTH + 20
        self.zombie_birds.append(ZombieBird(zombie_x))
    
    def draw(self, screen):
        for zombie in self.zombie_birds:
            zombie.draw(screen)
    
    def check_bullet_collisions(self, bullets):
        hits = 0
        for bullet in bullets[:]:
            if not bullet.active:
                continue
            for zombie in self.zombie_birds[:]:
                if bullet.get_rect().colliderect(zombie.get_rect()):
                    bullet.active = False
                    if zombie.take_damage():
                        hits += 1
                    break
        return hits
    
    def check_shooter_collision(self, shooter_bird):
        shooter_rect = shooter_bird.get_rect()
        for zombie in self.zombie_birds:
            if shooter_rect.colliderect(zombie.get_rect()):
                shooter_bird.health -= 1
                self.zombie_birds.remove(zombie)
                return True
        return False
    
    def clear(self):
        self.zombie_birds.clear()
        self.spawn_timer = 0

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Flappy Bird - 4 Levels Edition")
        self.clock = pygame.time.Clock()
        
        # Player system
        self.player_data = PlayerData()
        self.name_input_mode = False
        self.text_input = None
        self.show_home_page = True  # Start with home page
        
        # Level system
        self.current_level = 1
        self.level_config = LEVEL_CONFIG[self.current_level]
        self.level_selection = False  # Start with home page instead
        
        # Game states
        self.game_over_options = False  # New state for game over menu
        
        # Game objects
        self.bird = Bird(self.level_config['jump_strength'])
        self.pipes = []
        self.clouds = []
        self.particles = []
        self.score = 0  # Standard starting score
        self.game_over = False
        self.game_started = False
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        # Visual effects
        self.background_offset = 0
        self.score_animation = 0
        self.screen_shake = 0
        
        # Zombie Bird Shooter mode (for Fantastic level)
        self.shooter_mode = False
        self.shooter_bird = None
        self.zombie_manager = ZombieBirdManager()
        self.bullets = []
        self.mode_switch_score = 0  # Track when to switch modes
        self.mode_transition_effect = 0
        self.shooter_score = 0  # Score in shooter mode
        
        # Initialize sounds
        try:
            self.jump_sound = SoundGenerator.generate_jump_sound()
            self.score_sound = SoundGenerator.generate_score_sound()
            self.game_over_sound = SoundGenerator.generate_game_over_sound()
            self.shooter_gun_sound = SoundGenerator.generate_shooter_gun_sound()
            self.sounds_enabled = True
            print("✓ Sound system initialized successfully!")
        except Exception as e:
            self.sounds_enabled = False
            print(f"Sound initialization failed: {e}")
            print("Running without sound.")
        
        # Add initial elements (only if in game)
        if not (self.level_selection or self.show_home_page):
            self.pipes.append(Pipe(SCREEN_WIDTH, self.level_config['pipe_gap'], self.level_config['pipe_speed']))
        for _ in range(3):
            self.clouds.append(Cloud())
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # Handle name input mode
            if self.name_input_mode and self.text_input:
                result = self.text_input.handle_event(event)
                if result is not None:
                    if result:  # If name was entered
                        self.player_data.set_current_player(result)
                        self.name_input_mode = False
                        self.game_over_options = True
                    continue
            
            elif event.type == pygame.KEYDOWN:
                if self.show_home_page:
                    if event.key == pygame.K_SPACE:
                        self.show_home_page = False
                        self.level_selection = True
                    elif event.key == pygame.K_ESCAPE:
                        return False
                elif self.game_over_options:
                    if event.key == pygame.K_1:  # Restart
                        self.restart_game()
                    elif event.key == pygame.K_2:  # Level Select
                        self.back_to_level_selection()
                    elif event.key == pygame.K_3:  # Home Page
                        self.back_to_home()
                    elif event.key == pygame.K_ESCAPE:
                        self.back_to_home()
                elif self.level_selection:
                    if event.key == pygame.K_1:
                        self.select_level(1)
                    elif event.key == pygame.K_2:
                        self.select_level(2)
                    elif event.key == pygame.K_3:
                        self.select_level(3)
                    elif event.key == pygame.K_4:
                        self.select_level(4)
                    elif event.key == pygame.K_ESCAPE:
                        self.back_to_home()
                elif event.key == pygame.K_SPACE:
                    if not self.game_over and not self.game_started:
                        self.game_started = True
                        if self.current_level == 4 and self.shooter_mode and self.shooter_bird:
                            # Start shooting in shooter mode
                            bullet = self.shooter_bird.shoot()
                            if bullet:
                                self.bullets.append(bullet)
                                # Play shooter gun sound
                                if self.sounds_enabled:
                                    self.shooter_gun_sound.play()
                        else:
                            self.bird.jump()
                            # Play jump sound
                            if self.sounds_enabled:
                                self.jump_sound.play()
                    elif not self.game_over:
                        if self.current_level == 4 and self.shooter_mode and self.shooter_bird:
                            # Shoot bullets in shooter mode
                            bullet = self.shooter_bird.shoot()
                            if bullet:
                                self.bullets.append(bullet)
                                # Play shooter gun sound
                                if self.sounds_enabled:
                                    self.shooter_gun_sound.play()
                        else:
                            self.bird.jump()
                            # Play jump sound
                            if self.sounds_enabled:
                                self.jump_sound.play()
                # Add UP and DOWN arrow key controls for shooter mode
                elif event.key == pygame.K_UP:
                    if (self.current_level == 4 and self.shooter_mode and self.shooter_bird and 
                        not self.game_over and self.game_started):
                        self.shooter_bird.move_up()
                elif event.key == pygame.K_DOWN:
                    if (self.current_level == 4 and self.shooter_mode and self.shooter_bird and 
                        not self.game_over and self.game_started):
                        self.shooter_bird.move_down()
                elif event.key == pygame.K_ESCAPE:
                    if self.game_started or self.game_over:
                        self.back_to_home()
                    else:
                        return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.show_home_page:
                    self.show_home_page = False
                    self.level_selection = True
                elif self.game_over_options:
                    mouse_x, mouse_y = event.pos
                    if 120 <= mouse_y <= 170:  # Restart button
                        self.restart_game()
                    elif 180 <= mouse_y <= 230:  # Level Select button
                        self.back_to_level_selection()
                    elif 240 <= mouse_y <= 290:  # Home button
                        self.back_to_home()
                elif self.level_selection:
                    # Handle level selection clicks
                    mouse_x, mouse_y = event.pos
                    if 150 <= mouse_y <= 200:  # Level 1 area
                        self.select_level(1)
                    elif 220 <= mouse_y <= 270:  # Level 2 area
                        self.select_level(2)
                    elif 290 <= mouse_y <= 340:  # Level 3 area
                        self.select_level(3)
                    elif 360 <= mouse_y <= 410:  # Level 4 area
                        self.select_level(4)
                elif not self.game_over and not self.game_started:
                    self.game_started = True
                    if self.current_level == 4 and self.shooter_mode and self.shooter_bird:
                        bullet = self.shooter_bird.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                            # Play shooter gun sound
                            if self.sounds_enabled:
                                self.shooter_gun_sound.play()
                    else:
                        self.bird.jump()
                        # Play jump sound
                        if self.sounds_enabled:
                            self.jump_sound.play()
                elif not self.game_over:
                    if self.current_level == 4 and self.shooter_mode and self.shooter_bird:
                        bullet = self.shooter_bird.shoot()
                        if bullet:
                            self.bullets.append(bullet)
                            # Play shooter gun sound
                            if self.sounds_enabled:
                                self.shooter_gun_sound.play()
                    else:
                        self.bird.jump()
                        # Play jump sound
                        if self.sounds_enabled:
                            self.jump_sound.play()
                else:
                    self.restart_game()
        return True
    
    def select_level(self, level):
        """Select a game level and start the game"""
        self.current_level = level
        self.level_config = LEVEL_CONFIG[level]
        self.level_selection = False
        self.game_started = False
        self.game_over = False
        self.score = 0
        
        # Create new bird and pipes with level settings
        self.bird = Bird(self.level_config['jump_strength'])
        self.pipes = [Pipe(SCREEN_WIDTH, self.level_config['pipe_gap'], self.level_config['pipe_speed'])]
        self.particles = []
        self.screen_shake = 0
        self.score_animation = 0
        
        # Update window caption
        pygame.display.set_caption(f"Flappy Bird - Level {level} ({self.level_config['name']})")
    
    def back_to_level_selection(self):
        """Return to level selection screen"""
        self.level_selection = True
        self.show_home_page = False
        self.game_over_options = False
        self.name_input_mode = False
        self.game_started = False
        self.game_over = False
        pygame.display.set_caption("Flappy Bird - Select Level")
    
    def back_to_home(self):
        """Return to home page"""
        self.show_home_page = True
        self.level_selection = False
        self.game_over_options = False
        self.name_input_mode = False
        self.game_started = False
        self.game_over = False
        pygame.display.set_caption("Flappy Bird - Home")
    
    def handle_game_over(self):
        """Handle game over logic"""
        if not self.player_data.current_player:
            # Ask for player name
            self.name_input_mode = True
            self.text_input = TextInput(SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 200, 30, self.font)
        else:
            # Update player data and show options
            self.player_data.update_score(self.current_level, self.score)
            self.game_over_options = True
    
    def add_explosion_particles(self, x, y):
        """Add explosion particles when bird crashes"""
        for _ in range(15):
            self.particles.append(Particle(x, y, (255, 100, 100)))
    
    def add_score_particles(self, x, y):
        """Add particles when scoring"""
        for _ in range(8):
            self.particles.append(Particle(x, y, (255, 255, 0)))
    
    def draw_gradient_background(self):
        """Draw gradient background with parallax effect"""
        # Use dark theme for Fantastic level
        if self.current_level == 4:
            for y in range(SCREEN_HEIGHT - 50):
                ratio = y / (SCREEN_HEIGHT - 50)
                color = [
                    int(GRADIENT_DARK[0][i] * (1 - ratio) + GRADIENT_DARK[2][i] * ratio)
                    for i in range(3)
                ]
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        else:
            for y in range(SCREEN_HEIGHT - 50):
                # Create gradient from light blue to darker blue
                ratio = y / (SCREEN_HEIGHT - 50)
                color = [
                    int(GRADIENT_BLUE[0][i] * (1 - ratio) + GRADIENT_BLUE[2][i] * ratio)
                    for i in range(3)
                ]
                pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
    
    def draw_ground(self):
        """Draw detailed ground with texture"""
        ground_y = SCREEN_HEIGHT - 50
        
        # Use dark theme colors for Fantastic level
        if self.current_level == 4:
            ground_colors = DARK_GROUND_COLORS
            texture_color = (60, 60, 70)
        else:
            ground_colors = GROUND_COLORS
            texture_color = (100, 50, 0)
        
        # Draw ground layers with gradient
        for i in range(50):
            ratio = i / 50
            if ratio < 0.3:
                color = ground_colors[0]
            elif ratio < 0.7:
                color = ground_colors[1]
            else:
                color = ground_colors[2]
            pygame.draw.line(self.screen, color, (0, ground_y + i), (SCREEN_WIDTH, ground_y + i))
        
        # Add ground details/texture
        for x in range(0, SCREEN_WIDTH, 20):
            offset_x = (x + self.background_offset) % 40
            pygame.draw.line(self.screen, texture_color, 
                           (offset_x, ground_y), (offset_x, SCREEN_HEIGHT), 2)
    
    def draw_level_selection(self):
        """Draw the level selection screen"""
        # Draw gradient background
        self.draw_gradient_background()
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        # Draw title
        title_text = self.big_font.render("SELECT LEVEL", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Draw level options
        y_positions = [130, 200, 270, 340]
        for i, level in enumerate([1, 2, 3, 4]):
            config = LEVEL_CONFIG[level]
            y = y_positions[i]
            
            # Level button background (special styling for Level 4)
            button_rect = pygame.Rect(50, y, SCREEN_WIDTH - 100, 40)
            if level == 4:
                # Animated gradient for Fantastic level
                for j in range(button_rect.width):
                    gradient_ratio = j / button_rect.width
                    color = [
                        int(GRADIENT_PURPLE[0][k] * (1 - gradient_ratio) + GRADIENT_PURPLE[2][k] * gradient_ratio)
                        for k in range(3)
                    ]
                    pygame.draw.line(self.screen, color, 
                                   (button_rect.x + j, button_rect.y), 
                                   (button_rect.x + j, button_rect.y + button_rect.height))
                pygame.draw.rect(self.screen, config['color'], button_rect, 3)
            else:
                pygame.draw.rect(self.screen, (50, 50, 50), button_rect)
                pygame.draw.rect(self.screen, config['color'], button_rect, 3)
            
            # Level info text
            level_text = self.font.render(f"Level {level}: {config['name']}", True, config['color'])
            level_rect = level_text.get_rect(center=(SCREEN_WIDTH//2, y + 10))
            self.screen.blit(level_text, level_rect)
            
            # Level details
            if level == 1:
                details = "Easy - Large gaps, gentle jumps"
            elif level == 2:
                details = "Medium - Smaller gaps, faster pipes"
            elif level == 3:
                details = "Hard - Small gaps, higher jumps"
            else:  # Level 4
                details = "Fantastic - Dark theme, Zombie Bird Shooter mode!"
            
            detail_color = (255, 215, 0) if level == 4 else (200, 200, 200)
            detail_text = self.small_font.render(details, True, detail_color)
            detail_rect = detail_text.get_rect(center=(SCREEN_WIDTH//2, y + 25))
            self.screen.blit(detail_text, detail_rect)
            
            # High score for this level
            stats = self.player_data.get_player_stats()
            if stats and stats['high_scores'][level] > 0:
                score_text = self.small_font.render(f"Best: {stats['high_scores'][level]}", True, (255, 215, 0))
                self.screen.blit(score_text, (SCREEN_WIDTH - 100, y + 10))
        
        # Instructions
        instruction_text = self.small_font.render("Press 1, 2, 3, or 4 to select level | Click on level | ESC: Home", True, (180, 180, 180))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 430))
        self.screen.blit(instruction_text, instruction_rect)
    
    def draw_home_page(self):
        """Draw a tidy and well-organized home page"""
        import time
        
        # Draw gradient background
        self.draw_gradient_background()
        
        # Draw clouds (minimal animation)
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        # Draw ground
        self.draw_ground()
        
        # Clean title section
        time_offset = time.time()
        title_bounce = int(math.sin(time_offset * 1.2) * 1)  # Very subtle bounce
        
        # Main title with clean shadow
        shadow_text = self.big_font.render("FLAPPY BIRD", True, (80, 80, 80))
        shadow_rect = shadow_text.get_rect(center=(SCREEN_WIDTH//2 + 2, 70 + title_bounce + 2))
        self.screen.blit(shadow_text, shadow_rect)
        
        title_text = self.big_font.render("FLAPPY BIRD", True, (255, 215, 0))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 70 + title_bounce))
        self.screen.blit(title_text, title_rect)
        
        # Simplified subtitle
        subtitle_text = self.small_font.render("Multi-Level Adventure with Zombie Shooter", True, (220, 220, 220))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, 105))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Organized content sections with proper spacing
        self.draw_tidy_level_preview()
        self.draw_tidy_player_section()
        self.draw_tidy_start_section(time_offset)
    
    def draw_tidy_level_preview(self):
        """Draw a tidy and organized level preview section"""
        # Section with clean border
        section_y = 140
        section_height = 120
        
        # Background panel
        panel_rect = pygame.Rect(20, section_y, SCREEN_WIDTH - 40, section_height)
        panel_surface = pygame.Surface((SCREEN_WIDTH - 40, section_height))
        panel_surface.set_alpha(30)
        panel_surface.fill((50, 50, 100))
        self.screen.blit(panel_surface, (20, section_y))
        pygame.draw.rect(self.screen, (100, 100, 150), panel_rect, 2)
        
        # Section title
        title_text = self.small_font.render("SELECT DIFFICULTY LEVEL", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, section_y + 15))
        self.screen.blit(title_text, title_rect)
        
        # Level options in a clean grid
        levels = [
            {"num": 1, "name": "Easy", "color": (100, 255, 100), "desc": "Beginner"},
            {"num": 2, "name": "Medium", "color": (255, 255, 100), "desc": "Moderate"},
            {"num": 3, "name": "Hard", "color": (255, 100, 100), "desc": "Challenge"},
            {"num": 4, "name": "Fantastic", "color": (255, 100, 255), "desc": "Dual-Mode"}
        ]
        
        box_width = 90
        box_height = 45
        spacing = 15
        total_width = len(levels) * box_width + (len(levels) - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        for i, level in enumerate(levels):
            x = start_x + i * (box_width + spacing)
            y = section_y + 40
            
            # Clean level box
            box_rect = pygame.Rect(x, y, box_width, box_height)
            
            # Subtle background
            bg_surface = pygame.Surface((box_width, box_height))
            bg_surface.set_alpha(80)
            bg_surface.fill(level["color"])
            self.screen.blit(bg_surface, (x, y))
            
            # Clean border
            pygame.draw.rect(self.screen, level["color"], box_rect, 2)
            
            # Level number and name
            num_text = self.small_font.render(str(level["num"]), True, (255, 255, 255))
            num_rect = num_text.get_rect(center=(x + box_width//2, y + 12))
            self.screen.blit(num_text, num_rect)
            
            name_text = self.small_font.render(level["name"], True, (255, 255, 255))
            name_rect = name_text.get_rect(center=(x + box_width//2, y + 28))
            self.screen.blit(name_text, name_rect)
    
    def draw_clean_player_info(self):
        """Draw clean player information - deprecated, now handled by draw_tidy_player_section"""
        # This method is no longer used since home page redesign
        # Player info is drawn directly in draw_home_page() via draw_tidy_player_section()
        pass
    
    def draw_tidy_player_section(self):
        """Draw a tidy player information section"""
        stats = self.player_data.get_player_stats()
        if not stats:
            return
            
        section_y = 280
        section_height = 85
        
        # Clean stats panel
        panel_rect = pygame.Rect(40, section_y, SCREEN_WIDTH - 80, section_height)
        panel_surface = pygame.Surface((SCREEN_WIDTH - 80, section_height))
        panel_surface.set_alpha(40)
        panel_surface.fill((50, 100, 50))
        self.screen.blit(panel_surface, (40, section_y))
        pygame.draw.rect(self.screen, (100, 150, 100), panel_rect, 2)
        
        # Player name with nice styling
        player_text = self.small_font.render(f"PLAYER: {self.player_data.current_player.upper()}", True, (255, 255, 100))
        player_rect = player_text.get_rect(center=(SCREEN_WIDTH//2, section_y + 18))
        self.screen.blit(player_text, player_rect)
        
        # Best scores in organized layout
        y_offset = section_y + 40
        spacing = 85
        start_x = (SCREEN_WIDTH - (4 * spacing - 20)) // 2
        
        for i, level in enumerate([1, 2, 3, 4]):
            x = start_x + i * spacing
            score = stats['high_scores'][level]
            
            # Level box
            level_rect = pygame.Rect(x, y_offset, 65, 30)
            level_color = [(100, 255, 100), (255, 255, 100), (255, 100, 100), (255, 100, 255)][level-1]
            
            # Background
            bg_surface = pygame.Surface((65, 30))
            bg_surface.set_alpha(60)
            bg_surface.fill(level_color)
            self.screen.blit(bg_surface, (x, y_offset))
            pygame.draw.rect(self.screen, level_color, level_rect, 2)
            
            # Level number
            level_text = self.small_font.render(f"L{level}", True, (255, 255, 255))
            level_text_rect = level_text.get_rect(center=(x + 32, y_offset + 10))
            self.screen.blit(level_text, level_text_rect)
            
            # Score
            score_text = self.small_font.render(str(score), True, (255, 255, 255))
            score_text_rect = score_text.get_rect(center=(x + 32, y_offset + 22))
            self.screen.blit(score_text, score_text_rect)

    def draw_tidy_start_section(self, time_offset):
        """Draw a tidy and organized start instruction section"""
        section_y = 390
        section_height = 80
        
        # Clean instruction panel
        panel_rect = pygame.Rect(60, section_y, SCREEN_WIDTH - 120, section_height)
        panel_surface = pygame.Surface((SCREEN_WIDTH - 120, section_height))
        panel_surface.set_alpha(50)
        panel_surface.fill((100, 50, 100))
        self.screen.blit(panel_surface, (60, section_y))
        pygame.draw.rect(self.screen, (150, 100, 150), panel_rect, 2)
        
        # Animated "START" indicator with subtle bounce
        bounce = int(math.sin(time_offset * 3) * 3)
        start_text = self.font.render("▶ START GAME", True, (255, 255, 100))
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH//2, section_y + 20 + bounce))
        self.screen.blit(start_text, start_rect)
        
        # Control instructions in clean format
        controls = [
            "SPACE - Start Game",
            "↑↓ - Navigate Menu",
            "ESC - Exit"
        ]
        
        for i, control in enumerate(controls):
            x = SCREEN_WIDTH//2 - 120 + i * 80
            y = section_y + 50
            
            control_text = self.small_font.render(control, True, (200, 200, 200))
            control_rect = control_text.get_rect(center=(x, y))
            self.screen.blit(control_text, control_rect)
        
        # Subtle pulsing bottom border
        pulse = int(abs(math.sin(time_offset * 2)) * 100 + 155)
        bottom_y = section_y + section_height + 5
        pygame.draw.line(self.screen, (pulse, pulse//2, pulse), 
                        (80, bottom_y), (SCREEN_WIDTH-80, bottom_y), 3)

    def draw_clean_leaderboard(self):
        """Draw a clean leaderboard"""
        if not self.player_data.players:
            welcome_text = self.font.render("🌟 Welcome! Your scores will appear here 🌟", True, (200, 200, 200))
            welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH//2, 370))
            self.screen.blit(welcome_text, welcome_rect)
            return
        
        # Leaderboard title
        leaderboard_title = self.font.render("🏆 Top Players", True, (255, 215, 0))
        leaderboard_rect = leaderboard_title.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(leaderboard_title, leaderboard_rect)
        
        # Top 3 players
        top_players = self.player_data.get_top_players(3)
        medals = ["🥇", "🥈", "🥉"]
        
        for i, (name, data) in enumerate(top_players):
            y = 375 + i * 25
            medal = medals[i] if i < len(medals) else "🏅"
            
            player_text = f"{medal} {name}: {data['total_score']} pts"
            player_surface = self.small_font.render(player_text, True, (255, 255, 255))
            player_rect = player_surface.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(player_surface, player_rect)
    
    def draw_game_features_showcase(self, y_pos):
        """Draw beautiful game features with icons and animations"""
        import time
        time_offset = time.time()
        
        # Features list
        features = [
            {"icon": "🐦", "text": "4 Unique Levels", "color": (255, 215, 0)},
            {"icon": "🌙", "text": "Dark Theme Mode", "color": (138, 43, 226)},
            {"icon": "🎮", "text": "Dual Gameplay", "color": (0, 255, 255)},
            {"icon": "⚡", "text": "Auto-Switch", "color": (255, 69, 0)}
        ]
        
        feature_width = SCREEN_WIDTH // 4
        for i, feature in enumerate(features):
            x = i * feature_width + feature_width // 2
            
            # Animated bounce effect
            bounce = int(math.sin(time_offset * 2 + i * 0.5) * 3)
            
            # Feature background
            bg_rect = pygame.Rect(x - 50, y_pos + bounce - 10, 100, 60)
            bg_surface = pygame.Surface((100, 60))
            bg_surface.set_alpha(100)
            bg_surface.fill(feature["color"])
            self.screen.blit(bg_surface, bg_rect)
            
            # Border with glow
            pygame.draw.rect(self.screen, feature["color"], bg_rect, 2)
            
            # Icon
            icon_text = self.font.render(feature["icon"], True, feature["color"])
            icon_rect = icon_text.get_rect(center=(x, y_pos + bounce))
            self.screen.blit(icon_text, icon_rect)
            
            # Feature text
            text_surface = self.small_font.render(feature["text"], True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x, y_pos + bounce + 25))
            self.screen.blit(text_surface, text_rect)
    
    def draw_player_stats_card(self, stats, time_offset):
        """Draw beautiful player stats card"""
        # Card position and size
        card_width = 220
        card_height = 140
        card_x = SCREEN_WIDTH - card_width - 20
        card_y = 250
        
        # Animated card background with gradient
        for i in range(card_height):
            ratio = i / card_height
            color = [
                int(30 * (1 - ratio) + 60 * ratio),
                int(30 * (1 - ratio) + 60 * ratio),
                int(50 * (1 - ratio) + 100 * ratio)
            ]
            pygame.draw.line(self.screen, color, (card_x, card_y + i), (card_x + card_width, card_y + i))
        
        # Animated border
        border_pulse = int(abs(math.sin(time_offset * 2) * 50) + 150)
        border_color = (border_pulse, 215, 0)
        pygame.draw.rect(self.screen, border_color, (card_x, card_y, card_width, card_height), 3)
        
        # Player name with crown
        crown_text = self.font.render("👑", True, (255, 215, 0))
        self.screen.blit(crown_text, (card_x + 10, card_y + 10))
        
        name_text = self.small_font.render(f"{self.player_data.current_player}", True, (255, 215, 0))
        self.screen.blit(name_text, (card_x + 35, card_y + 15))
        
        # Level scores with animated icons
        level_icons = ["🟢", "🟡", "🔴", "🟣"]
        for i, level in enumerate([1, 2, 3, 4]):
            y = card_y + 40 + i * 20
            
            # Animated icon
            icon_bounce = int(math.sin(time_offset * 3 + i * 0.3) * 2)
            icon_text = self.small_font.render(level_icons[i], True, LEVEL_CONFIG[level]['color'])
            self.screen.blit(icon_text, (card_x + 10, y + icon_bounce))
            
            # Score
            score_text = self.small_font.render(f"Level {level}: {stats['high_scores'][level]}", True, (255, 255, 255))
            self.screen.blit(score_text, (card_x + 35, y))
        
        # Total score with sparkle effect
        total_y = card_y + card_height - 25
        sparkle_text = self.small_font.render("✨", True, (255, 255, 255))
        self.screen.blit(sparkle_text, (card_x + 10, total_y))
        
        total_text = self.small_font.render(f"Total: {stats['total_score']}", True, (255, 215, 0))
        self.screen.blit(total_text, (card_x + 35, total_y))
    
    def draw_beautiful_leaderboard(self, time_offset):
        """Draw beautiful animated leaderboard"""
        if not self.player_data.players:
            # Welcome message with animation
            welcome_pulse = abs(math.sin(time_offset))
            welcome_color = (255, int(200 + welcome_pulse * 55), int(200 + welcome_pulse * 55))
            welcome_text = self.font.render("🌟 Welcome to Flappy Bird! 🌟", True, welcome_color)
            welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH//2, 250))
            self.screen.blit(welcome_text, welcome_rect)
            return
        
        # Leaderboard section
        top_players = self.player_data.get_top_players(3)
        if top_players:
            # Title with glow
            leaderboard_text = self.font.render("🏆 Hall of Fame 🏆", True, (255, 215, 0))
            leaderboard_rect = leaderboard_text.get_rect(center=(SCREEN_WIDTH//2, 220))
            
            # Glow effect
            for offset in [(1, 1), (-1, -1), (1, -1), (-1, 1)]:
                glow_text = self.font.render("🏆 Hall of Fame 🏆", True, (200, 150, 0))
                glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + offset[0], 220 + offset[1]))
                self.screen.blit(glow_text, glow_rect)
            self.screen.blit(leaderboard_text, leaderboard_rect)
            
            # Player entries with medals
            medals = ["🥇", "🥈", "🥉"]
            for i, (name, data) in enumerate(top_players):
                y = 250 + i * 25
                
                # Animated background for each entry
                entry_bounce = int(math.sin(time_offset * 2 + i * 0.8) * 2)
                entry_bg = pygame.Rect(SCREEN_WIDTH//2 - 120, y + entry_bounce - 5, 240, 20)
                entry_surface = pygame.Surface((240, 20))
                entry_surface.set_alpha(80)
                entry_surface.fill((100, 100, 150))
                self.screen.blit(entry_surface, entry_bg)
                
                # Medal and player info
                medal_text = self.small_font.render(medals[i], True, (255, 255, 255))
                self.screen.blit(medal_text, (SCREEN_WIDTH//2 - 100, y + entry_bounce))
                
                player_info = f"{name} - {data['total_score']} pts"
                player_text = self.small_font.render(player_info, True, (255, 255, 255))
                self.screen.blit(player_text, (SCREEN_WIDTH//2 - 70, y + entry_bounce))
    
    def draw_fantastic_showcase(self):
        """Draw an animated showcase for the Fantastic level"""
        import time
        
        # Showcase box
        showcase_width = 400
        showcase_height = 120
        showcase_x = (SCREEN_WIDTH - showcase_width) // 2
        showcase_y = SCREEN_HEIGHT // 2 - 60
        
        # Animated gradient background
        time_offset = time.time() * 2
        for i in range(showcase_height):
            ratio = (i + time_offset * 10) % showcase_height / showcase_height
            color = [
                int(GRADIENT_PURPLE[0][j] * (1 - ratio) + GRADIENT_PURPLE[2][j] * ratio)
                for j in range(3)
            ]
            pygame.draw.line(self.screen, color, 
                           (showcase_x, showcase_y + i), 
                           (showcase_x + showcase_width, showcase_y + i))
        
        # Animated border
        border_pulse = int(abs(math.sin(time_offset) * 50) + 150)
        border_color = (border_pulse, border_pulse//2, 255)
        pygame.draw.rect(self.screen, border_color, 
                        (showcase_x, showcase_y, showcase_width, showcase_height), 3)
        
        # Main title with glow effect
        title_pulse = abs(math.sin(time_offset * 1.5))
        title_color = (255, int(215 + title_pulse * 40), int(title_pulse * 255))
        
        fantastic_text = self.font.render("✨ FANTASTIC LEVEL ✨", True, title_color)
        fantastic_rect = fantastic_text.get_rect(center=(SCREEN_WIDTH//2, showcase_y + 25))
        
        # Glow effect
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_text = self.font.render("✨ FANTASTIC LEVEL ✨", True, (100, 50, 150))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + offset[0], showcase_y + 25 + offset[1]))
            self.screen.blit(glow_text, glow_rect)
        self.screen.blit(fantastic_text, fantastic_rect)
        
        # Subtitle
        subtitle_text = self.small_font.render("🌙 Dark Theme • 🎮 Dual Game Modes • ⚡ Auto-Switch Every 10 Points", True, (200, 255, 255))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, showcase_y + 50))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Mode indicators
        flappy_text = self.small_font.render("🐦 Flappy Mode", True, (255, 215, 0))
        shooter_text = self.small_font.render("🧟 Zombie Shooter", True, (255, 100, 100))
        
        flappy_rect = flappy_text.get_rect(center=(SCREEN_WIDTH//2 - 80, showcase_y + 75))
        shooter_rect = shooter_text.get_rect(center=(SCREEN_WIDTH//2 + 80, showcase_y + 75))
        
        self.screen.blit(flappy_text, flappy_rect)
        
        # Animated separator
        separator_offset = int(math.sin(time_offset * 3) * 5)
        pygame.draw.line(self.screen, (255, 255, 255), 
                        (SCREEN_WIDTH//2 - 20, showcase_y + 75 + separator_offset), 
                        (SCREEN_WIDTH//2 + 20, showcase_y + 75 + separator_offset), 2)
        
        self.screen.blit(shooter_text, shooter_rect)
        
        # Call to action
        cta_pulse = abs(math.sin(time_offset * 2))
        cta_color = (255, 255, int(150 + cta_pulse * 105))
        cta_text = self.small_font.render("Press 4 or click Level 4 to experience the magic!", True, cta_color)
        cta_rect = cta_text.get_rect(center=(SCREEN_WIDTH//2, showcase_y + 95))
        self.screen.blit(cta_text, cta_rect)
        
        # Floating particles effect
        for i in range(8):
            particle_time = time_offset + i * 0.5
            particle_x = showcase_x + 50 + i * 40 + math.sin(particle_time) * 20
            particle_y = showcase_y - 10 + math.sin(particle_time * 1.5) * 15
            particle_size = int(3 + math.sin(particle_time * 2) * 2)
            particle_alpha = int(100 + math.sin(particle_time * 1.2) * 50)
            
            # Create particle surface with alpha
            particle_surface = pygame.Surface((particle_size * 2, particle_size * 2))
            particle_surface.set_alpha(particle_alpha)
            particle_color = [int(GRADIENT_PURPLE[1][j]) for j in range(3)]
            pygame.draw.circle(particle_surface, particle_color, (particle_size, particle_size), particle_size)
            self.screen.blit(particle_surface, (particle_x - particle_size, particle_y - particle_size))
    
    def draw_name_input(self):
        """Draw the name input screen"""
        # Draw game background with overlay
        self.draw_gradient_background()
        for cloud in self.clouds:
            cloud.draw(self.screen)
        self.draw_ground()
        for pipe in self.pipes:
            pipe.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        self.bird.draw(self.screen)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.big_font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
        self.screen.blit(score_text, score_rect)
        
        # Name input instruction
        instruction_text = self.font.render("Enter your name:", True, WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Draw text input
        if self.text_input:
            self.text_input.draw(self.screen)
        
        # Instructions
        enter_text = self.small_font.render("Press ENTER to continue", True, (180, 180, 180))
        enter_rect = enter_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
        self.screen.blit(enter_text, enter_rect)
    
    def draw_game_over_options(self):
        """Draw the game over options screen"""
        # Draw game background with overlay
        self.draw_gradient_background()
        for cloud in self.clouds:
            cloud.draw(self.screen)
        self.draw_ground()
        for pipe in self.pipes:
            pipe.draw(self.screen)
        for particle in self.particles:
            particle.draw(self.screen)
        self.bird.draw(self.screen)
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text with glow
        for offset in [(2, 2), (-2, -2), (2, -2), (-2, 2)]:
            glow_text = self.big_font.render("GAME OVER", True, (100, 0, 0))
            glow_rect = glow_text.get_rect(center=(SCREEN_WIDTH//2 + offset[0], 80 + offset[1]))
            self.screen.blit(glow_text, glow_rect)
        
        game_over_text = self.big_font.render("GAME OVER", True, (255, 100, 100))
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH//2, 80))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Player and score info
        if self.player_data.current_player:
            player_text = self.font.render(f"Player: {self.player_data.current_player}", True, (255, 215, 0))
            player_rect = player_text.get_rect(center=(SCREEN_WIDTH//2, 120))
            self.screen.blit(player_text, player_rect)
        
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 150))
        self.screen.blit(score_text, score_rect)
        
        # Check for new best
        if self.player_data.current_player:
            stats = self.player_data.get_player_stats()
            if stats and self.score == stats['high_scores'][self.current_level] and self.score > 0:
                new_best_text = self.font.render("NEW BEST!", True, (255, 215, 0))
                new_best_rect = new_best_text.get_rect(center=(SCREEN_WIDTH//2, 180))
                self.screen.blit(new_best_text, new_best_rect)
        
        # Menu options
        options = [
            ("1. Restart Level", (255, 255, 255)),
            ("2. Select Level", (255, 255, 0)),
            ("3. Home Page", (0, 255, 0))
        ]
        
        for i, (text, color) in enumerate(options):
            y = 250 + i * 60
            
            # Button background
            button_rect = pygame.Rect(50, y - 25, SCREEN_WIDTH - 100, 50)
            pygame.draw.rect(self.screen, (50, 50, 50), button_rect)
            pygame.draw.rect(self.screen, color, button_rect, 2)
            
            # Button text
            button_text = self.font.render(text, True, color)
            button_text_rect = button_text.get_rect(center=(SCREEN_WIDTH//2, y))
            self.screen.blit(button_text, button_text_rect)
        
        # Instructions
        instruction_text = self.small_font.render("Press 1, 2, or 3 | Click on option | ESC: Home", True, (180, 180, 180))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, 450))
        self.screen.blit(instruction_text, instruction_rect)
    
    def update(self):
        # Always update visual effects
        self.background_offset -= 0.5
        if self.background_offset <= -50:
            self.background_offset = 0
            
        # Update screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
            
        # Update score animation
        if self.score_animation > 0:
            self.score_animation -= 1
        
        # Always update clouds
        for cloud in self.clouds[:]:
            cloud.update()
            if cloud.is_off_screen():
                self.clouds.remove(cloud)
        
        # Add new clouds
        if random.randint(0, 200) == 0:
            self.clouds.append(Cloud())
        
        # Update text input if in name input mode
        if self.name_input_mode and self.text_input:
            self.text_input.update()
        
        # Don't update game logic if not in game
        if self.level_selection or self.show_home_page or self.game_over_options:
            return
        
        if not self.game_over and self.game_started:
            # Handle mode switching for Fantastic level (Level 4) - Zombie Bird Shooter
            if self.current_level == 4:
                # Check if we need to switch modes every 10 points
                if self.score > 0 and self.score % 10 == 0 and self.score != self.mode_switch_score:
                    self.mode_switch_score = self.score
                    self.shooter_mode = not self.shooter_mode
                    self.mode_transition_effect = 30
                    
                    if self.shooter_mode:
                        # Switch to Zombie Bird Shooter mode
                        self.shooter_bird = ShooterBird(self.bird.x, self.bird.y)
                        self.shooter_score = 0
                        self.pipes.clear()  # Remove all pipes
                        self.bullets.clear()  # Clear any existing bullets
                        self.zombie_manager.clear()  # Clear any existing zombies
                        # Ensure bird stops updating in shooter mode
                        self.bird.velocity = 0
                    else:
                        # Switch back to Flappy Bird mode
                        if self.shooter_bird:
                            self.bird.x = self.shooter_bird.x
                            self.bird.y = self.shooter_bird.y
                            self.bird.velocity = 0
                        self.shooter_bird = None
                        self.bullets.clear()
                        self.zombie_manager.clear()
                        # Ensure zombie manager is completely reset
                        self.zombie_manager = ZombieBirdManager()
                        # Add a pipe
                        self.pipes.append(Pipe(SCREEN_WIDTH, self.level_config['pipe_gap'], self.level_config['pipe_speed']))
            
            # Update based on current mode
            if self.current_level == 4 and self.shooter_mode:
                # Zombie Bird Shooter mode updates
                if self.shooter_bird:
                    self.shooter_bird.update()
                    
                    # Handle continuous key presses for smooth movement
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_UP]:
                        self.shooter_bird.move_up()
                    if keys[pygame.K_DOWN]:
                        self.shooter_bird.move_down()
                    # Note: SPACE key shooting is handled in event system to prevent conflicts
                    
                    # Update zombie manager
                    self.zombie_manager.update()
                    
                    # Update bullets
                    for bullet in self.bullets[:]:
                        bullet.update()
                        if not bullet.active:
                            self.bullets.remove(bullet)
                    
                    # Check bullet-zombie collisions
                    hits = self.zombie_manager.check_bullet_collisions(self.bullets)
                    if hits > 0:
                        self.shooter_score += hits
                        self.score += hits  # Also increase main score
                        self.score_animation = 30
                        if self.sounds_enabled:
                            self.score_sound.play()
                    
                    # Check shooter-zombie collisions
                    if self.zombie_manager.check_shooter_collision(self.shooter_bird):
                        self.screen_shake = 10
                        if self.shooter_bird.health <= 0:
                            if not self.game_over:
                                self.game_over = True
                                self.screen_shake = 15
                                self.add_explosion_particles(self.shooter_bird.x, self.shooter_bird.y)
                                if self.sounds_enabled:
                                    self.game_over_sound.play()
                                self.handle_game_over()
                    
                    # Check if shooter hits boundaries
                    if self.shooter_bird.y < 30 or self.shooter_bird.y > SCREEN_HEIGHT - 80:
                        if not self.game_over:
                            self.game_over = True
                            self.screen_shake = 15
                            self.add_explosion_particles(self.shooter_bird.x, self.shooter_bird.y)
                            if self.sounds_enabled:
                                self.game_over_sound.play()
                            self.handle_game_over()
            else:
                # Normal Flappy Bird mode - only run when NOT in shooter mode
                self.bird.update()
                
                # Check if bird hits ground or ceiling (only in flappy bird mode)
                if self.bird.y > SCREEN_HEIGHT - 50 - self.bird.radius or self.bird.y < self.bird.radius:
                    if not self.game_over:  # Only play sound once
                        self.game_over = True
                        self.screen_shake = 15
                        self.add_explosion_particles(self.bird.x, self.bird.y)
                        if self.sounds_enabled:
                            self.game_over_sound.play()
                        self.handle_game_over()
                
                # Update pipes (only in flappy bird mode)
                for pipe in self.pipes[:]:
                    pipe.update()
                    
                    # Check collision
                    if pipe.collides_with(self.bird):
                        if not self.game_over:  # Only play sound once
                            self.game_over = True
                            self.screen_shake = 15
                            self.add_explosion_particles(self.bird.x, self.bird.y)
                            if self.sounds_enabled:
                                self.game_over_sound.play()
                            self.handle_game_over()
                    
                    # Check if bird passed pipe
                    if not pipe.passed and pipe.x + PIPE_WIDTH < self.bird.x:
                        pipe.passed = True
                        self.score += 1
                        self.score_animation = 20
                        self.add_score_particles(pipe.x + PIPE_WIDTH // 2, self.bird.y)
                        if self.sounds_enabled:
                            self.score_sound.play()
                    
                    # Remove off-screen pipes
                    if pipe.is_off_screen():
                        self.pipes.remove(pipe)
                
                # Add new pipes (with progressive difficulty) - only in flappy bird mode
                pipe_spacing = max(250, 350 - self.score * 3)  # Increased base spacing and slower progression
                if len(self.pipes) == 0 or self.pipes[-1].x < SCREEN_WIDTH - pipe_spacing:
                    self.pipes.append(Pipe(SCREEN_WIDTH, self.level_config['pipe_gap'], self.level_config['pipe_speed']))
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
    
    def draw(self):
        if self.show_home_page:
            self.draw_home_page()
            pygame.display.flip()
            return
        elif self.level_selection:
            self.draw_level_selection()
            pygame.display.flip()
            return
        elif self.name_input_mode:
            self.draw_name_input()
            pygame.display.flip()
            return
        elif self.game_over_options:
            self.draw_game_over_options()
            pygame.display.flip()
            return
            
        # Calculate screen shake offset
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Draw gradient background
        self.draw_gradient_background()
        
        # Draw clouds
        for cloud in self.clouds:
            cloud.draw(self.screen)
        
        # Draw ground
        self.draw_ground()
        
        # Draw based on current mode
        if self.current_level == 4 and self.shooter_mode:
            # Draw zombie birds
            self.zombie_manager.draw(self.screen)
            
            # Draw bullets
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            # Draw shooter bird
            if self.shooter_bird:
                self.shooter_bird.draw(self.screen)
            
            # Draw mode indicator
            mode_text = self.small_font.render("🧟 ZOMBIE BIRD SHOOTER MODE 🧟", True, (255, 100, 100))
            mode_rect = mode_text.get_rect(center=(SCREEN_WIDTH//2, 30))
            self.screen.blit(mode_text, mode_rect)
            
            # Draw shooter score
            shooter_score_text = self.small_font.render(f"Zombies Killed: {self.shooter_score}", True, (255, 255, 100))
            shooter_score_rect = shooter_score_text.get_rect(center=(SCREEN_WIDTH//2, 50))
            self.screen.blit(shooter_score_text, shooter_score_rect)
            
            # Draw controls hint
            controls_text = self.small_font.render("↑↓ Move | SPACE/Click Shoot", True, (200, 200, 200))
            controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 30))
            self.screen.blit(controls_text, controls_rect)
        else:
            # Draw pipes
            for pipe in self.pipes:
                pipe.draw(self.screen)
            
            # Draw bird
            self.bird.draw(self.screen)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Mode transition effect
        if self.mode_transition_effect > 0:
            self.mode_transition_effect -= 1
            alpha = int(255 * (self.mode_transition_effect / 30))
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(alpha)
            overlay.fill((255, 255, 255))
            self.screen.blit(overlay, (0, 0))
            
            # Transition text
            if self.mode_transition_effect > 15:
                if self.shooter_mode:
                    transition_text = self.font.render("SWITCHING TO ZOMBIE SHOOTER!", True, (0, 0, 0))
                else:
                    transition_text = self.font.render("SWITCHING TO FLAPPY BIRD!", True, (0, 0, 0))
                transition_rect = transition_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                self.screen.blit(transition_text, transition_rect)
        
        # Draw level indicator
        level_text = self.small_font.render(f"Level {self.current_level} - {self.level_config['name']}", True, self.level_config['color'])
        self.screen.blit(level_text, (10 + shake_x, 10 + shake_y))
        
        # Draw score with animation
        score_scale = 1.0 + (self.score_animation / 20) * 0.3
        score_color = (255, 255, 255) if self.score_animation == 0 else (255, 255, 100)
        
        # Draw score shadow
        score_text = self.font.render(f"Score: {self.score}", True, (50, 50, 50))
        self.screen.blit(score_text, (12 + shake_x, 37 + shake_y))
        
        # Draw main score
        score_text = self.font.render(f"Score: {self.score}", True, score_color)
        if score_scale != 1.0:
            # Scale the text for animation
            scaled_size = (int(score_text.get_width() * score_scale), 
                          int(score_text.get_height() * score_scale))
            score_text = pygame.transform.scale(score_text, scaled_size)
        self.screen.blit(score_text, (10 + shake_x, 35 + shake_y))
        
        # Draw high score for current level
        if self.player_data.current_player:
            stats = self.player_data.get_player_stats()
            if stats and stats['high_scores'][self.current_level] > 0:
                high_score_text = self.small_font.render(f"Best: {stats['high_scores'][self.current_level]}", True, (200, 200, 200))
                self.screen.blit(high_score_text, (10 + shake_x, 75 + shake_y))
        
        # Draw start instructions
        if not self.game_started and not self.game_over:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Welcome text
            welcome_text = self.big_font.render("Flappy Bird", True, (255, 215, 0))
            welcome_rect = welcome_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 60))
            self.screen.blit(welcome_text, welcome_rect)
            
            # Instructions
            instruction1 = self.font.render("Press SPACE or Click to Start", True, WHITE)
            instruction1_rect = instruction1.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            self.screen.blit(instruction1, instruction1_rect)
            
            instruction2 = self.small_font.render("Navigate through the pipes!", True, (200, 200, 200))
            instruction2_rect = instruction2.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 30))
            self.screen.blit(instruction2, instruction2_rect)
            
            instruction3 = self.small_font.render("Avoid hitting pipes and ground", True, (200, 200, 200))
            instruction3_rect = instruction3.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50))
            self.screen.blit(instruction3, instruction3_rect)
        

        
        pygame.display.flip()
    
    def restart_game(self):
        self.bird = Bird(self.level_config['jump_strength'])
        self.pipes = [Pipe(SCREEN_WIDTH, self.level_config['pipe_gap'], self.level_config['pipe_speed'])]
        self.particles = []
        self.score = 0  # Standard starting score
        self.game_over = False
        self.game_over_options = False
        self.name_input_mode = False
        self.show_home_page = False
        self.level_selection = False
        self.game_started = False
        self.screen_shake = 0
        self.score_animation = 0
        
        # Reset zombie shooter mode
        self.shooter_mode = False
        self.shooter_bird = None
        self.bullets = []
        self.zombie_manager = ZombieBirdManager()
        self.shooter_score = 0
        self.mode_switch_score = 0
        self.mode_transition_effect = 0
    
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()








    