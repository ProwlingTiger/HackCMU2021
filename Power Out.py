import pygame, sys, copy, random, math
from pygame.locals import *
pygame.init()

FPS = 20
FramePerSec = pygame.time.Clock()

BLUE  = (0, 0, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (125,125,125)
DKGRAY = (200,200,150)
MAGENTA = (240,0,240)
BROWN = (139,69,19)
YELLOW = (255,255,0)
 
BGCOLOR = (25, 172, 31)
pygame.display.set_caption("POWER")

res = 750
BG = pygame.display.set_mode((res, res))

onMenu = False
gameEnd = False
font = pygame.font.SysFont('Corbel',80)
smallfont = pygame.font.SysFont('Corbel',38)

exitBtnBounds = (280,600,240,100)
playBtnBounds = (200,200,400,340)

gridSize = 20
global grid
grid = [ ([''] * gridSize) for i in range(gridSize)]
grid[3][3] = 'H'

l = 650//gridSize

items = ['F', 'P', 'R']
p,f,r = 1,1,6

def drawBG():
    #background and grid frame
    BG.fill(BGCOLOR)
    for i in range (50, 50+(1+gridSize)*l, l):
        pygame.draw.line(BG, BLACK, (i,50), (i, 700))
        pygame.draw.line(BG, BLACK, (50,i), (700, i))

    #grid items
    for i in range(gridSize):
        for j in range(gridSize):
            if grid[i][j] == 'F':
                pygame.draw.rect(BG, GRAY, (50+i*l, 50+j*l, l, l))
            elif grid[i][j] == 'P':
                pygame.draw.circle(BG, BLUE, (50+(i+.5)*l, 50+(j+.5)*l), l/7)
            elif grid[i][j] == 'H':
                pygame.draw.rect(BG, GREEN, (50+i*l, 50+j*l, l, l))
            elif grid[i][j] == 'O':
                pygame.draw.rect(BG, GREEN, (50+i*l, 50+j*l, l, l))
                pygame.draw.circle(BG, YELLOW, (50+(i+.5)*l, 50+(j+.5)*l), l/5)
            elif grid[i][j] == 'R':
                pygame.draw.rect(BG, BROWN, (50+i*l, 50+j*l, l, l))

def resetGrid():
    global grid
    grid = [ ([''] * gridSize) for i in range(gridSize)]
    grid[3][3] = 'H'

#MAIN MENU

def drawMenu():
    BG.fill(BGCOLOR)

    #buttons
    pygame.draw.rect(BG, MAGENTA, exitBtnBounds)
    pygame.draw.rect(BG, MAGENTA, playBtnBounds)
    
    #text
    text = font.render('NO POWER!', True, BLACK)
    BG.blit(text, (res/4,80))

    playTxt = smallfont.render('PLAY!', True, BLACK)
    exitTxt = smallfont.render('EXIT', True, BLACK)

    BG.blit(playTxt, (res/2 - 25,300 + 50))
    BG.blit(exitTxt, (res/2 - 12, 632))

def drawEnd(score):
    BG.fill(BGCOLOR)

    text = smallfont.render('Good game! Score: %i' % score, True, BLACK)
    BG.blit(text, (res/4, 330))

def buttonClicked(mouse):
    (x,y) = (mouse[0], mouse[1])
    #in bounds of a button
    #exit
    if (exitBtnBounds[0] <= x <= exitBtnBounds[0]+exitBtnBounds[2] and
            exitBtnBounds[1] <= y <= exitBtnBounds[1]+exitBtnBounds[3]):
        pygame.quit()
        sys.exit()
    
    #lvl
    if (playBtnBounds[0] <= x <= playBtnBounds[0]+playBtnBounds[2] and
            playBtnBounds[1] <= y <= playBtnBounds[1]+playBtnBounds[3]):
        global onMenu
        onMenu = False

#Player helpers
def move(obj, d):
    if d == 'L':
        obj.rect.move_ip(-l, 0)
        obj.coords = (obj.coords[0]-1, obj.coords[1])
    elif d == 'R':
        obj.rect.move_ip(l, 0)
        obj.coords = (obj.coords[0]+1, obj.coords[1])
    elif d == 'U':
        obj.rect.move_ip(0, -l)
        obj.coords = (obj.coords[0], obj.coords[1]-1)
    elif d == 'D':
        obj.rect.move_ip(0, l)
        obj.coords = (obj.coords[0], obj.coords[1]+1)

    obj.dir = Player.dirs[d]
    obj.getImage(obj.dir)

    #if we moved somewhere illegal, move back (unless we are undoing)
    if grid[obj.coords[0]][obj.coords[1]] in ['F', 'P', 'O']:     
        oppDirs = {'L': 'R', 'R': 'L', 'U': 'D', 'D': 'U', 'N': 'N'}
        move(obj, oppDirs[d])

        obj.dir = Player.dirs[d]
        obj.getImage(obj.dir)

def wireIntersect(wires, newWire):
    [(a,b),(c,d)] = newWire
    
    for [(w,x),(y,z)] in wires:
        #make lines
        #(w,x) + t[(y,z) - (w,x)]
        g,h,i,j = c-a,d-b, y-w,z-x
        #(w,x)+t(i,j) = (a,b)+s(g,h)
        if (g*j == h*i): #div by 0 error = parallel
            if (a == c):
                if (a != w): continue
                else: return (b < x < d or b < z < d or b > x > d or b > z > d
                              or x < b < z or x < d < z or x > b > z or x > d > z)
            elif (b == d):
                if (b != x): continue
                else: return (a < w < c or a < y < c or a > w > c or a > y > c
                              or w < a < y or w < c < y or w > a > y or w > c > y)
            elif (abs((w-a)/(c-a) - (x-b)/(d-b) ) <= 10e-5):
                #same line! check if (w,x) or (y,z) on newWire
                return 0 <= (w-a)/(c-a) <= 1 or 0 <= (x-b)/(d-b) <= 1
            else: continue
        
        s = (j*w-i*x - a*j + b*i) / (g*j - h*i)
        
        if i == 0:
            #old wire is vertical: w==y; (w,x)+t(0,j)=(a,c)+s(g,h)
            s = (w-a)/g
            t = (b + s*h - x) / j
        else:
            t = (a - w + s*g) / i

        if (s,t) in {(0,0), (0,1), (1,0), (1,1)}:
            continue
        elif (0 <= s <= 1 and 0 <= t <= 1):
            return True

    return False
def underWire(wires):
    validSqs = []

    for [(a,b),(c,d)] in wires:
        g = math.gcd(c-a, d-b)
        
        if g == 0 or g == 1: continue

        (s,t) = ((c-a)//g, (d-b)//g)
        
        for i in range(1,g):
            validSqs.append((a+s*i,b+t*i))
    
    return validSqs

class Player(pygame.sprite.Sprite):
    dirs = {'L': (-1,0), 'R': (1,0), 'U': (0,-1), 'D': (0,1)}

    #triangle for self.image
    def getImage(self,d): 
        baseRect = pygame.Surface([l*.8, l*.8])
        a,b,c = l*.1, l*.4, l*.7
        
        if d == self.dirs['R']:
            pygame.draw.polygon(baseRect, RED, [[b,a],[b,c],[c,b]])
        elif d == self.dirs['L']:
            pygame.draw.polygon(baseRect, RED, [[b,a],[b,c],[a,b]])
        elif d == self.dirs['D']:
            pygame.draw.polygon(baseRect, RED, [[b,c],[c,b],[a,b]])
        elif d == self.dirs['U']:
            pygame.draw.polygon(baseRect, RED, [[b,a],[c,b],[a,b]])
        
        self.image = baseRect

        return baseRect
        

    def __init__(self):
        super().__init__()
        
        self.coords = (0,0)
        self.dir = self.dirs['R']
        self.items = [f,p,r]

        self.image = self.getImage(self.dir)
        self.rect = self.image.get_rect()
        self.rect.center = (50+l*.5,50+l*.5)

        self.wires = list()
        self.hasWire = False
        self.powered = []

        self.G = Game()
    def reset(self):
        self.coords = (0,0)
        self.items = [f,p,r]
        self.rect.center = (50+l*.5, 50+l*.5)

        resetGrid()

        self.wires = list()
        self.hasWire = False
        self.powered = []

        self.G.reset()
    
    def update(self, key):
        #move by arrow keys
        if not (pygame.key.get_mods() & pygame.KMOD_SHIFT): #can't be holding shift
            if (self.coords[0] > 0):
                if key == K_LEFT:
                    move(self, 'L')
                    self.G.turnEnd(grid[self.coords[0]][self.coords[1]] == 'R')
            if (self.coords[0] < gridSize-1):
                if key == K_RIGHT:
                    move(self, 'R')
                    self.G.turnEnd(grid[self.coords[0]][self.coords[1]] == 'R')
            if (self.coords[1] > 0):
                if key == K_UP:
                    move(self, 'U')
                    self.G.turnEnd(grid[self.coords[0]][self.coords[1]] == 'R')
            if (self.coords[1] < gridSize-1):
                if key == K_DOWN:
                    move(self, 'D')
                    self.G.turnEnd(grid[self.coords[0]][self.coords[1]] == 'R')
        
        #change facing direction: holding shift keys
        if key in {K_UP, K_DOWN, K_LEFT, K_RIGHT} and (pygame.key.get_mods() & pygame.KMOD_SHIFT):
            keyToDir = {K_UP: (0,-1), K_DOWN: (0,1), K_LEFT: (-1,0), K_RIGHT: (1,0)}
            self.dir = keyToDir[key]
            self.getImage(self.dir)

        #restart
        if key == K_r:
            self.reset()
        
        #drop item
        if (key in {K_d, K_f, K_s} and 
            0 <= self.coords[0] + self.dir[0] < gridSize and 0 <= self.coords[1] + self.dir[1] < gridSize and
            grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] == ''):

            itemDict = {K_d: 'P', K_f: 'F', K_s: 'R'}
            item = itemDict[key]

            if(self.items[items.index(item)] > 0):
                self.items[items.index(item)] -= 1

                grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] = item
                
                self.G.turnEnd(grid[self.coords[0]][self.coords[1]] == 'R')
            
            #add factories to powered
            if item == 'F': self.powered.append((self.coords[0] + self.dir[0],self.coords[1] + self.dir[1]))

            #if a pole is put underneath a wire, split the wire into two
            place = (self.coords[0] + self.dir[0],self.coords[1] + self.dir[1])
            newWires = copy.deepcopy(self.wires)
            for wire in self.wires:
                if place in underWire([wire]):
                    [a,b] = wire
                    newWires.remove(wire)
                    newWires.extend([[a, place], [b,place]])
            self.wires = newWires
        
        #start/end wires
        if key == K_SPACE:
            if self.hasWire:
                #if facing P
                if grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] == 'P':
                    self.hasWire = False
                    self.wires[-1][1] = (self.coords[0] + self.dir[0], self.coords[1] + self.dir[1])

                    if wireIntersect(self.wires[:-1], self.wires[-1]): #can't intersect wires
                        self.wires.pop()
                    else:
                        self.calcPowered()
                #if facing F, must be stemming from P, and F can't have more than one wire
                if (grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] == 'F'
                    and grid[self.wires[-1][0][0]][self.wires[-1][0][1]] == 'P'):

                    factoryConnected = False
                    for (x,y) in self.wires:
                        if x == (self.coords[0] + self.dir[0], self.coords[1] + self.dir[1]):
                            factoryConnected = True
                            break
                    
                    if not factoryConnected:
                        self.hasWire = False
                        #need to make sure F is always first in self.wires[i]
                        self.wires[-1][1] = self.wires[-1][0]
                        self.wires[-1][0] = (self.coords[0] + self.dir[0], self.coords[1] + self.dir[1])

                        if wireIntersect(self.wires[:-1], self.wires[-1]): #can't intersect wires
                            self.wires.pop()
                        else:
                            self.calcPowered()
                
                #if connects a house, change to 'O', and update self.G
                if grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] == 'H':
                    self.hasWire = False
                    self.wires[-1][1] = (self.coords[0] + self.dir[0], self.coords[1] + self.dir[1])

                    if wireIntersect(self.wires[:-1], self.wires[-1]): #can't intersect wires
                        self.wires.pop()
                    else:
                        self.calcPowered()
                    '''else:
                        grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] = 'O'
                        data = self.G.decHouse()
                        
                        if data[0]:
                            #last house was just connected!
                            self.items[0] += data[1]
                            self.items[1] += data[2]
                            self.items[2] += data[3]'''

            else:
                #needs to be facing F or P
                if grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] == 'F':
                    #F can only support 1 wire total
                    factoryConnected = False
                    for (x,y) in self.wires:
                        if x == (self.coords[0] + self.dir[0], self.coords[1] + self.dir[1]):
                            factoryConnected = True
                            break

                    if not factoryConnected:
                        self.hasWire = True
                        self.wires.append([(self.coords[0] + self.dir[0], self.coords[1] + self.dir[1]), -1])

                elif grid[self.coords[0] + self.dir[0]][self.coords[1] + self.dir[1]] == 'P':
                    self.hasWire = True
                    self.wires.append([(self.coords[0] + self.dir[0], self.coords[1] + self.dir[1]), -1])
        
        #cut wires
        if key == K_a and self.hasWire:
            self.hasWire = False
            self.wires.pop()
        
        #get rid of 'dot' wires
        if len(self.wires) > 0 and self.wires[-1][0] == self.wires[-1][1]:
            self.wires.pop()

    def calcPowered(self): #called only when a new wire is added
        #if a wire is placed on top of any pole, split the wire
        newWire = self.wires[-1]
        for (x,y) in underWire([newWire]):
            if grid[x][y] == 'P':
                self.wires.pop()
                self.wires.append([newWire[0], (x,y)])

                #need to run calcPowered on the 2nd to last 'new' wire
                self.calcPowered()

                #only after may we finish this calcPowered()
                self.wires.append([(x,y), newWire[1]])

        #first, add things that were powered before
        powered = self.powered
        
        #see if new wire did anything
        needCalc = False
        (a,b) = self.wires[-1]
        ta, tb = a in powered, b in powered
        
        if ta or tb:
            if ta and not tb:
                powered.append(b)
                needCalc = True
            elif not ta and tb:
                powered.append(a)
                needCalc = True
            elif ta and tb: needCalc = True
        
        if not needCalc: return
                
        #don't forget about sqs that are right underneath a wire
        unders = underWire([(a,b)])
        for sq in unders:
            if sq not in powered: powered.append(sq)

        #recursively go through wires, until no more change is needed
        wireTracker = self.wires
        while(needCalc):
            needCalc = False

            for [a, b] in wireTracker:
                ta, tb = a in powered, b in powered
                if ta and not tb:
                    needCalc = True
                    powered.append(b)
                elif not ta and tb:
                    needCalc = True
                    powered.append(a)

        self.powered = powered

        #now, we may permanently power houses
        for (a,b) in powered:
            if grid[a][b] == 'H':
                grid[a][b] = 'O'
                data = self.G.decHouse(self.wires)
                
                if data[0]:
                    #last house was just connected!
                    self.items[0] += data[1]
                    self.items[1] += data[2]
                    self.items[2] += data[3]

                    break

    #DRAWING
    def getTurnCtr(self):
        return self.G.returnTurnCtr()
    def drawTurnCtr(self):
        turnFont = pygame.font.SysFont('Arial',int(l*.7))
        text = turnFont.render("Turns Left: %i" % self.getTurnCtr(), True, BLACK)
        BG.blit(text, (60, 25))

    def drawHotbar(self):
        (x,y) = (res//3,710)
        w = res//2
        v = 2*res//3
        numFont = pygame.font.SysFont('Arial',int(l*.7))

        #f,p,r numbers
        fNum = numFont.render(str(self.items[0]), True, BLACK)
        pygame.draw.rect(BG, GRAY, (x, y, l*.7, l*.7))

        BG.blit(fNum, (x-25,y))
        pNum = numFont.render(str(self.items[1]), True, BLACK)
        pygame.draw.circle(BG, BLUE, (v+l*.4, y+l*.4), 8)
        
        BG.blit(pNum, (v-25,y))

        rNum = numFont.render(str(self.items[2]), True, BLACK)
        pygame.draw.rect(BG, BROWN, (w, y, l*.7, l*.7))
        BG.blit(rNum, (w-25, y))

    def drawWires(self):
        for [w, x] in self.wires:
            if x == -1:
                x = self.coords
            (a,b) = w
            (c,d) = x
            pygame.draw.line(BG, BLACK, (50+l*(a+.5), 50+l*(b+.5)), (50+l*(c+.5), 50+l*(d+.5)))

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.drawHotbar()
        self.drawWires()
        self.drawTurnCtr()

#GAME
class Game():
    turnCtr = 30

    def __init__(self):
        self.houses = 1
        self.level = 1
    def reset(self):
        self.houses = 1
        self.level = 1

        self.turnCtr = 30

    def returnTurnCtr(self):
        return self.turnCtr
    def turnEnd(self, onRoad):
        if onRoad: self.turnCtr -= 0.5
        else: self.turnCtr -= 1

        if(self.turnCtr < 0):
            global gameEnd
            gameEnd = True #GAMEOVER

    def decHouse(self, wires):
        self.houses -= 1
        if(self.houses == 0):
            global grid
            #RAMP UP IN DIFFICULTY
            self.level += 1
            self.turnCtr += self.level*10

            newH = self.level
            newF = random.randint(0, self.level//2)
            newP = newH - newF
            newR = self.level

            #generate newH's
            self.houses = self.level
            range = min(gridSize-1, int(self.level*2.5))
            i=0
            underSqs = underWire(wires)
            while(i < newH):
                rx, ry = random.randint(0, range), random.randint(0, range)
                if grid[rx][ry] == '' and (rx,ry) not in underSqs:
                    grid[rx][ry] = 'H'
                    i+=1

            #lastly, see if hosues are under any wires
            
            return [True, newF, newP, newR]
        return [False]
            
#print('\n'.join(map(''.join, grid)))

P = Player()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        
        if onMenu:
            drawMenu()

            if event.type == pygame.MOUSEBUTTONDOWN:
                buttonClicked(pygame.mouse.get_pos())
                P.reset()
        elif gameEnd:
            #calc score
            score = P.G.level * (P.G.level + 1) // 2 - P.G.houses
            drawEnd(score)

            if event.type == pygame.MOUSEBUTTONDOWN:
                gameEnd = False
                onMenu = True
        else:
            if event.type == pygame.KEYDOWN:
                P.update(event.key)

            drawBG()
            P.draw(BG)

        pygame.display.update()
        FramePerSec.tick(FPS)