import pygame
import time
import math
from os import path
from utils import scale_image, blit_rotate_centrer, blit_text_center
pygame.font.init()

GRASS = scale_image(pygame.image.load("imgs/grass.png"), 2.0)
TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.7)
TRACK_BORDER = scale_image(pygame.image.load("imgs/track-border.png"), 0.7)
TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
FINISH = pygame.image.load("imgs/finish.png")
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (350, 9)

RED_CAR = scale_image(pygame.image.load("imgs/car-red.png"), 0.05)
BLUE_CAR = scale_image(pygame.image.load("imgs/car-blue.png"), 0.08)

BT_FILE = "besttime.txt"

# okno gry
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racing Game!")
FPS = 60       # 60 frames per sec

MAIN_FONT = pygame.font.SysFont("abadi", 30)

#wizualki
class GameInfo:
    LEVELS = 100

    def __init__(self, level = 1):
        self.level = level
        self.started = False
        self.level_start_time = 0 
        self.besttime = 0

    def next_level(self):
        print(self.besttime)
        self.get_best_time()
        print(self.besttime)
        self.level += 1
        self.started = False
        self.level_start_time = 0

    def reset(self):
        self.level = 1
        self.started = False
        self.level_start_time = 0

    def game_finished(self):
        self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_start_time = time.time()

    def get_level_time(self):
        level_time = round(time.time() - self.level_start_time)
        if not self.started:
            return 0
        return level_time

    def load_data(self):
        self.dir = path.dirname(__file__)
        with open(path.join(self.dir, BT_FILE), "r") as f:
            try:
                self.besttime = int(f.read())
            except:
                self.besttime = math.inf
        return self.besttime
        
    def get_best_time(self):
        level_time = self.get_level_time()
        if level_time < self.besttime:
            self.besttime = level_time
            with open(path.join(self.dir, BT_FILE), 'w') as f:
               f.write(str(self.besttime))

        
# wprowadzanie aut
class AbstractCar:

    def __init__(self, max_speed, rotation_speed):
        self.img = self.IMG 
        self.max_speed = max_speed
        self.speed = 0
        self.rotation_speed = rotation_speed
        self.angle = 90
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    #skręcanie, czyli zmiana kąta
    def rotate (self, left=False, right=False):
        if left:
            self.angle += self.rotation_speed
        elif right:
            self.angle -= self.rotation_speed

    #wyświetlanie auta + rotacja
    def draw (self, win):
        blit_rotate_centrer(win, self.img, (self.x, self.y), self.angle) 

    # poruszanie sie do przodu
    def move_forward(self):
        self.speed = min(self.speed + self.acceleration, self.max_speed)
        self.move()

    # poruszanie sie do tyłu
    def move_backward(self):
        self.speed = max(self.speed - self.acceleration, -self.max_speed/2)
        self.move()

    #poruszanie sie po przekątnych 
    def move(self,):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.speed
        horizontal = math.sin(radians) * self.speed

        self.y -= vertical # jeśli wartość dodatnia to w lewo i w górę, jeśli ujemna to w prawo i w dół 
        self.x -= horizontal

    #zderzenie
    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)     # point of intersection
        return poi

    #pozycja od nowej rundy
    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 90
        self.speed = 0

class PlayerCar(AbstractCar): 
    IMG = RED_CAR   #moje auto
    START_POS = (310, 36)
   
    #stopniowe zwalnianie jeśli nie przyspieszasz 
    def reduce_speed(self):
        self.speed = max(self.speed - self.acceleration / 2, 0)
        self.move()

    #odbicie sie od ściany przy uderzeniu 
    def bounce(self):
        self.speed = -self.speed
        self.move()

    def next_level(self):
        self.reset()

# funkcja do wyświetlania na ekranie kolejno img:
def draw(win, images, player_car, game_info):
    for img, pos in images:
        win.blit(img, pos)

    level_text = MAIN_FONT.render (f"Level {game_info.level}", 1, (255, 255, 255))
    win.blit(level_text, (1, HEIGHT - level_text.get_height() - 680))

    time_text = MAIN_FONT.render (f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
    win.blit(time_text, (1, HEIGHT - time_text.get_height() - 700))

    best_time_text = MAIN_FONT.render (f"Best time: {game_info.load_data()}s", 1, (255, 255, 255))
    win.blit(best_time_text, (1, HEIGHT - best_time_text.get_height() - 720))

    player_car.draw(win)
    pygame.display.update()

#poruszanie się za pomocą klawiatury
def move_player(player_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_car.move_backward()

#jeśli nie wciskam przspieszenia, tracę na prędkości
    if not moved:
        player_car.reduce_speed()

#sprawdzenie czy doszło do kolizji
def handle_collision(player_car, game_info):
    if player_car.collide(TRACK_BORDER_MASK) != None:
        player_car.bounce()

    player_finish_poi_collide = player_car.collide(FINISH_MASK, *FINISH_POSITION)
    if player_finish_poi_collide != None:
        if player_finish_poi_collide[0] == 0:
            player_car.bounce()
        else:
            game_info.next_level()
            player_car.reset()
           

run = True
clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_car = PlayerCar(3 , 3) #prędkość auta
game_info = GameInfo()

while run:
    clock.tick(FPS)

    draw(WIN, images, player_car, game_info)
    
    #kontynuuj grę
    while not game_info.started:
        blit_text_center(WIN, MAIN_FONT, f"Press any key to start level {game_info.level}!")
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break

            #jeśli wciśniesz jakikolwiek przycisk gra sie rozpocznie
            if event.type == pygame.KEYDOWN:   
                game_info.start_level()
                game_info.load_data()

    #wyjście z gry
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
        
    #wywołanie funkcji do poruszania autem
    move_player(player_car)

    #wywoływanie funkcji do kolizji
    handle_collision(player_car, game_info)

    if game_info.game_finished():
        blit_text_center(WIN, MAIN_FONT, "Game over")
        pygame.time.wait(5000)
        game_info.reset()
        player_car.reset()

pygame.quit() 