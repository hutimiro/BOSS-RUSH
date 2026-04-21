

import pygame
import sys
import math
import random
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


#object pool

class Bullet:
    def __init__(self):
        """bullet của player"""
        self.rect = pygame.Rect(0, 0, 8, 16) # kích thước đạn
        self.active = False
        self.speed = 15 # speed dương cho dễ tính hướng
        self.exact_x = 0.0
        self.exact_y = 0.0
        self.dx = 0.0
        self.dy = -self.speed

    def fire(self, x, y):
        """bắn bullet từ x y"""
        # bật đạn 
        self.active = True
        self.rect.centerx = x
        self.rect.bottom = y
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.dx = 0.0
        self.dy = -self.speed

    def update(self, target=None):
        """cập nhật bullet và tự nhắm khi có target"""
        if self.active:
            # có boss thì bẻ hướng nhẹ
            if target and target.active:
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
            pygame.draw.rect(surface, RED, self.rect)

class BulletPool:
    def __init__(self, size):
        """hồ chứa giữ đạn rảnh và đạn đang bay"""
        # tạo sẵn đạn để đỡ tạo mới liên tục
        self.pool = deque([Bullet() for _ in range(size)])
        self.active_bullets = [] # đạn đang bay

    def get_bullet(self, x, y):
        """lấy đạn từ pool"""
        if self.pool:
            # còn đạn rảnh thì lấy ra dùng
            bullet = self.pool.popleft()
            bullet.fire(x, y)
            self.active_bullets.append(bullet)

    def update_and_draw(self, surface, target=None):
        """update và vẽ active_bullets"""
        for bullet in self.active_bullets[:]: # lặp bản sao để xóa an toàn
            bullet.update(target)
            bullet.draw(surface)
            
            # đạn tắt thì trả về  hồ
            if not bullet.active:
                # dọn khỏi danh sách đang bay
                self.active_bullets.remove(bullet)
                self.pool.append(bullet)

class EnemyBullet:
    def __init__(self):
        """đạn của boss"""
        self.rect = pygame.Rect(0, 0, 10, 10)
        self.active = False
        self.speed_x = 0
        self.speed_y = 0
        self.exact_x = 0.0
        self.exact_y = 0.0
        self.bounces_left = 0

    def fire(self, x, y, dx, dy, bounces=0):
        """bắn đạn boss """
        # lưu vận tốc để update mỗi frame
        self.active = True
        self.exact_x = float(x)
        self.exact_y = float(y)
        self.rect.centerx = x
        self.rect.centery = y
        self.speed_x = dx
        self.speed_y = dy
        self.bounces_left = bounces

    def update(self):
        """cập nhật đạn boss và nảy tường"""
        if self.active:
            self.exact_x += self.speed_x
            self.exact_y += self.speed_y
            self.rect.centerx = int(self.exact_x)
            self.rect.centery = int(self.exact_y)

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

                if bounced:
                    # mỗi lần chạm tường thì trừ một lần nảy
                    self.bounces_left -= 1
                    self.rect.centerx = int(self.exact_x)
                    self.rect.centery = int(self.exact_y)

            # bay quá xa thì thu hồi
            if not (-50 < self.rect.x < WIDTH + 50 and -50 < self.rect.y < HEIGHT + 50):
                self.active = False

    def draw(self, surface):
        """vẽ enemy bullet"""
        if self.active:
            color = (255, 165, 0) if self.bounces_left > 0 else YELLOW # cam khi còn nảy
            pygame.draw.circle(surface, color, self.rect.center, 5)

class EnemyBulletPool:
    def __init__(self, size):
        """hồ chứa đạn của boss"""
        self.pool = deque([EnemyBullet() for _ in range(size)])
        self.active_bullets = []

    def get_bullet(self, x, y, dx, dy, bounces=0):
        """lấy đạn boss từ hồ"""
        if self.pool:
            # boss bắn
            bullet = self.pool.popleft()
            bullet.fire(x, y, dx, dy, bounces)
            self.active_bullets.append(bullet)

    def update_and_draw(self, surface):
        """update và vẽ đạn của boss"""
        for bullet in self.active_bullets[:]:
            bullet.update()
            bullet.draw(surface)
            if not bullet.active:
                # trả lại hồ
                self.active_bullets.remove(bullet)
                self.pool.append(bullet)

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

        if self.is_focused:
            # giữ shift thì thu nhỏ hitbõ
            phantom_rect = self.rect.copy()
            phantom_rect.inflate_ip(0, 0)
            pygame.draw.rect(surface, (50, 75, 125), phantom_rect) 
            pygame.draw.rect(surface, BLUE, self.rect)
            pygame.draw.circle(surface, BLUE, self.rect.center, 4)
        else:
            pygame.draw.rect(surface, BLUE, self.rect)

