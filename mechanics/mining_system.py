import pygame
from pygame_helper.helper_graphics import import_images_folder, draw_image
from item.item import ItemInstance
from settings import GRAPHICS_PATH, BLOCK_SIZE, PLAYER_MINE_RANGE, MAX_HUNGER
from dict.data import blocks_data, block_ids, tool_types
from random import randint, choice

class MiningSystem:
    def __init__(self, get_block_rects,get_chunk_rects, get_world_data, edit_chunk_data, get_scroll, get_structures, edit_structures, get_player_pos, get_selected,add_drop, get_player_blocks,remove_player_block,get_player_hunger,c_s_i,delete_special):
        
        
        self.first_time_press = True
        self.start_pressing = 0
        self.is_structure = False
        self.is_block = False

        self.chunk = None
        self.block = None
        self.chunk_pos = None
        self.structure = None

        self.get_block_rects = get_block_rects
        self.get_chunk_rects = get_chunk_rects
        self.get_world_data = get_world_data
        self.edit_chunk_data = edit_chunk_data
        self.get_scroll = get_scroll
        self.get_structures = get_structures
        self.edit_structures = edit_structures
        self.get_player_pos = get_player_pos
        self.get_selected = get_selected
        self.add_drop = add_drop
        self.get_player_blocks = get_player_blocks
        self.remove_player_block = remove_player_block
        self.get_player_hunger = get_player_hunger
        self.c_s_i = c_s_i
        self.delete_special = delete_special

        self.destroy_images = import_images_folder(f"{GRAPHICS_PATH}blocks/destroy_animation",True,None,(BLOCK_SIZE,BLOCK_SIZE))
        self.destroy_image = self.destroy_images[0]
        self.frame_speed = 0
        self.frame_index = 0
        self.cooldown = 0
        self.frame_num = len(self.destroy_images)

        self.tool_start = False

    def animate(self):
        
        if pygame.time.get_ticks()-self.start_pressing >= self.frame_speed*self.frame_index:
            self.frame_index += 1
            try:
                self.destroy_image = self.destroy_images[self.frame_index-1]
            except: pass

        draw_image(self.destroy_image,(self.block["pos"][0]*BLOCK_SIZE-self.get_scroll().x,self.block["pos"][1]*BLOCK_SIZE-self.get_scroll().y))

    def get_selection(self):
        pos = pygame.mouse.get_pos()
        block = None
        chunk = None
        for b in self.get_block_rects():
            if b[0].collidepoint(pos[0],pos[1]):
                if abs(b[0].centerx-self.get_player_pos().centerx) <= PLAYER_MINE_RANGE and abs(b[0].centery-self.get_player_pos().centery) <= PLAYER_MINE_RANGE:
                    block = b
                    break
        if not block:
            return False
        else:
            for c in self.get_chunk_rects():
                if c[0].collidepoint(pos[0],pos[1]):
                    chunk = c
                    self.chunk = self.get_world_data()[chunk[1]]
                    self.chunk_pos = c[1]
                    break
            for bl in self.chunk:
                if bl["unique"] != -1:
                    if block[1] == bl["unique"]:
                        if blocks_data[bl["id"]]["tool_required"] != tool_types["thepowerofgod"]:
                            self.block = bl
                            if self.get_selected().empty == True:
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]*blocks_data[bl["id"]]["max_cooldown"]
                                self.frame_speed = self.cooldown // self.frame_num
                                self.tool_start = False
                                return True
                            if self.get_selected().item.id == blocks_data[bl["id"]]["tool_required"] and self.get_selected().item.type == "tools":
                                self.tool_start = self.get_selected().item
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]
                                if self.get_selected().item.level > 0:
                                    self.cooldown/= (((self.get_selected().item.level+1)/5)+1)
                            else:
                                self.tool_start = False
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]*blocks_data[bl["id"]]["max_cooldown"]
                                if self.get_selected().item.type == "tools":
                                    if self.get_selected().item.level > 0:
                                        self.cooldown/= (((self.get_selected().item.level+1)/5)+1)
                            hunger__multiplier = (MAX_HUNGER-self.get_player_hunger())/20 +1
                            self.cooldown *= hunger__multiplier
                            self.frame_speed = self.cooldown // self.frame_num
                            return True
        return False

    def remove_blocks(self):
        self.chunk.remove(self.block)
        if self.block["id"] in [block_ids["grassblock"],block_ids["sand"],block_ids["redsand"],block_ids["stonegrass"],block_ids["stonedirt"]]:
            for c in self.get_chunk_rects():
                chunk = self.get_world_data()[c[1]]
                for bl in chunk:
                    if bl["id"] in [block_ids["grass"],block_ids["desertgrass"],block_ids["littlestone"]] and bl["pos"][1] == self.block["pos"][1]-1 and bl["pos"][0]==self.block["pos"][0]:
                        chunk.remove(bl)
                        chunk.append({"pos":bl["pos"],"id":-1,"unique":-1})
                        self.edit_chunk_data(chunk,c[1])
        self.chunk.append({"pos":self.block["pos"],"id":-1,"unique":-1})
        self.edit_chunk_data(self.chunk,self.chunk_pos)
        self.reset()

    def get_player_block_selection(self):
        pos = pygame.mouse.get_pos()
        block = None
        for b in self.get_block_rects():
            if b[0].collidepoint(pos[0],pos[1]):
                if abs(b[0].centerx-self.get_player_pos().centerx) <= PLAYER_MINE_RANGE and abs(b[0].centery-self.get_player_pos().centery) <= PLAYER_MINE_RANGE:
                    block = b
                    break
        if not block:
            return False
        else:
            
            for bl in self.get_player_blocks():
                if bl["unique"] != -1:
                    if block[1] == bl["unique"]:
                        if blocks_data[bl["id"]]["tool_required"] != tool_types["thepowerofgod"]:
                            self.block = bl
                            if self.get_selected().empty == True:
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]*blocks_data[bl["id"]]["max_cooldown"]
                                self.frame_speed = self.cooldown // self.frame_num
                                self.tool_start = False
                                return True
                            if self.get_selected().item.id == blocks_data[bl["id"]]["tool_required"] and self.get_selected().item.type == "tools":
                                self.tool_start = self.get_selected().item
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]
                                if self.get_selected().item.level > 0:
                                    self.cooldown/= (((self.get_selected().item.level+1)/5)+1)
                            else:
                                self.tool_start = False
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]*blocks_data[bl["id"]]["max_cooldown"]
                                if self.get_selected().item.type == "tools":
                                    if self.get_selected().item.level > 0:
                                        self.cooldown/= (((self.get_selected().item.level+1)/5)+1)
                            hunger__multiplier = (MAX_HUNGER-self.get_player_hunger())/20 +1
                            self.cooldown *= hunger__multiplier
                            self.frame_speed = self.cooldown // self.frame_num
                            return True
        return False

    def remove_p_block(self):
        self.remove_player_block(self.block)
        self.reset()

    def remove_b_structure(self):
        self.structure[0].remove(self.block)
        self.edit_structures(self.structure[1],self.structure[0])
        self.reset()

    def reset(self):
        self.block = None
        self.first_time_press = True
        self.chunk = None
        self.chunk_pos = None
        self.frame_index = 0
        self.is_structure = False
        self.structure = None
        self.cooldown = 0
        self.is_block = False
        self.tool_start = False

    def input(self,mouse):

        if mouse[0] and not mouse[2]:

            if self.first_time_press:
                if self.get_selection():
                    self.is_structure = False
                    self.is_block = False
                    self.start_pressing = pygame.time.get_ticks()
                    self.first_time_press = False
                else:
                    if self.get_structure_selection():
                        self.is_structure = True
                        self.is_block = False
                        self.start_pressing = pygame.time.get_ticks()
                        self.first_time_press = False
                    else:
                        if self.get_player_block_selection():
                            self.is_block = True
                            self.start_pressing = pygame.time.get_ticks()
                            self.first_time_press = False
                        else:
                            self.first_time_press = True

            #if self.first_time_press != False:
                #self.first_time_press = False

            if self.block:
                if abs(self.block["pos"][0]*BLOCK_SIZE-self.get_scroll().x-self.get_player_pos().centerx) > PLAYER_MINE_RANGE or abs(self.block["pos"][1]*BLOCK_SIZE-self.get_scroll().y-self.get_player_pos().centery) > PLAYER_MINE_RANGE:
                    self.reset()
                else:
                    self.animate()
                    if pygame.time.get_ticks()-self.start_pressing >= self.cooldown:

                        if self.block["id"] == block_ids["furnace"]:
                            self.delete_special("furnace",self.block)
                        
                        if blocks_data[self.block["id"]]["ignore_tool"] == True:
                            self.add_drop((self.block["pos"][0]*BLOCK_SIZE-self.get_scroll().x+BLOCK_SIZE/2+randint(0,BLOCK_SIZE//4)*choice([1,-1]),self.block["pos"][1]*BLOCK_SIZE-self.get_scroll().y+BLOCK_SIZE/2),ItemInstance(blocks_data[self.block["id"]]["drop"]["id"],blocks_data[self.block["id"]]["drop"]["type"],True))
                        else:
                            if self.tool_start != False:
                                if blocks_data[self.block["id"]]["tool_required"] == self.tool_start.id:
                                    if self.tool_start.level >= blocks_data[self.block["id"]]["level_required"]:
                                        self.add_drop((self.block["pos"][0]*BLOCK_SIZE-self.get_scroll().x+BLOCK_SIZE/2+randint(0,BLOCK_SIZE//4)*choice([1,-1]),self.block["pos"][1]*BLOCK_SIZE-self.get_scroll().y+BLOCK_SIZE/2),ItemInstance(blocks_data[self.block["id"]]["drop"]["id"],blocks_data[self.block["id"]]["drop"]["type"],True))

                        if not self.is_structure and not self.is_block:
                            self.remove_blocks()
                        else:
                            if self.is_structure:
                                self.remove_b_structure()
                            else:
                                self.remove_p_block()
                        if self.get_selected().empty == False:
                            if self.get_selected().item.type == "tools":
                                self.get_selected().item.durability -= 1
                                if self.get_selected().item.durability <= 0:
                                    self.get_selected().empty = True
                                    self.get_selected().item = None
                                    self.c_s_i(None)
                                else:
                                    self.get_selected().refresh_durability()
                        self.first_time_press = True

        if ((not (mouse[0])) and (not self.first_time_press)) or mouse[2]:
            self.reset()

    def get_structure_selection(self):
        pos = pygame.mouse.get_pos()
        block = None

        for b in self.get_block_rects():
            if b[0].collidepoint(pos[0],pos[1]):
                if abs(b[0].centerx-self.get_player_pos().centerx) <= PLAYER_MINE_RANGE and abs(b[0].centery-self.get_player_pos().centery) <= PLAYER_MINE_RANGE:
                    block = b
                    break
        if not block:
            return False
        else:
            for index,s in enumerate(self.get_structures()):
                for bl in s:
                    if block[1] == bl["unique"]:
                        if blocks_data[bl["id"]]["tool_required"] != tool_types["thepowerofgod"]:
                            self.block = bl
                            self.structure = [s,index]
                            if self.get_selected().empty == True:
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]*blocks_data[bl["id"]]["max_cooldown"]
                                self.frame_speed = self.cooldown // self.frame_num
                                self.tool_start = False
                                return True
                            if self.get_selected().item.id == blocks_data[bl["id"]]["tool_required"] and self.get_selected().item.type == "tools":
                                self.tool_start = self.get_selected().item
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]
                                if self.get_selected().item.level > 0:
                                    self.cooldown/= (((self.get_selected().item.level+1)/5)+1)
                            else:
                                self.tool_start = False
                                self.cooldown = blocks_data[bl["id"]]["mine_cooldown"]*blocks_data[bl["id"]]["max_cooldown"]
                                if self.get_selected().item.type == "tools":
                                    if self.get_selected().item.level > 0:
                                        self.cooldown/= (((self.get_selected().item.level+1)/5)+1)
                            hunger__multiplier = (MAX_HUNGER-self.get_player_hunger())/20 +1
                            self.cooldown *= hunger__multiplier
                            self.frame_speed = self.cooldown // self.frame_num
                            return True
        return False

    def update(self,mouse):
        self.input(mouse)