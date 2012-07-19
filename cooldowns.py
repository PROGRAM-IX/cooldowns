import random, sys, time, pygame
from pygame.locals import *

class HitBlock(object):
    hit = 0
    score = 10
    rect = None
    xMod = 0
    yMod = 0
    changeDir = 0 # counter to determine if we should attempt a direction change
    def __init__(self, h, r):
        object.__init__(self)
        self.hit = h
        self.rect = r
        self.xMod = random.randint(-2, 2)
        self.yMod = random.randint(1, 3)
    def activate(self):
        self.hit = -1 # if planning to grey out blocks you've hit
        return self.score 
    def update(self):
        self.changeDirTest()
        self.draw()
    def draw(self):
        pygame.draw.rect(DISPLAYSURF, colours[self.hit], self.rect)
    def changeDirTest(self):
        if self.changeDir % 60 == 0:
            if random.randint(0, 5) == 0:
                self.xMod = random.randint(-2, 2)
                self.yMod = random.randint(1, 3)
        self.changeDir = self.changeDir + 1
    

FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 640
BUTTONSIZE = 100
BUTTONGAPSIZE = 20

BASICFONT = None
BIGFONT = None
MEDFONT = None

#                R    G    B
WHITE        = (255, 255, 255)
BLACK        = (  0,   0,   0)
BRIGHTRED    = (255,   0,   0)
RED          = (155,   0,   0)
BRIGHTGREEN  = (  0, 255,   0)
GREEN        = (  0, 155,   0)
BRIGHTBLUE   = (  0,   0, 255)
BLUE         = (  0,   0, 155)
BRIGHTYELLOW = (255, 255,   0)
YELLOW       = (155, 155,   0)
DARKGRAY     = ( 40,  40,  40)
LIGHTGRAY    = (100, 100, 100)
bgColor = DARKGRAY

XMARGIN = int((WINDOWWIDTH - (4 * BUTTONSIZE) - (3 * BUTTONGAPSIZE)) / 2)
YMARGIN = int((WINDOWHEIGHT - (BUTTONSIZE) - XMARGIN))

# Rect objects for each of the four buttons
Q_RECT = pygame.Rect(XMARGIN, YMARGIN, BUTTONSIZE, BUTTONSIZE)
W_RECT = pygame.Rect(XMARGIN + BUTTONSIZE + BUTTONGAPSIZE, YMARGIN, BUTTONSIZE, BUTTONSIZE)
E_RECT = pygame.Rect(XMARGIN + (BUTTONSIZE * 2) + (BUTTONGAPSIZE * 2), YMARGIN, BUTTONSIZE, BUTTONSIZE)
R_RECT = pygame.Rect(XMARGIN + (BUTTONSIZE * 3) + (BUTTONGAPSIZE * 3), YMARGIN, BUTTONSIZE, BUTTONSIZE)

# Cooldown variables
CD_Q = 2
CD_W = 4
CD_E = 3
CD_R = 5
_Q = True
_W = True
_E = True
_R = True
curr_CD_Q = 0
curr_CD_W = 0
curr_CD_E = 0
curr_CD_R = 0
start_Q = time.time()
start_W = time.time()
start_E = time.time()
start_R = time.time()

paused = False

