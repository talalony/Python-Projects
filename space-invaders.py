import pygame
import random
import math
from pygame import mixer
import time

pygame.init()

# create a screen
screen = pygame.display.set_mode((800, 600))

# background
background = pygame.image.load('background.png')

# backGround sound
mixer.music.load('backgroundSound.wav')
mixer.music.play(-1)

# title and icon
pygame.display.set_caption('space invaders')
icon = pygame.image.load('alien.png')
pygame.display.set_icon(icon)

# player
playerImg = pygame.image.load('space-invaders.png')
playerX = 370
playerY = 480
playerX_change = 0

# enemy
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
numOfEnemys = 6
enemySpeed = 2.5

for i in range(numOfEnemys):
    enemyImg.append(pygame.image.load('monster.png'))
    enemyX.append(random.randint(0, 735))
    enemyY.append(random.randint(50, 100))
    enemyX_change.append(3.5)
    enemyY_change.append(40)

# bullet
bulletImg = pygame.image.load('laserbullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 15
bulletState = 'ready'  # you can't see the bullet

# score
scoreValue = 0
enemyScore = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
textY = 10

# gameOver
overFont = pygame.font.Font('freesansbold.ttf', 64)

restartFont = pygame.font.Font('freesansbold.ttf', 32)


def gameOverText():
    overText = overFont.render('GAME OVER', True, (255, 255, 255))
    restartText = restartFont.render('press ENTER to play again', True, (255, 255, 255))
    screen.blit(overText, (200, 250))
    screen.blit(restartText, (190, 320))


def showScore(x, y):
    score = font.render('score :' + str(scoreValue), True, (255, 255, 255))
    screen.blit(score, (x, y))


def fireBullet(x, y):
    global bulletState
    bulletState = 'fire'  # the bullet is moving
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt((math.pow(enemyX - bulletX, 2)) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False

def increaseEnemySpeed():
    global enemySpeed
    enemySpeed += 0.5


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def player(x, y):
    screen.blit(playerImg, (x, y))


# game loop
running = True
while running:
    # RGB
    screen.fill((0, 0, 0))
    # background image
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # right, left and space keystrokes
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                playerX_change = -5
            if event.key == pygame.K_RIGHT:
                playerX_change = 5
            if event.key == pygame.K_SPACE:
                if bulletState is 'ready':
                    bulletSound = mixer.Sound('laserSound.wav')
                    bulletSound.play()
                    bulletX = playerX
                    fireBullet(bulletX, bulletY)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                playerX_change = 0
    # player boundaries
    playerX += playerX_change

    if playerX <= 0:
        playerX = 0
    elif playerX >= 736:
        playerX = 736

    if enemyScore == 10:
        increaseEnemySpeed()
        enemyScore = 0

    # enemy movement
    for i in range(numOfEnemys):
        # gameOver
        while enemyY[i] > 440:
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                enemyX[i] = random.randint(0, 735)
                enemyY[i] = random.randint(50, 100)
                screen.blit(background, (0, 0))
                player(playerX, playerY)
                showScore(textX, textY)
                scoreValue = 0
                enemySpeed = 2.5
                enemyScore = 0
            else:
                for j in range(numOfEnemys):
                    enemyY[j] = 2000
                gameOverText()
            break


        enemyX[i] += enemyX_change[i]
        if enemyX[i] <= 0:
            enemyX_change[i] = enemySpeed
            enemyY[i] += enemyY_change[i]
        elif enemyX[i] >= 736:
            enemyX_change[i] = -enemySpeed
            enemyY[i] += enemyY_change[i]

        # collision
        collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
        if collision:
            bulletY = 480
            bulletState = "ready"
            scoreValue += 1
            enemyScore += 1
            enemyX[i] = random.randint(0, 735)
            enemyY[i] = random.randint(50, 100)


        enemy(enemyX[i], enemyY[i], i)

    # bullet movement
    if bulletY <= 0:
        bulletY = 480
        bulletState = 'ready'
    if bulletState is 'fire':
        fireBullet(bulletX, bulletY)
        bulletY -= bulletY_change

    player(playerX, playerY)
    showScore(textX, textY)
    pygame.display.update()
