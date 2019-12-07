from lib import *   # load local help module
import logging
WIDTH = 800
HEIGHT = 500
FPS = 60

#Initialising pygame
pygame.init() 
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("Metro Gnome")

#Colours
BLACK = (0,0,0)
WHITE = (255,255,255)
BACKGROUND_COLOR = (153,204,255) #aka the sky
GRAVITY = 0.55
RED = (255, 0, 0)
BROWN = (153,76,0)
HIGH_SCORE = 0
#Sounds-------------------------------------------------------------

gameMusic = pygame.mixer.Sound('sprites/metroGnome_Music_01.wav')

jump_sound = [pygame.mixer.Sound('sprites/jump01.wav'),\
              pygame.mixer.Sound('sprites/jump02.wav'),\
              pygame.mixer.Sound('sprites/jump03.wav'),\
              pygame.mixer.Sound('sprites/jump04.wav'),\
              pygame.mixer.Sound('sprites/jump05.wav'),\
              pygame.mixer.Sound('sprites/jump06.wav')]

gnomeLand = [pygame.mixer.Sound('sprites/gnome_land_01.wav'),\
              pygame.mixer.Sound('sprites/gnome_land_02.wav'),\
              pygame.mixer.Sound('sprites/gnome_land_03.wav'),\
              pygame.mixer.Sound('sprites/gnome_land_04.wav')]

gnomeSlide = [pygame.mixer.Sound('sprites/gnome_slide_01.wav'),\
              pygame.mixer.Sound('sprites/gnome_slide_02.wav'),\
              pygame.mixer.Sound('sprites/gnome_slide_03.wav')]

die_sound1 = pygame.mixer.Sound('sprites/hitObject.wav')
die_sound2 = pygame.mixer.Sound('sprites/splat01.wav')
checkPoint_sound = pygame.mixer.Sound('sprites/checkPoint.wav')
checkPoint_Timer = pygame.mixer.Sound('sprites/checkPointTimer.wav')

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
enermys = pygame.sprite.Group()
last_obstacle = pygame.sprite.Group()
bullets = pygame.sprite.Group()
grounds = pygame.sprite.Group()
clouds = pygame.sprite.Group()

class Gnome(pygame.sprite.Sprite):
    def __init__(self, sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self)
        self.run = False
        self.images,self.rect = load_sprite_sheet('gnome.png',5,1,sizex,sizey,-1) #splice sprite sheet running gnome
        self.images1,self.rect1 = load_sprite_sheet('gnome_ducking.png',2,1,59,sizey,-1) #splice sprite sheet ducking gnome
        self.rect.bottom = int(0.80* HEIGHT) #set gnome height to 80% of screen (standing on path)
        self.rect.left = WIDTH / 15
        self.image = self.images[0]
        self.index = 0
        self.counter = 0
        self.score = 0
        self.isJumping = False
        self.isDead = False
        self.isDucking = False
        self.isjumping = False
        self.movement = [0,0]
        self.jumpSpeed = 14.5 #speed of jumping

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width
        self.last_shoot = 0
    
    #LANDING FUNCTION TO SET WHERE THE JUMP DROPS TOO 
    def checkbounds(self): 
        if self.rect.bottom > int(0.80* HEIGHT):
            self.rect.bottom = int(0.80*HEIGHT)
            self.isJumping = False

    def shoot(self):
        if pygame.time.get_ticks() - self.last_shoot < 500: return
        self.last_shoot = pygame.time.get_ticks()
        bullet = Bullet(self.rect.right, self.rect.y + self.rect.height / 2)
        all_sprites.add(bullet)
        bullets.add(bullet)

    def update(self):
        # event for gnom object
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.run = True
            if self.rect.bottom == int(0.80*HEIGHT): #jump from height
                self.isJumping = True
                jump_sound[random.randint(0,5)].play() #Play jump sound chooses random jump sound from array
                self.movement[1] = -1*self.jumpSpeed
        else:
            self.isDucking = False
        if keys[pygame.K_LSHIFT]:
            gnomeSlide[random.randint(0,2)].play()
            if not (self.isJumping and self.isDead):
                self.isDucking = True
        if keys[pygame.K_RCTRL]:
            self.shoot()
        # update for game play
        if self.isJumping:
            self.movement[1] = self.movement[1] + GRAVITY
        #jumping
        if self.isJumping:
            self.index = 0
        elif self.isjumping:
            if self.index == 0:
                if self.counter % 400 == 399:
                    self.index = (self.index + 1)%2
            else:
                if self.counter % 20 == 19:
                    self.index = (self.index + 1)%2
        #ducking
        elif self.isDucking:
            if self.counter % 5 == 0:
                self.index = (self.index + 1)%2
        else:
            if self.counter % 5 == 0 and self.run:
                self.index = (self.index + 1)%2 + 2

        if self.isDead:
           self.index = 4

        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[(self.index)%2]
            self.rect.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()
        self.counter = (self.counter + 1)