blockTypes = [pygame.Rect(XMARGIN, -90, 80, 80), pygame.Rect(XMARGIN, -50, 40, 40), pygame.Rect(XMARGIN, -50, 50, 50), pygame.Rect(XMARGIN, -50, 30, 30)]
scores = [10, 20, 30, 40]
blocks = [] # list of active blocks 
spawnBlock = 0
mousex = 0
mousey = 0
colours = [BRIGHTYELLOW, BRIGHTBLUE, BRIGHTRED, BRIGHTGREEN]
score = 0
missed = 0 # number of keypresses that have not hit an appropriate target
dropped = 0 # number of blocks that have fallen offscreen


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT, MEDFONT, BEEP1, BEEP2, BEEP3, BEEP4, start_Q, start_W, start_E, start_R, _Q, _W, _E, _R, curr_CD_Q, curr_CD_W, curr_CD_E, curr_CD_R, spawnBlock, blocks, mousex, mousey, score, missed, dropped, paused
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Cooldowns')
    curr_CD_Q = 0
    curr_CD_W = 0
    curr_CD_E = 0
    curr_CD_R = 0   
    BASICFONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 90)
    MEDFONT = pygame.font.Font('freesansbold.ttf', 70)

    infoSurf = BASICFONT.render('Learn cooldown patterns by using the Q, W, E, R keys.', 1, WHITE)
    infoRect = infoSurf.get_rect()
    infoRect.topleft = (10, WINDOWHEIGHT - 20)

    # load the sound files
    BEEP1 = pygame.mixer.Sound('beep1.ogg')
    BEEP2 = pygame.mixer.Sound('beep2.ogg')
    BEEP3 = pygame.mixer.Sound('beep3.ogg')
    BEEP4 = pygame.mixer.Sound('beep4.ogg')

    while True: # main game loop
        
        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEMOTION:
                mousex, mousey = event.pos
                
            elif event.type == KEYDOWN:
                if not paused:
                    
                    if event.key == K_q and _Q:
                        q()
                        clickedButton = YELLOW
                    elif event.key == K_w and _W:
                        w()
                        clickedButton = BLUE
                    elif event.key == K_e and _E:
                        e()
                        clickedButton = RED
                    elif event.key == K_r and _R:
                        r()
                        clickedButton = GREEN
                if event.key == K_p:
                    pauseUnpause()
        
        if not paused:
            clickedButton = None # button that was clicked (set to YELLOW, RED, GREEN, or BLUE)
            DISPLAYSURF.fill(bgColor)
            
            if spawnBlock % 60 == 0:
                newBlock()
            spawnBlock = spawnBlock + 1
        
                
            
            for a in blocks:
                #print "test"
                if a.rect.y > WINDOWHEIGHT:
                    blocks.remove(a)
                    dropped += 1
                
                else:
                    if a.rect.x + a.rect.width >= WINDOWWIDTH or a.rect.x <= 0:
                        a.xMod = a.xMod * -1
                    a.rect.y = a.rect.y + a.yMod
                    a.rect.x = a.rect.x + a.xMod
                    #pygame.draw.rect(DISPLAYSURF, BRIGHTYELLOW, a)
                    a.update()
        
            drawButtons()
            updateCooldowns()
            displayCooldowns()
            scoreSurf = BASICFONT.render("Score: " + str(score) + " Missed: " + str(missed) + " Dropped: " + str(dropped), 1, WHITE)
            scoreRect = scoreSurf.get_rect()
            scoreRect.topleft = (10, 10)
            DISPLAYSURF.blit(scoreSurf, scoreRect) 
            DISPLAYSURF.blit(infoSurf, infoRect)
            pygame.display.update()
            FPSCLOCK.tick(FPS)


def newBlock():
    blockType = random.randint(0, 3)
    block = HitBlock(blockType, blockTypes[blockType].copy())
    block.rect.x = random.randint(0, WINDOWHEIGHT - (block.rect.width))
    blocks.append(block)
    print "BLOCK!"


def displayCooldowns():
    global BASICFONT, BIGFONT, BLACK, curr_CD_Q, curr_CD_W, curr_CD_E, curr_CD_R, Q_RECT, W_RECT, E_RECT, R_RECT
    qSurf = BASICFONT.render('Q', 1, BLACK)
    DISPLAYSURF.blit(qSurf, Q_RECT)
    wSurf = BASICFONT.render('W', 1, BLACK)
    DISPLAYSURF.blit(wSurf, W_RECT)
    eSurf = BASICFONT.render('E', 1, BLACK)
    DISPLAYSURF.blit(eSurf, E_RECT)
    rSurf = BASICFONT.render('R', 1, BLACK)
    DISPLAYSURF.blit(rSurf, R_RECT)
    if not _Q:
        cd = curr_CD_Q % 1000.0
        if cd < 1.0:
            qCDSurf = MEDFONT.render("{0:.1f}".format(cd), 1, BLACK)
        else:
            qCDSurf = BIGFONT.render(str(int(cd)), 1, BLACK)
        DISPLAYSURF.blit(qCDSurf, Q_RECT)
    if not _W:
        cd = curr_CD_W % 1000.0
        if cd < 1.0:
            wCDSurf = MEDFONT.render("{0:.1f}".format(cd), 1, BLACK)
        else:
            wCDSurf = BIGFONT.render(str(int(cd)), 1, BLACK)
        DISPLAYSURF.blit(wCDSurf, W_RECT)
    if not _E:
        cd = curr_CD_E % 1000.0
        if cd < 1.0:
            eCDSurf = MEDFONT.render("{0:.1f}".format(cd), 1, BLACK)
        else:
            eCDSurf = BIGFONT.render(str(int(cd)), 1, BLACK)
        DISPLAYSURF.blit(eCDSurf, E_RECT)
    if not _R:
        cd = curr_CD_R % 1000.0
        if cd < 1.0:
            rCDSurf = MEDFONT.render("{0:.1f}".format(cd), 1, BLACK)
        else:
            rCDSurf = BIGFONT.render(str(int(cd)), 1, BLACK)
        DISPLAYSURF.blit(rCDSurf, R_RECT)


