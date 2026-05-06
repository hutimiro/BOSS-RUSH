"""
Define
In/Args
Out/Returns
Purpose
Last modify,When
"""
import pygame
import sys
import math
import random
import re
from pathlib import Path
from collections import deque

# khởi tạo 
pygame.init()
WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BOSS RUSH")
clock = pygame.time.Clock()
FPS = 60

# màu
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (100, 150, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)


ASSET_ROOT = Path(__file__).resolve().parent / "Royalty Free Game Art - Spaceships from Unlucky Studio" / "Spaceship_art_pack"
ICON_ROOT = Path(__file__).resolve().parent / "free-pixel-art-sci-fi-icons-pack" / "PNG"
FONT_ROOT = Path(__file__).resolve().parent / "nulshock"
NULSHOCK_FONT_PATH = FONT_ROOT / "Nulshock Bd.otf"
_IMAGE_CACHE = {}


def _natural_key(path):
    parts = re.split(r"(\d+)", path.stem)
    return [int(part) if part.isdigit() else part.lower() for part in parts]


def load_image(*parts, alpha=True, root=ASSET_ROOT):
    cache_key = (str(root), parts, alpha)
    if cache_key in _IMAGE_CACHE:
        return _IMAGE_CACHE[cache_key]

    path = root.joinpath(*parts)
    try:
        image = pygame.image.load(str(path))
        image = image.convert_alpha() if alpha else image.convert()
        _IMAGE_CACHE[cache_key] = image
        return image
    except (pygame.error, FileNotFoundError):
        return None


def load_sequence(*parts):
    directory = ASSET_ROOT.joinpath(*parts)
    if not directory.exists():
        return []

    frames = []
    for path in sorted(directory.glob("*.png"), key=_natural_key):
        image = load_image(*(parts + (path.name,)))
        if image is not None:
            frames.append(image)
    return frames


def fit_image(image, size):
    if image is None:
        return None
    if image.get_size() == size:
        return image
    return pygame.transform.smoothscale(image, size)


def draw_centered_image(surface, image, center, size=None, angle=None):
    if image is None:
        return False

    sprite = image
    if size is not None:
        sprite = fit_image(sprite, size)
    if angle is not None:
        sprite = pygame.transform.rotozoom(sprite, angle, 1.0)

    rect = sprite.get_rect(center=center)
    surface.blit(sprite, rect)
    return True


def bullet_angle(dx, dy):
    if dx == 0 and dy == 0:
        return 0.0
    return math.degrees(math.atan2(-dy, dx)) - 90.0


PLAYER_FRAMES = load_sequence("Blue", "spaceship_blue_animation")
if not PLAYER_FRAMES:
    fallback_player = load_image("Blue", "alienship_new.png") or load_image("Blue", "Communicationship_blue.png")
    PLAYER_FRAMES = [fallback_player] if fallback_player is not None else []

ENEMY_FRAMES = load_sequence("Red", "Enemy_animation")
if not ENEMY_FRAMES:
    fallback_enemy = load_image("Red", "spaceship_enemy_red.png") or load_image("Red", "alienship_new_red_try.png")
    ENEMY_FRAMES = [fallback_enemy] if fallback_enemy is not None else []

BACKGROUND_IMAGE = load_image("Background", "background.jpg", alpha=False)
PLAYER_BULLET_IMAGE = load_image("Blue", "bullet.png")
ENEMY_BULLET_IMAGE = load_image("Red", "bullet_red.png")
BOUNCE_BULLET_IMAGE = load_image("Red", "space_mine.png") or load_image("Red", "space_mine_blue.png") or ENEMY_BULLET_IMAGE
EXPLOSIVE_BULLET_IMAGE = load_image("Red", "space_bomb.png") or load_image("Red", "space_bomb_blue.png") or ENEMY_BULLET_IMAGE

BOSS_VISUALS = {
    "circle": load_image("Red", "mothership_try.png") or load_image("Red", "mothership_blue.png"),
    "fan": load_image("Red", "alienship_new_red_try.png") or load_image("Red", "alienship_new.png"),
    "orbit": load_image("Red", "space_mine.png") or load_image("Red", "space_mine_blue.png"),
    "triple_left": load_image("Red", "Communicationship2.png") or load_image("Blue", "Communicationship_blue.png"),
    "triple_right": load_image("Red", "small_ships.png") or load_image("Blue", "small_ships.png"),
    "explode": load_image("Red", "space_bomb.png") or load_image("Blue", "space_bomb_blue.png"),
    "generic": ENEMY_FRAMES[0] if ENEMY_FRAMES else None,
}


def draw_background(surface):
    if BACKGROUND_IMAGE is not None:
        surface.blit(fit_image(BACKGROUND_IMAGE, (WIDTH, HEIGHT)), (0, 0))
    else:
        surface.fill(BLACK)


def load_icon(*parts, alpha=True):
    return load_image(*parts, alpha=alpha, root=ICON_ROOT)


def load_nulshock_font(size):
    try:
        return pygame.font.Font(str(NULSHOCK_FONT_PATH), size)
    except (FileNotFoundError, OSError, pygame.error):
        return pygame.font.SysFont(None, size)


BACKGROUND_SCROLL_SPEED = -10
BACKGROUND_OFFSET = 0

GUN_TYPE_ICONS = {
    1: load_icon("Shooting1.png"),
    2: load_icon("Shooting2.png"),
    3: load_icon("Shooting3.png"),
}

UPGRADE_OPTION_ICONS = {
    1: load_icon("OptionLife.png"),
    2: load_icon("OptionChange.png"),
    3: load_icon("OptionDamage.png"),
}

BOSS_STAGE_ICONS = [
    load_icon("4.png"),
    load_icon("5.png"),
    load_icon("6.png"),
]


def boss_stage_icon(index):
    if not BOSS_STAGE_ICONS:
        return None
    return BOSS_STAGE_ICONS[index % len(BOSS_STAGE_ICONS)]


