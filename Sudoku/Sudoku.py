import pygame, sys, os.path
import random, time, sqlite3

db = sqlite3.connect('sudokuDB.db')

myCursor = db.cursor()
try:
    myCursor.execute("SELECT * FROM board")
    myCursor.execute("SELECT * FROM solvedBoard")
    myCursor.execute("SELECT * FROM status")
    myCursor.execute("SELECT * FROM time")
except:
    myCursor.execute("CREATE TABLE IF NOT EXISTS board (cell TEXT, value INTEGER)")
    myCursor.execute("CREATE TABLE IF NOT EXISTS solvedBoard (cell TEXT, value INTEGER)")
    myCursor.execute("CREATE TABLE IF NOT EXISTS status (lives INTEGER, saved INTEGER)")
    myCursor.execute("CREATE TABLE IF NOT EXISTS time (timeOfEnding INTEGER, startTime INTEGER)")
    myCursor.execute("INSERT INTO status VALUES (?,?)", (0, 0))
    myCursor.execute("INSERT INTO time VALUES (?, ?)", (0, 0))
    for i in range(9):
        for j in range(9):
            x = "c" + str(i) + str(j)
            myCursor.execute("INSERT INTO board VALUES (?,?)", (x, 0))
            myCursor.execute("INSERT INTO solvedBoard VALUES (?,?)", (x, 0))
    db.commit()


pygame.init()
BLACK = (0, 0, 0)
BBLACK = (60, 60, 60)
WHITE = (255, 255, 255)
GREY = (128, 128, 128)
GREEN = (6, 189, 9)
RED = (255, 0, 0)
BLUE = (0, 0, 234)
DBLUE = (0, 0, 184)
BBLUE = (0, 0, 254)
fnt = pygame.font.SysFont("comicsans", 50)

width = 405
rows = 9
gap = width // rows
FPS = 60
difficulty = "Easy"
start = False
start_time = 0

screen = pygame.display.set_mode((width, width+40))
pygame.display.set_caption("Sudoku")
icon = pygame.image.load('favicon.ico')
page = pygame.image.load('sudoku.jpg')
page = pygame.transform.scale(page, (width, width+40))
pygame.display.set_icon(icon)

num = 0

clock = pygame.time.Clock()

class Spot:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value
        self.x = col * gap
        self.y = row * gap
        self.storedVal = num
        self.isFull = False

    def draw(self):
        if self.storedVal != 0:
            text_box = fnt.render(str(self.storedVal), 1, GREY)
            screen.blit(text_box, (self.x + 13, self.y + 8))

    def markSpot(self, win):
        pygame.draw.rect(win, GREEN, (self.x, self.y, gap, gap), 2)

    def makeValue(self):
        self.value = self.storedVal
        self.storedVal = 0

    def showBoard(self):
        if self.value != 0:
            text_box = fnt.render(str(self.value), 1, BLACK)
            screen.blit(text_box, (self.x + 13, self.y + 8))

    def makeFull(self):
        self.isFull = True

    def makeEmpty(self):
        self.isFull = False
        self.storedVal = 0
        self.value = 0

def convertMillis(millis):
    mil=(millis/10)%100
    seconds=(millis/1000)%60
    minutes=(millis/(1000*60))%60

    return mil, seconds, minutes

def message(msg, color, posx, posy, size):
    font_style = pygame.font.SysFont(None, size)
    mesg = font_style.render(msg, True, color)
    screen.blit(mesg, [posx, posy])

def text_objects(text, font, color):
    textSurface = font.render(text, True, color)
    return textSurface, textSurface.get_rect()

def button(msg, x, y, w, h, ic, ac, activated):
    global click, difficulty, start, start_time
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if activated:
        pygame.draw.rect(screen, ic, (x, y, w, h), 5, 10)
        return

    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h), 5, 10)
        if click[0] == 1:
            difficulty = msg
            start = True
            start_time = pygame.time.get_ticks()
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h), 5, 10)

    smallText = pygame.font.Font('freesansbold.ttf', 15)
    textSurf, textRect = text_objects(msg, smallText, ic)
    textRect.center = ((x + (w / 2)), (y + (h / 2)))
    screen.blit(textSurf, textRect)

