import pygame
from typing import Optional

from globals import screen, GameInfo
import functions

from views.towers import ArcherTower, BombTower, TeslaTower
from models.item_models import ItemModel, ArcherTowerModel, BombTowerModel, TeslaTowerModel
from views.buildings import House
from views.player_abilities import Bomb

from fonts import font
import colors

class Item:
    def __init__(self, game_info: GameInfo, x: int, y: int, text: str, title: str, cost: Optional[int]=None, base_cooldown: Optional[int]=None, repair_amount: Optional[int]=None):
        self.x: int = x
        self.y: int = y
        self.w: int = 100
        self.h: int = 50
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.curr_color = (200, 100, 200)
        self.hover_color = (100, 100, 100)
        self.default_color = (200, 100, 200)
        self.text_color = (255, 255, 255)
        self.text: str = text
        self.title: str = title
        self.cost: Optional[int] = cost
        self.base_cooldown: Optional[int] = base_cooldown
        self.cooldown: int = 0
        self.repair_amount: Optional[int] = repair_amount

        #Item Image
        self.cap = game_info.caps[title+"Cap"]
        self.base_image: pygame.Surface = functions.load_image(self.title, 40)

    def draw(self, game_info: GameInfo, amount_owned: int) -> None:
        self.rect.center = (self.x, self.y)
        self.cap = game_info.caps[self.title+"Cap"]
        pygame.draw.rect(screen, self.curr_color, self.rect)

        #if costs money display price, if is cooldown based show cooldown
        if self.cost is not None:
            functions.display_text(self.text, self.text_color, font, self.x, int(self.y-self.h*.25))
            functions.display_text("Costs: " + str(self.cost), self.text_color, font, self.x, int(self.y+self.h*.25))
        elif self.cooldown is not None:
            functions.display_text(self.text, self.text_color, font, self.x, int(self.y-self.h*.25))
            if self.cooldown != 0:
                functions.display_text("Cooldown is: " + str(int(self.cooldown/60)) + " seconds.", self.text_color, font, self.x, int(self.y+self.h*.25))
            else:
                functions.display_text("Cooldown is: Ready!", self.text_color, font, self.x, int(self.y+self.h*.25))
        functions.display_text("Owned: " + str(amount_owned) + "/"+str(self.cap), (255, 255, 255), font, self.x+90, self.y)