class Boss:
    def __init__(self):
        """boss và thông tin máu"""
        self.rect = pygame.Rect(WIDTH//2 - 40, -100, 80, 80)
        self.target_y = 100
        self.speed = 2
        self.ready = False
        self.last_shot_time = 0
        self.shoot_delay = 200 # thời gian giữa 2 lượt bắn
        self.max_health = 1000
        self.health = self.max_health
        self.active = True
        self.shoot_angle_offset = 0 # góc lệch đạn

    def update(self, current_time, enemy_bullet_pool):
        """cập nhật boss và gọi bắn"""
        if not self.active:
            return
            
        # boss đi chuyển vào màng hình
        if self.rect.y < self.target_y:
            self.rect.y += self.speed
        else:
            self.ready = True

        # đủ nhịp thì bắn tiếp
        if self.ready and current_time - self.last_shot_time > self.shoot_delay:
            self.shoot(enemy_bullet_pool)
            self.last_shot_time = current_time

    def shoot(self, enemy_bullet_pool):
        """bắn vòng đạn xoay"""
        # mỗi lượt bắn một vòng đạn
        num_bullets = random.randint(15, 20)
        base_speed = random.uniform(3.0, 5.0)
        
        # tăng góc lệch để vòng sau khác vòng trước
        self.shoot_angle_offset += random.uniform(10.0, 25.0) 

        for i in range(num_bullets):
            # chia đều 360 độ cho cả vòng
            angle_deg = self.shoot_angle_offset + i * (360 / num_bullets)
            angle = math.radians(angle_deg)
            
            speed = base_speed + random.uniform(-1.0, 1.0)

            dx = math.cos(angle) * speed
            dy = math.sin(angle) * speed
            
            bounces = 0
            if random.random() < 0.10: # random đạn nảy
                bounces = random.randint(1, 2)

            enemy_bullet_pool.get_bullet(self.rect.centerx, self.rect.centery, dx, dy, bounces)

    def draw(self, surface):
        """vẽ boss và vòng máu"""
        if not self.active:
            return
            
        pygame.draw.rect(surface, GREEN, self.rect)
        
        # vẽ vòng máu quanh boss
        center = self.rect.center
        radius = 70
        pygame.draw.circle(surface, (50, 50, 50), center, radius, 5) # nền vòng máu
        
        if self.health > 0:
            health_ratio = self.health / self.max_health
            rect_for_arc = pygame.Rect(center[0] - radius, center[1] - radius, radius * 2, radius * 2)
            start_angle = math.pi / 2 # bắt đầu từ phía trên
            end_angle = start_angle + (2 * math.pi * health_ratio)
            pygame.draw.arc(surface, RED, rect_for_arc, start_angle, end_angle, 5)

# ==========================================
# phần 3: game loop
# ==========================================
def main():
    """vòng lặp chính của game"""
    player = Player()
    boss = Boss()
    # pool đạn của player
    bullet_pool = BulletPool(100) 
    # pool đạn của boss
    enemy_bullet_pool = EnemyBulletPool(300)

    running = True
    game_state = "playing" # trạng thái hiện tại
    last_shot_time = 0
    shoot_delay = 100 # thời gian giữa 2 phát

    font_large = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 36)

    while running:
        current_time = pygame.time.get_ticks()

        # đọc sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and game_state != "playing":
                if event.key == pygame.K_r: # bấm r để chơi lại
                    return main()
                elif event.key == pygame.K_q: # bấm q để thoát
                    running = False

        if game_state == "playing":
            # cập nhật
            keys = pygame.key.get_pressed()
            player.move(keys)
            boss.update(current_time, enemy_bullet_pool)
            
            # giữ z để  bắn
            if keys[pygame.K_z]:
                if current_time - last_shot_time > shoot_delay:
                    # nòng súng là mép trên player
                    bullet_pool.get_bullet(player.rect.centerx, player.rect.top)
                    last_shot_time = current_time

            # đạn player trúng boss
            if boss.active:
                for bullet in bullet_pool.active_bullets:
                    if bullet.active and bullet.rect.colliderect(boss.rect):
                        bullet.active = False
                        boss.health -= 15
                        if boss.health <= 0:
                            boss.health = 0
                            boss.active = False
                            # hết máu thì qua màn thắng
                            game_state = "win"
                            break

            # đạn boss hoặc boss chạm player
            if current_time > player.invulnerable_until:
                hit = False
                # trúng đạn boss
                for bullet in enemy_bullet_pool.active_bullets:
                    if bullet.active and bullet.rect.colliderect(player.rect):
                        bullet.active = False
                        hit = True
                        break
                
                # chạm boss
                if not hit and boss.active and player.rect.colliderect(boss.rect):
                    hit = True
                #nếu trúng đạn
                if hit:
                    player.lives -= 1
                    player.invulnerable_until = current_time + 2000 # miễn nhiễm tạm thời
                    if player.lives <= 0:
                        # hết mạng thì thua
                        game_state = "lose"

        # vẽ frame mới
        screen.fill(BLACK)
        
        if game_state == "playing":
            boss.draw(screen)
            player.draw(screen, current_time)
            bullet_pool.update_and_draw(screen, boss)
            enemy_bullet_pool.update_and_draw(screen)

            # hiện số mạng
            lives_text = font_small.render(f"Lives: {player.lives}", True, (255, 255, 255))
            screen.blit(lives_text, (10, 10))
        
        elif game_state == "win":
            # màn hình thắng
            win_text = font_large.render("YOU WIN!", True, GREEN)
            win_rect = win_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(win_text, win_rect)

            prompt_text = font_small.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            screen.blit(prompt_text, prompt_rect)

        elif game_state == "lose":
            # màn hình thua
            lose_text = font_large.render("GAME OVER", True, RED)
            lose_rect = lose_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
            screen.blit(lose_text, lose_rect)

            prompt_text = font_small.render("Press R to Restart or Q to Quit", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 20))
            screen.blit(prompt_text, prompt_rect)

        pygame.display.flip() # đẩy frame ra màn hình
        clock.tick(FPS)       # giữ fps ổn định

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