def draw_grid(win, row, width):
    gap = width // row
    for i in range(row):
        pygame.draw.line(win, GREY, (0, i * gap),(width, i * gap))
        for j in range(row):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))
    for i in range(row):
        if i != 0:
            pygame.draw.line(win, BLACK, (0, int(i * 3 * gap)), (width, int(i * 3 * gap)), 3)
        for j in range(row):
            pygame.draw.line(win, BLACK, (int(i * 3 * gap), 0), (int(i * 3 * gap), width), 3)

def make_grid(rows):
    grid = []
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = Spot(i, j, 0)
            grid[i].append(spot)

    return grid

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    y, x = pos

    row = x // gap
    col = y // gap
    return row, col


def generate_Board(row, grid):
    last = []
    for i in range(row):
        grid[0][i].value = random.randint(1, 9)
        while grid[0][i].value in last:
            grid[0][i].value = random.randint(1, 9)
        last.append(grid[0][i].value)
    return grid

def copyBoard(copy, toCopy):
    for i in range(len(toCopy[0]) - 1):
        copy[0][i].value = toCopy[0][i].value
    return copy



def solve(bo):
    find = find_empty(bo)
    if not find:
        return True
    else:
        row, col = find

    for i in range(1, 10):
        if valid(bo, i, (row, col)):
            bo[row][col].value = i

            if solve(bo):
                return True

            bo[row][col].value = 0

    return False


def valid(bo, num, pos):
    # check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i].value == num and pos[1] != i:
            return False

    # check column
    for i in range(len(bo)):
        if bo[i][pos[1]].value == num and pos[0] != i:
            return False

    # check box
    box_x = pos[1] // 3
    box_y = pos[0] // 3

    for i in range(box_y * 3, box_y * 3 + 3):
        for j in range(box_x * 3, box_x * 3 + 3):
            if bo[i][j].value == num and (i, j) != pos:
                return False

    return True

def find_empty(bo):
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j].value == 0:
                return (i, j)  # row, column

    return None