class Shop:
    def __init__(self, game_info: GameInfo):
        self.placing_item: bool = False
        self.item_being_placed: Optional[Item] = None
        self.min_distance_between_items: int = 35
        self.placed_too_close: bool = False
        self.placed_too_close_warning_base_duration: int = 120
        self.placed_too_close_warning_duration: int = self.placed_too_close_warning_base_duration

        inc: int = 60
        self.base_x: int = 75
        self.base_y: int = 50
        self.items: list[Item] = [
            Item(game_info, self.base_x, self.base_y+inc, "Archer Tower", "ArcherTower", cost=2),
            Item(game_info, self.base_x, self.base_y+inc*2, "Tesla Tower", "TeslaTower", cost=4),
            Item(game_info, self.base_x, self.base_y+inc*3, "Bomb Tower", "BombTower", cost=6),
            Item(game_info, self.base_x, self.base_y+inc*4, "House", "House", cost=2,),
            Item(game_info, self.base_x, self.base_y+inc*5, "Bomb", "Bomb", base_cooldown=2000),
            Item(game_info, self.base_x, self.base_y+inc*6, "Repair", "Repair", base_cooldown=3000, repair_amount=150)
        ]

        self.items_owned: dict[str, int] = dict()
    
    def update_placed_too_close_warning(self) -> None:
        if self.placed_too_close:
            if self.placed_too_close_warning_duration <= 0:
                self.placed_too_close = False
                self.placed_too_close_warning_duration = self.placed_too_close_warning_base_duration
            else:
                functions.display_text("Placed too close to another tower", (255, 255, 255), font, int(screen.get_width()/2), 50)
                self.placed_too_close_warning_duration -= 1

    def draw_items(self, game_info: GameInfo) -> None:
        functions.display_rect(self.base_x, self.base_y, 125, 50, colors.PINK)
        functions.display_text("Item Shop", colors.WHITE, font, self.base_x, self.base_y)
        for item in self.items:
            amount_owned = self.items_owned[item.title]
            item.draw(game_info, amount_owned)
    
    def draw_item_being_placed(self, game_info) -> None:
        if self.item_being_placed is None:
            return
        else:
            #blit the image of the item being placed at ur mouse position
            mouse_pos = pygame.mouse.get_pos()
            if self.too_close(game_info, mouse_pos):
                functions.display_rect(int(screen.get_width()/2), 50, 100, 50, (255, 0, 0))
                functions.display_text("Too Close!", (0, 0, 0), font, int(screen.get_width()/2), 50)
            else:
                functions.display_rect(int(screen.get_width()/2), 50, 100, 50, (0, 255, 0))
                functions.display_text("Ok!", (0, 0, 0), font, int(screen.get_width()/2), 50)
            functions.display_image_new_rect(self.item_being_placed.base_image, mouse_pos[0], mouse_pos[1])
    
    def update_items_owned(self, game_info: GameInfo) -> None:
        all_items_owned: list[ItemModel] = game_info.all_purchasables

        #create dict for all items possible to place and set vals to 0
        self.items_owned = dict() 
        for item in self.items:
            self.items_owned[item.title] = 0

        #increment item value by one for each instance existing
        for owned in all_items_owned:
            if not owned.title == "TownHall":
                self.items_owned[owned.title] += 1
    
    def too_close(self, game_info: GameInfo, item_cord: tuple[int, int]) -> bool:
        all_items = game_info.all_purchasables
        for item in all_items:
            distance = functions.find_distance(item.pos, item_cord)
            if not distance > self.min_distance_between_items:
                return True
        return False
    
    def append_if_possible(self, list_to_append_to: list[ItemModel], game_info: GameInfo, to_place: ItemModel, cost: int) -> None:
        if self.too_close(game_info, to_place.pos):
            self.placed_too_close = True
            return
        game_info.gold -= cost
        list_to_append_to.append(to_place)


    def check_place_item(self, event_list: list[pygame.event.Event], game_info: GameInfo) -> None:
        if self.item_being_placed is None:
            return
        elif functions.pressed_left_click(event_list):
            print('click')
            mouse_pos = pygame.mouse.get_pos()
            item_being_placed = self.item_being_placed
            item_title = item_being_placed.title
            item_cost = item_being_placed.cost
            building_list = game_info.building_list
            tower_list = game_info.tower_list
    
            #if left click, place item at mouse position and append an item instance to corresponding list. have to check if item_cost is int to make mypy happy.
            if item_cost is not None:
                match item_title:
                    case "House":
                        self.append_if_possible(building_list, game_info, House(item_title, mouse_pos), item_cost)
                    case "ArcherTower":
                        self.append_if_possible(tower_list, game_info, ArcherTower(ArcherTowerModel(), mouse_pos), item_cost)
                    case "BombTower":
                        self.append_if_possible(tower_list, game_info, BombTower(BombTowerModel(), mouse_pos), item_cost)
                    case "TeslaTower":
                        self.append_if_possible(tower_list, game_info, TeslaTower(TeslaTowerModel(), mouse_pos), item_cost)
            else:
                match item_title:
                    case "Bomb":
                        game_info.unattackable_list.append(Bomb(item_title, mouse_pos))
                    case "Repair":
                        if self.item_being_placed.repair_amount is None:
                            return
                        elif not functions.repair_tower_clicked(self.item_being_placed.repair_amount, game_info, event_list):
                            self.placing_item = False
                            self.item_being_placed = None
                            return
            
            if self.item_being_placed.base_cooldown is not None:
                self.item_being_placed.cooldown = self.item_being_placed.base_cooldown
            #update gold/cooldown depending on if a tower/ability.

            self.placing_item = False
            self.item_being_placed = None
            game_info.update()
        
        #cancel placing tower by rightclick
        elif functions.pressed_right_click(event_list):
            self.placing_item = False
            self.item_being_placed = None
    
    def can_get_item(self, item: Item, game_info: GameInfo) -> bool:
        #if below item cap, and have enough gold / item is not on cooldown, return True, else False
        if self.items_owned[item.title] < game_info.caps[item.title+'Cap']:
            if item.cost is not None:
                if game_info.gold >= item.cost:
                    return True
            elif item.cooldown is not None:
                if item.cooldown <= 0:
                    return True
        return False

    def update_menu(self, event_list: list[pygame.event.Event], game_info: GameInfo) -> None:
        mouse_pos = pygame.mouse.get_pos()

        #make sure items owned is up to date
        self.update_items_owned(game_info)

        #draw items
        self.draw_items(game_info)

        #display warning if item placement canceled due to being too close to another tower
        self.update_placed_too_close_warning()

        #If item was clicked previously, begin drawing that image at ur mouse pos. 
        if self.placing_item:
            self.draw_item_being_placed(game_info)
            self.check_place_item(event_list, game_info)
    

        for item in self.items:
            if item.rect.collidepoint(mouse_pos):
                item.curr_color = item.hover_color

                #if someone clicks on item in menu, begin placing that item
                if functions.is_clicked_on(item.rect, event_list): 
                    if self.can_get_item(item, game_info):
                        self.placing_item = True
                        self.item_being_placed = item
            else:
                item.curr_color = item.default_color
            
            if item.cooldown is not None:
                if item.cooldown > 0:
                    item.cooldown -= 1