# 2025-2학기 알고리즘과게임컨텐츠 기말 프로젝트: 영웅의 식탁(게임)
# 제작: 놀고싶조 (9분반)
# 소스 코드: https://github.com/miles-tails-prower05/2025-2_Heros_Table

import pygame
import random
import os

# --- Pygame 초기 설정 ---
pygame.init()
pygame.font.init()
pygame.mixer.init()  # 오디오 초기화

# --- 배경음악 로드 및 재생 ---
bgm_path = os.path.join("src\sound", "bgm.mp3")
try:
    pygame.mixer.music.load(bgm_path)
    pygame.mixer.music.play(-1)  # 무한 반복
except Exception as e:
    print(f"배경음악 로딩 실패: {e}")


# --- 효과음 로드 ---
bite_sound_path = os.path.join("src\sound", "bite.mp3")
armor_sound_path = os.path.join("src\sound", "armor.mp3")
jump_sound_path = os.path.join("src\sound", "jump.mp3")

try:
    bite_sound = pygame.mixer.Sound(bite_sound_path)
except Exception as e:
    print(f"효과음 로딩 실패: {e}")
    bite_sound = None

try:
    armor_sound = pygame.mixer.Sound(armor_sound_path)
except Exception as e:
    print(f"효과음(armor) 로딩 실패: {e}")
    armor_sound = None

try:
    jump_sound = pygame.mixer.Sound(jump_sound_path)
except Exception as e:
    print(f"효과음(jump) 로딩 실패: {e}")
    jump_sound = None

# --- 게임 상수 정의 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- 색상 정의 ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (211, 47, 47)
GREEN = (56, 142, 60)
BLUE = (25, 118, 210)
YELLOW = (253, 216, 53)
GREY = (158, 158, 158)

# 영양소 게이지 색상 
CARB_COLOR = (245, 222, 179) # 탄수화물 (베이지)
PROTEIN_COLOR = (210, 105, 30) # 단백질 (브라운)
FAT_COLOR = (255, 255, 0)   # 지방 (노랑)

# --- 폰트 설정 ---
UI_FONT = pygame.font.SysFont('malgungothic', 24)
GAME_OVER_FONT = pygame.font.SysFont('malgungothic', 64)

# --- 음식 데이터 정의 ---
# 제안서의 표를 기반으로 함 
FOOD_DATA = [
    {"name": "밥 한 공기", "carbs": 20, "protein": 2, "fat": 2, "color": CARB_COLOR, "image": "rice.png"},
    {"name": "닭가슴살 스테이크", "carbs": 10, "protein": 20, "fat": 7, "color": PROTEIN_COLOR, "image": "chickenSteak.png"},
    {"name": "아보카도 샐러드", "carbs": 2, "protein": 10, "fat": 5, "color": GREEN, "image": "avocadoSalads.png"},
    {"name": "초콜릿 바", "carbs": 20, "protein": 5, "fat": 22, "color": FAT_COLOR, "image": "chocolate.png"},
    {"name": "삶은 달걀", "carbs": 0, "protein": 15, "fat": 15, "color": WHITE, "image": "egg.png"},
    {"name": "피자 한 조각", "carbs": 20, "protein": 10, "fat": 20, "color": RED, "image": "pizza.png"},
    {"name": "버터 한 조각", "carbs": 0, "protein": 0, "fat": 25, "color": FAT_COLOR, "image": "butter.png"},
    {"name": "단백질 쉐이크", "carbs": 5, "protein": 25, "fat": 5, "color": PROTEIN_COLOR, "image": "protainShake.png"},
]

