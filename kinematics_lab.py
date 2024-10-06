import sys
from dataclasses import dataclass
import pygame as pg
import kl_graphics
import button

pg.init()
window_size = [pg.display.Info().current_w - 100, pg.display.Info().current_h - 100]
screen = pg.display.set_mode(window_size)
screen_width, screen_height = screen.get_size()
pg.display.set_caption('Kinematics Lab')
font = pg.font.Font('freesansbold.ttf', 70)

# Fixed parameters
fps = 100
delta_t = 1 / fps
scale_ratio = screen_height / 3  # meters
border_width = 1 / 2  # meters
ground_height = 2 / 5  # meters
box_length = 2  # meters
box_top_gap = 1 / 30  # meters
box_side_gap = 1 / 15  # meters
max_height = 10  # meters

fullscreen = False

class PhysicsObject:
    def __init__(self, x, y, x_speed, y_speed, mass, cor, mu):
        self.x = x
        self.y = y
        self.x_speed = x_speed
        self.y_speed = y_speed
        self.mass = mass
        self.cor = cor
        self.mu = mu


class Ball(PhysicsObject):
    def __init__(self, x, y, x_speed, y_speed, mass, cor, mu, radius):
        super().__init__(x, y, x_speed, y_speed, mass, cor, mu)
        self.radius = radius
        self.player = None
        self.outline = 0
        self.selected = False
        self.error = [0, 0]

    def draw(self, draw_pos=None):
        if draw_pos is None:
            draw_pos = [self.x, self.y]
        self.player = pg.draw.circle(screen, 'black', draw_pos, self.radius, self.outline)

    def evolution(self, borders, gravity, pointer_pos, delta_t):
        if not self.selected:

            # Ground collision
            if self.y > screen_height - (ground_height * scale_ratio) - self.radius:
                self.y = screen_height - (ground_height * scale_ratio) - self.radius

            if self.y < screen_height - (ground_height * scale_ratio) - self.radius:
                self.y_speed += gravity * delta_t
            elif self.y_speed > (0.05 * gravity):
                self.y_speed = -1 * self.y_speed * self.cor
            elif abs(self.y_speed) < (0.05 * gravity):
                self.y_speed = 0
            
            # Border collision
            if borders:
                if self.x < self.radius:
                    self.x = self.radius
                elif self.x > screen_width - self.radius:
                    self.x = screen_width - self.radius
                if self.y < self.radius:
                    self.y = self.radius

                if (self.x <= self.radius and self.x_speed < 0) or (self.x >= screen_width - self.radius and self.x_speed > 0):
                    self.x_speed = -1 * self.x_speed * self.cor
                if self.y <= self.radius and self.y_speed < 0:
                    self.y_speed = -1 * self.y_speed * self.cor

            # Friction
            if self.y_speed == 0 and self.x_speed != 0:
                if self.x_speed > 0:
                    self.x_speed -= (self.mu * gravity) * delta_t
                elif self.x_speed < 0:
                    self.x_speed += (self.mu * gravity) * delta_t

            # Stop ball if it is moving slowly
            if abs(self.x_speed) < 0.005 * gravity:
                self.x_speed = 0

            # Update position (implicit euler)
            self.x += (self.x_speed * delta_t) * scale_ratio
            self.y += (self.y_speed * delta_t) * scale_ratio

        else:
            self.x = pointer_pos[0] + self.error[0]
            self.y = pointer_pos[1] + self.error[1]


