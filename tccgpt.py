import pygame
import random
import math
import sys

# ============================================================
# CONFIGURAÇÕES E INICIALIZAÇÃO
# ============================================================
pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pokemon 3D Safari - Infinite Edition")
clock = pygame.time.Clock()

# Cores
COLOR_SKY = (120, 190, 245)
COLOR_GROUND = (60, 160, 75)
COLOR_BLACK = (15, 15, 15)
COLOR_WHITE = (245, 245, 245)
COLOR_PANEL = (20, 25, 30, 230)
COLOR_ACCENT = (255, 215, 0)
COLOR_HP = (46, 204, 113)
COLOR_HP_BG = (231, 76, 60)

# Fontes
FONT_TITLE = pygame.font.SysFont("Trebuchet MS", 26, bold=True)
FONT_BODY = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
FONT_SMALL = pygame.font.SysFont("Trebuchet MS", 13, bold=True)

# ============================================================
# CÂMERA E PROJEÇÃO 3D
# ============================================================
class Camera:
    def __init__(self):
        self.offset_y = 11.0
        self.offset_z = -15.0
        self.pos = pygame.math.Vector3(0, self.offset_y, self.offset_z)
        self.fov = 480.0

    def update(self, player_pos):
        self.pos.x = player_pos.x
        self.pos.y = player_pos.y + self.offset_y
        self.pos.z = player_pos.z + self.offset_z

    def project(self, world_pos):
        dx = world_pos.x - self.pos.x
        dy = world_pos.y - self.pos.y
        dz = world_pos.z - self.pos.z

        if dz <= 0.8:
            return None

        screen_x = int(WIDTH / 2 + (dx * self.fov) / dz)
        screen_y = int(HEIGHT / 2 - (dy * self.fov) / dz)
        scale = self.fov / dz

        return (screen_x, screen_y, dz, scale)

# ============================================================
# ENTIDADES DO JOGO
# ============================================================
class Pokemon:
    TYPES = [
        {"name": "Pikachu", "color": (255, 220, 40), "speed": 2.5, "points": 15, "catch_rate": 0.70, "max_hp": 50},
        {"name": "Bulbasaur", "color": (75, 180, 120), "speed": 1.5, "points": 18, "catch_rate": 0.65, "max_hp": 60},
        {"name": "Charmander", "color": (250, 110, 40), "speed": 2.0, "points": 25, "catch_rate": 0.50, "max_hp": 55},
        {"name": "Squirtle", "color": (60, 170, 240), "speed": 1.5, "points": 30, "catch_rate": 0.55, "max_hp": 65},
        {"name": "Eevee", "color": (160, 115, 80), "speed": 2.2, "points": 45, "catch_rate": 0.40, "max_hp": 70},
        {"name": "Mew", "color": (255, 130, 190), "speed": 3.5, "points": 120, "catch_rate": 0.15, "max_hp": 120}
    ]

    def __init__(self, spawn_center=pygame.math.Vector3(0,0,0)):
        info = random.choice(Pokemon.TYPES)
        self.name = info["name"]
        self.color = info["color"]
        self.speed = info["speed"]
        self.points = info["points"]
        self.catch_rate = info["catch_rate"]
        self.max_hp = info["max_hp"]
        self.hp = self.max_hp
        self.level = random.randint(1, 50)

        x = spawn_center.x + random.uniform(-40, 40)
        z = spawn_center.z + random.uniform(-40, 40)
        self.pos = pygame.math.Vector3(x, 0.5, z)

        angle = random.uniform(0, math.pi * 2)
        self.dir = pygame.math.Vector3(math.cos(angle), 0, math.sin(angle))
        self.walk_timer = random.uniform(1, 4)

    def update(self, dt):
        self.walk_timer -= dt
        if self.walk_timer <= 0:
            angle = random.uniform(0, math.pi * 2)
            self.dir = pygame.math.Vector3(math.cos(angle), 0, math.sin(angle))
            self.walk_timer = random.uniform(2, 5)

        self.pos += self.dir * self.speed * dt

class Player:
    def __init__(self):
        self.pos = pygame.math.Vector3(0.0, 0.0, 0.0)
        self.level = 1
        self.focus_upgrade = 0
        self.interaction_range = 8.5

    def level_up(self):
        self.level += 1
        self.interaction_range = 8.5 + (self.level * 0.5)

    def handle_input(self, dt):
        keys = pygame.key.get_pressed()
        speed = 16.0 if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) else 9.0

        move = pygame.math.Vector3(0, 0, 0)
        if keys[pygame.K_w] or keys[pygame.K_UP]: move.z += 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move.z -= 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move.x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x += 1

        if move.length_squared() > 0:
            move = move.normalize()
            self.pos += move * speed * dt

