import pygame
import random
import numpy as np

TILE_SIZE = 40

COLS = 20
ROWS = 20

MINE_COUNT = 50

WIDTH = COLS * TILE_SIZE
HEIGHT = ROWS * TILE_SIZE

GREEN_LIGHT = pygame.Color(173, 232, 100)
GREEN_DARK = pygame.Color(153, 212, 80)
GREEN_HOVER = pygame.Color(213, 255, 122)
YELLOW_LIGHT = pygame.Color(247, 222, 176)
YELLOW_DARK = pygame.Color(237, 209, 159)
RED_FLAG = pygame.Color(255, 51, 51)

MINE_COLORS = (
    pygame.Color(252, 109, 0),
    pygame.Color(202, 252, 0),
    pygame.Color(0, 255, 140),
    pygame.Color(0, 247, 255),
    pygame.Color(132, 0, 255),
    pygame.Color(255, 0, 115)
)

pygame.mixer.init()

class Tile:

    def __init__(self, row: int, col: int) -> None:
        self.row = row
        self.col = col
        
        self.x = self.col * TILE_SIZE
        self.y = self.row * TILE_SIZE

        self.color = GREEN_DARK if (self.row + self.col) % 2 else GREEN_LIGHT

        self.mine = False
        self.flag = False
        self.flip = False
        self.hover = False

        self.number = 0
        self.digit_surf = None


    def draw(self) -> None:
        
        pygame.draw.rect(screen, self.color, (self.x, self.y, TILE_SIZE, TILE_SIZE))

        if self.flag:
            draw_flag(self.x, self.y)
        
        elif self.flip and self.digit_surf:
            screen.blit(self.digit_surf, (self.x, self.y))


    def toggle_hover(self):
        
        self.hover = not self.hover

        if self.flip:
            return
        
        if self.hover:
            self.old_color = self.color
            self.color = GREEN_HOVER
            return 
        
        self.color = self.old_color
        

    def flip_tile(self) -> None:
        
        if self.flip or self.flag:
            return

        self.flip = True

        drop_tile(self.x, self.y, self.color)

        if self.mine:
            self.color = random.choice(MINE_COLORS)

            if not LOST:
                lose_game()
            
            return
    
        self.color = YELLOW_DARK if (self.row + self.col) % 2 else YELLOW_LIGHT


        if self.number == 0 and not LOST:

            for neighbor in self.neighbors:
                neighbor.flip_tile()
        

    def toggle_flag(self):

        if self.flip:
            return
        
        if self.flag:
            self.flag = False
            drop_flag(self.x, self.y)

        else:
            self.flag = True

        
    def set_connections(self):

        self.neighbors = []

        mine_count = 0

        for row in range(self.row - 1, self.row + 2):
            for col in range(self.col - 1, self.col + 2):

                if 0 <= col < COLS and 0 <= row < ROWS:

                    tile = tiles[row][col]
                    self.neighbors.append(tile)

                    if tile.mine:
                        mine_count += 1

        self.number = mine_count

        if self.number and not self.mine:
            self.digit_surf = digit_surfs[self.number]


    def auto_flip(self):

        if not self.flip:
            return

        marks_count = len([neighbor for neighbor in self.neighbors if neighbor.flag])

        if marks_count == self.number:
            for neighbor in self.neighbors:
                neighbor.flip_tile()


