import pygame, sys
import math
from queue import PriorityQueue
import random
import time
from collections import deque
from array import array

WIDTH = 600
pygame.init()
win = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption('AI Snake')

clock = pygame.time.Clock()

RED = (255, 0, 0)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)

snakeBlock = 25
snakeSpeed = 25


# class for every spot in the graph
class Spot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def __repr__(self):
        return '[{}, {}]'.format(self.row, self.col)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def get_pos(self):
        return self.row, self.col

    def is_open(self):
        return self.color == GREEN

    def is_path(self):
        return self.color == PURPLE or self.color == BLACK

    def is_barrier(self):
        return self.color == RED

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == BLACK

    def is_clear(self):
        return self.color == WHITE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = RED

    def make_end(self):
        self.color = BLACK

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # right
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # left
            self.neighbors.append(grid[self.row][self.col - 1])

    def __it__(self, other):
        return False


def hamiltonian_cycle(size):
    path = []
    flag = True
    for i in range(size - 1, 0, -1):
        spot = Spot(0, i, 0, 0)
        path.append(spot)
    for i in range(size - 1):
        spot = Spot(i, 0, 0, 0)
        path.append(spot)
    for i in range(size):
        spot = Spot(size - 1, i, 0, 0)
        path.append(spot)
    for i in range(size - 2, 0, -1):
        if flag:
            for j in range(size - 1, 0, -1):
                spot = Spot(i, j, 0, 0)
                path.append(spot)
        else:
            for j in range(1, size):
                spot = Spot(i, j, 0, 0)
                path.append(spot)
        flag = not flag

    return path


# helper
def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def find(grid, s):
    for i in range(24):
        for j in range(24):
            if grid[i][j] == s:
                return i, j
    return -1, -1
# helper
def reconstract_path(came_from, current):
    path = []
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path


