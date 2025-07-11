import pygame
from globals import screen, GameInfo
from views.enemies import Enemy
import functions

class Ability:
    def __init__(self, title: str, pos: tuple[int, int]) -> None:
        self.title: str = title
        self.pos: tuple[int, int] = pos

        self.image_width: int = 20
        self.image: pygame.Surface
        self.image_rect: pygame.Rect
        self.image, self.image_rect = functions.load_image_and_rect(self.title, self.image_width, self.pos)
    
    def draw(self) -> None:
        functions.display_image_static(self.image, self.image_rect)

class Bomb(Ability):
    def __init__(self, title: str, pos: tuple[int, int]) -> None:
        super().__init__(title, pos)

        #Bomb Stats
        self.base_fuse_time: int = 100
        self.fuse_time: int = self.base_fuse_time

        self.damage: int = 40
        self.explosion_radius: int = 60

    
    def draw(self) -> None:
        cooldown_bar_color = (255, 255, 255)
        functions.display_image_static(self.image, self.image_rect)
        functions.display_health_bar(self, self.fuse_time, self.base_fuse_time, cooldown_bar_color)

    def is_exploding(self) -> bool:
        if self.fuse_time <= 0:
            return True
        else:
            self.fuse_time -= 1
            return False
    
    def explode(self, enemy_list: list[Enemy]) -> None:
        for enemy in enemy_list:
            distance_between = functions.find_distance(self.pos, enemy.pos)
            if distance_between <= self.explosion_radius:
                enemy.take_damage(self.damage)
    
    def update(self, game_info: GameInfo) -> None:
        self.draw()
        
        if self.is_exploding():
            self.explode(game_info.enemy_list)
            game_info.unattackable_list.remove(self)