class DroppingTile:

    points = (
        (-20, -20),
        (-20, 20),
        (20, 20),
        (20, -20)
    )

    sound = pygame.mixer.Sound("./pop_tile.mp3")

    def __init__(self, x: int, y:int, color:pygame.Color) -> None:

        DroppingFlag.sound.play()

        self.color = color

        self.pos = np.array([x + TILE_SIZE / 2, y + TILE_SIZE / 2], dtype=np.float64)
        self.velocity = np.array(
            [random.random() * 4 - 2, -3], dtype=np.float64
        )

        self.acceleration = np.array([0, 0.1 + 0.1 * random.random()])
        self.angle = 0
        self.speed_angle = random.random() * 0.02 + 0.02

        self.scale = 1
        self.speed_scale = 0.02
    
    def update(self):

        self.velocity += self.acceleration
        self.pos += self.velocity

        self.angle += self.speed_angle
        self.scale -= self.speed_scale

    
    def draw(self):

        draw_points = []

        for x, y in DroppingTile.points:

            draw_x = (x * np.cos(self.angle) - y * np.sin(self.angle)) * self.scale + self.pos[0]
            draw_y = (x * np.sin(self.angle) + y * np.cos(self.angle)) * self.scale + self.pos[1]
            draw_points.append((draw_x, draw_y))
        
        pygame.draw.polygon(screen, self.color, draw_points)