class Environment():
    def __init__(self, borders):
        self.borders = borders
        self.ground_pos = [0, 0]
        self.fixed_x = None
        self.fixed_y = None
        self.offset_x = None
        self.offset_y = None
        self.released = True

    def draw_ground(self):
        left_box_pos = self.ground_pos[0] / scale_ratio
        right_box_pos = self.ground_pos[0] / scale_ratio
        box_list = [self.ground_pos[0] / scale_ratio]

        while right_box_pos < screen_width / scale_ratio:
            box_list.append(right_box_pos)
            right_box_pos += box_length + box_side_gap  # 16 / 15
        while left_box_pos > -1 * box_length:
            box_list.append(left_box_pos)
            left_box_pos -= box_length + box_side_gap  # 16 / 15

        box_y = screen_height + self.ground_pos[1] + ((box_top_gap - ground_height) * scale_ratio)
        pg.draw.line(screen, 'beige', (0, screen_height), (screen_width, screen_height), round(2 * (screen_height - box_y + (box_top_gap * scale_ratio))))

        for i in box_list:
            pg.draw.rect(screen, 'tan', (i * scale_ratio, box_y, box_length * scale_ratio, box_length * scale_ratio))

    def update_env(self, obj):
        border_width_px = border_width * scale_ratio
        if not self.borders and not obj.selected:

            # Update ground_pos[1]
            if self.released:
                obj.y -= self.ground_pos[1]
                self.released = False

            if obj.y_speed < 0:
                if obj.y >= border_width_px:
                    self.ground_pos[1] = 0  # To be robust
                    self.fixed_y = None
                elif obj.y > border_width_px - self.ground_pos[1]:
                    self.fixed_y = obj.y + self.ground_pos[1]
                else:
                    if self.fixed_y is None:
                        self.fixed_y = obj.y + self.ground_pos[1]
                    
                    self.offset_y = self.fixed_y - border_width_px

                    if self.offset_y < -5:
                        self.fixed_y -= self.offset_y / 10

                    self.ground_pos[1] = self.fixed_y - obj.y
                
            elif self.ground_pos[1] == 0:
                self.fixed_y = None

            elif obj.y > border_width_px - self.ground_pos[1]:
                if self.fixed_y is None:
                    self.fixed_y = obj.y + self.ground_pos[1]
                
                self.offset_y = self.fixed_y - border_width_px

                if self.offset_y > 5:
                    self.fixed_y -= self.offset_y / 10

                self.ground_pos[1] = self.fixed_y - obj.y

            else:
                if self.fixed_y is None:
                    self.fixed_y = obj.y + self.ground_pos[1]
                
                self.offset_y = self.fixed_y - border_width_px

                if self.offset_y < -5:
                    self.fixed_y -= self.offset_y / 10

                self.ground_pos[1] = self.fixed_y - obj.y

            if self.ground_pos[1] < 0:
                self.ground_pos[1] = 0

            # Update ground_pos[0]
            if (obj.x > screen_width - border_width_px and obj.x_speed >= 0) or (obj.x < border_width_px and obj.x_speed <= 0):
                if self.fixed_x is None:
                    self.fixed_x = obj.x

                if obj.x > screen_width - border_width_px:
                    self.offset_x = self.fixed_x - (screen_width - border_width_px)
                else:
                    self.offset_x = self.fixed_x - border_width_px

                if abs(self.offset_x) > 5:
                    self.fixed_x -= self.offset_x / 100
                    self.ground_pos[0] -= self.offset_x / 100

                self.ground_pos[0] -= (obj.x_speed * delta_t) * scale_ratio * 0.5  # slowed

            else:
                if self.fixed_x is not None:
                    obj.x = self.fixed_x
                self.fixed_x = None

        elif not self.borders:
            self.fixed_x = None
            self.fixed_y = None
            self.released = True
        else:
            self.fixed_x = None
            self.fixed_y = None
            # self.released = True

        self.draw_ground()

        object_x = self.fixed_x if self.fixed_x is not None else obj.x
        object_y = self.fixed_y if self.fixed_y is not None else obj.y

        return object_x, object_y