def draw_text_with_icon(surface, icon, text, font, x, y, color=(255, 255, 255), icon_size=(24, 24), gap=8, align="left", icon_after=False):
    text_surface = font.render(text, True, color)

    if icon is None:
        surface.blit(text_surface, text_surface.get_rect(topleft=(x, y)) if align == "left" else text_surface.get_rect(center=(x, y)))
        return

    icon_surface = fit_image(icon, icon_size)
    if icon_surface is None:
        surface.blit(text_surface, text_surface.get_rect(topleft=(x, y)) if align == "left" else text_surface.get_rect(center=(x, y)))
        return

    if align == "center":
        total_width = icon_surface.get_width() + gap + text_surface.get_width()
        start_x = x - total_width // 2
        if icon_after:
            text_rect = text_surface.get_rect(midleft=(start_x, y))
            icon_rect = icon_surface.get_rect(midleft=(start_x + text_surface.get_width() + gap, y))
        else:
            icon_rect = icon_surface.get_rect(midleft=(start_x, y))
            text_rect = text_surface.get_rect(midleft=(start_x + icon_surface.get_width() + gap, y))
    else:
        if icon_after:
            text_rect = text_surface.get_rect(topleft=(x, y))
            icon_rect = icon_surface.get_rect(midleft=(x + text_surface.get_width() + gap, y + text_surface.get_height() // 2))
        else:
            icon_rect = icon_surface.get_rect(topleft=(x, y))
            text_rect = text_surface.get_rect(midleft=(x + icon_surface.get_width() + gap, y + icon_surface.get_height() // 2))

    surface.blit(icon_surface, icon_rect)
    surface.blit(text_surface, text_rect)


def draw_scrolling_background(surface, offset):
    if BACKGROUND_IMAGE is None:
        surface.fill(BLACK)
        return

    background = fit_image(BACKGROUND_IMAGE, (WIDTH, HEIGHT))
    if background is None:
        surface.fill(BLACK)
        return

    tile_height = background.get_height()
    if tile_height <= 0:
        surface.blit(background, (0, 0))
        return

    y = -(offset % tile_height)
    while y < HEIGHT:
        surface.blit(background, (0, y))
        y += tile_height


#object pool

class Bullet:
    def __init__(self):
        """bullet của player"""
        self.rect = pygame.Rect(0, 0, 14, 28) # kích thước đạn
        self.active = False
        self.speed = 15 # speed dương cho dễ tính hướng
        self.exact_x = 0.0
        self.exact_y = 0.0
        self.dx = 0.0
        self.dy = -self.speed
        self.homing = False
        self.damage = 15

    def fire(self, x, y, dx=0.0, dy=None, homing=False, damage=15):
        """bắn bullet từ x y"""
        if dy is None:
            dy = -self.speed

        # bật đạn 
        self.active = True
        self.rect.centerx = x
        self.rect.bottom = y
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.dx = dx
        self.dy = dy
        self.homing = homing
        self.damage = damage

    def update(self, target=None):
        """cập nhật bullet và tự nhắm khi có target"""
        if self.active:
            if target is not None and hasattr(target, "get_homing_target"):
                target = target.get_homing_target(self)

            # có boss thì bẻ hướng nhẹ
            if self.homing and target and target.active:
                # khi đạn đã vượt qua boss thì ngừng tự nhắm để tránh vòng lại quanh boss
                if self.exact_y <= target.rect.top:
                    self.homing = False
                
            if self.homing and target and target.active:
                dir_x = target.rect.centerx - self.exact_x
                dir_y = target.rect.centery - self.exact_y
                dist = math.hypot(dir_x, dir_y)
                if dist > 0:
                    # càng lớn thì cua càng gắt
                    homing_power = 0.08
                    
                    target_dx = (dir_x / dist) * self.speed
                    target_dy = (dir_y / dist) * self.speed
                    
                    self.dx += (target_dx - self.dx) * homing_power
                    self.dy += (target_dy - self.dy) * homing_power
                    
                    # giữ tốc độ ổn định
                    current_speed = math.hypot(self.dx, self.dy)
                    if current_speed > 0:
                        self.dx = (self.dx / current_speed) * self.speed
                        self.dy = (self.dy / current_speed) * self.speed

            # đi bằng float
            self.exact_x += self.dx
            self.exact_y += self.dy
            self.rect.centerx = int(self.exact_x)
            self.rect.centery = int(self.exact_y)

            # ra ngoài màn hình thì tắt
            if self.rect.bottom < 0 or self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
                self.active = False

    def draw(self, surface):
        """vẽ đạn"""
        if self.active:
            sprite = PLAYER_BULLET_IMAGE
            angle = bullet_angle(self.dx, self.dy)
            if sprite is not None:
                draw_centered_image(surface, sprite, self.rect.center, self.rect.size, angle=angle)
            else:
                bullet_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                pygame.draw.rect(bullet_surface, (255, 0, 0, 120), bullet_surface.get_rect())
                surface.blit(bullet_surface, self.rect.topleft)

class BulletPool:
    def __init__(self, size):
        """hồ chứa giữ đạn rảnh và đạn đang bay"""
        # tạo sẵn đạn để đỡ tạo mới liên tục
        self.pool = deque([Bullet() for _ in range(size)])
        self.active_bullets = [] # đạn đang bay

    def get_bullet(self, x, y, dx=0.0, dy=None, homing=False, damage=15):
        """lấy đạn từ pool"""
        if self.pool:
            # còn đạn rảnh thì lấy ra dùng
            bullet = self.pool.popleft()
            bullet.fire(x, y, dx, dy, homing, damage)
            self.active_bullets.append(bullet)

    def update(self, target=None):
        """update active_bullets"""
        for bullet in self.active_bullets[:]: # lặp bản sao để xóa an toàn
            bullet.update(target)
            
            # đạn tắt thì trả về  hồ
            if not bullet.active:
                # dọn khỏi danh sách đang bay
                self.active_bullets.remove(bullet)
                self.pool.append(bullet)

    def draw(self, surface):
        """vẽ active_bullets"""
        for bullet in self.active_bullets:
            bullet.draw(surface)

    def clear(self):
        """xóa toàn bộ đạn đang bay"""
        for bullet in self.active_bullets:
            bullet.active = False
            self.pool.append(bullet)
        self.active_bullets.clear()

class EnemyBullet:
    def __init__(self):
        """đạn của boss"""
        self.rect = pygame.Rect(0, 0, 14, 14)
        self.active = False
        self.speed_x = 0
        self.speed_y = 0
        self.exact_x = 0.0
        self.exact_y = 0.0
        self.bounces_left = 0
        self.damage = 1
        self.squiggle = False
        self.origin_x = 0.0
        self.origin_y = 0.0
        self.direction_x = 0.0
        self.direction_y = 0.0
        self.perp_x = 0.0
        self.perp_y = 0.0
        self.travel_speed = 0.0
        self.travel_distance = 0.0
        self.wobble_amplitude = 0.0
        self.wobble_frequency = 0.0
        self.wobble_phase = 0.0
        self.spawn_time = 0
        self.explosive = False
        self.bullet_kind = "normal"
        self.explode_after = 0
        self.child_count = 0
        self.child_size = 6
        self.child_speed = 3.5
        self.child_damage = 1
        self.is_child = False

    def fire(
        self,
        x,
        y,
        dx,
        dy,
        bounces=0,
        size=10,
        damage=1,
        current_time=None,
        squiggle=False,
        wobble_amplitude=0.0,
        wobble_frequency=0.0,
        wobble_phase=0.0,
        explosive=False,
        bullet_kind="normal",
        explode_after=0,
        child_count=0,
        child_size=6,
        child_speed=3.5,
        child_damage=1,
        is_child=False,
    ):
        """bắn đạn boss """
        # lưu vận tốc để update mỗi frame
        self.active = True
        size = max(int(round(size * 1.25)), 14)
        self.rect.size = (size, size)
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_x = dx
        self.speed_y = dy
        self.bounces_left = bounces
        self.damage = damage
        self.squiggle = squiggle
        self.origin_x = float(x)
        self.origin_y = float(y)
        self.travel_distance = 0.0
        self.wobble_amplitude = wobble_amplitude
        self.wobble_frequency = wobble_frequency
        self.wobble_phase = wobble_phase
        self.spawn_time = current_time if current_time is not None else pygame.time.get_ticks()
        self.explosive = explosive
        self.bullet_kind = bullet_kind if not explosive else "explode_main"
        self.explode_after = explode_after
        self.child_count = child_count
        self.child_size = child_size
        self.child_speed = child_speed
        self.child_damage = child_damage
        self.is_child = is_child

        if self.squiggle:
            travel_speed = math.hypot(dx, dy)
            if travel_speed > 0:
                self.travel_speed = travel_speed
                self.direction_x = dx / travel_speed
                self.direction_y = dy / travel_speed
                self.perp_x = -self.direction_y
                self.perp_y = self.direction_x
            else:
                self.travel_speed = 0.0
                self.direction_x = 0.0
                self.direction_y = 0.0
                self.perp_x = 0.0
                self.perp_y = 0.0
        else:
            self.travel_speed = 0.0
            self.direction_x = 0.0
            self.direction_y = 0.0
            self.perp_x = 0.0
            self.perp_y = 0.0

    def update(self, current_time=None):
        """cập nhật đạn boss và nảy tường"""
        if self.active:
            if current_time is None:
                current_time = pygame.time.get_ticks()

            if self.squiggle:
                self.travel_distance += self.travel_speed
                base_x = self.origin_x + self.direction_x * self.travel_distance
                base_y = self.origin_y + self.direction_y * self.travel_distance
                wobble = math.sin(self.wobble_phase + self.travel_distance * self.wobble_frequency) * self.wobble_amplitude
                self.exact_x = base_x + self.perp_x * wobble
                self.exact_y = base_y + self.perp_y * wobble
            else:
                self.exact_x += self.speed_x
                self.exact_y += self.speed_y

            self.rect.centerx = int(self.exact_x)
            self.rect.centery = int(self.exact_y)

            if self.bullet_kind == "explode_main" and current_time - self.spawn_time >= self.explode_after:
                spawned_bullets = []
                if self.child_count > 0:
                    for index in range(self.child_count):
                        angle = math.tau * index / self.child_count
                        dx = math.cos(angle) * self.child_speed
                        dy = math.sin(angle) * self.child_speed
                        spawned_bullets.append(
                            {
                                "x": self.rect.centerx,
                                "y": self.rect.centery,
                                "dx": dx,
                                "dy": dy,
                                "bounces": 0,
                                "size": self.child_size,
                                "damage": self.child_damage,
                                "current_time": current_time,
                                "squiggle": False,
                                "wobble_amplitude": 0.0,
                                "wobble_frequency": 0.0,
                                "wobble_phase": 0.0,
                                "explosive": False,
                                "bullet_kind": "explode_child",
                                "explode_after": 0,
                                "child_count": 0,
                                "child_size": 6,
                                "child_speed": 3.5,
                                "child_damage": 1,
                                "is_child": True,
                            }
                        )

                self.active = False
                return spawned_bullets

            if self.bounces_left > 0:
                # chỉ xử lý nảy khi còn lần nảy
                bounced = False
                if self.rect.left <= 0:
                    self.speed_x = abs(self.speed_x)
                    self.exact_x = self.rect.width / 2
                    bounced = True
                elif self.rect.right >= WIDTH:
                    self.speed_x = -abs(self.speed_x)
                    self.exact_x = WIDTH - self.rect.width / 2
                    bounced = True
                
                if self.rect.top <= 0:
                    self.speed_y = abs(self.speed_y)
                    self.exact_y = self.rect.height / 2
                    bounced = True
                elif self.rect.bottom >= HEIGHT:
                    self.speed_y = -abs(self.speed_y)
                    self.exact_y = HEIGHT - self.rect.height / 2
                    bounced = True

                if bounced:
                    # mỗi lần chạm tường thì trừ một lần nảy
                    self.bounces_left -= 1
                    self.rect.centerx = int(self.exact_x)
                    self.rect.centery = int(self.exact_y)

            # bay quá xa thì thu hồi
            if not (-50 < self.rect.x < WIDTH + 50 and -50 < self.rect.y < HEIGHT + 50):
                self.active = False

        return []

    def draw(self, surface):
        """vẽ enemy bullet"""
        if self.active:
            if self.bullet_kind == "explode_main":
                sprite = EXPLOSIVE_BULLET_IMAGE
            elif self.bounces_left > 0:
                sprite = BOUNCE_BULLET_IMAGE
            elif self.is_child:
                sprite = ENEMY_BULLET_IMAGE
            elif self.squiggle:
                sprite = ENEMY_BULLET_IMAGE
            else:
                sprite = ENEMY_BULLET_IMAGE

            angle = bullet_angle(self.speed_x, self.speed_y)
            if sprite is not None:
                draw_centered_image(surface, sprite, self.rect.center, self.rect.size, angle=angle)
            else:
                if self.is_child:
                    color = (200, 255, 200)
                elif self.bullet_kind == "explode_main":
                    color = (255, 90, 90)
                elif self.squiggle:
                    color = (255, 120, 255)
                else:
                    color = (255, 165, 0) if self.bounces_left > 0 else YELLOW
                pygame.draw.circle(surface, color, self.rect.center, max(self.rect.width, self.rect.height) // 2)

class EnemyBulletPool:
    def __init__(self, size):
        """hồ chứa đạn của boss"""
        self.pool = deque([EnemyBullet() for _ in range(size)])
        self.active_bullets = []

    def get_bullet(self, x, y, dx, dy, bounces=0, size=10, damage=1, current_time=None, squiggle=False, wobble_amplitude=0.0, wobble_frequency=0.0, wobble_phase=0.0, explosive=False, bullet_kind="normal", explode_after=0, child_count=0, child_size=6, child_speed=3.5, child_damage=1, is_child=False):
        """lấy đạn boss từ hồ"""
        if self.pool:
            # boss bắn
            bullet = self.pool.popleft()
            bullet.fire(
                x,
                y,
                dx,
                dy,
                bounces,
                size=size,
                damage=damage,
                current_time=current_time,
                squiggle=squiggle,
                wobble_amplitude=wobble_amplitude,
                wobble_frequency=wobble_frequency,
                wobble_phase=wobble_phase,
                explosive=explosive,
                bullet_kind=bullet_kind,
                explode_after=explode_after,
                child_count=child_count,
                child_size=child_size,
                child_speed=child_speed,
                child_damage=child_damage,
                is_child=is_child,
            )
            self.active_bullets.append(bullet)

    def update(self, current_time=None):
        """update đạn của boss"""
        spawned_bullets = []
        for bullet in self.active_bullets[:]:
            spawned_bullets.extend(bullet.update(current_time))
            if not bullet.active:
                # trả lại hồ
                self.active_bullets.remove(bullet)
                self.pool.append(bullet)

        for bullet_data in spawned_bullets:
            self.get_bullet(**bullet_data)

    def draw(self, surface):
        """vẽ đạn của boss"""
        for bullet in self.active_bullets:
            bullet.draw(surface)

    def clear(self):
        """xóa toàn bộ đạn boss đang bay"""
        for bullet in self.active_bullets:
            bullet.active = False
            self.pool.append(bullet)
        self.active_bullets.clear()


class Quadtree:
    def __init__(self, bounds, capacity=6, max_depth=5, depth=0):
        self.bounds = bounds.copy()
        self.capacity = capacity
        self.max_depth = max_depth
        self.depth = depth
        self.objects = []
        self.children = None

    def _subdivide(self):
        half_width = self.bounds.width // 2
        half_height = self.bounds.height // 2
        x = self.bounds.x
        y = self.bounds.y

        self.children = [
            Quadtree(pygame.Rect(x, y, half_width, half_height), self.capacity, self.max_depth, self.depth + 1),
            Quadtree(pygame.Rect(x + half_width, y, self.bounds.width - half_width, half_height), self.capacity, self.max_depth, self.depth + 1),
            Quadtree(pygame.Rect(x, y + half_height, half_width, self.bounds.height - half_height), self.capacity, self.max_depth, self.depth + 1),
            Quadtree(pygame.Rect(x + half_width, y + half_height, self.bounds.width - half_width, self.bounds.height - half_height), self.capacity, self.max_depth, self.depth + 1),
        ]

    def _get_child_index(self, rect):
        vertical_midpoint = self.bounds.x + self.bounds.width / 2
        horizontal_midpoint = self.bounds.y + self.bounds.height / 2

        top_quadrant = rect.bottom <= horizontal_midpoint
        bottom_quadrant = rect.top >= horizontal_midpoint

        if rect.right <= vertical_midpoint:
            if top_quadrant:
                return 0
            if bottom_quadrant:
                return 2
        elif rect.left >= vertical_midpoint:
            if top_quadrant:
                return 1
            if bottom_quadrant:
                return 3

        return -1

    def insert(self, obj):
        if not self.bounds.colliderect(obj.rect):
            return False

        if self.children is not None:
            child_index = self._get_child_index(obj.rect)
            if child_index != -1:
                return self.children[child_index].insert(obj)

        self.objects.append(obj)

        if len(self.objects) > self.capacity and self.depth < self.max_depth:
            if self.children is None:
                self._subdivide()

            for stored_obj in self.objects[:]:
                child_index = self._get_child_index(stored_obj.rect)
                if child_index != -1:
                    self.objects.remove(stored_obj)
                    self.children[child_index].insert(stored_obj)

        return True

    def query(self, area, found=None):
        if found is None:
            found = []

        if not self.bounds.colliderect(area):
            return found

        for obj in self.objects:
            if obj.rect.colliderect(area):
                found.append(obj)

        if self.children is not None:
            for child in self.children:
                if child.bounds.colliderect(area):
                    child.query(area, found)

        return found

"""player và boss"""

class Player:
    def __init__(self):
        """player chính"""
        self.rect = pygame.Rect(WIDTH//2 - 20, HEIGHT - 60, 40, 40)
        self.normal_speed = 6
        self.slow_speed = 3
        self.is_focused = False
        self.lives = 4
        self.invulnerable_until = 0
        self.sprite_frames = PLAYER_FRAMES
        self.sprite_frame_delay = 120

    def move(self, keys):
        """di chuyển player theo keys"""
        # shift để  focus
        self.is_focused = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = self.slow_speed if self.is_focused else self.normal_speed

        # giữ tâm để đổi hitbox không bị lệch
        center = self.rect.center
        if self.is_focused:
            self.rect.size = (5, 5) # hitbox focus
        else:
            self.rect.size = (16, 16) # hitbox thường
        self.rect.center = center

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= current_speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += current_speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= current_speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += current_speed

    def draw(self, surface, current_time):
        """vẽ player và buffer screen"""
        # nhấp nháy
        if current_time < self.invulnerable_until and (current_time // 100) % 2 == 0:
            return

        sprite = None
        if self.sprite_frames:
            frame_index = (current_time // self.sprite_frame_delay) % len(self.sprite_frames)
            sprite = self.sprite_frames[frame_index]

        if sprite is not None:
            if self.is_focused:
                display_size = (44, 44)
                focused_sprite = fit_image(sprite, display_size)
                if focused_sprite is not None:
                    focused_sprite = focused_sprite.copy()
                    focused_sprite.set_alpha(120)
                    surface.blit(focused_sprite, focused_sprite.get_rect(center=self.rect.center))
                pygame.draw.circle(surface, BLUE, self.rect.center, max(4, min(self.rect.width, self.rect.height) // 2))
            else:
                draw_centered_image(surface, sprite, self.rect.center, (58, 58))
        elif self.is_focused:
            # giữ shift thì thu nhỏ hitbõ
            phantom_rect = self.rect.copy()
            phantom_rect.inflate_ip(0, 0)
            pygame.draw.rect(surface, (50, 75, 125), phantom_rect) 
            pygame.draw.rect(surface, BLUE, self.rect)
            pygame.draw.circle(surface, BLUE, self.rect.center, max(4, min(self.rect.width, self.rect.height) // 2))
        else:
            pygame.draw.rect(surface, BLUE, self.rect)

class BaseBoss:
    def __init__(self, x, y, width, height, health, color, name, target_y=100, speed=2, shoot_delay=200, entry_delay=1000, sprite_image=None, sprite_frames=None):
        """boss nền để tạo nhiều kiểu boss khác nhau"""
        self.rect = pygame.Rect(x, y, width, height)
        self.target_y = target_y
        self.speed = speed
        self.ready = False
        self.last_shot_time = 0
        self.shoot_delay = shoot_delay
        self.max_health = health
        self.health = self.max_health
        self.active = True
        self.shoot_angle_offset = 0
        self.color = color
        self.name = name
        self.entry_delay = entry_delay
        self.spawn_time = None
        self.sprite_image = sprite_image
        self.sprite_frames = sprite_frames if sprite_frames is not None else ENEMY_FRAMES

    def update(self, current_time, enemy_bullet_pool):
        """cập nhật chuyển động và gọi bắn"""
        if not self.active:
            return

        if self.spawn_time is None:
            self.spawn_time = current_time

        if current_time - self.spawn_time < self.entry_delay:
            return

        if self.rect.y < self.target_y:
            self.rect.y += self.speed
        else:
            self.ready = True

        if self.ready and current_time - self.last_shot_time > self.shoot_delay:
            self.shoot(enemy_bullet_pool)
            self.last_shot_time = current_time

    def shoot(self, enemy_bullet_pool):
        """ghi đè ở lớp con"""
        raise NotImplementedError

    def take_damage(self, amount, hit_rect=None):
        """giảm máu boss"""
        if not self.active:
            return

        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.active = False

    def collision_rects(self):
        """trả về các hitbox có thể bị trúng"""
        if self.active:
            return [self.rect]
        return []

    def is_cleared(self):
        """boss này đã bị hạ chưa"""
        return not self.active

    def draw(self, surface):
        """vẽ boss và vòng máu"""
        if not self.active:
            return

        sprite = None
        if self.sprite_image is not None:
            sprite = self.sprite_image
        elif self.sprite_frames:
            frame_index = (pygame.time.get_ticks() // 120) % len(self.sprite_frames)
            sprite = self.sprite_frames[frame_index]

        if sprite is not None:
            sprite = pygame.transform.flip(sprite, False, True)
            draw_centered_image(surface, sprite, self.rect.center, self.rect.size)
        else:
            pygame.draw.rect(surface, self.color, self.rect)

        center = self.rect.center
        radius = max(self.rect.width, self.rect.height) // 2 + 20
        pygame.draw.circle(surface, (50, 50, 50), center, radius, 5)

        if self.health > 0:
            health_ratio = self.health / self.max_health
            rect_for_arc = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
            start_angle = math.pi / 2
            end_angle = start_angle + (2 * math.pi * health_ratio)
            pygame.draw.arc(surface, RED, rect_for_arc, start_angle, end_angle, 5)


class CircleShotBoss(BaseBoss):
    def __init__(self):
        super().__init__(WIDTH // 2 - 40, -100, 80, 80, 1000, GREEN, "Circle Shot Boss", entry_delay=1000, sprite_image=BOSS_VISUALS["circle"])

    def shoot(self, enemy_bullet_pool):
        """bắn vòng đạn tròn"""
        num_bullets = random.randint(15, 20)
        base_speed = random.uniform(3.0, 5.0)
        self.shoot_angle_offset += random.uniform(10.0, 25.0)

        for i in range(num_bullets):
            angle_deg = self.shoot_angle_offset + i * (360 / num_bullets)
            angle = math.radians(angle_deg)
            speed = base_speed + random.uniform(-1.0, 1.0)

            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            enemy_bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, dx, dy, 0)


class FanBounceBoss(BaseBoss):
    def __init__(self):
        super().__init__(WIDTH // 2 - 45, -100, 90, 90, 1200, (80, 220, 255), "Fan Bounce Boss", shoot_delay=240, entry_delay=1000, sprite_image=BOSS_VISUALS["fan"])

    def shoot(self, enemy_bullet_pool):
        """bắn quạt và có đạn nảy"""
        num_bullets = random.randint(5, 8)
        spread_deg = random.uniform(40.0, 70.0)
        base_angle = math.pi / 2
        base_speed = random.uniform(4.0, 6.0)

        for i in range(num_bullets):
            if num_bullets == 1:
                offset = 0.0
            else:
                t = i / (num_bullets - 1)
                offset = math.radians(-spread_deg / 2 + spread_deg * t)

            angle = base_angle + offset
            speed = base_speed + random.uniform(-0.6, 0.8)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            bounces = 0
            if random.random() < 0.65:
                bounces = random.randint(1, 2)

            enemy_bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, dx, dy, bounces)

class OrbitCircleBoss(BaseBoss):
    def __init__(self):
        super().__init__(WIDTH // 2 - 45, -100, 90, 90, 1600, (255, 120, 120), "Orbit Circle Boss", target_y=130, speed=2, shoot_delay=450, entry_delay=1000, sprite_image=BOSS_VISUALS["orbit"])
        self.patrol_speed = 2.5
        self.patrol_direction = 1
        self.patrol_ready = False
        self.left_bound = 60
        self.right_bound = WIDTH - 60 - self.rect.width

    def update(self, current_time, enemy_bullet_pool):
        """di chuyển tới giữa rồi đi ngang trái phải"""
        if not self.active:
            return

        if self.spawn_time is None:
            self.spawn_time = current_time

        if current_time - self.spawn_time < self.entry_delay:
            return

        if not self.patrol_ready:
            if self.rect.y < self.target_y:
                self.rect.y += self.speed
                return
            self.patrol_ready = True
            self.rect.y = self.target_y

        self.rect.x += self.patrol_direction * self.patrol_speed

        if self.rect.x <= self.left_bound:
            self.rect.x = self.left_bound
            self.patrol_direction = 1
        elif self.rect.x >= self.right_bound:
            self.rect.x = self.right_bound
            self.patrol_direction = -1

        if current_time - self.last_shot_time > self.shoot_delay:
            self.shoot(enemy_bullet_pool)
            self.last_shot_time = current_time

    def shoot(self, enemy_bullet_pool):
        """bắn 8 đạn lớn, chậm, theo hình tròn"""
        num_bullets = 8
        base_speed = 1.8

        for i in range(num_bullets):
            angle_deg = i * (360 / num_bullets)
            angle = math.radians(angle_deg)
            speed = base_speed + random.uniform(-0.2, 0.2)

            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            enemy_bullet_pool.get_bullet(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                0,
                size=60,
            )


class SquiggleBoss(BaseBoss):
    def shoot(self, enemy_bullet_pool):
        """bắn 6 hướng ngẫu nhiên theo quỹ đạo squiggle"""
        num_bullets = 6

        for _ in range(num_bullets):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(3.2, 4.8)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            enemy_bullet_pool.get_bullet(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                0,
                size=14,
                squiggle=True,
                wobble_amplitude=random.uniform(4.0, 9.0),
                wobble_frequency=random.uniform(0.10, 0.20),
                wobble_phase=random.uniform(0.0, math.tau),
            )


def draw_boss_health_bar(surface, x, y, width, height, health_ratio, color, label):
    """vẽ thanh máu boss có nhãn"""
    background_rect = pygame.Rect(x, y, width, height)
    filled_width = max(0, int(width * max(0.0, min(health_ratio, 1.0))))
    filled_rect = pygame.Rect(x, y, filled_width, height)

    pygame.draw.rect(surface, (35, 35, 35), background_rect, border_radius=4)
    if filled_width > 0:
        pygame.draw.rect(surface, color, filled_rect, border_radius=4)
    pygame.draw.rect(surface, (220, 220, 220), background_rect, 2, border_radius=4)

    label_surface = load_nulshock_font(18).render(label, True, (255, 255, 255))
    surface.blit(label_surface, (x, y - 18))


class TripleSquiggleBossStage:
    def __init__(self):
        """boss màn 4 với 3 boss riêng"""
        self.name = "Triple Squiggle Boss"
        self.active = True
        self.ready = False
        self.last_shot_time = 0
        self.shoot_delay = 320
        self.entry_delay = 1000
        self.spawn_time = None

        self.center_boss = SquiggleBoss(
            WIDTH // 2 - 48,
            -150,
            96,
            96,
            1100,
            (240, 130, 255),
            "Center Squiggle Boss",
            target_y=88,
            speed=2,
            shoot_delay=360,
            entry_delay=self.entry_delay,
            sprite_frames=ENEMY_FRAMES,
        )
        self.left_boss = SquiggleBoss(
            WIDTH // 2 - 170,
            -150,
            78,
            78,
            800,
            (255, 170, 90),
            "Left Squiggle Boss",
            target_y=118,
            speed=2,
            shoot_delay=260,
            entry_delay=self.entry_delay,
            sprite_image=BOSS_VISUALS["triple_left"],
        )
        self.right_boss = SquiggleBoss(
            WIDTH // 2 + 92,
            -150,
            78,
            78,
            800,
            (90, 220, 255),
            "Right Squiggle Boss",
            target_y=118,
            speed=2,
            shoot_delay=260,
            entry_delay=self.entry_delay,
            sprite_image=BOSS_VISUALS["triple_right"],
        )
        self.bosses = [self.center_boss, self.left_boss, self.right_boss]
        self.max_health = sum(boss.max_health for boss in self.bosses)
        self.health = self.max_health
        self.rect = pygame.Rect(0, 0, 1, 1)
        self._timers_synced = False
        self._refresh_bounds()

    def _sync_timers(self, current_time):
        for boss in self.bosses:
            boss.spawn_time = current_time
            boss.last_shot_time = current_time
            boss.ready = False
        self._timers_synced = True

    def _refresh_bounds(self):
        active_rects = [boss.rect for boss in self.bosses if boss.active]
        if not active_rects:
            self.rect = pygame.Rect(0, 0, 1, 1)
            self.active = False
            return

        left = min(rect.left for rect in active_rects)
        top = min(rect.top for rect in active_rects)
        right = max(rect.right for rect in active_rects)
        bottom = max(rect.bottom for rect in active_rects)
        self.rect = pygame.Rect(left, top, right - left, bottom - top)
        self.active = True

    def collision_rects(self):
        return [boss.rect for boss in self.bosses if boss.active]

    def get_homing_target(self, bullet=None):
        """trả về boss mà đạn tìm đường nên bám theo"""
        if self.center_boss.active:
            return self.center_boss

        active_side_bosses = [boss for boss in (self.left_boss, self.right_boss) if boss.active]
        if not active_side_bosses:
            return None

        if bullet is None:
            return min(active_side_bosses, key=lambda boss: abs(boss.rect.centerx - self.rect.centerx))

        return min(active_side_bosses, key=lambda boss: math.hypot(boss.rect.centerx - bullet.exact_x, boss.rect.centery - bullet.exact_y))

    def take_damage(self, amount, hit_rect=None):
        if not self.active:
            return

        targets = [boss for boss in self.bosses if boss.active]
        if hit_rect is not None:
            targets = [boss for boss in targets if boss.rect.colliderect(hit_rect)]

        if not targets:
            return

        target_boss = targets[0]
        target_boss.take_damage(amount)

        self.health = sum(max(boss.health, 0) for boss in self.bosses)
        self._refresh_bounds()

    def is_cleared(self):
        return not any(boss.active for boss in self.bosses)

    def update(self, current_time, enemy_bullet_pool):
        if not self.active:
            return

        if self.spawn_time is None:
            self.spawn_time = current_time

        if not self._timers_synced:
            self._sync_timers(self.spawn_time)

        for boss in self.bosses:
            boss.update(current_time, enemy_bullet_pool)

        self.health = sum(max(boss.health, 0) for boss in self.bosses)
        self._refresh_bounds()

    def draw(self, surface):
        if not self.active:
            return

        # boss giữa vẽ trước để hai boss bên nhìn như đứng phía trước
        self.center_boss.draw(surface)
        self.left_boss.draw(surface)
        self.right_boss.draw(surface)


class ExplodeBulletBoss(BaseBoss):
    def __init__(self):
        super().__init__(WIDTH // 2 - 46, -100, 92, 92, 1800, (190, 255, 120), "Explode Bullet Boss", target_y=110, speed=2, shoot_delay=620, entry_delay=1000, sprite_image=BOSS_VISUALS["explode"])

    def shoot(self, enemy_bullet_pool):
        """bắn 6 đạn trung bình có timer nổ"""
        num_bullets = 8
        base_speed = 2.8

        for i in range(num_bullets):
            angle = math.tau * i / num_bullets
            speed = base_speed + random.uniform(-0.25, 0.25)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed

            enemy_bullet_pool.get_bullet(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                0,
                size=18,
                damage=1,
                explosive=True,
                bullet_kind="explode_main",
                explode_after=1500,
                child_count=8,
                child_size=10,
                child_speed=4.2,
                child_damage=1,
            )


class RandomPatternBoss(BaseBoss):
    def __init__(self, x, y, width, height, health, color, name, target_y=100, speed=2, shoot_delay=260, entry_delay=1000, sprite_image=None, sprite_frames=None):
        if sprite_image is None and sprite_frames is None:
            sprite_frames = ENEMY_FRAMES
        super().__init__(x, y, width, height, health, color, name, target_y=target_y, speed=speed, shoot_delay=shoot_delay, entry_delay=entry_delay, sprite_image=sprite_image, sprite_frames=sprite_frames)

    def shoot(self, enemy_bullet_pool):
        """bắn ngẫu nhiên theo nhiều hình khác nhau"""
        pattern = random.choice([
            self._shoot_circle,
            self._shoot_fan,
            self._shoot_cross,
            self._shoot_squiggle,
            self._shoot_explode,
        ])
        pattern(enemy_bullet_pool)

    def _shoot_circle(self, enemy_bullet_pool):
        bullet_count = random.randint(10, 16)
        base_speed = random.uniform(2.6, 4.0)

        for index in range(bullet_count):
            angle = math.tau * index / bullet_count
            speed = base_speed + random.uniform(-0.25, 0.35)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            enemy_bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, dx, dy, 0, size=random.randint(10, 16), damage=1)

    def _shoot_fan(self, enemy_bullet_pool):
        bullet_count = random.randint(5, 9)
        spread_deg = random.uniform(50.0, 95.0)
        base_angle = math.pi / 2 + random.uniform(-0.5, 0.5)
        base_speed = random.uniform(3.0, 5.0)

        for index in range(bullet_count):
            if bullet_count == 1:
                offset = 0.0
            else:
                t = index / (bullet_count - 1)
                offset = math.radians(-spread_deg / 2 + spread_deg * t)

            angle = base_angle + offset
            speed = base_speed + random.uniform(-0.4, 0.6)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            enemy_bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, dx, dy, 0, size=random.randint(10, 15), damage=1)

    def _shoot_cross(self, enemy_bullet_pool):
        angles = [0, 45, 90, 135, 180, 225, 270, 315]
        speed = random.uniform(2.6, 4.2)

        for angle_deg in angles:
            angle = math.radians(angle_deg)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            enemy_bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, dx, dy, 0, size=random.randint(12, 18), damage=1)

    def _shoot_squiggle(self, enemy_bullet_pool):
        for _ in range(random.randint(5, 7)):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(3.0, 4.6)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            enemy_bullet_pool.get_bullet(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                0,
                size=random.randint(12, 16),
                squiggle=True,
                wobble_amplitude=random.uniform(4.0, 9.0),
                wobble_frequency=random.uniform(0.10, 0.20),
                wobble_phase=random.uniform(0.0, math.tau),
            )

    def _shoot_explode(self, enemy_bullet_pool):
        bullet_count = random.randint(6, 8)
        base_speed = random.uniform(2.4, 3.2)

        for index in range(bullet_count):
            angle = math.tau * index / bullet_count
            speed = base_speed + random.uniform(-0.2, 0.2)
            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            enemy_bullet_pool.get_bullet(
                self.rect.centerx,
                self.rect.centery,
                dx,
                dy,
                0,
                size=random.randint(14, 18),
                damage=1,
                explosive=True,
                bullet_kind="explode_main",
                explode_after=random.randint(900, 1500),
                child_count=8,
                child_size=8,
                child_speed=4.0,
                child_damage=1,
            )

class BossRush:
    def __init__(self, bosses):
        """quản lý danh sách boss theo thứ tự boss rush"""
        self.bosses = bosses
        self.current_index = 0

    def current_boss(self):
        if self.current_index >= len(self.bosses):
            return None
        return self.bosses[self.current_index]

    def has_next_boss(self):
        return self.current_index < len(self.bosses) - 1

    def advance_to_next_boss(self, current_time):
        if not self.has_next_boss():
            return

        self.current_index += 1
        boss = self.current_boss()
        if boss is not None:
            boss.spawn_time = current_time
            boss.ready = False
            boss.last_shot_time = 0

    def update(self, current_time, enemy_bullet_pool):
        boss = self.current_boss()
        if boss is None:
            return

        boss.update(current_time, enemy_bullet_pool)

    def draw(self, surface):
        boss = self.current_boss()
        if boss is not None:
            boss.draw(surface)

    def is_cleared(self):
        return self.current_index >= len(self.bosses)

# ==========================================
# phần 3: game loop
# ==========================================
def main():
    """vòng lặp chính của game"""
    global BACKGROUND_OFFSET
    player = Player()
    boss_rush = BossRush([
        CircleShotBoss(),
        FanBounceBoss(),
        OrbitCircleBoss(),
        TripleSquiggleBossStage(),
        ExplodeBulletBoss(),
        RandomPatternBoss(WIDTH // 2 - 48, -100, 96, 96, 1400, (255, 110, 180), "Chaos Boss A", target_y=95, speed=2, shoot_delay=280, entry_delay=1000, sprite_frames=ENEMY_FRAMES),
        RandomPatternBoss(WIDTH // 2 - 42, -100, 84, 84, 1500, (110, 255, 190), "Chaos Boss B", target_y=110, speed=2, shoot_delay=250, entry_delay=1000, sprite_image=load_image("Red", "spaceship_enemy_red.png")),
        RandomPatternBoss(WIDTH // 2 - 50, -100, 100, 100, 1650, (120, 170, 255), "Chaos Boss C", target_y=100, speed=3, shoot_delay=220, entry_delay=1000, sprite_image=load_image("Red", "Communicationship2.png")),
        RandomPatternBoss(WIDTH // 2 - 44, -100, 88, 88, 1750, (255, 200, 90), "Chaos Boss D", target_y=120, speed=2, shoot_delay=200, entry_delay=1000, sprite_image=load_image("Red", "small_ships.png")),
        RandomPatternBoss(WIDTH // 2 - 52, -100, 104, 104, 1900, (210, 120, 255), "Chaos Boss E", target_y=105, speed=2, shoot_delay=180, entry_delay=1000, sprite_image=load_image("Red", "alienship_new_red_try.png")),
    ])
    # pool đạn của player
    bullet_pool = BulletPool(100) 
    # pool đạn của boss
    enemy_bullet_pool = EnemyBulletPool(300)

    running = True
    game_state = "menu" # trạng thái hiện tại
    selected_ammo = None
    fire_mode_choices = []
    damage_bonus = 0
    last_shot_time = 0
    shoot_delay = 100 # thời gian giữa 2 phát

    ammo_configs = {
        1: {
            "name": "Dan thang (damage cao)",
            "damage": 15,
            "homing": False,
            "fan_angles": [0],
        },
        2: {
            "name": "Dan tim duong (damage thap)",
            "damage": 50,
            "homing": True,
            "fan_angles": [0],
        },
        3: {
            "name": "Dan quat (damage trung binh)",
            "damage": 10,
            "homing": False,
            "fan_angles": [-20, 0, 20],
        },
    }

    def build_fire_mode_choices(current_ammo):
        """trả về 2 lựa chọn đổi mode khác với mode hiện tại"""
        return [ammo_id for ammo_id in (1, 2, 3) if ammo_id != current_ammo]

    def fire_mode_label(ammo_id):
        return ammo_configs[ammo_id]["name"]

    def draw_boss_position_marker(surface, x_position, y_position):
        """vẽ tam giác đánh dấu vị trí đứng dưới boss"""
        triangle_surface = pygame.Surface((28, 28), pygame.SRCALPHA)
        triangle_points = [
            (14, 2),
            (2, 24),
            (26, 24),
        ]
        pygame.draw.polygon(triangle_surface, (255, 255, 0, 90), triangle_points)
        surface.blit(triangle_surface, (x_position - 14, y_position - 14))

    font_large = load_nulshock_font(56)
    font_small = load_nulshock_font(28)

    while running:
        current_time = pygame.time.get_ticks()

        # đọc sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game_state == "menu":
                    if event.key in (pygame.K_1, pygame.K_KP1):
                        selected_ammo = 1
                        game_state = "playing"
                    elif event.key in (pygame.K_2, pygame.K_KP2):
                        selected_ammo = 2
                        game_state = "playing"
                    elif event.key in (pygame.K_3, pygame.K_KP3):
                        selected_ammo = 3
                        game_state = "playing"
                    elif event.key == pygame.K_q:
                        running = False
                elif game_state == "upgrade_fire_mode":
                    if event.key == pygame.K_1:
                        selected_ammo = fire_mode_choices[0]
                        boss_rush.advance_to_next_boss(current_time)
                        enemy_bullet_pool.clear()
                        bullet_pool.clear()
                        game_state = "playing"
                    elif event.key == pygame.K_2:
                        selected_ammo = fire_mode_choices[1]
                        boss_rush.advance_to_next_boss(current_time)
                        enemy_bullet_pool.clear()
                        bullet_pool.clear()
                        game_state = "playing"
                    elif event.key == pygame.K_q:
                        game_state = "upgrade"
                elif game_state == "upgrade":
                    if event.key == pygame.K_1:
                        player.lives += 1
                        boss_rush.advance_to_next_boss(current_time)
                        enemy_bullet_pool.clear()
                        bullet_pool.clear()
                        game_state = "playing"
                    elif event.key == pygame.K_2:
                        fire_mode_choices = build_fire_mode_choices(selected_ammo)
                        game_state = "upgrade_fire_mode"
                    elif event.key == pygame.K_3:
                        damage_bonus += 3
                        boss_rush.advance_to_next_boss(current_time)
                        enemy_bullet_pool.clear()
                        bullet_pool.clear()
                        game_state = "playing"
                    elif event.key == pygame.K_q:
                        running = False
                elif game_state != "playing":
                    if event.key == pygame.K_r: # bấm r để chơi lại
                        return main()
                    elif event.key == pygame.K_q: # bấm q để thoát
                        running = False

        if game_state == "playing":
            BACKGROUND_OFFSET += BACKGROUND_SCROLL_SPEED

            # cập nhật
            keys = pygame.key.get_pressed()
            player.move(keys)
            boss_rush.update(current_time, enemy_bullet_pool)

            current_boss = boss_rush.current_boss()

            # giữ z để  bắn
            if keys[pygame.K_z]:
                if current_time - last_shot_time > shoot_delay:
                    ammo = ammo_configs[selected_ammo]

                    # nòng súng là mép trên player
                    for angle_deg in ammo["fan_angles"]:
                        angle = math.radians(angle_deg)
                        dx = math.sin(angle) * 15
                        dy = -math.cos(angle) * 15
                        bullet_pool.get_bullet(
                            player.rect.centerx,
                            player.rect.top,
                            dx=dx,
                            dy=dy,
                            homing=ammo["homing"],
                            damage=ammo["damage"] + damage_bonus,
                        )
                    last_shot_time = current_time

            bullet_pool.update(current_boss)
            enemy_bullet_pool.update(current_time)

            player_bullet_tree = Quadtree(pygame.Rect(0, 0, WIDTH, HEIGHT))
            for bullet in bullet_pool.active_bullets:
                if bullet.active:
                    player_bullet_tree.insert(bullet)

            enemy_bullet_tree = Quadtree(pygame.Rect(0, 0, WIDTH, HEIGHT))
            for bullet in enemy_bullet_pool.active_bullets:
                if bullet.active:
                    enemy_bullet_tree.insert(bullet)

            # đạn người chơi phá đạn boss trước khi đạn boss kịp chạm người chơi
            for player_bullet in bullet_pool.active_bullets:
                if not player_bullet.active:
                    continue

                for enemy_bullet in enemy_bullet_tree.query(player_bullet.rect):
                    if enemy_bullet.active and enemy_bullet.bullet_kind == "explode_main" and player_bullet.rect.colliderect(enemy_bullet.rect):
                        player_bullet.active = False
                        enemy_bullet.active = False
                        break

            # đạn player trúng boss hiện tại
            if current_boss is not None and current_boss.active:
                boss_hitboxes = current_boss.collision_rects() if hasattr(current_boss, "collision_rects") else [current_boss.rect]
                for bullet in player_bullet_tree.query(current_boss.rect):
                    if not bullet.active:
                        continue

                    hit_rect = None
                    for boss_rect in boss_hitboxes:
                        if bullet.rect.colliderect(boss_rect):
                            hit_rect = boss_rect
                            break

                    if hit_rect is not None:
                        bullet.active = False
                        current_boss.take_damage(bullet.damage, hit_rect)
                        if current_boss.is_cleared():
                            if boss_rush.has_next_boss():
                                game_state = "upgrade"
                                enemy_bullet_pool.clear()
                                bullet_pool.clear()
                            else:
                                game_state = "win"
                            current_boss = boss_rush.current_boss()
                            break

            # đạn boss hoặc boss chạm player
            if current_time > player.invulnerable_until:
                hit = False
                boss_hitboxes = current_boss.collision_rects() if current_boss is not None and hasattr(current_boss, "collision_rects") else ([current_boss.rect] if current_boss is not None else [])
                # trúng đạn boss
                for bullet in enemy_bullet_tree.query(player.rect):
                    if bullet.active and bullet.rect.colliderect(player.rect):
                        bullet.active = False
                        hit = True
                        break
                
                # chạm boss
                if not hit and current_boss is not None and current_boss.active:
                    for boss_rect in boss_hitboxes:
                        if player.rect.colliderect(boss_rect):
                            hit = True
                            break
                #nếu trúng đạn
                if hit:
                    player.lives -= 1
                    player.invulnerable_until = current_time + 2000 # miễn nhiễm tạm thời
                    if player.lives <= 0:
                        # hết mạng thì thua
                        game_state = "lose"

        # vẽ frame mới
        draw_scrolling_background(screen, BACKGROUND_OFFSET if game_state == "playing" else 0)

        if game_state != "playing":
            shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            shade.fill((0, 0, 0, 115))
            screen.blit(shade, (0, 0))

        if game_state == "menu":
            title_text = font_large.render("BOSS RUSH", True, RED)
            title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 140))
            screen.blit(title_text, title_rect)

            draw_text_with_icon(screen, GUN_TYPE_ICONS[1], "Press 1 : Machine gun", font_small, WIDTH//2, HEIGHT//2 - 30, color=(255, 255, 255), icon_size=(28, 28), align="center")
            draw_text_with_icon(screen, GUN_TYPE_ICONS[2], "Press 2 : Homing missles", font_small, WIDTH//2, HEIGHT//2 + 20, color=(255, 255, 255), icon_size=(28, 28), align="center")
            draw_text_with_icon(screen, GUN_TYPE_ICONS[3], "Press 3 : Spraying", font_small, WIDTH//2, HEIGHT//2 + 70, color=(255, 255, 255), icon_size=(28, 28), align="center")
            menu_q = font_small.render("Press Q to quit", True, (180, 180, 180))
            screen.blit(menu_q, menu_q.get_rect(center=(WIDTH//2, HEIGHT//2 + 130)))

        elif game_state == "playing":
            boss_rush.draw(screen)
            current_boss = boss_rush.current_boss()
            if current_boss is not None:
                marker_y = HEIGHT - 10
                if isinstance(current_boss, TripleSquiggleBossStage):
                    for boss in current_boss.bosses:
                        if boss.active:
                            marker_x = max(15, min(WIDTH - 15, boss.rect.centerx))
                            draw_boss_position_marker(screen, marker_x, marker_y)
                else:
                    marker_x = max(15, min(WIDTH - 15, current_boss.rect.centerx))
                    draw_boss_position_marker(screen, marker_x, marker_y)

            player.draw(screen, current_time)
            bullet_pool.draw(screen)
            enemy_bullet_pool.draw(screen)

            # hiện số mạng
            lives_text = font_small.render(f"Lives: {player.lives}", True, (255, 255, 255))
            screen.blit(lives_text, (10, 10))

            draw_text_with_icon(screen, GUN_TYPE_ICONS[selected_ammo], "Ammo:", font_small, 10, 45, color=(255, 255, 255), icon_size=(22, 22), align="left", icon_after=True)

            if current_boss is not None:
                draw_text_with_icon(
                    screen,
                    boss_stage_icon(boss_rush.current_index),
                    f"Boss: {boss_rush.current_index + 1}/{len(boss_rush.bosses)}",
                    font_small,
                    10,
                    80,
                    color=(255, 255, 255),
                    icon_size=(22, 22),
                    align="left",
                    icon_after=True,
                )

            damage_text = font_small.render(f"Damage Bonus: +{damage_bonus}", True, (255, 255, 255))
            screen.blit(damage_text, (10, 115))

        elif game_state == "upgrade":
            title_text = font_large.render("UPGRADE", True, YELLOW)
            title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 140))
            screen.blit(title_text, title_rect)

            draw_text_with_icon(screen, UPGRADE_OPTION_ICONS[1], "1: +1 Life", font_small, WIDTH//2, HEIGHT//2 - 30, color=(255, 255, 255), icon_size=(28, 28), align="center")
            draw_text_with_icon(screen, UPGRADE_OPTION_ICONS[2], "2: Switch Fire Mode", font_small, WIDTH//2, HEIGHT//2 + 20, color=(255, 255, 255), icon_size=(28, 28), align="center")
            draw_text_with_icon(screen, UPGRADE_OPTION_ICONS[3], "3: +Damage (Stack)", font_small, WIDTH//2, HEIGHT//2 + 70, color=(255, 255, 255), icon_size=(28, 28), align="center")
            line_4 = font_small.render(f"Current Damage Bonus: +{damage_bonus}", True, (200, 200, 200))
            line_5 = font_small.render("Press Q to Quit", True, (180, 180, 180))

            screen.blit(line_4, line_4.get_rect(center=(WIDTH//2, HEIGHT//2 + 120)))
            screen.blit(line_5, line_5.get_rect(center=(WIDTH//2, HEIGHT//2 + 170)))

        elif game_state == "upgrade_fire_mode":
            title_text = font_large.render("SELECT FIRE MODE", True, YELLOW)
            title_rect = title_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 140))
            screen.blit(title_text, title_rect)

            draw_text_with_icon(screen, GUN_TYPE_ICONS[fire_mode_choices[0]], "1:", font_small, WIDTH//2, HEIGHT//2 - 10, color=(255, 255, 255), icon_size=(28, 28), align="center", icon_after=True)
            draw_text_with_icon(screen, GUN_TYPE_ICONS[fire_mode_choices[1]], "2:", font_small, WIDTH//2, HEIGHT//2 + 40, color=(255, 255, 255), icon_size=(28, 28), align="center", icon_after=True)
            line_3 = font_small.render("Q: Back", True, (180, 180, 180))

            screen.blit(line_3, line_3.get_rect(center=(WIDTH//2, HEIGHT//2 + 110)))
        
        elif game_state == "win":
            # màn hình thắng
            win_text = font_large.render("YOU WIN!", True, GREEN)
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(win_text, win_rect)

            prompt_text_1 = font_small.render("Press R to Restart", True, (255, 255, 255))
            prompt_text_2 = font_small.render("or Q to Quit", True, (255, 255, 255))
            screen.blit(prompt_text_1, prompt_text_1.get_rect(center=(WIDTH//2, HEIGHT//2 + 15)))
            screen.blit(prompt_text_2, prompt_text_2.get_rect(center=(WIDTH//2, HEIGHT//2 + 55)))

        elif game_state == "lose":
            # màn hình thua
            lose_text = font_large.render("GAME OVER", True, RED)
            lose_rect = lose_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(lose_text, lose_rect)

            prompt_text_1 = font_small.render("Press R to Restart", True, (255, 255, 255))
            prompt_text_2 = font_small.render("or Q to Quit", True, (255, 255, 255))
            screen.blit(prompt_text_1, prompt_text_1.get_rect(center=(WIDTH//2, HEIGHT//2 + 15)))
            screen.blit(prompt_text_2, prompt_text_2.get_rect(center=(WIDTH//2, HEIGHT//2 + 55)))

        pygame.display.flip() # đẩy frame ra màn hình
        clock.tick(FPS)       # giữ fps ổn định

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