def main():
    global num, GREEN, difficulty, start, start_time, WHITE
    won = 0
    WHITE = (255, 255, 255)
    GREEN = (6, 189, 9)
    page.set_alpha(300)
    mark = False
    running = True
    gameOver = False
    pause = False
    lastSaveScreen = False
    countFlag = False
    countDown = 20
    lives = 3
    sCount = 1
    numList = []

    grid = make_grid(rows)
    tempGrid = make_grid(rows)

    board = generate_Board(rows, grid)
    tempBoard = copyBoard(tempGrid, board)

    solve(board)
    solve(tempBoard)

    while running:
        screen.fill(WHITE)
        if start:
            if sCount > 0:
                if difficulty == "Easy":
                    first = 2
                    second = 5
                if difficulty == "Medium":
                    first = 3
                    second = 6
                if difficulty == "Hard":
                    first = 4
                    second = 7
                for i in range(rows):
                    rand = random.sample(range(9), random.randint(first, second))
                    for j in rand:
                        grid[i][j].value = 0
                sCount = 0

        draw_grid(screen, rows, width)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if start and not gameOver and won < 81:
                    for i in range(9):
                        for j in range(9):
                            x = "c" + str(i) + str(j)
                            myCursor.execute("UPDATE solvedBoard SET value = ? WHERE cell = ?", (tempBoard[i][j].value, x))
                            myCursor.execute("UPDATE Board SET value = ? WHERE cell = ?", (board[i][j].value, x))
                            db.commit()

                    myCursor.execute("UPDATE status SET saved = True")
                    myCursor.execute("UPDATE status SET lives = ? WHERE saved = ?", (lives, True))
                    if pause:
                        timeOfEnding = oldTime
                    else:
                        timeOfEnding = pygame.time.get_ticks()
                    myCursor.execute("UPDATE time SET timeOfEnding = ?", (timeOfEnding,))
                    myCursor.execute("UPDATE time SET startTime = ? WHERE timeOfEnding = ?", (start_time, timeOfEnding))
                    db.commit()
                running = False
                pygame.quit()
                sys.exit()
            if mark:
                if event.type == pygame.KEYDOWN:
                    if not spot.isFull and not gameOver and not pause:
                        if event.key == pygame.K_1 and mark:
                            spot.storedVal = 1
                            num = 1
                        if event.key == pygame.K_2 and mark:
                            spot.storedVal = 2
                            num = 2
                        if event.key == pygame.K_3 and mark:
                            spot.storedVal = 3
                            num = 3
                        if event.key == pygame.K_4 and mark:
                            spot.storedVal = 4
                            num = 4
                        if event.key == pygame.K_5 and mark:
                            spot.storedVal = 5
                            num = 5
                        if event.key == pygame.K_6 and mark:
                            spot.storedVal = 6
                            num = 6
                        if event.key == pygame.K_7 and mark:
                            spot.storedVal = 7
                            num = 7
                        if event.key == pygame.K_8 and mark:
                            spot.storedVal = 8
                            num = 8
                        if event.key == pygame.K_9 and mark:
                            spot.storedVal = 9
                            num = 9
                    if event.key == pygame.K_BACKSPACE:
                        if spot.storedVal != 0:
                            spot.makeEmpty()

                    if event.key == pygame.K_RETURN and spot.isFull == False:
                        if spot.storedVal != 0:
                            spot.makeValue()
                            spot.makeFull()
                            if spot.value != tempBoard[row][col].value:
                                countFlag = True
                                lives -= 1
                                if countDown > 0:
                                    countDown = 20
                                    GREEN = (161, 5, 13)
                                if lives <= 0:
                                    spot.makeEmpty()
                                    num = 0
                                    gameOver = True
                                    time_since_enter = pygame.time.get_ticks() - start_time
                                spot.value = 0
                                spot.makeEmpty()
                            for i in range(rows):
                                for j in range(rows):
                                    if grid[i][j].isFull:
                                        won += 1

            if pygame.mouse.get_pressed()[0] and not gameOver and not pause:
                if pygame.mouse.get_pos()[1] < width:
                    mark = True
                    pos = pygame.mouse.get_pos()

        if mark and pos[1] < width:
            row, col = get_clicked_pos(pos, rows, width)
            spot = grid[row][col]
            if spot.isFull == False:
                spot.markSpot(screen)
                if num != 0:
                    drawSpot = spot
                    numList.append(drawSpot)
            for i in range(len(numList)):
                    numList[i].draw()

        for i in range(rows):
            for j in range(rows):
                grid[i][j].showBoard()
                if grid[i][j].value != 0 and start:
                    grid[i][j].makeFull()

        if gameOver:
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                spot.makeEmpty()
                start = False
                main()
            else:
                WHITE = (215, 215, 215)
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(70, 135, 265, 185),  0, 12)
                message("Game Over", BLACK, 128, 155, 40)
                message("You have made 3 mistakes and lost", GREY, 90, 205, 20)
                message("this game", GREY, 170, 220, 20)
                message("press 'SPACE' to play", BLUE, 115, 275, 25)

        if not start:
            screen.fill(BLACK)
            screen.blit(page, (0, 0))
            message("Choose Difficulty Level", BLACK, 28, 165, 40)
            message("To Play", BLACK, 152, 202, 40)
            easyButton = button("Easy", 8, 250, 120, 40, BLACK, BBLACK, lastSaveScreen)
            mediumButton = button("Medium", 143, 250, 120, 40, BLACK, BBLACK, lastSaveScreen)
            hardButton = button("Hard", 277, 250, 120, 40, BLACK, BBLACK, lastSaveScreen)

        myCursor.execute("SELECT * FROM status")
        if myCursor.fetchone()[1] == 1:
            if pygame.key.get_pressed()[pygame.K_RETURN]:
                lastSaveScreen = False
                myCursor.execute("SELECT * FROM board")
                data = myCursor.fetchall()
                for i in range(9):
                    for j in range(9):
                        x = data[(i * 9) + j][1]
                        board[i][j].value = x

                myCursor.execute("SELECT * FROM solvedBoard")
                data = myCursor.fetchall()
                for i in range(9):
                    for j in range(9):
                        x = data[(i * 9) + j][1]
                        tempBoard[i][j].value = x

                sCount = 0
                myCursor.execute("SELECT * FROM time")
                times = myCursor.fetchall()[0]
                endTime = pygame.time.get_ticks() - times[0]
                start_time = times[1] + endTime
                myCursor.execute("SELECT * FROM status")
                lives = myCursor.fetchone()[0]
                myCursor.execute("UPDATE status SET saved = False")
                db.commit()
                page.set_alpha(300)
                start = True

            elif pygame.key.get_pressed()[pygame.K_ESCAPE]:
                lastSaveScreen = False
                page.set_alpha(300)
                myCursor.execute("UPDATE status SET saved = False")
                db.commit()
            else:
                page.set_alpha(180)
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(70, 135, 265, 185), 0, 12)
                message("you have a saved game", BLACK, 92, 155, 30)
                message("do you want to continue from where", GREY, 90, 205, 20)
                message("you left off?", GREY, 167, 220, 20)
                message("press 'ENTER' to continue", BLUE, 120, 255, 20)
                message("press 'ESCAPE' for a new game", BLUE, 103, 280, 20)
                lastSaveScreen = True

        if countFlag:
            countDown -= 1
        if countDown <= 0:
            GREEN = (6, 189, 9)
            countFlag = False
            countDown = 20

        if start:
            message("Press 'ESCAPE' to Pause", BLACK, 10, width+13, 25)
            message("Time:", BLACK, 250, width + 12, 30)
            if not gameOver and won < 81 and not pause:
                time_since_enter = pygame.time.get_ticks() - start_time
            mil, sec, min = convertMillis(time_since_enter)
            timer = str("%02d:%02d:%02d" % (min, sec, mil))
            message(timer, BLACK, 310, width+12, 30)

            if pygame.key.get_pressed()[pygame.K_ESCAPE] and not gameOver and not pause:
                pause = True
                time_since_enter = pygame.time.get_ticks() - start_time
                oldTime = pygame.time.get_ticks()

            if pause:
                if pygame.key.get_pressed()[pygame.K_RETURN]:
                    start = False
                    num = 0
                    if mark:
                        spot.makeEmpty()
                    main()
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    WHITE = (255, 255, 255)
                    start_time = start_time + (pygame.time.get_ticks() - oldTime)
                    pause = False
                else:
                    WHITE = (215, 215, 215)
                    pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(70, 135, 265, 185), 0, 12)
                    message("Pause", BLACK, 160, 155, 40)
                    message("Are you sure you want to", GREY, 125, 205, 20)
                    message("leave the game?", GREY, 155, 220, 20)
                    message("Press 'ENTER' to Exit", BLUE, 80, 280, 17)
                    message("Press 'SPACE' to Play", BLUE, 210, 280, 17)

        if won >= 81:
            time_since_enter = time_since_enter
            if pygame.key.get_pressed()[pygame.K_SPACE]:
                num = 0
                start = False
                main()
            else:
                WHITE = (215, 215, 215)
                pygame.draw.rect(screen, (255, 255, 255), pygame.Rect(70, 135, 265, 185), 0, 12)
                message("Congratulations!", BLACK, 88, 155, 40)
                message("You have won this game", BLACK, 83, 210, 30)
                message("press 'SPACE' to play", BLUE, 115, 275, 25)
        else:
            won = 0

        pygame.display.update()
        clock.tick(FPS)

main()