class DroppingFlag:

    points = (
        (-5, 15),
        (-5, 10),
        (-8, 10),
        (-8, 0),
        (15, -8),
        (-12, -18),
        (-12, 10),
        (-15, 10),
        (-15, 15),
        (-5, 15)
    )

    sound = pygame.mixer.Sound("./pop_unflag.mp3")

    def __init__(self, x: int, y:int) -> None:

        DroppingFlag.sound.play()

        self.pos = np.array([x + TILE_SIZE // 2, y + TILE_SIZE // 2], dtype=np.float64)
        self.velocity = np.array(
            [random.random() * 4 - 2, -3], dtype=np.float64
        )

        self.acceleration = np.array([0, 0.1 + 0.1 * random.random()])
        self.angle = 0
        self.speed_angle = random.random() * 0.02 + 0.02

        self.scale = 1
        self.speed_scale = 0.02

    
    def update(self):

        self.velocity += self.acceleration
        self.pos += self.velocity

        self.angle += self.speed_angle
        self.scale -= self.speed_scale
        
    
    def draw(self):

        draw_points = []

        for x, y in DroppingFlag.points:

            draw_x = (x * np.cos(self.angle) - y * np.sin(self.angle)) * self.scale + self.pos[0]
            draw_y = (x * np.sin(self.angle) + y * np.cos(self.angle)) * self.scale + self.pos[1]
            draw_points.append((draw_x, draw_y))
        
        pygame.draw.polygon(screen, RED_FLAG, draw_points)



def draw_flag(draw_x:int, draw_y:int) -> pygame.Surface:

    scaled_points = [(x + draw_x + TILE_SIZE // 2, y + draw_y + TILE_SIZE // 2) for x, y in DroppingFlag.points]

    flag_surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
    
    pygame.draw.polygon(screen, RED_FLAG, scaled_points)

    return flag_surf


def get_digit_surfs() -> None:

    pygame.font.init()

    font_size = int(TILE_SIZE * 0.75)
    font = pygame.font.SysFont("Calibri", font_size, bold=True)

    digit_colors = ("blue", "forestgreen", "red", "purple", "orange", "black", "black", "black", "black")
 
    digit_surfs = {}

    for digit, color in enumerate(digit_colors, 1):
        
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        digit_surf = font.render(str(digit), True, color)

        x = (TILE_SIZE - digit_surf.get_width()) // 2
        y = (TILE_SIZE - digit_surf.get_height()) // 2

        surf.blit(digit_surf, (x, y))

        digit_surfs[digit] = surf
    
    return digit_surfs


def draw_tiles(mouse_row:int, mouse_col:int) -> None:

    if  pygame.mouse.get_focused():
        tile_hovered = tiles[mouse_row][mouse_col]
        tile_hovered.toggle_hover()

    for row in tiles:
        for tile in row:
            tile.draw()

    if  pygame.mouse.get_focused():
        tile_hovered.toggle_hover()

def draw_falling_tiles():
    to_remove = []

    for i, tile in enumerate(dropping_tiles):
        tile.update()
        tile.draw()

        if tile.scale < 0.05:
            to_remove.append(i)
    
    for index in to_remove[::-1]:
        del dropping_tiles[index]

def draw_falling_flags():
    to_remove = []

    for i, flag in enumerate(dropping_flags):
        flag.update()
        flag.draw()

        if flag.scale < 0.05:
            to_remove.append(i)
    
    for index in reversed(to_remove):
        del dropping_flags[index]


def generate_mines(mouse_row: int, mouse_col: int, radius: int = 4) -> None:

    count = 0

    while count < MINE_COUNT:
        
        rand_row = random.randrange(0, ROWS)
        rand_col = random.randrange(0, COLS)

        distance_x = abs(rand_row - mouse_row)
        distance_y = abs(rand_col - mouse_col)

        tile = tiles[rand_row][rand_col]

        if (distance_x < radius and distance_y < radius) or tile.mine:
            continue
        
        tile.mine = True
        count += 1

def remove_wrong_flags():

    for row in tiles:
        for tile in row:

            if tile.flag and not tile.mine:
                tile.toggle_flag()



def lose_game():
    global LOST

    LOST = True
    count = 0

    col_auto = 0
    row_auto = 0

    remove_wrong_flags()

    while True:

        mouse = pygame.mouse.get_pos()
        col = mouse[0] // TILE_SIZE
        row = mouse[1] // TILE_SIZE

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
            
            elif event.type == pygame.KEYDOWN:

                if event.ket == pygame.K_q:
                    pygame.quit()
    
        draw_tiles(row, col)
        draw_falling_tiles()
        draw_falling_flags()

        pygame.display.update()
        clock.tick(60)

        tile = tiles[row_auto][col_auto]

        if tile.mine and not tile.flip:
            
            if tile.flag:
                tile.toggle_flag()

            tile.flip_tile()

        count += 1

        col_auto = count % COLS
        row_auto = count // ROWS

    
        if row_auto >= ROWS or col_auto >= COLS:
            return


def win_game():

    while True:

        mouse = pygame.mouse.get_pos()
        col = mouse[0] // TILE_SIZE
        row = mouse[1] // TILE_SIZE

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
            
            elif event.type == pygame.KEYDOWN:

                if event.ket == pygame.K_q:
                    pygame.quit()
    
        draw_tiles(row, col)
        draw_falling_tiles()
        draw_falling_flags()

        screen.blit(win_surf, win_rect)

        pygame.display.update()
        clock.tick(60)



def drop_tile(x: int, y: int, color: pygame.Color) -> None:
    dropping_tiles.append(DroppingTile(x, y, color))


def drop_flag(x: int, y: int) -> None:
    dropping_flags.append(DroppingFlag(x, y))


tiles:list[list[Tile]] = [[Tile(row, col) for col in range(COLS)] for row in range(ROWS)]
dropping_tiles:list[DroppingTile] = []
dropping_flags:list[DroppingFlag] = []

pygame.init()
pygame.display.set_caption("MineSweeper")


clock = pygame.time.Clock()

screen = pygame.display.set_mode((WIDTH, HEIGHT))

digit_surfs = get_digit_surfs()
win_font = pygame.font.SysFont("Courrier", 100)
win_surf = win_font.render("You Won!", True, "blue")
win_rect = win_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))

STARTED = False
LOST = False

def main():
    global STARTED

    while True:

        mouse = pygame.mouse.get_pos()
        col = mouse[0] // TILE_SIZE
        row = mouse[1] // TILE_SIZE

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    if not STARTED:

                        STARTED = True
                        generate_mines(row, col)
                        
                        [tile.set_connections() for row in tiles for tile in row]

                    tiles[row][col].flip_tile()

                elif event.button == 2:
                    tiles[row][col].auto_flip()
        
                elif event.button == 3:
                    tiles[row][col].toggle_flag()


        draw_tiles(row, col)
        draw_falling_tiles()
        draw_falling_flags()

        pygame.display.update()
        
        clock.tick(60)

        if LOST:
            return


        not_flipped_count = 0

        for row in tiles:
            for tile in row:

                if not tile.flip:
                    not_flipped_count += 1
        
        if not_flipped_count == MINE_COUNT:
            win_game()


main()