class Logo(pygame.sprite.Sprite):
    def __init__(self, cent_x, cent_y, sizex=-1, sizey=-1):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('logo.png',300,140,-1) 
        self.rect.centerx = cent_x
        self.rect.centery = cent_y

class Ground(pygame.sprite.Sprite):
    def __init__(self,speed=-5, left = 0):
        pygame.sprite.Sprite.__init__(self)
        self.image,self.rect = load_image('ground.jpg',-1,-1,-1)
        self.rect.bottom = HEIGHT
        self.rect.width = WIDTH
        self.rect.left = left
        self.speed = speed
        self.rect.width = WIDTH
    
    def update(self):
        self.rect.left += self.speed
        if self.rect.right < 0:
            left = 0
            for i in grounds:
                if i.rect.right > left: left = i.rect.right
            self.rect.left = left - 10

class Obstacle(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('obstacles-small.png',3,1,sizex,sizey,-1) #reading from the sprite sheet
        self.rect.bottom = int(0.80*HEIGHT) #height of the obstacles on the screen
        self.rect.left = WIDTH + self.rect.width + random.randint(30, WIDTH / 2)
        self.image = self.images[random.randrange(0,3)]
        self.movement = [-1*speed,0]
        
    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            obstacles.remove(self)
            all_sprites.remove(self)

class Enermy(pygame.sprite.Sprite):
    def __init__(self,speed=5,sizex=-1,sizey=-1):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.images,self.rect = load_sprite_sheet('enemy.png',2,1,sizex,sizey,-1) #reading from the sprite sheet
        self.enemy_height = [HEIGHT*0.74,HEIGHT*0.68,HEIGHT*0.53] #Adjusting the ground level, max height and duck height ranges of the enemy
        self.rect.centery = self.enemy_height[random.randrange(0,3)]
        self.rect.left = WIDTH + self.rect.width
        self.image = self.images[0]
        self.movement = [-1*speed,0]
        self.index = 0
        self.counter = 0

    def update(self):
        if self.counter % 10 == 0:
            self.index = (self.index+1)%2
        self.image = self.images[self.index]
        self.rect = self.rect.move(self.movement)
        self.counter = (self.counter + 1)
        if self.rect.right < 0:
            self.kill()

class RetButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('replay_button.png',35,31,-1)
        self.rect.centerx = WIDTH / 2
        self.rect.top = HEIGHT*0.52

class GameOver(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('game_over.png',190,11,-1)
        self.rect.centerx = WIDTH / 2
        self.rect.centery = HEIGHT*0.35

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 10))
        self.image.fill(BROWN)
        self.rect = self.image.get_rect()
        self.rect.right = x
        self.rect.centery = y
        self.speedx = 10
    
    def update(self):
        self.rect.x += self.speedx
        if self.rect.left > WIDTH:
            self.kill()

class ScoreBoard(pygame.sprite.Sprite):
    def __init__(self,x=-1,y=-1):
        pygame.sprite.Sprite.__init__(self)
        self.score = 0
        self.tempimages,self.temprect = load_sprite_sheet('numbers.png',12,1,11,int(11*6/5),-1)
        self.image = pygame.Surface((55,int(11*6/5)))
        self.rect = self.image.get_rect()
        if x == -1:
            self.rect.left = WIDTH*0.89
        else:
            self.rect.left = x
        if y == -1:
            self.rect.top = HEIGHT*0.1
        else:
            self.rect.top = y
    def update(self):
        score_digits = extractDigits(self.score)
        self.image.fill(BACKGROUND_COLOR)
        for s in score_digits:
            self.image.blit(self.tempimages[s],self.temprect)
            self.temprect.left += self.temprect.width
        self.temprect.left = 0

class Cloud(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self,self.containers)
        self.image,self.rect = load_image('cloud.png',int(90*30/42),30,-1) #image dimensions of cloud
        self.speed = 1 #cloud speed range
        self.rect.left = x
        self.rect.top =  y  
        self.Cloud_height = [HEIGHT*0.42,HEIGHT*0.23,HEIGHT*0.10] #reduce numbers to increase cloud height
        self.rect.centery = self.Cloud_height[random.randrange(0,3)]
        self.rect.left = WIDTH + self.rect.width
        self.movement = [-2*self.speed,0]
        

    def update(self):
        self.rect = self.rect.move(self.movement)
        if self.rect.right < 0:
            self.kill()

Obstacle.containers = obstacles
Enermy.containers = enermys
Cloud.containers = clouds
# Game loop

