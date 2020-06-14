import pygame
import random
import os
import time
from pygame import mixer

pygame.font.init()

pygame.init()

# screen
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('space shooter')

# background sound
mixer.music.load('backgroundSound.wav')
mixer.music.play(-1)

# player images
playerimage = pygame.image.load('space-invaders.png')

# enemy images
enemyGrey = pygame.transform.scale(pygame.image.load('enemy1.png'), (40, 40))
enemyBlue = pygame.transform.scale(pygame.image.load('enemy.png'), (40, 40))
enemyRed = pygame.transform.scale(pygame.image.load('enemy2.png'), (40, 40))

# lasers
playerLaser = pygame.transform.scale(pygame.image.load('playerbullet.png'), (45, 45))
enemyLaser = pygame.transform.scale(pygame.image.load('enemybullet.png'), (30, 30))
enemyLaser1 = pygame.transform.scale(pygame.image.load('enemybullet1.png'), (30, 30))

# background
BG = pygame.transform.scale(pygame.image.load('background-black.png'), (width, height))


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, speed):
        self.y += speed

    def offScreen(self, height):
        return not (self.y <= height and self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)


class Ship:
    COOLDOWN = 20

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.shipImg = None
        self.laserImg = None
        self.lasers = []
        self.coolDown = 0

    def draw(self, window):
        window.blit(self.shipImg, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def get_width(self):
        return self.shipImg.get_width()

    def moveLaser(self, speed, obj):
        self.CoolDown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.offScreen(height):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def get_height(self):
        return self.shipImg.get_height()

    def Shoot(self):
        if self.coolDown == 0:
            laser = Laser(self.x + 8, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDown = 1

    def CoolDown(self):
        if self.coolDown >= self.COOLDOWN:
            self.coolDown = 0
        elif self.coolDown > 0:
            self.coolDown += 1


class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.shipImg = playerimage
        self.laserImg = playerLaser
        self.mask = pygame.mask.from_surface(self.shipImg)
        self.maxHealth = health

    def moveLaser(self, speed, objs):
        self.CoolDown()
        for laser in self.lasers:
            laser.move(speed)
            if laser.offScreen(height):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthBar(window)

    def healthBar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.shipImg.get_height() + 10, self.shipImg.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.shipImg.get_height() + 10, self.shipImg.get_width() * (self.health / self.maxHealth),
            10))


class Enemy(Ship):
    COLOR_MAP = {
        'red': (enemyRed, enemyLaser),
        'grey': (enemyGrey, enemyLaser1),
        'blue': (enemyBlue, enemyLaser)
    }

    def __init__(self, x, y, color, healt=100):
        super().__init__(x, y, healt)
        self.shipImg, self.laserImg = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.shipImg)

    def move(self, speed):
        self.y += speed

    def Shoot(self):
        if self.coolDown == 0:
            laser = Laser(self.x + 5, self.y, self.laserImg)
            self.lasers.append(laser)
            self.coolDown = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


# game loop
def main():
    running = True
    FPS = 60
    level = 0
    lives = 5
    mainFont = pygame.font.SysFont('comicsans', 50)
    lostFont = pygame.font.SysFont('comicsans', 60)

    enemies = []
    waveLenght = 5
    enemySpeed = 1

    laserSpeed = 7
    playerSpeed = 7

    player = Player(375, 510)

    clock = pygame.time.Clock()

    lost = False

    lostCount = 0

    def redrawWindow():
        screen.blit(BG, (0, 0))

        # draw text
        livesText = mainFont.render(f'lives: {lives}', 1, (255, 255, 255))
        levelText = mainFont.render(f'level: {level}', 1, (255, 255, 255))

        screen.blit(livesText, (10, 10))
        screen.blit(levelText, (width - levelText.get_width() - 10, 10))

        for enemy in enemies:
            enemy.draw(screen)

        player.draw(screen)

        if lost:
            lostLabel = lostFont.render('GAME OVER!!', 1, (255, 255, 255))
            screen.blit(lostLabel, (width / 2 - lostLabel.get_width() / 2, 280))

        pygame.display.update()


    while running:
        clock.tick(FPS)
        redrawWindow()

        if lives <= 0 or player.health <= 0:
            lost = True
            lostCount += 1

        if lost:
            if lostCount > FPS * 3:
                running = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            waveLenght += 5
            for i in range(waveLenght):
                enemy = Enemy(random.randrange(50, width - 100), random.randrange(-1500, -100),
                              random.choice(['red', 'grey', 'blue']))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - playerSpeed > 0:
            player.x -= playerSpeed
        if keys[pygame.K_RIGHT] and player.x + playerSpeed + player.get_width() < width:
            player.x += playerSpeed
        if keys[pygame.K_UP] and player.y - playerSpeed > 0:
            player.y -= playerSpeed
        if keys[pygame.K_DOWN] and player.y + playerSpeed + player.get_height() + 25 < height:
            player.y += playerSpeed
        if keys[pygame.K_SPACE]:
            player.Shoot()
            bulletSound = mixer.Sound('laserSound.wav')
            bulletSound.play()

        for enemy in enemies:
            enemy.move(enemySpeed)
            enemy.moveLaser(laserSpeed, player)

            if random.randrange(0, 2 * 60) == 1:
                enemy.Shoot()

            if collide(enemy, player):
                player.health -= 10
                enemies.remove(enemy)

            elif enemy.y + enemy.get_height() > height:
                lives -= 1
                enemies.remove(enemy)

        player.moveLaser(-laserSpeed, enemies)


def mainMenu():
    titleFont = pygame.font.SysFont('comicsans', 70)
    running = True
    while running:
        screen.blit(BG, (0, 0))
        titleText = titleFont.render('press ENTER to start', 1, (255, 255, 255))
        screen.blit(titleText, (width / 2 - titleText.get_width() / 2, 280))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                main()
    pygame.quit()


mainMenu()