# ============================================================
# GERENCIADOR DO JOGO, MIRA E LOJA
# ============================================================
class SafariGame:
    def __init__(self):
        self.player = Player()
        self.camera = Camera()

        self.pokemons = [Pokemon(self.player.pos) for _ in range(25)]
        self.environment = self._generate_environment()

        self.state = "EXPLORE"
        self.score = 0
        self.coins = 50
        self.pokeballs = 15

        # Batalha e Mira
        self.battle_pokemon = None
        self.aim_timer = 0.0
        self.aim_speed = 3.0
        self.aim_x = WIDTH // 2

        self.ball_in_air = False
        self.ball_air_timer = 0.0
        self.ball_start_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT - 100)
        self.ball_target_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2)
        self.ball_current_pos = pygame.math.Vector2(self.ball_start_pos)

        self.poke_target_pos = pygame.math.Vector2(WIDTH // 2, HEIGHT // 2 + 20)

        self.message_text = ""
        self.message_timer = 0.0
        self.shop_rects = []

    def _generate_environment(self):
        objs = []
        for _ in range(120):
            x = random.uniform(-150, 150)
            z = random.uniform(-150, 150)
            if abs(x) > 4 or abs(z) > 4:
                objs.append({"type": "TREE", "pos": pygame.math.Vector3(x, 0, z), "h": random.uniform(3.5, 5.5)})

        colors = [(255, 235, 59), (255, 255, 255), (244, 67, 54), (180, 100, 220)]
        for _ in range(200):
            x = random.uniform(-150, 150)
            z = random.uniform(-150, 150)
            objs.append({"type": "FLOWER", "pos": pygame.math.Vector3(x, 0, z), "color": random.choice(colors)})
        return objs

    def show_message(self, text, duration=2.5):
        self.message_text = text
        self.message_timer = duration

    def check_emergency_pokeballs(self):
        """Mecânica de emergência: se o jogador ficar sem bolas e sem moedas, recebe ajuda."""
        if self.pokeballs <= 0 and self.coins < 20:
            self.pokeballs += 5
            self.show_message("O Prof. Oak te enviou +5 Pokébolas de emergência!", 3.5)

    def buy_item(self, item_num):
        if item_num == 1:
            cost = 20
            if self.coins >= cost:
                self.coins -= cost
                self.pokeballs += 5
                self.show_message("+5 Pokébolas Compradas!")
            else:
                self.show_message("Moedas insuficientes!")

        elif item_num == 2:
            cost = (self.player.focus_upgrade + 1) * 45
            if self.coins >= cost:
                self.coins -= cost
                self.player.focus_upgrade += 1
                self.show_message("Precisão Aumentada! Mira mais lenta.")
            else:
                self.show_message("Moedas insuficientes!")

    def start_battle(self, pokemon):
        if self.pokeballs <= 0:
            self.check_emergency_pokeballs()
            if self.pokeballs <= 0:
                self.show_message("SEM POKÉBOLAS! Compre na Loja [M].")
                return

        self.battle_pokemon = pokemon
        self.state = "BATTLE"

        level_diff = self.battle_pokemon.level - self.player.level
        base_speed = 3.0 - (self.player.focus_upgrade * 0.4)
        
        self.aim_speed = max(1.0, min(12.0, base_speed + (level_diff * 0.22)))
        self.reset_aim()

    def reset_aim(self):
        self.ball_in_air = False
        self.ball_air_timer = 0.0
        self.ball_current_pos = pygame.math.Vector2(self.ball_start_pos)

    def shoot_pokeball(self):
        if self.ball_in_air or self.pokeballs <= 0:
            return

        self.pokeballs -= 1
        self.ball_in_air = True
        self.ball_air_timer = 0.0
        self.ball_target_pos = pygame.math.Vector2(self.aim_x, self.poke_target_pos.y)

    def resolve_catch_attempt(self):
        dist = abs(self.ball_target_pos.x - (WIDTH // 2))

        if dist <= 25:
            accuracy_bonus = 0.35 if dist <= 10 else 0.20
            damage = random.randint(25, 45)

            self.battle_pokemon.hp = max(0, self.battle_pokemon.hp - damage)
            hp_factor = 1.0 - (self.battle_pokemon.hp / self.battle_pokemon.max_hp)
            final_chance = self.battle_pokemon.catch_rate + (hp_factor * 0.35) + accuracy_bonus

            if random.random() < final_chance or self.battle_pokemon.hp <= 0:
                self.score += 1
                self.player.level_up()
                earned_coins = self.battle_pokemon.points + (self.battle_pokemon.level * 2)
                
                # Recompensa extra: +2 Pokébolas bônus ao capturar
                bonus_balls = 2
                self.coins += earned_coins
                self.pokeballs += bonus_balls
                
                self.show_message(f"Capturado {self.battle_pokemon.name}! (+{earned_coins} Moedas, +{bonus_balls} Bolas)")

                if self.battle_pokemon in self.pokemons:
                    self.pokemons.remove(self.battle_pokemon)
                self.pokemons.append(Pokemon(self.player.pos))
                self.state = "EXPLORE"
            else:
                self.show_message(f"Escapou! HP: {self.battle_pokemon.hp}/{self.battle_pokemon.max_hp}")
                self.reset_aim()
                self.check_emergency_pokeballs()
        else:
            self.show_message("Você errou o lançamento!")
            self.reset_aim()
            self.check_emergency_pokeballs()

    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= dt

        if self.state == "EXPLORE":
            self.player.handle_input(dt)
            for poke in self.pokemons:
                poke.update(dt)
                if (poke.pos - self.player.pos).length() > 80:
                    poke.pos.x = self.player.pos.x + random.uniform(-40, 40)
                    poke.pos.z = self.player.pos.z + random.uniform(-40, 40)

            for obj in self.environment:
                if (obj["pos"] - self.player.pos).length() > 120:
                    obj["pos"].x = self.player.pos.x + random.uniform(-100, 100)
                    obj["pos"].z = self.player.pos.z + random.uniform(-100, 100)

            self.camera.update(self.player.pos)

        elif self.state == "BATTLE":
            if not self.ball_in_air:
                self.aim_timer += dt * self.aim_speed
                min_x = WIDTH * 0.2
                max_x = WIDTH * 0.8
                self.aim_x = min_x + (math.sin(self.aim_timer) + 1.0) / 2.0 * (max_x - min_x)
            else:
                self.ball_air_timer += dt * 2.2
                if self.ball_air_timer >= 1.0:
                    self.ball_air_timer = 1.0
                    self.resolve_catch_attempt()
                else:
                    self.ball_current_pos = self.ball_start_pos.lerp(self.ball_target_pos, self.ball_air_timer)
                    self.ball_current_pos.y -= math.sin(self.ball_air_timer * math.pi) * 120

    # ============================================================
    # DESENHO DE SPRITES E INTERFACE
    # ============================================================
    def draw_player(self, sx, sy, scale):
        size = max(8, int(22 * scale / 25))
        pygame.draw.ellipse(screen, (35, 95, 45), (sx - size, sy - 3, size * 2, size // 2))
        pygame.draw.rect(screen, (40, 90, 220), (sx - size//2, sy - size * 1.3, size, size))
        pygame.draw.circle(screen, (255, 205, 160), (sx, sy - size * 1.5), size // 2)
        pygame.draw.arc(screen, (220, 40, 40), (sx - size//1.8, sy - size * 2.1, size * 1.1, size), 0, math.pi, int(size//1.8))
        pygame.draw.rect(screen, COLOR_WHITE, (sx - size//3, sy - size * 1.7, size//1.5, size//4))

    def draw_pokemon_sprite(self, sx, sy, scale, poke):
        s = max(10, int(22 * scale / 25))
        pygame.draw.ellipse(screen, (35, 95, 45), (sx - s, sy - 2, s * 2, s // 2))

        if poke.name == "Pikachu":
            pygame.draw.ellipse(screen, poke.color, (sx - s, sy - s * 1.3, s * 2, s * 1.3))
            pygame.draw.polygon(screen, poke.color, [(sx - s//2, sy - s*1.2), (sx - s, sy - s*2.2), (sx - s//4, sy - s*1.4)])
            pygame.draw.polygon(screen, poke.color, [(sx + s//2, sy - s*1.2), (sx + s, sy - s*2.2), (sx + s//4, sy - s*1.4)])
            pygame.draw.circle(screen, (230, 40, 40), (sx - s//2, sy - s//1.8), max(1, s//4))
            pygame.draw.circle(screen, (230, 40, 40), (sx + s//2, sy - s//1.8), max(1, s//4))
        elif poke.name == "Charmander":
            pygame.draw.ellipse(screen, poke.color, (sx - s, sy - s * 1.3, s * 2, s * 1.3))
            pygame.draw.circle(screen, (255, 60, 0), (sx + s, sy - s//2), max(1, s//3))
            pygame.draw.circle(screen, (255, 200, 0), (sx + s, sy - s//2), max(1, s//6))
        elif poke.name == "Bulbasaur":
            pygame.draw.circle(screen, (40, 140, 70), (sx, sy - s*1.2), int(s*0.7))
            pygame.draw.ellipse(screen, poke.color, (sx - s, sy - s, s * 2, s))
        elif poke.name == "Squirtle":
            pygame.draw.circle(screen, (160, 90, 40), (sx, sy - s*0.7), int(s*0.9))
            pygame.draw.circle(screen, poke.color, (sx, sy - s*0.7), int(s*0.7))
        elif poke.name == "Mew":
            pygame.draw.circle(screen, poke.color, (sx, sy - s*0.8), s)
        else:
            pygame.draw.ellipse(screen, poke.color, (sx - s, sy - s * 1.2, s * 2, s * 1.2))

        pygame.draw.circle(screen, COLOR_BLACK, (sx - s//3, sy - s*0.7), max(1, s//6))
        pygame.draw.circle(screen, COLOR_BLACK, (sx + s//3, sy - s*0.7), max(1, s//6))

    def draw_pokeball_sprite(self, sx, sy, radius):
        pygame.draw.circle(screen, (230, 30, 30), (sx, sy), radius)
        pygame.draw.rect(screen, COLOR_WHITE, (sx - radius, sy, radius * 2, radius))
        pygame.draw.circle(screen, COLOR_WHITE, (sx, sy), radius, 2)
        pygame.draw.line(screen, COLOR_BLACK, (sx - radius, sy), (sx + radius, sy), 3)
        pygame.draw.circle(screen, COLOR_BLACK, (sx, sy), max(3, radius // 3))
        pygame.draw.circle(screen, COLOR_WHITE, (sx, sy), max(1, radius // 6))

    def draw_shop_screen(self):
        screen.fill((25, 30, 40))
        shop_rect = pygame.Rect(150, 80, 700, 540)
        pygame.draw.rect(screen, COLOR_PANEL, shop_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_ACCENT, shop_rect, 3, border_radius=15)

        title = FONT_TITLE.render("LOJA DE UPGRADES SAFARI", True, COLOR_ACCENT)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 110))

        coins_txt = FONT_BODY.render(f"Suas Moedas: {self.coins} 🪙  |  Nível do Jogador: Lv.{self.player.level}", True, COLOR_WHITE)
        screen.blit(coins_txt, (WIDTH//2 - coins_txt.get_width()//2, 160))

        ball_cost = 20
        focus_cost = (self.player.focus_upgrade + 1) * 45

        items = [
            (1, "[1 ou CLIQUE] COMPRAR POKÉBOLAS (+5 Bolas)", f"Custo: {ball_cost} Moedas", "Aumenta seu estoque total de Pokébolas."),
            (2, "[2 ou CLIQUE] MIRA DE PRECISÃO (Foco +1)", f"Custo: {focus_cost} Moedas", "Reduz permanentemente a velocidade da mira.")
        ]

        self.shop_rects = []
        start_y = 230
        mouse_pos = pygame.mouse.get_pos()

        for num, name, cost, desc in items:
            item_rect = pygame.Rect(180, start_y, 640, 95)
            self.shop_rects.append((item_rect, num))

            is_hover = item_rect.collidepoint(mouse_pos)
            bg_color = (45, 60, 75) if is_hover else (35, 45, 55)

            pygame.draw.rect(screen, bg_color, item_rect, border_radius=8)
            pygame.draw.rect(screen, COLOR_ACCENT if is_hover else (70, 85, 105), item_rect, 1, border_radius=8)

            t_name = FONT_BODY.render(name, True, COLOR_ACCENT)
            t_cost = FONT_BODY.render(cost, True, (46, 204, 113))
            t_desc = FONT_SMALL.render(desc, True, (200, 200, 200))

            screen.blit(t_name, (item_rect.x + 15, item_rect.y + 15))
            screen.blit(t_cost, (item_rect.x + 480, item_rect.y + 15))
            screen.blit(t_desc, (item_rect.x + 15, item_rect.y + 52))

            start_y += 120

        exit_txt = FONT_BODY.render("Pressione [M] ou [ESC] para Voltar ao Jogo", True, COLOR_WHITE)
        screen.blit(exit_txt, (WIDTH//2 - exit_txt.get_width()//2, 570))

    def draw_battle_screen(self):
        screen.fill((100, 180, 240))
        pygame.draw.ellipse(screen, (50, 150, 60), (WIDTH//2 - 300, HEIGHT//2 - 50, 600, 350))
        pygame.draw.ellipse(screen, (35, 110, 45), (WIDTH//2 - 220, HEIGHT//2, 440, 250))

        poke = self.battle_pokemon
        center_x, center_y = int(self.poke_target_pos.x), int(self.poke_target_pos.y)

        self.draw_pokemon_sprite(center_x, center_y, 75.0, poke)

        bar_y = HEIGHT - 140
        min_x = int(WIDTH * 0.2)
        max_x = int(WIDTH * 0.8)

        pygame.draw.rect(screen, (200, 50, 50), (min_x, bar_y - 8, max_x - min_x, 16), border_radius=8)
        pygame.draw.rect(screen, (46, 204, 113), (WIDTH//2 - 25, bar_y - 8, 50, 16), border_radius=4)

        aim_x_int = int(self.aim_x)
        pygame.draw.line(screen, COLOR_WHITE, (aim_x_int, center_y - 100), (aim_x_int, bar_y + 15), 2)
        pygame.draw.circle(screen, COLOR_ACCENT, (aim_x_int, bar_y), 12)
        pygame.draw.circle(screen, COLOR_BLACK, (aim_x_int, bar_y), 12, 2)

        ball_r = 22 if not self.ball_in_air else max(10, int(22 * (1.0 - self.ball_air_timer * 0.5)))
        self.draw_pokeball_sprite(int(self.ball_current_pos.x), int(self.ball_current_pos.y), ball_r)

        card_rect = pygame.Rect(WIDTH//2 - 160, 30, 320, 95)
        pygame.draw.rect(screen, COLOR_PANEL, card_rect, border_radius=10)
        pygame.draw.rect(screen, COLOR_ACCENT, card_rect, 2, border_radius=10)

        name_txt = FONT_BODY.render(f"{poke.name} (Lv.{poke.level})", True, COLOR_WHITE)
        screen.blit(name_txt, (card_rect.x + 15, card_rect.y + 8))

        hp_ratio = poke.hp / poke.max_hp
        pygame.draw.rect(screen, COLOR_HP_BG, (card_rect.x + 15, card_rect.y + 45, 290, 16), border_radius=4)
        pygame.draw.rect(screen, COLOR_HP, (card_rect.x + 15, card_rect.y + 45, int(290 * hp_ratio), 16), border_radius=4)

        hp_txt = FONT_SMALL.render(f"HP: {poke.hp} / {poke.max_hp}", True, COLOR_WHITE)
        screen.blit(hp_txt, (card_rect.x + 110, card_rect.y + 45))

        tip_txt = FONT_BODY.render("ACERTE A FAIXA VERDE PARA CAPTURAR!", True, COLOR_ACCENT)
        screen.blit(tip_txt, (WIDTH//2 - tip_txt.get_width()//2, HEIGHT - 50))

        ball_count = FONT_BODY.render(f"x{self.pokeballs}", True, COLOR_WHITE)
        screen.blit(ball_count, (WIDTH - 60, HEIGHT - 60))

    def draw(self):
        if self.state == "SHOP":
            self.draw_shop_screen()
        elif self.state == "BATTLE":
            self.draw_battle_screen()
        else:
            screen.fill(COLOR_SKY)
            horizon_y = HEIGHT // 3.2
            pygame.draw.rect(screen, COLOR_GROUND, (0, horizon_y, WIDTH, HEIGHT - horizon_y))

            render_queue = []
            proj = self.camera.project(self.player.pos)
            if proj: render_queue.append(("PLAYER", proj, self.player.pos))

            for poke in self.pokemons:
                proj = self.camera.project(poke.pos)
                if proj: render_queue.append(("POKEMON", proj, poke))

            for obj in self.environment:
                proj = self.camera.project(obj["pos"])
                if proj: render_queue.append(("ENV", proj, obj))

            render_queue.sort(key=lambda item: item[1][2], reverse=True)

            for item_type, proj, data in render_queue:
                sx, sy, dz, scale = proj
                if item_type == "PLAYER":
                    self.draw_player(sx, sy, scale)
                elif item_type == "POKEMON":
                    poke = data
                    self.draw_pokemon_sprite(sx, sy, scale, poke)
                    if (poke.pos - self.player.pos).length() < self.player.interaction_range:
                        lbl = FONT_SMALL.render(f"{poke.name} (Lv.{poke.level})", True, COLOR_WHITE)
                        screen.blit(lbl, (sx - lbl.get_width()//2, sy - int(35 * scale / 25)))
                elif item_type == "ENV":
                    obj = data
                    if obj["type"] == "TREE":
                        h = int(obj["h"] * scale / 18)
                        w = max(4, int(10 * scale / 22))
                        pygame.draw.rect(screen, (110, 70, 40), (sx - w//2, sy - h, w, h))
                        pygame.draw.circle(screen, (35, 115, 45), (sx, sy - h), int(w * 1.8))
                    elif obj["type"] == "FLOWER":
                        pygame.draw.circle(screen, obj["color"], (sx, sy), max(2, int(4 * scale / 25)))

            self._draw_hud()

        if self.message_timer > 0:
            msg_surface = FONT_TITLE.render(self.message_text, True, COLOR_ACCENT)
            rect = msg_surface.get_rect(center=(WIDTH // 2, 105 if self.state == "EXPLORE" else 150))
            bg_rect = rect.inflate(40, 14)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((15, 20, 25, 230))
            screen.blit(bg_surface, bg_rect.topleft)
            pygame.draw.rect(screen, COLOR_ACCENT, bg_rect, 2, border_radius=6)
            screen.blit(msg_surface, rect)

    def _draw_hud(self):
        hud_surface = pygame.Surface((WIDTH, 52), pygame.SRCALPHA)
        hud_surface.fill(COLOR_PANEL)
        screen.blit(hud_surface, (0, 0))
        pygame.draw.line(screen, COLOR_ACCENT, (0, 52), (WIDTH, 52), 2)

        txt_lvl = FONT_BODY.render(f"Jogador Lv.{self.player.level}", True, COLOR_WHITE)
        txt_pokeballs = FONT_BODY.render(f"Pokébolas: {self.pokeballs}", True, COLOR_WHITE)
        txt_score = FONT_BODY.render(f"Capturados: {self.score}", True, COLOR_WHITE)
        txt_coins = FONT_BODY.render(f"Moedas: {self.coins} 🪙", True, COLOR_ACCENT)

        screen.blit(txt_lvl, (20, 14))
        screen.blit(txt_pokeballs, (180, 14))
        screen.blit(txt_score, (360, 14))
        screen.blit(txt_coins, (540, 14))

        txt_controls = FONT_SMALL.render("[WASD] Mover  |  [ESPAÇO] Batalha  |  [M] Loja DE UPGRADES", True, COLOR_WHITE)
        screen.blit(txt_controls, (20, HEIGHT - 25))

    def run(self):
        running = True
        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.state == "SHOP":
                        pos = pygame.mouse.get_pos()
                        for rect, item_num in self.shop_rects:
                            if rect.collidepoint(pos):
                                self.buy_item(item_num)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state in ["BATTLE", "SHOP"]:
                            self.state = "EXPLORE"
                        else:
                            running = False

                    elif event.key == pygame.K_m:
                        if self.state == "EXPLORE":
                            self.state = "SHOP"
                        elif self.state == "SHOP":
                            self.state = "EXPLORE"

                    elif self.state == "SHOP":
                        if event.key in [pygame.K_1, pygame.K_KP1]:
                            self.buy_item(1)
                        elif event.key in [pygame.K_2, pygame.K_KP2]:
                            self.buy_item(2)

                    elif event.key == pygame.K_SPACE:
                        if self.state == "EXPLORE":
                            closest = None
                            closest_dist = float("inf")
                            for poke in self.pokemons:
                                d = (self.player.pos - poke.pos).length()
                                if d < closest_dist:
                                    closest_dist = d
                                    closest = poke

                            if closest and closest_dist <= self.player.interaction_range:
                                self.start_battle(closest)
                            else:
                                self.show_message("Chegue mais perto de um Pokémon!", 1.2)

                        elif self.state == "BATTLE":
                            self.shoot_pokeball()

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SafariGame()
    game.run()