# ----- Scene 1 (Intro) ------------------------
def introscreen():
    temp_gnome = Gnome(44,47)
    #logo image for intro screen
    logo = Logo(WIDTH * 0.6, HEIGHT * 0.6)
    all_sprites.add(temp_gnome)
    all_sprites.add(logo)
    gameMusic.set_volume(0.1)
    gameMusic.play(-1,0,4000) # Calls the game music on intro screen. Fades in over 4000ms


    running = True
    while running:
        clock.tick(FPS)
        # Process input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        # Update    
        all_sprites.update()
        # Draw / render
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        pygame.display.flip()

        if temp_gnome.run == True and temp_gnome.isJumping == False and temp_gnome.isjumping == False:
            all_sprites.remove(temp_gnome)
            all_sprites.remove(logo)
            gameMusic.fadeout(1000)
            # scene 1 is over , game started
            return 

    pygame.quit()
# ----- Scene 1 (Intro) over------------------------

# ----- Scene 2 (Game Play)-------------------------
def gameplay():
    global HIGH_SCORE #global variable essential
    GAME_SPEED = 4
    playergnome = Gnome(44,47)
    playergnome.run = True
    ground1 = Ground(-1*GAME_SPEED)
    ground2 = Ground(-1*GAME_SPEED, WIDTH)
    grounds.add(ground1)
    grounds.add(ground2)
    gameMusic.set_volume(0.6)
    die_sound2.set_volume(0.5)
    gameMusic.play(-1,0,4000) # Calls the game music at the start of gameplay. Fades in over 4000ms
    
    score = 0
    scoreboard = ScoreBoard()
    highsc = ScoreBoard(WIDTH*0.78)
    highsc.score = HIGH_SCORE
    counter = 0
    all_sprites.add(ground1)
    all_sprites.add(ground2)
    all_sprites.add(playergnome)
    all_sprites.add(scoreboard)
    all_sprites.add(highsc)

    o = Obstacle(GAME_SPEED,70,70)
    all_sprites.add(o)

    running = True
    while running:
        clock.tick(FPS)
        logging.info('This is an info message')
        # Process input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and playergnome.isDead:
                grounds.empty()
                all_sprites.empty()
                obstacles.empty()
                last_obstacle.empty()
                bullets.empty()
                enermys.empty()
                gameMusic.fadeout(1000)
                return "REPLAY"
        
        if playergnome.isDead != True:
            # Update    
            all_sprites.update()
            
            for c in obstacles:
                if pygame.sprite.collide_mask(playergnome,c):
                    playergnome.isDead = True
                    
            
            for e in enermys:
                if pygame.sprite.collide_mask(playergnome,e):
                    playergnome.isDead = True
            
            if playergnome.isDead == True:
                die_sound1.play() # play die sound
                if score > HIGH_SCORE:
                    HIGH_SCORE = score
                    highsc.score = score
                    highsc.update()
                reset = RetButton()
                over = GameOver()
                all_sprites.add(reset)
                all_sprites.add(over)

            hits = pygame.sprite.groupcollide(enermys, bullets, True, True)
            hits = pygame.sprite.groupcollide(obstacles, bullets, False, True)
            if len(obstacles) < 2:
                if len(obstacles) == 0:
                    last_obstacle.empty()
                    o = Obstacle(GAME_SPEED,70,70)
                    last_obstacle.add(o) #obstacle size
                    all_sprites.add(o)
                else:
                    for l in last_obstacle:
                        if l.rect.right < WIDTH*0.8 and random.randrange(0,50) == 10: #obstacle randomisation
                            last_obstacle.empty()
                            o = Obstacle(GAME_SPEED,70,70)
                            last_obstacle.add(o) #obstacle size
                            all_sprites.add(o)
            if len(enermys) == 0 and random.randrange(0,200) == 10 and counter > 500: #enemy randomisation
                for l in last_obstacle:
                    if l.rect.right < WIDTH*0.8:
                        last_obstacle.empty()
                        e = Enermy(GAME_SPEED, 46, 40)
                        last_obstacle.add(e)
                        all_sprites.add(e)
            if len(clouds) < 5 and random.randrange(0,300) == 10: #cloud randomisation

                c = Cloud(WIDTH,random.randrange(HEIGHT/5,HEIGHT/2))
                all_sprites.add(c) 
        # Draw / render
        screen.fill(BACKGROUND_COLOR)
        all_sprites.draw(screen)
        pygame.display.flip()
        counter += 1
        if counter % 10 == 0: score += 1
        scoreboard.score = score
        

        if counter%700 == 699:
            for g in grounds:
                g.speed -= 1
            GAME_SPEED += 1


# ----- Scene 2 (Game Play Over)-------------------------
def main():
    introscreen()
    ret = gameplay()
    while ret == "REPLAY":
        ret = gameplay()
if __name__ == "__main__":
    main()
    os._exit(0)