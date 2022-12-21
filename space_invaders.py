import pygame
import pygame.freetype
from pygame import mixer
import os
import random
import time
from sys import exit

pygame.init()
pygame.font.init()
pygame.freetype.init()

# Window
width, height = 750, 750
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Galactic Defenders")
icon = pygame.image.load(os.path.join("assets", "icon.ico"))
pygame.display.set_icon(icon)

main_char = pygame.image.load(os.path.join("assets", "player.png"))
main_char = pygame.transform.scale(main_char, (80, 80))
redenemy = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
yellowenemy = pygame.image.load(os.path.join("assets", "enemy2.png"))
yellowenemy = pygame.transform.scale(yellowenemy, (90, 90))
greenenemy = pygame.image.load(os.path.join("assets", "pixel_ship_green_small.png"))
red_laser = pygame.image.load(os.path.join("assets", "pixel_laser_red.png"))
blue_laser = pygame.image.load(os.path.join("assets", "pixel_laser_blue.png"))
yellow_laser = pygame.image.load(os.path.join("assets", "pixel_laser_yellow.png"))
green_laser = pygame.image.load(os.path.join("assets", "pixel_laser_green.png"))
bg_img = pygame.image.load(os.path.join("assets", "background.jpg"))
bg = pygame.transform.scale(bg_img, (width, height))
main_menu_img = pygame.image.load(os.path.join("assets", "main_menu.jpg"))
main_menu_bg = pygame.transform.scale(main_menu_img, (width, height))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def move(self, vel):
        self.y -= vel

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def collision(self, obj):
        # idea for collision: detect when x and y of  both ship and laser overlap
        return collide(self, obj)

    def off_screen(self, height):
        return not (self.y <= height and self.y >= 0)


