import pygame
import os
import random

# Function to detect collision
def collide(obj1, obj2):
    return (obj1.x < obj2.x + obj2.get_width() and 
            obj1.x + obj1.get_width() > obj2.x and 
            obj1.y < obj2.y + obj2.get_height() and 
            obj1.y + obj1.get_height() > obj2.y)

# Set game font
pygame.font.init()
pygame.mixer.init()

# Set window size
WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Space Shooters")

# Load spaceship images
RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_blue_small.png"))

# Player ship
YELLOW_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_yellow.png"))

# Load laser images
RED_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))

LASER_SOUND = pygame.mixer.Sound(os.path.join("assets", "Player_Laser.mp3"))
EXPLOSION_SOUND = pygame.mixer.Sound(os.path.join("assets", "Explosion.mp3"))
pygame.mixer.music.load(os.path.join("assets", "Background.mp3" ))


# Game backdrop
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background-black.png")), (WIDTH, HEIGHT))

# Create laser class
class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)  # Create a mask for collision detection

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

    def get_width(self):
        return self.img.get_width()

    def get_height(self):
        return self.img.get_height()

# Create ship class
class Ship:
    COOLDOWN = 30

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width() // 2 - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            LASER_SOUND.play() 

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

# Create player class
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        EXPLOSION_SOUND.play
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))

# Create enemy class
class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x + self.get_width() // 2 - 20, self.y + self.get_height(), self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
            LASER_SOUND.play()

    def move_lasers(self, vel, player):
        self.cooldown()  # Add this line to increment the cooldown counter
        for laser in self.lasers[:]:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
             self.lasers.remove(laser)
            else:
                if laser.collision(player):
                    player.health -= 10
                    self.lasers.remove(laser)
# Main game function
def main():
    run = True
    fps = 60
    level = 0
    lives = 5
    pl_velocity = 5
    main_font = pygame.font.SysFont("comicSans", 50)
    laser_velocity = 5
    enemy_list = []
    wave_length = 5
    enemy_velocity = 1

    player = Player(300, 650)
    clock = pygame.time.Clock()
    pygame.mixer.music.play(-1)  

    def redraw_window():
        WIN.blit(BG, (0, 0))
        for enemy in enemy_list:
            enemy.draw(WIN)
        player.draw(WIN)
        pygame.display.update()

    while run:
        clock.tick(fps)
        redraw_window()

        if len(enemy_list) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                enemy_list.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.x - pl_velocity > 0:  # Move left
            player.x -= pl_velocity
        if keys[pygame.K_d] and player.x + pl_velocity + 50 < WIDTH:  # Move right
            player.x += pl_velocity
        if keys[pygame.K_w] and player.y - pl_velocity > 0:  # Move up
            player.y -= pl_velocity
        if keys[pygame.K_s] and player.y + pl_velocity + 50 < HEIGHT:  # Move down
            player.y += pl_velocity
        if keys[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemy_list[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.shoot()

            # Check for collision with player
            if collide(enemy, player):
                player.health -= 10
                enemy_list.remove(enemy)
                EXPLOSION_SOUND.play()

            # Remove enemy if it goes off the screen
            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemy_list.remove(enemy)

        player.move_lasers(-laser_velocity, enemy_list)
# Main menu function
def main_menu():

    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(BG, (0, 0))
        title_label = title_font.render("Press the mouse to begin...", True, (255, 255, 255))
        WIN.blit(title_label, (WIDTH / 2 - title_label.get_width() / 2, 350))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:  # Check for mouse clicks
                main()

    pygame.quit()

# Start the game
main_menu()