# --- 플레이어 클래스 ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
         # 플레이어 캐릭터 이미지 적용
        image_path = os.path.join("src\image", "PC.png")
        try:
            loaded_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(loaded_image, (160, 100))
        except Exception:
            # 이미지가 없으면 임시 파란색 사각형 사용
            self.image = pygame.Surface((70, 100))
            self.image.fill(BLUE)
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        
        # 기본 스탯
        self.base_move_speed = 5
        self.base_jump_height = 16
        self.gravity = 0.8
        self.vel_x = 0
        self.vel_y = 0
        self.is_jumping = False
        self.on_ground = True

        # 영양소 속성 
        self.carbs = 100
        self.protein = 100
        self.fat = 100
        # 영양소 범위: 0 ~ 200 [cite: 13]

    def calculate_modifiers(self):
        """ 영양소 값에 따라 이동 속도와 점프 높이를 계산합니다.  """
        deficient_count = 0
        excess_count = 0
        
        nutrients = [self.carbs, self.protein, self.fat]
        
        for n in nutrients:
            if n < 50: # 부족한 영양소 [cite: 14]
                deficient_count += 1
            elif n > 150: # 과다한 영양소 [cite: 15]
                excess_count += 1
                
        # 25%p씩 증감
        speed_modifier = 1.0 + (excess_count * 0.25) - (deficient_count * 0.25)
        jump_modifier = 1.0 + (excess_count * 0.25) - (deficient_count * 0.25)
        
        # 0 이하로 떨어지지 않도록 보정
        self.current_move_speed = max(1, self.base_move_speed * speed_modifier)
        self.current_jump_height = max(1, self.base_jump_height * jump_modifier)

    def update(self):
        # 키 입력 처리 
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: # 'A' 키로 좌 
            self.vel_x = -self.current_move_speed
        elif keys[pygame.K_d]: # 'D' 키로 우 
            self.vel_x = self.current_move_speed
        else:
            self.vel_x = 0
            
        # 영양소 기반 스탯 업데이트
        self.calculate_modifiers()

        # 중력 적용
        self.vel_y += self.gravity
        
        # 이동
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # 화면 경계 처리
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # 바닥 경계 처리
        if self.rect.bottom >= SCREEN_HEIGHT - 20:
            self.rect.bottom = SCREEN_HEIGHT - 20
            self.vel_y = 0
            self.is_jumping = False
            self.on_ground = True

    def jump(self):
        # '스페이스 바'로 점프 
        if self.on_ground:
            self.is_jumping = True
            self.on_ground = False
            self.vel_y = -self.current_jump_height
            # 점프 효과음 재생
            if armor_sound:
                armor_sound.play()
            if jump_sound:
                jump_sound.play() 

    def add_nutrients(self, food):
        """ 음식의 영양소를 플레이어에게 더합니다.  """
        self.carbs += food.carbs
        self.protein += food.protein
        self.fat += food.fat
        # 0~200 범위 유지 [cite: 13]
        self.carbs = max(0, min(200, self.carbs))
        self.protein = max(0, min(200, self.protein))
        self.fat = max(0, min(200, self.fat))
        
        # 음식 먹는 효과음 재생
        if bite_sound:
            bite_sound.play()

    def decay_nutrients(self):
        """ 매 초마다 모든 영양소 1씩 감소  """
        self.carbs = max(0, self.carbs - 1)
        self.protein = max(0, self.protein - 1)
        self.fat = max(0, self.fat - 1)

    def check_game_over(self):
        """ 게임 오버 조건 확인  """
        nutrients = [self.carbs, self.protein, self.fat]
        if any(n <= 0 for n in nutrients) or any(n >= 200 for n in nutrients):
            return True
        return False

# --- 음식 클래스 ---
class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 떨어지는 음식 [cite: 7]
        food_type = random.choice(FOOD_DATA)
        
        self.name = food_type["name"]
        self.carbs = food_type["carbs"]
        self.protein = food_type["protein"]
        self.fat = food_type["fat"]
        
        # 이미지 폴더 경로
        image_folder = "src\image"
        image_path = os.path.join(image_folder, food_type["image"])
        try:
            loaded_image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(loaded_image, (50, 50))
        except Exception:
            # 이미지가 없으면 기존 방식(단색 사각형) 사용
            self.image = pygame.Surface((50, 50))
            self.image.fill(food_type["color"])
        
        # 무작위 x좌표, 동일한 y좌표(화면 상단)에서 생성 
        self.rect = self.image.get_rect(center=(random.randint(20, SCREEN_WIDTH - 20), -50))
        
        # 영양소 수치에 따라 떨어지는 속도 조절 [cite: 18, 19]
        base_speed = 3
        avg_nutrient = (self.carbs + self.protein + self.fat) / 3
        self.speed = base_speed + (avg_nutrient / 20) # 

    def update(self):
        self.rect.y += self.speed
        # 화면 밖으로 나가면 자동 삭제
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

# --- UI 그리기 함수 ---
def draw_ui(screen, player, score):
    # 영양소 게이지 그리기 
    # 탄수화물
    pygame.draw.rect(screen, GREY, (10, 10, 204, 30))
    pygame.draw.rect(screen, CARB_COLOR, (12, 12, player.carbs, 26)) # 1칸이 1
    carb_text = UI_FONT.render(f"탄수화물: {int(player.carbs)} / 200", True, BLACK)
    screen.blit(carb_text, (220, 10))
    
    # 단백질
    pygame.draw.rect(screen, GREY, (10, 50, 204, 30))
    pygame.draw.rect(screen, PROTEIN_COLOR, (12, 52, player.protein, 26))
    protein_text = UI_FONT.render(f"단백질: {int(player.protein)} / 200", True, BLACK)
    screen.blit(protein_text, (220, 50))
    
    # 지방
    pygame.draw.rect(screen, GREY, (10, 90, 204, 30))
    pygame.draw.rect(screen, FAT_COLOR, (12, 92, player.fat, 26))
    fat_text = UI_FONT.render(f"지방: {int(player.fat)} / 200", True, BLACK)
    screen.blit(fat_text, (220, 90))
    
    # 생존 시간 (점수)
    score_text = UI_FONT.render(f"생존 시간: {score:.1f} 초", True, BLACK)
    screen.blit(score_text, (SCREEN_WIDTH - 200, 10))

