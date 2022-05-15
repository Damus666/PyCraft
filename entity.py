import pygame
from pygame_helper.helper_graphics import draw_image, load_image, scale_image
from item import ItemInstance
from settings import GRAPHICS_PATH, GRAVITY_CONSTANT, BLOCK_SIZE, SAFE_BLOCKS_NUM, ENTITY_DIR_COOLDOWN
from data import entities_data, items_ids
from random import choice, randint
from pygame.transform import flip
from pygame_helper.pygame_helper import debug


class Entity:
    def __init__(self, start_pos, type, add_drop,delete_entity,h=None,p_f=0):

        scale = 0.8
        self.type = type
        self.ori_body_image = scale_image(load_image(
            f"{GRAPHICS_PATH}entities/{type}/body.png", True), scale)
        self.body_img = self.ori_body_image
        self.rect = self.body_img.get_rect(center=start_pos)

        self.inf_height = 0

        self.x_speed = entities_data[self.type]["speed"]
        self.gravity = 0

        self.is_standing = False
        self.is_moving = False
        self.first_time_land = False
        self.pixel_fell = p_f
        self.direction = -1

        self.max_health = entities_data[self.type]["health"]
        if h: self.health = h
        else: self.health = self.max_health

        self.last_change = 0

        self.width = self.body_img.get_width()

        self.add_drop = add_drop
        self.delete_entity = delete_entity

        self.drops = [{"id":items_ids["meat"],"type":"items","chances":100,"quantity":1,"more":[50,1]}]

    def damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.die()

    def die(self):
        if self.drops:
            for d in self.drops:
                if d["chances"] != 0:
                    pos = (self.rect.centerx+randint(-self.ori_body_image.get_width()//2,self.ori_body_image.get_width()//2),self.rect.centery)
                    if randint(0,100) <= d["chances"]:
                        self.add_drop(pos,ItemInstance(d["id"],d["type"],True),d["quantity"])
                        if d["more"][0] != 0:
                            if randint(0,100) <= d["more"][0]:
                                self.add_drop(pos,ItemInstance(d["id"],d["type"],True),d["more"][1])

        self.delete_entity(self)

    def flip_image(self):
        if self.direction == -1:
            self.body_img = self.ori_body_image
        else:
            self.body_img = flip(self.ori_body_image, True, False)

    def fall(self):
        if not self.is_standing:
            self.gravity += GRAVITY_CONSTANT
            self.rect.y += self.gravity

    def obstacles_collisions(self, obstacles):
        not_collided = 0
        near_blocks = 0

        if self.gravity != 0:
            if self.is_standing != False:
                self.is_standing = False
        if obstacles:
            for obstacle in obstacles:
                obs = obstacle[0]
                r = self.rect.inflate(0, self.inf_height*2)
                inf_y = r.inflate(-self.width+10, 2)
                if abs(obs.x-self.rect.x) <= BLOCK_SIZE*3 and abs(obs.y-self.rect.y) <= BLOCK_SIZE*3:
                    near_blocks += 1
                    if r.colliderect(obs):
                        if self.gravity >= 0:
                            if r.bottom > obs.top:
                                if (r.bottom < obs.centery) or (self.rect.left > obs.left and self.rect.right < obs.right):
                                    if self.rect.left < obs.right - 5 or self.rect.right > obs.left + 5:
                                        self.rect.bottom = obs.top-self.inf_height
                                        self.is_standing = True
                                        self.gravity = 0
                                        if self.first_time_land:
                                            self.first_time_land = False
                                            blocks_fell = (
                                                (self.pixel_fell)/BLOCK_SIZE)-SAFE_BLOCKS_NUM
                                            if int(blocks_fell) > 0:
                                                self.damage(int(blocks_fell))
                                            self.pixel_fell = 0
                        if self.direction == 1:
                            if 0 < (obs.left+15)-(self.rect.right-15) < BLOCK_SIZE//2:
                                if self.rect.right > obs.left:
                                    self.rect.right = obs.left
                                    self.direction = choice([0, -1])
                                    self.flip_image()
                        elif self.direction == -1:
                            if 0 < (self.rect.left+15)-(obs.right-15) < BLOCK_SIZE//2:
                                if self.rect.left < obs.right:
                                    self.rect.left = obs.right
                                    self.direction = choice([0, 1])
                                    self.flip_image()
                    else:
                        if not inf_y.colliderect(obs):
                            not_collided += 1

        if not_collided == near_blocks:
            self.is_standing = False
            self.first_time_land = True

    def change_dir(self):
        if pygame.time.get_ticks()-self.last_change >= ENTITY_DIR_COOLDOWN:
            self.last_change = pygame.time.get_ticks()
            dir = choice([-1, 0, 1])
            flip = False
            if dir != 0:
                if dir != self.direction:
                    flip = True
            self.direction = dir
            if flip:
                self.flip_image()

    def move(self):
        self.rect.x += self.x_speed*self.direction

    def draw_body(self):
        draw_image(self.body_img, self.rect)

    def update(self, obstacles):
        self.obstacles_collisions(obstacles)
        self.fall()
        self.change_dir()
        self.move()

    def draw(self):
        """override"""