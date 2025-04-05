# junosoft-tech project #1

########################
#                       INFO.                       #
#------------------------------------------------- # #
# Rock Paper Scissors Simulation #
# Coded in saturday 5, 2025.          #                     #                                                             #
#                                                             #
#                BYE                                     #
########################

import pygame
import numpy as np
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
UNIT_SIZE = 20
FPS = 30
STATS_HEIGHT = 60

# Colors
BLACK = (0, 0, 0)
RED = (255, 50, 50)      # Rock
GREEN = (50, 255, 50)    # Paper
BLUE = (50, 50, 255)     # Scissors
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)

class Unit:
    def __init__(self, x, y, unit_type):
        self.x = x
        self.y = y
        self.type = unit_type
        self.base_speed = 2.0
        self.speed = self.base_speed
        self.size = UNIT_SIZE
        self.direction = random.uniform(0, 2 * np.pi)
        self.reproduction_counter = 0
        self.energy = 100  # New energy system

    def move(self, units):
        self.energy -= 0.1  # Energy cost for existing
        self.reproduction_counter += 1

        # Find nearest prey and predator
        nearest_prey = None
        nearest_predator = None
        min_prey_distance = float('inf')
        min_predator_distance = float('inf')

        prey_type = (self.type + 2) % 3
        predator_type = (self.type + 1) % 3

        for other in units:
            dist = np.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
            if other.type == prey_type and dist < min_prey_distance:
                min_prey_distance = dist
                nearest_prey = other
            elif other.type == predator_type and dist < min_predator_distance:
                min_predator_distance = dist
                nearest_predator = other

        # Movement behavior
        if nearest_predator and min_predator_distance < 100:
            # Run from predator
            angle = np.arctan2(nearest_predator.y - self.y, nearest_predator.x - self.x)
            self.direction = angle + np.pi
            self.speed = self.base_speed * 1.5
            self.energy -= 0.2  # Extra energy cost for running
        elif nearest_prey and min_prey_distance < 150:
            # Chase prey
            angle = np.arctan2(nearest_prey.y - self.y, nearest_prey.x - self.x)
            self.direction = angle
            self.speed = self.base_speed * 1.2
            self.energy -= 0.15  # Extra energy cost for chasing
        else:
            # Random movement
            self.direction += random.uniform(-0.3, 0.3)
            self.speed = self.base_speed

        # Move
        self.x += self.speed * np.cos(self.direction)
        self.y += self.speed * np.sin(self.direction)

        # Bounce off walls
        if self.x <= 0 or self.x >= WIDTH - self.size:
            self.direction = np.pi - self.direction
        if self.y <= 0 or self.y >= HEIGHT - self.size:
            self.direction = -self.direction

        # Keep within bounds
        self.x = max(0, min(self.x, WIDTH - self.size))
        self.y = max(0, min(self.y, HEIGHT - self.size))

    def fight(self, other):
        return ((self.type == 0 and other.type == 2) or  # Rock beats Scissors
                (self.type == 1 and other.type == 0) or  # Paper beats Rock
                (self.type == 2 and other.type == 1))    # Scissors beats Paper

def create_unit(type_id):
    x = random.randint(0, WIDTH - UNIT_SIZE)
    y = random.randint(0, HEIGHT - UNIT_SIZE - STATS_HEIGHT)
    return Unit(x, y, type_id)

# Initialize screen
screen = pygame.display.set_mode((WIDTH, HEIGHT + STATS_HEIGHT))
pygame.display.set_caption("Rock Paper Scissors Ecosystem - R/P/S: Add units, SPACE: Pause, Q: Quit")
clock = pygame.time.Clock()

# Initialize font
font = pygame.font.SysFont('Arial', 16)

# Create initial units
units = []
for _ in range(12):  # Start with 12 of each type
    for type_id in range(3):
        units.append(create_unit(type_id))

# Game loop
running = True
paused = False
frame_count = 0

while running and frame_count < 900:
    frame_count += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_SPACE:
                paused = not paused
            elif not paused:
                if event.key == pygame.K_r:
                    units.append(create_unit(0))
                    print("Added Rock")
                elif event.key == pygame.K_p:
                    units.append(create_unit(1))
                    print("Added Paper")
                elif event.key == pygame.K_s:
                    units.append(create_unit(2))
                    print("Added Scissors")

    if not paused:
        # Update units
        units = [u for u in units if u.energy > 0]  # Remove dead units

        # Move units
        for unit in units:
            unit.move(units)

            # Reproduction with population control
            if unit.reproduction_counter >= 90 and unit.energy > 50:
                population_of_type = sum(1 for u in units if u.type == unit.type)
                if population_of_type < 50:  # Population cap per type
                    if random.random() < 0.2:  # 20% chance
                        new_unit = create_unit(unit.type)
                        new_unit.x = unit.x + random.uniform(-20, 20)
                        new_unit.y = unit.y + random.uniform(-20, 20)
                        units.append(new_unit)
                        unit.energy -= 30  # Energy cost for reproduction
                unit.reproduction_counter = 0

        # Check for battles
        for i, unit1 in enumerate(units):
            for unit2 in units[i+1:]:
                distance = np.sqrt((unit1.x - unit2.x)**2 + (unit1.y - unit2.y)**2)
                if distance < UNIT_SIZE:
                    if unit1.fight(unit2):
                        unit2.type = unit1.type
                        unit1.energy += 20  # Energy gain for winning
                        unit2.energy = max(20, unit2.energy - 30)  # Energy loss for losing
                    elif unit2.fight(unit1):
                        unit1.type = unit2.type
                        unit2.energy += 20  # Energy gain for winning
                        unit1.energy = max(20, unit1.energy - 30)  # Energy loss for losing

    # Draw everything
    screen.fill(BLACK)

    # Draw units
    for unit in units:
        if unit.type == 0:  # Rock
            pygame.draw.circle(screen, RED, (int(unit.x + unit.size/2), int(unit.y + unit.size/2)), unit.size//2)
        elif unit.type == 1:  # Paper
            pygame.draw.rect(screen, GREEN, (unit.x, unit.y, unit.size, unit.size))
        else:  # Scissors
            points = [(unit.x + unit.size/2, unit.y),
                     (unit.x, unit.y + unit.size),
                     (unit.x + unit.size, unit.y + unit.size)]
            pygame.draw.polygon(screen, BLUE, points)

    # Count populations
    rocks = sum(1 for unit in units if unit.type == 0)
    papers = sum(1 for unit in units if unit.type == 1)
    scissors = sum(1 for unit in units if unit.type == 2)

    # Draw stats bar
    pygame.draw.rect(screen, GRAY, (0, HEIGHT, WIDTH, STATS_HEIGHT))

    # Display stats
    status1 = f"{'PAUSED' if paused else 'RUNNING'} | Frame: {frame_count}"
    status2 = f"Rocks: {rocks} | Papers: {papers} | Scissors: {scissors} | Total: {len(units)}"
    text1 = font.render(status1, True, WHITE)
    text2 = font.render(status2, True, WHITE)
    screen.blit(text1, (10, HEIGHT + 10))
    screen.blit(text2, (10, HEIGHT + 35))

    pygame.display.flip()
    clock.tick(FPS)

    # Print stats every 30 frames
    if frame_count % 30 == 0:
        print(f"Frame {frame_count}: Rocks: {rocks}, Papers: {papers}, Scissors: {scissors}")
        sys.stdout.flush()

pygame.quit()

print("\nFinal Population:")
print(f"Rocks: {rocks}")
print(f"Papers: {papers}")
print(f"Scissors: {scissors}")
print(f"Total units: {len(units)}")