def draw_game_over(screen, score):
    text_surf = GAME_OVER_FONT.render("게임 오버!", True, RED)
    text_rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(text_surf, text_rect)
    
    score_surf = UI_FONT.render(f"생존 시간: {score:.1f} 초", True, BLACK)
    score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
    screen.blit(score_surf, score_rect)
    
    restart_surf = UI_FONT.render("", True, GREY)
    restart_rect = restart_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    screen.blit(restart_surf, restart_rect)

# --- 메인 게임 루프 ---
def main_game():
    # --- 프로그램 아이콘 설정 ---
    icon_path = os.path.join("src\image", "PC.png")
    try:
        icon_img = pygame.image.load(icon_path)
        pygame.display.set_icon(icon_img)
    except Exception as e:
        print(f"아이콘 이미지 로딩 실패: {e}")

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("영웅의 식탁") # [cite: 1]
    clock = pygame.time.Clock()

     # --- 배경 이미지 로드 ---
    background_path = os.path.join("src\image", "background.jpeg")
    try:
        background_img = pygame.image.load(background_path).convert()
        background_img = pygame.transform.scale(background_img, (SCREEN_WIDTH, SCREEN_HEIGHT+200))
    except Exception:
        background_img = None  # 이미지가 없으면 None

    # --- 게임 상태 변수 ---
    game_over = False
    running = True
    waiting_for_restart = False # 게임 오버 후 재시작 대기
    
    # --- 게임 루프 시작 ---
    while running:
        
        # 새 게임 시작 시 변수 초기화
        if not game_over:
            player = Player()
            all_sprites = pygame.sprite.Group()
            food_group = pygame.sprite.Group()
            all_sprites.add(player)
            
            start_time = pygame.time.get_ticks()
            
            # --- 커스텀 이벤트 설정 ---
            # 1초마다 영양소 감소 이벤트 
            DECAY_NUTRIENTS_EVENT = pygame.USEREVENT + 1
            pygame.time.set_timer(DECAY_NUTRIENTS_EVENT, 1000) 
            
            # 음식 생성 이벤트 
            SPAWN_FOOD_EVENT = pygame.USEREVENT + 2
            initial_spawn_interval = 2000 # 2초
            pygame.time.set_timer(SPAWN_FOOD_EVENT, initial_spawn_interval)
            
            game_over = False # 루프가 다시 돌 때를 대비
            waiting_for_restart = False
        
        # --- 내부 게임 루프 ---
        while not game_over and running:
            # 1. 이벤트 처리
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                # 키 입력 (점프)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE: # 
                        player.jump()
                        
                # 영양소 감소 이벤트
                if event.type == DECAY_NUTRIENTS_EVENT:
                    player.decay_nutrients()
                    
                # 음식 생성 이벤트
                if event.type == SPAWN_FOOD_EVENT:
                    new_food = Food()
                    all_sprites.add(new_food)
                    food_group.add(new_food)
                    
                    # 플레이 시간에 비례해 생성 빈도 증가 (간격 감소) 
                    elapsed_seconds = (pygame.time.get_ticks() - start_time) / 1000
                    # 1초마다 20ms씩 간격 감소, 최소 300ms
                    new_interval = max(300, initial_spawn_interval - int(elapsed_seconds * 20))
                    pygame.time.set_timer(SPAWN_FOOD_EVENT, new_interval)

            # 2. 게임 로직 업데이트
            all_sprites.update()
            
            # 충돌 감지 
            hits = pygame.sprite.spritecollide(player, food_group, True) # True: 충돌 시 음식 삭제
            for hit_food in hits:
                player.add_nutrients(hit_food)
                
            # 게임 오버 확인 
            if player.check_game_over():
                game_over = True
                waiting_for_restart = True
                
            # 생존 시간 계산
            survival_time = (pygame.time.get_ticks() - start_time) / 1000

            # 3. 렌더링 (그리기)
            if background_img:
                screen.blit(background_img, (0, 0))
            else:
                screen.fill(BLACK) # 이미지 없을 때 기본 배경
            
            # 바닥 그리기
            pygame.draw.rect(screen, GREY, (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20))
            
            all_sprites.draw(screen)
            draw_ui(screen, player, survival_time)
            
            pygame.display.flip()
            clock.tick(FPS)
            
        # --- 게임 오버 루프 ---
        while waiting_for_restart and running:
            draw_game_over(screen, survival_time)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN: # 아무 키나 누르면
                    waiting_for_restart = False # -> game_over가 True인 상태로 외부 루프 재시작

    pygame.quit()

if __name__ == "__main__":
    main_game()