class Ship:
    # Class that is to be called by the player class
    COOLDOWN = 20

    def __init__(self, x, y, color, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down = 0

    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_width(self):
        return self.ship_img.get_height()

    def get_height(self):
        return self.ship_img.get_width()

    def shoot_laser(self):
        if self.cool_down == 0:
            laser = Laser(self.x - 8, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down = 1

    def cooldown(self):
        if self.cool_down >= self.COOLDOWN:
            self.cool_down = 0
        elif self.cool_down > 0:
            self.cool_down += 1

    print("Ship class")


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = main_char
        self.laser_img = blue_laser
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        explosion_sound = mixer.Sound(os.path.join("assets", "sounds", 'explosion.wav'))
                        explosion_sound.play()
                        self.lasers.remove(laser)

    # healthbar that is green bar that slowly turns red each time player loses health (or gains green when player GAINS health??? (maybe add powerups?))
    def healthbar(self, window):
        green = (0, 255, 0)
        red = (255, 0, 0)
        pygame.draw.rect(window, red, (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, green, (
            self.x, self.y + self.ship_img.get_height() + 10,
            self.ship_img.get_width() * (self.health / self.max_health),
            10))

    def draw(self, window):
        Ship.draw(self, window)
        self.healthbar(window)


class Enemy(Ship):
    e_colors = {"red": (redenemy, red_laser),
                "yellow": (yellowenemy, yellow_laser),
                "green": (greenenemy, green_laser)}

    def __init__(self, x, y, colors, health=100, ):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.e_colors[colors]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

    print("based enemy")


class Button:
    def __init__(self, color, x, y, width, height, text=''):
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text

    def draw_button(self, window, outline=None):
        if outline:
            pygame.draw.rect(window, outline, (self.x - 2, self.y - 2, self.width + 4, self.height + 4), 0)
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height), 0)

        if self.text != '':
            font = pygame.font.SysFont('Arial', 50)
            otherfont = pygame.freetype.Font(os.path.join("assets", 'Chopsic-K6Dp.ttf'), 50)
            text = font.render(self.text, True, (0, 0, 0))
            window.blit(text, (
                self.x + (self.width / 2 - text.get_width() / 2), self.y + (self.height / 2 - text.get_height() / 2)))

    def isOver(self, pos):
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
        return False


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# Menu where user starts the game and is taken to from lose screen
def main_menu():
    print("in main menu")
    # menu_font = pygame.freetype.Font(os.path.join("assets",'wolfenstein.ttf'), 50)
    main_font = pygame.freetype.Font(os.path.join("assets", 'Chopsic-K6Dp.ttf'), 100)
    sub_font = pygame.freetype.Font(os.path.join("assets", 'Chopsic-K6Dp.ttf'), 40)
    fps_clock = pygame.time.Clock()  # the pygame clock function functions as a collision detector checking for collisions per second (e.g. FPS)
    FPS = 60
    run = True
    x, y = 180, 96
    start_button = Button((0, 255, 0), width // 2 - x / 2, height // 2 - 40, x, y, 'START')
    mixer.music.load(os.path.join("assets", "sounds", 'menumusic.mp3'))
    mixer.music.play(-1)

    while run:
        mouse = pygame.mouse.get_pos()
        window.blit(main_menu_bg, (0, 0))
        start_button.draw_button(window)
        fps_clock.tick(FPS)
        main_font.render_to(window, (width // 2 - 250, height // 2 - 320), f"Galaxy", (255, 0, 0))
        main_font.render_to(window, (width // 2 - 330, height // 2 - 200), f"Defender", (255, 0, 0))
        pygame.display.update()
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.isOver(mouse):
                    print("Start button clicked")
                    main()

            if event.type == pygame.MOUSEMOTION:
                if start_button.isOver(mouse):
                    start_button.color = (255, 0, 0)
                else:
                    start_button.color = (0, 255, 0)
    print("Quitting pygame")
    pygame.display.quit()
    pygame.quit()
    exit()


def main():
    run = True
    player_vel = 5
    enemy_vel = 1.15
    laser_vel = 5
    player = Player(300, 660)

    fps_clock = pygame.time.Clock()  # the pygame clock function functions as a collision detector checking for collisions per second (e.g. FPS)
    FPS = 60
    lives = 5
    level = 0
    enemies = []
    wave_length = 1
    main_font = pygame.freetype.Font(os.path.join("assets", 'Chopsic-K6Dp.ttf'), 50)
    mixer.music.load(os.path.join("assets", "sounds", 'background.wav'))
    mixer.music.play(-1)
    lost = False

    i = 0

    def lose_menu():
        fps_clock = pygame.time.Clock()  # the pygame clock function functions as a collision detector checking for collisions per second (e.g. FPS)
        FPS = 60
        main_font = pygame.freetype.Font(os.path.join("assets", 'Chopsic-K6Dp.ttf'), 50)
        run = True
        while run:
            fps_clock.tick(FPS)
            pygame.display.update()
            pygame.event.pump()
            main_font.render_to(window, (width // 2 - 300, height // 2), f"You Lose! \n Level: {level}", (30, 100, 255))
            pygame.display.update()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_m] and run == True:
                main_menu()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
        pygame.display.quit()
        pygame.quit()
        exit()

    # While loop keeps background scrolling, spawns enemies, keeps track of levels and lives, and basically
    # everything else

    while run:
        fps_clock.tick(FPS)
        pygame.event.pump()
        window.blit(bg, (0, i))
        time.sleep(0.015)
        window.blit(bg, (0, -height + i))
        if i == height:
            window.blit(bg, (0, -height + i))
            i = 0
        i += 0.8

        for enemy in enemies:
            enemy.draw(window)
        player.draw(window)
        main_font.render_to(window, (10, 10), f"Lives: {lives}", (255, 255, 255))
        main_font.render_to(window, (width - 275, 10), f"Level: {level}", (255, 255, 255))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
        if len(enemies) == 0:
            level += 1
            wave_length += 4
            for i in range(wave_length):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-700, -100),
                              random.choice(["red", "yellow", "green"]))
                enemies.append(enemy)
        keys = pygame.key.get_pressed()
        if lost:
            if level > 5:
                print(f'GOTDAMN! User made it to level {level}')
            else:
                print(f"Congratulations! user made it to level {level}!")
            print("User lost! F for respects")                   
            lose_menu()
       
        if keys[pygame.K_a] and player.x - player_vel > 0:  # left
            player.x -= player_vel
        if keys[pygame.K_d] and player.x + player_vel + player.get_width() < width:  # right
            player.x += player_vel
        if keys[pygame.K_w] and player.y - player_vel > 0:  # up
            player.y -= player_vel
        if keys[pygame.K_s] and player.y + player_vel + player.get_height() < height:  # down
            player.y += player_vel
        if keys[pygame.K_SPACE]:
            player.shoot_laser()
            laser_sound = mixer.Sound(os.path.join("assets", "sounds", 'laser.wav'))
            laser_sound.play()
            print("player shoots laser")
        explosion_sound = mixer.Sound(os.path.join("assets", "sounds", 'explosion.wav'))

        for enemy in enemies:
            enemy.move(enemy_vel)
            enemy.move_lasers(-laser_vel, player)
            if enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)
                print("enemy broke barrier")
            if random.randrange(0, 4 * 60) == 1 and enemy.y + enemy.get_height() > 0:
                enemy.shoot_laser()
                enemy_laser_sound = mixer.Sound(os.path.join("assets", "sounds", 'enemylaser.wav'))
                enemy_laser_sound.play()
                print("enemy shoots laser")
            if collide(enemy, player):
                player.health -= 10
                explosion_sound.play()
                enemies.remove(enemy)
                print("Player took damage!")
        player.move_lasers(laser_vel, enemies)
        if lives <= 0 or player.health <= 0:
            lost = True

    print("User quit/lost! F for respects")
    print(f"Congratulations! user made it to level {level}!")
    pygame.display.quit()
    pygame.quit()
    exit()


main_menu()
main()