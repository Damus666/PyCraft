import pygame, json
from utility.pixel_calculator import medium_calculator,height_calculator
from settings import BG_COLOR,ITEM_SIZE,SLOT_OFFSET,WIDTH,HEIGHT, STACK_SIZE,BLOCK_SIZE
from pygame_helper.helper_graphics import draw_image,get_window_surface
from inventory.inventory_slot import InventorySlot
from item.item import ItemInstance
from random import randint,choice

class StorageManager:
    def __init__(self,left,top,place_in_inv,get_chest_open):

        self.slots = {}
        self.slot_rects = {}

        self.top = top
        self.left = left

        self.outline_size = medium_calculator(3,True)

        self.rows = 4
        self.columns = 9
        
        self.b_radius = medium_calculator(5,True)

        self.slot_image = pygame.Surface((ITEM_SIZE+SLOT_OFFSET,ITEM_SIZE+SLOT_OFFSET))
        self.slot_image.fill(BG_COLOR)
        self.slot_image.set_alpha(100)

        self.inv_offset = 30
        self.inv_sizes = ((self.columns)*(ITEM_SIZE+SLOT_OFFSET)+(SLOT_OFFSET*self.columns)+self.inv_offset-SLOT_OFFSET,(self.rows)*(ITEM_SIZE+SLOT_OFFSET)+(SLOT_OFFSET*self.rows)+self.inv_offset-SLOT_OFFSET)
        self.height_offset = height_calculator(100)
        self.offset = [self.left,self.top+self.height_offset]
        self.inv_rect = pygame.Rect(self.offset[0],self.offset[1],self.inv_sizes[0]+4,self.inv_sizes[1]+4)

        self.font = pygame.font.Font("assets/fonts/regular.ttf",medium_calculator(40,True))
        self.chest_text = self.font.render("Chest",True,"white")
        self.chest_rect = self.chest_text.get_rect(center=(WIDTH/2,self.top+self.height_offset/2))

        self.can_click = True
        self.first_time_pressed = True
        self.selected_slot = []
        self.was_clicking = False

        self.storages = {}
        self.selected_id = 0

        self.place_in_inv = place_in_inv
        self.get_chest_open = get_chest_open

        self.init_slots()
        self.load_rects()

    def try_place_item_in_here_please(self,selected_slot,pos):
        if self.get_chest_open():
            if self.inv_rect.collidepoint(pos[0],pos[1]):
                self.selected_slot = [selected_slot[0].__copy__(),selected_slot[1]]
                if self.place_selected_slot(pos,False):
                    return True
                else:
                    return 3

        return False

    def load_storages(self,dictt):
        for id in dictt.keys():
            real_id = int(id)
            self.open_storage(real_id,dictt[id])

    def create_storage(self):
        storage = {}
        for y in range(self.rows):
            for x in range(self.columns):
                storage[str(x)+";"+str(y)] = {"empty":True,"item":None,"quantity":1}
        return storage

    def open_storage(self,id,dictt=False):
        if not id in self.storages.keys():
            if dictt == False:
                new_s = self.create_storage()
                self.storages[id] = new_s
            else:
                copy = dictt.copy()

                self.storages[id] = copy
        
        self.selected_id = id
        self.read_storage_data()

    def paste_slots_to_storage(self):
        for pos in self.slots.keys():
            slot = self.slots[pos]
            empty = slot.empty
            item = slot.item
            quantity = slot.quantity
            if empty:
                final_item = None
            else:
                final_item = {"id":item.id,"type":item.type,"level":item.level,"durability":item.durability,"is_stackable":item.is_stackable}
            self.storages[self.selected_id][pos] = {"empty":empty,"item":final_item,"quantity":quantity}

    def read_storage_data(self):
        for pos in self.slots.keys():
            self.slots[pos].empty = self.storages[self.selected_id][pos]["empty"]
            self.slots[pos].quantity = self.storages[self.selected_id][pos]["quantity"]
            if self.storages[self.selected_id][pos]["item"] == None:
                self.slots[pos].item = None
            else:
                self.slots[pos].item = ItemInstance(self.storages[self.selected_id][pos]["item"]["id"],self.storages[self.selected_id][pos]["item"]["type"],self.storages[self.selected_id][pos]["item"]["is_stackable"],self.storages[self.selected_id][pos]["item"]["level"],self.storages[self.selected_id][pos]["item"]["durability"])
            self.slots[pos].refresh_quantity_img()

    def get_chests_dict(self):
        return self.storages

    def load_rects(self):
        for y in range(self.rows):
            for x in range(self.columns):
                x_t= (ITEM_SIZE+SLOT_OFFSET)*x+self.offset[0]
                y_t= (ITEM_SIZE+SLOT_OFFSET)*y+self.offset[1]
                rect = pygame.Rect(x_t+SLOT_OFFSET*x,y_t+SLOT_OFFSET*y,ITEM_SIZE+SLOT_OFFSET+4,ITEM_SIZE+SLOT_OFFSET+4)
                pos = str(x)+";"+str(y)
                self.slot_rects[pos] = rect

    def init_slots(self):
        for y in range(self.rows):
            for x in range(self.columns):
                self.slots[str(x)+";"+str(y)] = InventorySlot()

    def add_item(self,pos,item,quantity=1):
        if not self.slots[pos].empty:
            if item.is_stackable == True:
                if self.slots[pos].item.type == item.type:
                    if self.slots[pos].item.id == item.id:
                        if self.slots[pos].quantity < STACK_SIZE:
                            self.slots[pos].quantity += quantity
                            if self.slots[pos].quantity > STACK_SIZE:
                                self.add_item(self.get_free_pos_by_id(item.id,item.type),item,self.slots[pos].quantity-STACK_SIZE)
                                self.slots[pos].quantity = STACK_SIZE
                            self.slots[pos].refresh_quantity_img()
                            return True
        elif self.slots[pos].empty == True:
            self.slots[pos].item = item
            self.slots[pos].empty = False
            self.slots[pos].quantity = quantity
            self.slots[pos].refresh_quantity_img()
            return True
        else:
            return False

    def get_empty_slot_pos(self):
        for y in range(self.rows):
            for x in range(self.columns):
                if self.slots[str(x)+";"+str(y)].empty == True:
                    return str(x)+";"+str(y)
        return False

    def remove_item(self,type,id,quantity):
        quantity_removed = 0
        for slot in self.slots.values():
            if quantity_removed == quantity:
                break
            if slot.empty == False:
                if slot.item.type == type and slot.item.id == id:
                    if slot.quantity == 1:
                        slot.item = None
                        slot.empty = True
                        quantity_removed+= 1
                    else:
                        previous = slot.quantity
                        slot.quantity -= (quantity-quantity_removed)
                        if slot.quantity <= 0:
                            slot.item = None
                            slot.empty = True
                            slot.quantity = 1
                            quantity_removed+= previous
                        else:
                            quantity_removed += (quantity-quantity_removed)
                    slot.refresh_quantity_img()

    def get_free_pos_by_id(self,id,type):
        free_pos = []
        for y in range(self.rows):
            for x in range(self.columns):
                if self.slots[str(x)+";"+str(y)].empty== False:
                    if self.slots[str(x)+";"+str(y)].item.type == type:
                        if self.slots[str(x)+";"+str(y)].item.id== id:
                            if self.slots[str(x)+";"+str(y)].item.is_stackable== True:
                                if self.slots[str(x)+";"+str(y)].quantity < STACK_SIZE:
                                    return str(x)+";"+str(y)
                elif self.slots[str(x)+";"+str(y)].empty == True:
                    free_pos.append(str(x)+";"+str(y))
        if free_pos:
            return free_pos[0]
        return False

    def get_slots(self):
        return self.slots

    def render_slots(self):
        draw_image(self.chest_text,self.chest_rect)
        #pygame.draw.rect(get_window_surface(),"black",self.inv_rect,4,10)
        #pygame.draw.rect(get_window_surface(),INV_BG_COLOR,pygame.Rect(self.offset[0]-self.inv_offset/2+2,self.offset[1]-self.inv_offset/2+2,self.inv_sizes[0],self.inv_sizes[1]),0,10)

        for y in range(self.rows):
            for x in range(self.columns):
                x_t= (ITEM_SIZE+SLOT_OFFSET)*x+self.offset[0]
                y_t= (ITEM_SIZE+SLOT_OFFSET)*y+self.offset[1]
                #pygame.draw.rect(get_window_surface(),"black",self.slot_rects[str(x)+";"+str(y)],2,5)
                draw_image(self.slot_image,(x_t+SLOT_OFFSET*x+2,y_t+SLOT_OFFSET*y+2))
                pygame.draw.rect(get_window_surface(),(200,200,200),self.slot_rects[str(x)+";"+str(y)],self.outline_size,self.b_radius)
                self.slots[str(x)+";"+str(y)].draw_item(x_t+SLOT_OFFSET*x,y_t+SLOT_OFFSET*y,SLOT_OFFSET)

    def get_collided_slot(self,posi):
        pos = None
        for rect_pos in self.slot_rects.keys():
            r = self.slot_rects[rect_pos]
            if r.collidepoint(posi[0],posi[1]):
                pos = rect_pos
        return pos

    def get_selected_slot(self,posi):
        pos = self.get_collided_slot(posi)

        if pos != None:
            slot = self.slots[pos]
            if slot.empty == False:
                self.selected_slot = [slot.__copy__(),pos]
                return True
            else:
                return False
        else:
            return False

    def place_selected_slot(self,posi,can_swap=True):
        pos = self.get_collided_slot(posi)
        do_search = False
        do_swap = False
        could_place = False

        if pos != None:
            if self.slots[pos].empty == True:
                self.slots[pos].empty = False
                self.slots[pos].item = self.selected_slot[0].item
                self.slots[pos].quantity = self.selected_slot[0].quantity
                self.slots[pos].refresh_quantity_img()
                could_place = True
            elif self.slots[pos].item.is_stackable:
                if self.slots[pos].item.type == self.selected_slot[0].item.type:
                    if self.slots[pos].item.id == self.selected_slot[0].item.id:
                        if self.slots[pos].quantity < STACK_SIZE:
                            self.add_item(pos,self.selected_slot[0].item,self.selected_slot[0].quantity)
                            could_place = True
                        else: do_swap=True
                    else: do_swap = True
                else:
                    do_swap = True
            else:
                do_swap = True
        else:
            do_search = True
        
        if do_swap:
            if can_swap:
                poss = self.selected_slot[1]
                if self.slots[poss].empty == True:
                    self.slots[poss].empty = False
                    self.slots[poss].item = self.slots[pos].item
                    self.slots[poss].quantity = self.slots[pos].quantity
                    self.slots[pos].empty = False
                    self.slots[pos].item = self.selected_slot[0].item
                    self.slots[pos].quantity = self.selected_slot[0].quantity
                    self.slots[pos].refresh_quantity_img()
                    self.slots[poss].refresh_quantity_img()
                else:
                    do_search = True
            
        if do_search and can_swap:
            poss = self.selected_slot[1]
            if self.slots[poss].empty == True:
                self.slots[poss].empty = False
                self.slots[poss].item = self.selected_slot[0].item
                self.slots[poss].quantity = self.selected_slot[0].quantity
            else:
                pos = (self.get_p_data()[0][0] + BLOCK_SIZE*self.get_p_data()[1],self.get_p_data()[0][1])
                self.add_drop(pos,self.selected_slot[0].item,self.selected_slot[0].quantity)

        return could_place
        
    def input(self,mouse):
        pos = pygame.mouse.get_pos()

        if ((mouse[0]) and (not mouse[2])) or self.was_clicking:
            if (self.can_click):
                if self.inv_rect.collidepoint(pos[0],pos[1]) or self.first_time_pressed == False:
                    if self.first_time_pressed:
                        if self.get_selected_slot(pos) == True:
                            self.first_time_pressed = False
                            self.slots[self.selected_slot[1]].empty = True
                            self.slots[self.selected_slot[1]].quantity = 0
                            self.slots[self.selected_slot[1]].item = None
                            self.selected_slot[0].refresh_quantity_img()
                        else:
                            self.can_click = False
                            self.first_time_pressed = True
                            self.selected_slot = []
                    else:
                        draw_image(self.selected_slot[0].item.image,(pos[0]-ITEM_SIZE//2,pos[1]-ITEM_SIZE//2))
                        if self.selected_slot[0].item.is_stackable:
                            pygame.draw.rect(get_window_surface(),"white",pygame.Rect(pos[0]-ITEM_SIZE//2-2,pos[1]-ITEM_SIZE//2-2,self.selected_slot[0].quantity_img.get_width()+4,self.selected_slot[0].quantity_img.get_height()),0,3)
                            draw_image(self.selected_slot[0].quantity_img,(pos[0]-ITEM_SIZE//2,pos[1]-ITEM_SIZE//2-2))
                else:
                    self.can_click = False
            if self.was_clicking == False:
                self.was_clicking = True

        if (not mouse[0]):
            if self.first_time_pressed == False:
                if self.inv_rect.collidepoint(pos[0],pos[1]):
                    self.place_selected_slot(pos)
                else:
                    if not self.place_in_inv(self.selected_slot,pos):
                        self.place_selected_slot(pos)
                self.first_time_pressed = True
                self.selected_slot = []
            self.can_click = True
            self.was_clicking = False
    """
    def drop_all(self):
        for y in range(self.rows):
            for x in range(self.columns):
                slot = self.slots[str(x)+";"+str(y)]
                if not slot.empty:
                    pos = (self.get_p_data()[0][0] +randint(-BLOCK_SIZE//2,BLOCK_SIZE//2)*choice([-1,1]),self.get_p_data()[0][1])
                    self.add_drop(pos,slot.item,slot.quantity)"""

    def clear(self):
        for y in range(self.rows):
            for x in range(self.columns):
                slot = self.slots[str(x)+";"+str(y)]
                if not slot.empty:
                    slot.empty = True
                    slot.item = None
                    slot.quantity = 1
                    slot.selected = False

    def update(self,mouse):
        self.input(mouse)