# The A* algo
def algorithm(grid, start, end, mult):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float('inf') for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float('inf') for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            return reconstract_path(came_from, end)

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((mult * f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

    if mult == -2:
        return reconstract_path(came_from, current)
    return False


# making a grid of spots
def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


# drawing the lines for the grid
def draw_grid(win, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)


# returning the position in row and col
def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap
    return row, col


# score view
def yourScore(score):
    score_font = pygame.font.SysFont("comicsansms", 35)
    scoreValue = score_font.render("Your Score: " + str(score), True, BLACK)
    win.blit(scoreValue, [5, 0])


def message(msg, color, posx, posy):
    font_style = pygame.font.SysFont(None, 50)
    mesg = font_style.render(msg, True, color)
    win.blit(mesg, [posx, posy])


# drawing the snake body
def snakeBody(snakeBlock, snakeList):
    for x in snakeList:
        pygame.draw.rect(win, RED, [x[0], x[1], snakeBlock, snakeBlock])


# return true if x,y collided with x1,y1
def isCollision(playerX, playerY, snackX, snackY):
    distance = math.sqrt((math.pow(playerX - snackX, 2)) + (math.pow(playerY - snackY, 2)))
    if distance < 10:
        return True
    else:
        return False


def move(path, x1, y1, x1_change, y1_change, end):
    s = Spot(x1 // snakeBlock, y1 // snakeBlock, 0, 0)
    path.insert(0, end)
    try:
        idx = path.index(s)
    except:
        return x1_change, y1_change
    loc = path[idx]
    idxP = idx - 1
    move = path[idxP]
    if loc.row == move.row and move.col > loc.col:
        x1_change = 0
        y1_change = snakeBlock
    if loc.row == move.row and move.col < loc.col:
        x1_change = 0
        y1_change = -snakeBlock
    if loc.col == move.col and move.row > loc.row:
        x1_change = snakeBlock
        y1_change = 0
    if loc.col == move.col and move.row < loc.row:
        x1_change = -snakeBlock
        y1_change = 0

    return x1_change, y1_change


def survive(grid, x1, y1, x1_change, y1_change, snakeList, rows, width):
    down = grid[rows-1][rows-1]
    right = grid[rows-1][rows-1]
    left = grid[0][0]
    up = grid[0][0]

    downPos = [x1, y1 + snakeBlock]
    downrow, downcol = get_clicked_pos(downPos, rows, width)
    if downrow < rows and downcol < rows:
        downspot = grid[downrow][downcol]
        down = downspot

    rightPos = [x1 + snakeBlock, y1]
    rightrow, rightcol = get_clicked_pos(rightPos, rows, width)
    if rightrow < rows and rightcol < rows:
        rightspot = grid[rightrow][rightcol]
        right = rightspot

    leftPos = [x1 - snakeBlock, y1]
    leftrow, leftcol = get_clicked_pos(leftPos, rows, width)
    if leftrow < rows and leftcol < rows:
        leftspot = grid[leftrow][leftcol]
        left = leftspot

    upPos = [x1, y1 - snakeBlock]
    uprow, upcol = get_clicked_pos(upPos, rows, width)
    if uprow < rows and upcol < rows:
        upspot = grid[uprow][upcol]
        up = upspot

    if y1_change == snakeBlock:
        if [x1, (y1 + snakeBlock)] in snakeList or y1 + snakeBlock >= WIDTH:
            if left.is_clear() and leftrow >= 0:
                x1_change = -snakeBlock
                y1_change = 0
            elif right.is_clear() and rightrow < rows:
                x1_change = snakeBlock
                y1_change = 0

    if x1_change == -snakeBlock:
        if [(x1 - snakeBlock), y1] in snakeList or x1 == 0:
            if down.is_clear() and downcol < rows:
                y1_change = snakeBlock
                x1_change = 0
            elif up.is_clear() and upcol >= 0:
                y1_change = -snakeBlock
                x1_change = 0

    if x1_change == snakeBlock:
        if [(x1 + snakeBlock), y1] in snakeList or x1 + snakeBlock >= WIDTH:
            if down.is_clear() and downcol < rows:
                y1_change = snakeBlock
                x1_change = 0
            elif up.is_clear() and upcol >= 0:
                y1_change = -snakeBlock
                x1_change = 0

    if y1_change == -snakeBlock:
        if [x1, (y1 - snakeBlock)] in snakeList or y1 == 0:
            if left.is_clear() and leftrow >= 0:
                x1_change = -snakeBlock
                y1_change = 0
            elif right.is_clear() and rightrow < rows:
                x1_change = snakeBlock
                y1_change = 0

    return x1_change, y1_change


# main function
def main(win, width):
    rows = 24
    grid = make_grid(rows, width)
    gameOver = False

    start = None
    first = True
    path = []
    mult = 1

    x1 = 300
    y1 = 200

    x1_change = 0
    y1_change = 0

    snakeList = []
    lengthOfSnake = 1

    foodx = random.randrange(snakeBlock, WIDTH - snakeBlock * 2, snakeBlock)
    foody = random.randrange(snakeBlock, WIDTH - snakeBlock * 2, snakeBlock)
    Epos = [foodx, foody]
    Erow, Ecol = get_clicked_pos(Epos, rows, width)
    Espot = grid[Erow][Ecol]
    end = Espot

    Spos = [x1, y1]
    Srow, Scol = get_clicked_pos(Spos, rows, width)
    if Scol < rows and Srow < rows:
        Sspot = grid[Srow][Scol]
        start = Sspot

    for row in grid:
        for spot in row:
            spot.update_neighbors(grid)

    # res = hamiltonian_cycle(24)
    # print(res)
    # print(len(res))
    run = True
    started = False
    while run:
        # moving with arrows
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            # uncomment if you want to use arrow keys to play!!
            # if event.type == pygame.KEYDOWN and gameOver != True:
            #     if event.key == pygame.K_UP:
            #         y1_change = -snakeBlock
            #         x1_change = 0
            #         y1 -= snakeBlock
            #     elif event.key == pygame.K_DOWN:
            #         y1_change = snakeBlock
            #         x1_change = 0
            #         y1 += snakeBlock
            #     elif event.key == pygame.K_LEFT:
            #         x1_change = -snakeBlock
            #         y1_change = 0
            #         x1 -= snakeBlock
            #     elif event.key == pygame.K_RIGHT:
            #         x1_change = snakeBlock
            #         y1_change = 0
            #         x1 += snakeBlock

        grid = make_grid(rows, width)

        if len(snakeList) > 2900:
            mult = -1

        if len(snakeList) > 1:
            for i in range(len(snakeList)):
                Bpos = [snakeList[i][0], snakeList[i][1]]
                Brow, Bcol = get_clicked_pos(Bpos, rows, width)
                if x1 + snakeBlock <= WIDTH and y1 + snakeBlock <= WIDTH:
                    try:
                        Bspot = grid[Brow][Bcol]
                        barrier = Bspot
                        barrier.make_barrier()
                    except:
                        pass

        if path is False:
            x1_change, y1_change = survive(grid, x1, y1, x1_change, y1_change, snakeList, rows, width)
            path = algorithm(grid, start, end, mult)

        else:
            if first or mult == 1 and path is not False:
                path = algorithm(grid, start, end, mult)
                first = False

            if not gameOver:
                x1_change, y1_change = move(path, x1, y1, x1_change, y1_change, end)

        x1 += x1_change
        y1 += y1_change
        Spos = [x1, y1]
        Srow, Scol = get_clicked_pos(Spos, rows, width)
        if Scol < rows and Srow < rows:
            Sspot = grid[Srow][Scol]
            start = Sspot

        Epos = [foodx, foody]
        Erow, Ecol = get_clicked_pos(Epos, rows, width)
        Espot = grid[Erow][Ecol]
        end = Espot

        for row in grid:
            for spot in row:
                spot.update_neighbors(grid)

        win.fill(BLACK)
        draw(win, grid, rows, WIDTH)
        pygame.draw.rect(win, GREEN, [foodx, foody, snakeBlock, snakeBlock])
        snakeHead = []
        snakeHead.append(x1)
        snakeHead.append(y1)
        snakeList.append(snakeHead)
        if len(snakeList) > lengthOfSnake:
            del snakeList[0]
        for x in snakeList[:-1]:
            if x == snakeHead:
                gameOver = True
            if isCollision(x[0], x[1], foodx, foody):
                foodx = random.randrange(snakeBlock, WIDTH - snakeBlock, snakeBlock)
                foody = random.randrange(snakeBlock, WIDTH - snakeBlock, snakeBlock)

        snakeBody(snakeBlock, snakeList)

        # placing the eyes
        if x1_change == 0 and y1_change == 0:
            pygame.draw.ellipse(win, BLACK, [x1 + 2, y1 + 2, 4, 4])
            pygame.draw.ellipse(win, BLACK, [x1 + 18, y1 + 2, 4, 4])
        elif y1_change == snakeBlock:
            pygame.draw.ellipse(win, BLACK, [x1 + 2, y1 + 18, 4, 4])
            pygame.draw.ellipse(win, BLACK, [x1 + 18, y1 + 18, 4, 4])
        elif y1_change == -snakeBlock:
            pygame.draw.ellipse(win, BLACK, [x1 + 2, y1 + 2, 4, 4])
            pygame.draw.ellipse(win, BLACK, [x1 + 18, y1 + 2, 4, 4])
        elif x1_change == -snakeBlock:
            pygame.draw.ellipse(win, BLACK, [x1 + 2, y1 + 2, 4, 4])
            pygame.draw.ellipse(win, BLACK, [x1 + 2, y1 + 18, 4, 4])
        elif x1_change == snakeBlock:
            pygame.draw.ellipse(win, BLACK, [x1 + 18, y1 + 2, 4, 4])
            pygame.draw.ellipse(win, BLACK, [x1 + 18, y1 + 18, 4, 4])

        yourScore(lengthOfSnake - 1)

        if x1 + snakeBlock > width or x1 < 0 or y1 + snakeBlock > width or y1 < 0:
            print(x1, y1)
            print("out of bound")
            gameOver = True
        while gameOver:
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                main(win, WIDTH)
            else:
                win.fill(WHITE)
                draw_grid(win, rows, width)
                yourScore(lengthOfSnake - 1)
                x1 = (WIDTH // 2)
                y1 = 264
                message("You lost!", RED, 240, 220)
                message("Please press enter to play again", RED, 40, 270)
            break

        pygame.display.update()

        collision = isCollision(x1, y1, foodx, foody)
        if collision:
            grid = make_grid(rows, width)
            foodx = random.randrange(snakeBlock, WIDTH - snakeBlock * 2, snakeBlock)
            foody = random.randrange(snakeBlock, WIDTH - snakeBlock * 2, snakeBlock)
            Epos = [foodx, foody]
            Erow, Ecol = get_clicked_pos(Epos, rows, width)
            Espot = grid[Erow][Ecol]
            end = Espot
            end.make_end()
            lengthOfSnake += 1
            if lengthOfSnake <= 100:
                path = algorithm(grid, start, end, mult)

        clock.tick(snakeSpeed)


main(win, WIDTH)