def q():
    global start_Q, _Q, BEEP1, mousex, mousey, score, missed
    start_Q = time.time()
    _Q = False
    #print start_Q
    for b in blocks:
        if b.rect.collidepoint( (mousex, mousey) ):
            if b.hit == 0:
                BEEP1.play()
                score += scores[b.hit]
                blocks.remove(b)
                print "Hit!"
                return
    missed +=1
    


def w():
    global start_W, _W, BEEP2, mousex, mousey, score, missed
    start_W = time.time()
    _W = False
    #print start_W
    for b in blocks:
        if b.rect.collidepoint( (mousex, mousey) ):
            if b.hit == 1:
                BEEP2.play()
                score += scores[b.hit]
                blocks.remove(b)
                print "W Hit!"
                return
    missed +=1

   
    
def e():
    global start_E, _E, BEEP3, mousex, mousey, score, missed
    start_E = time.time()
    _E = False
    #print start_E
    for b in blocks:
        if b.rect.collidepoint( (mousex, mousey) ):
            if b.hit == 2:
                BEEP3.play()
                score += scores[b.hit]
                blocks.remove(b)
                print "E Hit!"
                return
    missed +=1

    
def r():
    global start_R, _R, BEEP4, mousex, mousey, score, missed
    start_R = time.time()
    _R = False
    #print start_R
    for b in blocks:
        if b.rect.collidepoint( (mousex, mousey) ):
            if b.hit == 3:
                BEEP4.play()
                score += scores[b.hit]
                blocks.remove(b)
                print "R Hit!"
                return
    missed +=1


def updateCooldowns():
    global curr_CD_Q, curr_CD_W, curr_CD_E, curr_CD_R, _Q, _W, _E, _R
      
    if not _Q:
        #curr_CD_Q = int(CD_Q - ((time.time() - start_Q) % 1000.0))
        curr_CD_Q = (CD_Q) - (time.time() - start_Q)  
    if not _W:
        #curr_CD_W = int(CD_W - ((time.time() - start_W) % 1000.0))
        curr_CD_W = (CD_W) - (time.time() - start_W) 
    if not _E:
        #curr_CD_E = int(CD_E - ((time.time() - start_E) % 1000.0))
        curr_CD_E = (CD_E) - (time.time() - start_E)
    if not _R:
        #curr_CD_R = int(CD_R - ((time.time() - start_R) % 1000.0))
        curr_CD_R = (CD_R) - (time.time() - start_R) 
    
    if curr_CD_Q <= 0:
        curr_CD_Q = 0
        _Q = True
    if curr_CD_W <= 0:
        curr_CD_W = 0
        _W = True
    if curr_CD_E <= 0:
        curr_CD_E = 0
        _E = True
    if curr_CD_R <= 0:
        curr_CD_R = 0
        _R = True
    
    
def terminate():
    pygame.quit()
    sys.exit()
    raise SystemExit 

def pauseUnpause():
    global paused, start_Q, start_W, start_E, start_R
    if paused:
        now = time.time()
        paused = False
        print (CD_Q) - curr_CD_Q
        start_Q = now - ((CD_Q) - curr_CD_Q)
        start_W = now - ((CD_W) - curr_CD_W)
        start_E = now - ((CD_E) - curr_CD_E)
        start_R = now - ((CD_R) - curr_CD_R)
    else:
        paused = True
        pause_time = time.time()

def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def drawButtons():
    if _Q:
        pygame.draw.rect(DISPLAYSURF, BRIGHTYELLOW, Q_RECT)
    else:
        pygame.draw.rect(DISPLAYSURF, YELLOW, Q_RECT)
    if _W:
        pygame.draw.rect(DISPLAYSURF, BRIGHTBLUE, W_RECT)
    else:
        pygame.draw.rect(DISPLAYSURF, BLUE, W_RECT)
    if _E:
        pygame.draw.rect(DISPLAYSURF, BRIGHTRED, E_RECT)
    else:
        pygame.draw.rect(DISPLAYSURF, RED, E_RECT)
    if _R:
        pygame.draw.rect(DISPLAYSURF, BRIGHTGREEN, R_RECT)
    else:
        pygame.draw.rect(DISPLAYSURF, GREEN, R_RECT)


if __name__ == '__main__':
    main()