class Game():
    def __init__(self, env, obj_type, obj_params, gravity):
        self.env = env
        self.obj_type = obj_type
        self.obj_params = obj_params
        self.gravity = gravity
        self.load = True
        self.t = 0
        self.current_time = 0
        self.accumulator = 0
        self.current_state = None
        self.previous_state = None
        self.pointer_list = []

    def pointer(self, obj):
        pos = pg.mouse.get_pos()
        highlight = False

        if not pg.mouse.get_pressed()[0]:
            obj.selected = False

        if obj.player.collidepoint(pos) and not obj.selected:
            highlight = True
            if pg.mouse.get_pressed()[0]:
                # obj.error = [obj.x - pos[0], obj.y - pos[1]]
                highlight = False
                obj.selected = True

        if obj.selected and pg.mouse.get_pressed()[0]:
            self.pointer_list.append(pos)
            if len(self.pointer_list) > 20:
                self.pointer_list.pop(0)
                obj.x_speed, obj.y_speed = [0, 0]

                # Calculate pointer speed
                if len(self.pointer_list) > 10:
                    obj.x_speed = (self.pointer_list[-1][0] - self.pointer_list[0][0]) / ((len(self.pointer_list) * delta_t) * scale_ratio)
                    obj.y_speed = (self.pointer_list[-1][1] - self.pointer_list[0][1]) / ((len(self.pointer_list) * delta_t) * scale_ratio)

        if highlight:
            obj.outline = 5
        else:
            obj.outline = 0

    def load_object(self):
        radius_temp, ground_height_temp = [0, 0]
        frames = 3 * fps
        for i in range(frames + 1):
            screen.fill('white')
            kl_graphics.background(screen, screen_width, screen_height)
            if self.obj_type == 'ball':
                object = Ball(screen_width/2, screen_height/2, 0, 0, self.obj_params.mass, self.obj_params.cor, self.obj_params.mu, radius_temp)
                object.draw()
                radius_temp += self.obj_params.radius * (1 / frames)

            self.env.draw_ground()
            ground_height_temp += ground_height * (1 / frames)
            pg.display.update()
        return object

    def scale_pos(self, obj, screen_width, screen_height):
        new_screen_width, new_screen_height = screen.get_size()
        obj.x = obj.x * (new_screen_width / screen_width)
        obj.y = obj.y * (new_screen_height / screen_height)

        return new_screen_width, new_screen_height
        
    # def scale_bar(self):
    #     bar_dim = pg.Rect(screen_width - (0.1 * scale_ratio), screen_height / 2, 0.1 * scale_ratio, scale_ratio)
    #     bar = pg.draw.rect(screen, 'white', bar_dim, 5)

    def update_game(self, screen_width, screen_height):
        if self.load:
            self.env.ground_pos = [0, 0]
            self.pointer_list = []
            self.env.fixed_x = None
            self.env.fixed_y = None
            object = self.load_object()
            self.current_state = object
            self.previous_state = object
            self.load = False

            self.t = 0
            self.current_time = pg.time.get_ticks() / 1000
            self.accumulator = 0

        else:
            screen_width, screen_height = self.scale_pos(self.current_state, screen_width, screen_height)

            new_time = pg.time.get_ticks() / 1000
            frame_time = new_time - self.current_time
            if frame_time > 0.25:
                frame_time = 0.25
            self.current_time = new_time
            self.accumulator += frame_time

            screen.fill('white')
            kl_graphics.background(screen, screen_width, screen_height)
            
            if not self.env.borders:
                if self.current_state.selected:
                    object_height = screen_height - (ground_height * scale_ratio) - self.current_state.y + self.env.ground_pos[1]
                else:
                    object_height = screen_height - (ground_height * scale_ratio) - self.current_state.y

                height = int(object_height / scale_ratio)
                height_text = font.render(str(height), True, (255, 255, 255))
                screen.blit(height_text, (screen_width - (0.3 * scale_ratio) - 27, (0.3 * scale_ratio) - 27))

                if object_height > max_height * scale_ratio:
                    self.load = True

            while self.accumulator >= delta_t:
                self.previous_state = self.current_state
                pos = pg.mouse.get_pos()
                self.pointer(self.current_state)
                self.current_state.evolution(self.env.borders, self.gravity, pos, delta_t)
                self.t += delta_t
                self.accumulator -= delta_t

            draw_pos = self.env.update_env(self.current_state)
            self.current_state.draw(draw_pos)

        return screen_width, screen_height


@dataclass
class BallParams:
    mass: float
    cor: float
    mu: float
    radius: float


def main_menu_screen():
    screen_width, screen_height = screen.get_size()

def game_menu_screen():
    screen_width, screen_height = screen.get_size()


object = 'ball'
ball_params = BallParams(mass=10, cor=0.8, mu=0.5, radius=45)
current_screen = 'game'

environment = Environment(borders=True)

game = Game(env=environment, obj_type=object, obj_params=ball_params, gravity=9.8)

# Game loop
running = True
while running:

    if current_screen == 'main_menu':
        screen_width, screen_height = main_menu_screen()

    elif current_screen == 'game':
        screen_width, screen_height = game.update_game(screen_width, screen_height)

    elif current_screen == 'game_menu':
        screen_width, screen_height = game_menu_screen()

    for event in pg.event.get():
        # Switch screen size
        if event.type == pg.KEYDOWN and event.key == pg.K_f:
            fullscreen = not fullscreen
            if fullscreen:
                screen = pg.display.set_mode((0,0), pg.FULLSCREEN)
            else:
                screen = pg.display.set_mode(window_size)

        # End program
        if event.type == pg.QUIT:
            running = False
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            running = False

    pg.display.update()

pg.quit()
sys.exit()
