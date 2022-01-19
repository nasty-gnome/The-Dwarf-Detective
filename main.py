import pygame
import os
import sys


def load_image(name, colorkey=None):
    fullname = os.path.join('sprites', name)
    # если файл не существует, то выходим
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


pygame.init()
pygame.display.set_caption("Карлик-детектив")
running = True
screen = pygame.display.set_mode((1280, 720))
backgrounds = {
    'flat': load_image('flat.jpg'),
    'menu': load_image('menu.png')
}
player_image = load_image('player.png')  # КАРТИНКА ГГ

# группы спрайтов
things_sprites = pygame.sprite.Group()
backgrounds_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
cursor_group = pygame.sprite.Group()
inventory_group = pygame.sprite.Group()
research_background_group = pygame.sprite.Group()
pygame.mouse.set_visible(False)  # СКРЫВАЕМ СТАНДАРТНЫЙ КУРСОР
pick_mark = None
all_items = {}
things = {}


class PickMark(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(inventory_group)
        self.image = load_image("pick_mark.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y


class Inventory(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(inventory_group)
        self.image = load_image("inventory.png")
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = 0, 0
        self.spis = []  # список вещей в инвентаре

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(pygame.mouse.get_pos()) and\
                not cursor.pressed:
            cursor.pressed = True
            if pygame.mouse.get_pos()[1] in range(200, 320):
                global pick_mark
                if len(self.spis) >= 1:
                    pick_mark = PickMark(120, 220)
                    cursor.in_hands = self.spis[0]
            elif pygame.mouse.get_pos()[1] in range(320, 450):
                if len(self.spis) >= 2:
                    pick_mark = PickMark(120, 340)
                    cursor.in_hands = self.spis[1]
            elif pygame.mouse.get_pos()[1] in range(450, 570):
                if len(self.spis) >= 3:
                    pick_mark = PickMark(120, 470)
                    cursor.in_hands = self.spis[2]
            elif pygame.mouse.get_pos()[1] >= 570:
                if len(self.spis) >= 4:
                    pick_mark = PickMark(120, 590)
                    cursor.in_hands = self.spis[3]


class Cursor(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(cursor_group, things_sprites)
        self.standart_cursor = load_image("cursor.gif")
        self.loupe_cursor = load_image("cursor_loupe.png")
        self.back_cursor = load_image("cursor_back.png")
        self.image = self.standart_cursor
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pygame.mouse.get_pos()
        self.research_zone = False  # В ЗОНЕ С КУРСОРОМ-ЛУПОЙ
        self.in_hands = "hand"  # ВЫБРАННЫЙ ПЕРСОНАЖЕМ ПРЕДМЕТ ДЛЯ ИСПОЛЬЗОВАНИЯ
        self.pressed = False  # ЧТОБЫ НЕ ПРОИСХОДИЛИ МНОЖЕСТВЕННЫЕ КЛИКИ

    def update_pos(self):
        global research
        self.rect.x, self.rect.y = pygame.mouse.get_pos()
        if self.research_zone:
            if not research:
                self.image = self.loupe_cursor
            else:
                self.image = self.back_cursor
        else:
            self.image = self.standart_cursor


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group)
        self.image = player_image
        self.rect = self.image.get_rect()
        self.rect.x = pos_x
        self.rect.y = pos_y


class Item (pygame.sprite.Sprite):
    def __init__(self, name):
        super().__init__(inventory_group)
        self.image = load_image(f"{name}.png")
        self.rect = self.image.get_rect()
        add_to_inventory(self, name)


class Thing(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, name):
        self.name = name
        if "SL" not in name:
            super().__init__(things_sprites)
            self.image = load_image(f"{name}.png")
            self.rect = self.image.get_rect()
            self.rect.x = pos_x
            self.rect.y = pos_y

    def update(self, *args):
        global research
        global level_name
        if "RES" in self.name and self.rect.collidepoint(pygame.mouse.get_pos()):
            cursor.research_zone = True
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(pygame.mouse.get_pos()) and\
                not cursor.pressed:
            cursor.pressed = True  # УСТАНАВЛИВАЕМ, ЧТО КУРСОР НАЖАТ
            if level_name == "menu":  # ЭТО УСКОРИТ РАБОТУ
                global menu_run
                if self.name == "continue_button":
                    level_name = "flat"
                    menu_run = False
                    load_level(level_name)
            if level_name == "flat":
                global all_items
                if self.name == "picture" and "ключ" not in things and not research:
                    if cursor.in_hands == "hand":
                        global active_animations
                        active_animations.append([self, 2, 4])
                        things["ключ"] = Thing(600, 85, "key")
                        things.pop("картина")
                    else:
                        print("WRONG")
                    del_pick_mark()
                if self.name == "key" and not research:
                    if cursor.in_hands == "hand":
                        all_items["key_item"] = Item("key_item")
                        things.pop("ключ")
                        self.kill()
                    else:
                        print("WRONG")
                    del_pick_mark()
                if self.name == "closet RES":
                    if cursor.in_hands == "hand":
                        global research_things
                        if not research:
                            research = True
                            global res_back
                            res_back =\
                                pygame.sprite.Sprite(research_background_group)
                            res_back.image = load_image("closet_back.jpg")
                            res_back.rect = res_back.image.get_rect()
                            res_back.rect.x = 200
                            res_back.rect.y = 0
                            things["шкаф"].rect.y = 300
                            if "gun_item" not in inventory.spis:
                                research_things["пистолет"] = Thing(800, 80, "gun")
                            if "hanger_item" not in inventory.spis:
                                research_things["вешалка"] = Thing(600, 255,
                                                                   "hanger")
                            research_things["выход"] = things["шкаф"]
                        else:
                            research = False
                            if "пистолет" in research_things:
                                research_things["пистолет"].kill()
                            if "вешалка" in research_things:
                                research_things["вешалка"].kill()
                            research_things.clear()
                            things["шкаф"].rect.y = 0
                    else:
                        print("WRONG")
                    del_pick_mark()
                if self.name == "gun":
                    if cursor.in_hands == "hanger_item":
                        inventory.spis.pop(inventory.spis.index("hanger_item"))
                        all_items["hanger_item"].kill()
                        del all_items["hanger_item"]
                        all_items["gun_item"] = Item("gun_item")
                        research_things.pop("пистолет")
                        self.kill()
                        arrenge_inventory()
                    else:
                        print("WRONG")
                    del_pick_mark()
                if self.name == "hanger":
                    if cursor.in_hands == "hand":
                        all_items["hanger_item"] = Item("hanger_item")
                        research_things.pop("вешалка")
                        self.kill()
                    else:
                        print("WRONG")
                    del_pick_mark()


def del_pick_mark():
    global pick_mark
    if pick_mark:
        pick_mark.kill()
    pick_mark = None
    cursor.in_hands = "hand"


def add_to_inventory(item, name):  # ИНВЕНТАРЬ УЖЕ ДОЛЖЕН БЫТЬ СОЗДАН
    if len(inventory.spis) == 0:
        item.rect.x = 20
        item.rect.y = 200
    elif len(inventory.spis) == 1:
        item.rect.x = 20
        item.rect.y = 320
    elif len(inventory.spis) == 2:
        item.rect.x = 20
        item.rect.y = 450
    elif len(inventory.spis) == 3:
        item.rect.x = 20
        item.rect.y = 570
    inventory.spis.append(name)


def arrenge_inventory():
    place = 0
    for elem in inventory.spis:
        item = all_items[elem]
        if place == 0:
            item.rect.x = 20
            item.rect.y = 200
        elif place == 1:
            item.rect.x = 20
            item.rect.y = 320
        elif place == 2:
            item.rect.x = 20
            item.rect.y = 450
        elif place == 3:
            item.rect.x = 20
            item.rect.y = 570
        place += 1


def play_animation(elem):
    elem[0].image = load_image(f"{elem[0].name}{elem[1]}.png")
    elem[1] += 1
    if elem[1] > elem[2]:
        active_animations.pop(active_animations.index(elem))


def load_level(level_name):
    new_player = Player(20, 38)
    background = pygame.sprite.Sprite(backgrounds_group)
    background.image = backgrounds[level_name]
    background.rect = background.image.get_rect()
    background.rect.x = 0
    background.rect.y = 0
    global things
    global research
    research = False
    if level_name == "menu":
        things = {"продолжить": Thing(50, 10, "continue_button")}
    else:
        if level_name == "flat":  # ОБЪЕКТЫ СОЗДАЮТСЯ ПОД УРОВНИ
            for elem in things.keys():
                things[elem].kill()
            things = {"картина": Thing(500, 50, "picture"),
                      "шкаф": Thing(1000, 0, "closet RES")}
        things_sprites.draw(screen)
        inventory_group.draw(screen)
        player_group.draw(screen)


cursor = Cursor()
inventory = Inventory()
research_things = {}
active_animations = []  # ПРОИГРЫВАЮЩИЕСЯ АНИМАЦИИ (1 элемент - объект,
# 2 - следующий кадр,3 - количество кадров)
level_name = "menu"  # ЗАДАЁМ ИМЯ УРОВНЯ
load_level(level_name)  # ЗАГРУЖАЕМ ТЕКУЩИЙ УРОВЕНЬ
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        if event.type == pygame.MOUSEBUTTONUP:
            cursor.pressed = False
    screen.fill((0, 0, 0))
    if not research:
        for elem in things.copy().keys():
            things[elem].update(event)
        backgrounds_group.draw(screen)
        things_sprites.draw(screen)
    else:
        research_background_group.draw(screen)
        for elem in research_things.copy().keys():
            screen.blit(research_things[elem].image, research_things[elem].rect)
            research_things[elem].update(event)
    for elem in active_animations:
        play_animation(elem)
    if level_name != "menu":
        inventory.update(event)
        inventory_group.draw(screen)
        player_group.draw(screen)
    cursor.update_pos()
    cursor.research_zone = False
    cursor_group.draw(screen)
    pygame.display.flip()