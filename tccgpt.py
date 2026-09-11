# Importa a biblioteca principal do Pygame para criação de jogos
import pygame
# Importa o módulo random para gerar números aleatórios (usado em posições, spawns e chances)
import random
# Importa o módulo math para operações matemáticas (como seno, cosseno e distâncias)
import math
# Importa o módulo sys para interagir com o sistema, como fechar o programa corretamente
import sys
# Importa o módulo json para salvar e carregar os dados de progresso do jogador
import json
# Importa o módulo os para verificar a existência de arquivos no computador
import os

# Inicializa todos os módulos básicos necessários da biblioteca Pygame
pygame.init()
# Inicializa o mixer do Pygame para permitir a reprodução de sons e músicas
pygame.mixer.init()
# Inicializa o sistema de fontes do Pygame para desenhar textos na tela
pygame.font.init()

# Obtém as informações detalhadas da tela atual do monitor do usuário
infoObject = pygame.display.Info()
# Define a largura da tela com base na resolução atual do monitor
SCREEN_WIDTH = infoObject.current_w
# Define a altura da tela com base na resolução atual do monitor
SCREEN_HEIGHT = infoObject.current_h

# Define uma flag booleana indicando que o jogo começa em modo tela cheia
IS_FULLSCREEN = True
# Cria a janela principal do Pygame utilizando tela cheia e suporte a buffer duplo para melhor desempenho gráfico
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
# Define o título que aparece na barra superior da janela do jogo
pygame.display.set_caption("Pokémon Safari 3D - TCC Edition v4.0 Ultimate")
# Cria um relógio interno para controlar a taxa de quadros por segundo (FPS) do jogo
clock = pygame.time.Clock()

# Define a cor preta padrão utilizada em fundos e elementos de interface
COLOR_BLACK = (10, 10, 15)
# Define a cor branca padrão utilizada em textos e detalhes claros
COLOR_WHITE = (250, 250, 250)
# Define a cor de fundo dos painéis da interface com transparência (RGBA)
COLOR_PANEL = (15, 20, 28, 240)
# Define a cor de destaque (amarelo dourado) para títulos e itens importantes
COLOR_ACCENT = (255, 204, 0)
# Define a cor verde usada para representar a barra de vida (HP) dos Pokémon
COLOR_HP = (46, 204, 113)
# Define a cor vermelha usada para o fundo da barra de vida ou alertas
COLOR_HP_BG = (231, 76, 60)
# Define a cor amarela brilhante exclusiva para identificar Pokémon na versão Shiny
COLOR_SHINY = (255, 225, 60)
# Define a cor azul usada para representar a barra de experiência (XP) do jogador
COLOR_XP = (52, 152, 219)

# Dicionário contendo todas as configurações, custos e restrições de cada ilha do jogo
ISLAND_CONFIGS = {
    # Configurações detalhadas da primeira ilha do jogo
    1: {
        "name": "Ilha Inicial", "min_lvl": 1, "cost": 0, "min_poke_lvl": 1, "max_poke_lvl": 10,
        "sky_day": (135, 195, 235), "sky_night": (10, 15, 30),
        "ground_day": (45, 125, 55), "ground_night": (12, 30, 18),
        "env_type": "TREE", "rain": True, "fog_color": (150, 180, 200),
        "allowed_pokemons": ["Pikachu", "Bulbasaur", "Eevee"]
    },
    # Configurações detalhadas da segunda ilha do jogo
    2: {
        "name": "Ilha Tropical", "min_lvl": 10, "cost": 200, "min_poke_lvl": 11, "max_poke_lvl": 25,
        "sky_day": (80, 205, 255), "sky_night": (15, 25, 45),
        "ground_day": (220, 200, 120), "ground_night": (50, 45, 25),
        "env_type": "PALM", "rain": False, "fog_color": (180, 200, 220),
        "allowed_pokemons": ["Squirtle", "Psyduck", "Poliwag"]
    },
    # Configurações detalhadas da terceira ilha do jogo
    3: {
        "name": "Ilha Volcânica", "min_lvl": 25, "cost": 600, "min_poke_lvl": 26, "max_poke_lvl": 50,
        "sky_day": (220, 90, 40), "sky_night": (35, 8, 8),
        "ground_day": (55, 45, 45), "ground_night": (20, 10, 10),
        "env_type": "LAVA_ROCK", "rain": False, "fog_color": (120, 60, 40),
        "allowed_pokemons": ["Charmander", "Magmar", "Snorlax"]
    },
    # Configurações detalhadas da quarta ilha do jogo
    4: {
        "name": "Ilha Lendária", "min_lvl": 45, "cost": 1500, "min_poke_lvl": 51, "max_poke_lvl": 100,
        "sky_day": (110, 70, 175), "sky_night": (10, 3, 25),
        "ground_day": (65, 35, 85), "ground_night": (15, 8, 25),
        "env_type": "CRYSTAL", "rain": True, "fog_color": (100, 60, 140),
        "allowed_pokemons": ["Mew", "Dragonite", "Arcanine"]
    }
}

# Cria a fonte de texto em tamanho grande para títulos utilizando a fonte Trebuchet MS em negrito
FONT_TITLE = pygame.font.SysFont("Trebuchet MS", 28, bold=True)
# Cria a fonte de texto em tamanho médio para o corpo de menus e textos gerais
FONT_BODY = pygame.font.SysFont("Trebuchet MS", 18, bold=True)
# Cria a fonte de texto em tamanho pequeno para legendas e dicas na tela
FONT_SMALL = pygame.font.SysFont("Trebuchet MS", 13, bold=True)

# Função matemática para calcular a interpolação linear entre duas cores baseada em um fator t (0 a 1)
def lerp_color(c1, c2, t):
    # Garante que o valor de t fique estritamente preso entre 0.0 e 1.0
    t = max(0.0, min(1.0, t))
    # Retorna uma nova tupla RGB calculada proporcionalmente entre a cor c1 e a cor c2
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t)
    )

# Classe utilitária responsável por sintetizar e tocar efeitos sonoros proceduralmente
class SoundManager:
    # Decorador que define o método como estático, permitindo chamá-lo sem instanciar a classe
    @staticmethod
    def play_tone(freq=440, duration=0.1, volume=0.2):
        # Define a taxa de amostragem padrão de áudio em Hz
        sample_rate = 22050
        # Calcula o número total de amostras de áudio com base na duração desejada
        n_samples = int(sample_rate * duration)
        # Cria um buffer de bytes vazio para armazenar os dados de onda sonora
        buf = bytearray()
        # Loop para gerar cada amostra individual da onda senoidal
        for i in range(n_samples):
            # Calcula o tempo atual em segundos para a amostra corrente
            t = float(i) / sample_rate
            # Calcula o valor da onda senoidal mapeando para a escala de áudio de 8 bits (0 a 255)
            val = int(127 + 127 * math.sin(2 * math.pi * freq * t))
            # Adiciona o valor calculado ao buffer de bytes
            buf.append(val)
        # Tenta carregar e reproduzir o som gerado no mixer do Pygame de forma segura
        try:
            # Cria um objeto de som do Pygame utilizando diretamente os bytes do buffer
            snd = pygame.mixer.Sound(buffer=bytes(buf))
            # Define o volume de reprodução do som criado
            snd.set_volume(volume)
            # Executa a reprodução do som
            snd.play()
        # Captura qualquer exceção caso o sistema de áudio falhe ou esteja indisponível
        except Exception:
            pass

# Classe que gerencia partículas visuais individuais na tela (como brilhos e efeitos)
class Particle:
    # Método construtor que inicializa a posição, cor, velocidades e tempo de vida da partícula
    def __init__(self, x, y, color, vel_x=0, vel_y=0, lifetime=0.5):
        # Define a coordenada X inicial da partícula
        self.x = x
        # Define a coordenada Y inicial da partícula
        self.y = y
        # Define a cor RGB da partícula
        self.color = color
        # Define a velocidade horizontal, gerando um valor aleatório caso não seja informada
        self.vel_x = vel_x if vel_x != 0 else random.uniform(-2, 2)
        # Define a velocidade vertical, gerando um valor aleatório caso não seja informada
        self.vel_y = vel_y if vel_y != 0 else random.uniform(-2, 2)
        # Define o tempo de vida restante da partícula em segundos
        self.lifetime = lifetime
        # Armazena o tempo de vida máximo inicial para fins de cálculo de opacidade
        self.max_lifetime = lifetime

    # Atualiza a posição espacial e reduz o tempo de vida da partícula a cada quadro
    def update(self, dt):
        # Atualiza a coordenada X multiplicando a velocidade pelo delta tempo e fator de escala
        self.x += self.vel_x * dt * 50
        # Atualiza a coordenada Y multiplicando a velocidade pelo delta tempo e fator de escala
        self.y += self.vel_y * dt * 50
        # Decrementa o tempo de vida restante com base no tempo decorrido (dt)
        self.lifetime -= dt

    # Desenha a partícula na superfície gráfica caso ainda esteja ativa
    def draw(self, surface):
        # Verifica se o tempo de vida da partícula ainda é maior que zero
        if self.lifetime > 0:
            # Calcula a transparência (alfa) proporcional ao tempo de vida restante
            alpha = int((self.lifetime / self.max_lifetime) * 255)
            # Calcula o tamanho atual da partícula diminuindo gradualmente
            size = max(1, int((self.lifetime / self.max_lifetime) * 6))
            # Cria uma superfície temporária com suporte a transparência (SRCALPHA)
            p_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            # Desenha um círculo preenchido com a cor e canal alfa na superfície temporária
            pygame.draw.circle(p_surf, (*self.color, alpha), (size, size), size)
            # Copia a superfície da partícula para a tela principal na posição ajustada
            surface.blit(p_surf, (self.x - size, self.y - size))

# Classe que gerencia o sistema procedural de chuva na tela de exploração
class RainSystem:
    # Método construtor que define dimensões e propriedades iniciais de uma gota de chuva
    def __init__(self, width, height):
        # Armazena a largura máxima da tela para limites de posicionamento
        self.width = width
        # Armazena a altura máxima da tela
        self.height = height
        # Sorteia uma posição horizontal aleatória para a gota de chuva
        self.x = random.randint(0, width)
        # Sorteia uma posição vertical inicial acima da tela visível
        self.y = random.randint(-50, height)
        # Sorteia uma velocidade de queda aleatória para criar variação de perspectiva
        self.speed = random.uniform(700, 1100)
        # Sorteia o comprimento visual do traço da gota de chuva
        self.length = random.randint(15, 25)
        # Sorteia um fator de profundidade para simular distância (paralaxe)
        self.depth = random.uniform(0.5, 1.0)

    # Atualiza a posição da gota de chuva simulando queda e vento leve
    def update(self, dt):
        # Move a gota para baixo com base na velocidade, profundidade e delta tempo
        self.y += self.speed * self.depth * dt
        # Move a gota levemente para a esquerda simulando a ação do vento
        self.x -= self.speed * 0.2 * dt
        # Verifica se a gota ultrapassou o limite inferior da tela
        if self.y > self.height:
            # Reposiciona a gota aleatoriamente no topo da tela para continuar o ciclo
            self.y = random.randint(-50, -10)
            self.x = random.randint(0, self.width)

    # Desenha a linha correspondente à gota de chuva na superfície gráfica
    def draw(self, surface, night_factor):
        # Calcula a transparência da gota ajustando com base na profundidade e no ciclo de noite
        alpha = int(200 * self.depth * (1.0 - night_factor * 0.3))
        # Desenha uma linha diagonal na tela representando a gota de chuva em movimento rápido
        pygame.draw.line(surface, (200, 225, 255, alpha), (self.x, self.y), (self.x - 3, self.y + self.length * self.depth), max(1, int(2 * self.depth)))

# Classe responsável por simular uma câmera virtual tridimensional e projetar elementos no espaço 2D
class VirtualCamera3D:
    # Método construtor que define os offsets iniciais, campo de visão e resolução da câmera
    def __init__(self, width, height):
        # Define a altura base padrão do ponto de vista da câmera em relação ao mundo 3D
        self.base_offset_y = 11.0
        # Inicializa o deslocamento vertical atual com o valor base
        self.offset_y = self.base_offset_y
        # Define o deslocamento fixo no eixo Z (distância de afastamento da cena)
        self.offset_z = -15.0
        # Cria um vetor tridimensional representando a posição espacial da câmera
        self.pos = pygame.math.Vector3(0, self.offset_y, self.offset_z)
        # Define o fator de campo de visão (FOV) utilizado na projeção perspectiva
        self.fov = 540.0
        # Armazena a largura atual da tela
        self.w = width
        # Armazena a altura atual da tela
        self.h = height
        # Inicializa o temporizador usado para simular o balanço dos passos ao caminhar
        self.walk_timer = 0.0

    # Atualiza as dimensões da câmera caso ocorra redimensionamento de tela
    def resize(self, width, height):
        # Atualiza a largura armazenada
        self.w = width
        # Atualiza a altura armazenada
        self.h = height

    # Atualiza a posição da câmera com base na movimentação do jogador e simulação de passos
    def update(self, player_pos, is_moving, dt, is_running):
        # Verifica se o jogador está se movimentando no mapa
        if is_moving:
            # Define o multiplicador de velocidade do balanço baseado em se o jogador está correndo ou andando
            speed_mult = 14.0 if is_running else 9.0
            # Incrementa o temporizador de caminhada utilizando o delta tempo e o multiplicador
            self.walk_timer += dt * speed_mult
            # Simula um movimento senoidal vertical na câmera imitando o balanço natural dos passos
            self.offset_y = self.base_offset_y + math.sin(self.walk_timer) * 0.5
        else:
            # Interpola suavemente o deslocamento vertical de volta à posição base quando parado
            self.offset_y += (self.base_offset_y - self.offset_y) * 8.0 * dt

        # Atualiza a coordenada X da câmera acompanhando a posição do jogador
        self.pos.x = player_pos.x
        # Atualiza a coordenada Y da câmera somando o deslocamento vertical calculado
        self.pos.y = player_pos.y + self.offset_y
        # Atualiza a coordenada Z da câmera mantendo o distanciamento em relação ao jogador
        self.pos.z = player_pos.z + self.offset_z

    # Realiza a projeção matemática de coordenadas tridimensionais (3D) do mundo para bidimensionais (2D) da tela
    def project(self, world_pos):
        # Calcula a diferença de posição no eixo X entre o mundo e a câmera
        dx = world_pos.x - self.pos.x
        # Calcula a diferença de posição no eixo Y entre o mundo e a câmera
        dy = world_pos.y - self.pos.y
        # Calcula a diferença de posição no eixo Z entre o mundo e a câmera
        dz = world_pos.z - self.pos.z

        # Retorna None caso o objeto esteja atrás da câmera ou muito próximo para evitar divisão por zero
        if dz <= 0.8:
            return None

        # Calcula a coordenada X na tela usando proporção de perspectiva baseada em FOV e profundidade (dz)
        screen_x = int(self.w / 2 + (dx * self.fov) / dz)
        # Calcula a coordenada Y na tela invertendo o eixo vertical para o sistema de coordenadas do Pygame
        screen_y = int(self.h / 2 - (dy * self.fov) / dz)
        # Calcula o fator de escala visual do objeto com base na distância (quanto mais perto, maior)
        scale = self.fov / dz

        # Retorna uma tupla contendo a posição de tela (X, Y), a profundidade (dz) e a escala visual
        return (screen_x, screen_y, dz, scale)

# Classe que define os atributos, estatísticas e comportamentos dos Pokémon selvagens no mundo
class PokemonEntity:
    # Dicionário estático contendo os atributos base de todas as espécies de Pokémon disponíveis no jogo
    BASE_STATS = {
        "Pikachu": {"color": (255, 210, 40), "speed": 2.5, "points": 15, "catch_rate": 0.70, "max_hp": 50, "type": "electric", "evolves_at": 18, "evolves_to": "Raichu"},
        "Raichu": {"color": (230, 150, 20), "speed": 3.0, "points": 35, "catch_rate": 0.45, "max_hp": 85, "type": "electric", "evolves_at": 999, "evolves_to": None},
        "Bulbasaur": {"color": (80, 190, 120), "speed": 1.5, "points": 18, "catch_rate": 0.65, "max_hp": 60, "type": "grass", "evolves_at": 16, "evolves_to": "Ivysaur"},
        "Ivysaur": {"color": (60, 150, 100), "speed": 1.6, "points": 35, "catch_rate": 0.45, "max_hp": 85, "type": "grass", "evolves_at": 32, "evolves_to": "Venusaur"},
        "Venusaur": {"color": (40, 120, 80), "speed": 1.7, "points": 70, "catch_rate": 0.25, "max_hp": 120, "type": "grass", "evolves_at": 999, "evolves_to": None},
        "Eevee": {"color": (160, 115, 80), "speed": 2.2, "points": 45, "catch_rate": 0.40, "max_hp": 70, "type": "normal", "evolves_at": 20, "evolves_to": "Vaporeon"},
        "Vaporeon": {"color": (50, 150, 220), "speed": 2.5, "points": 80, "catch_rate": 0.25, "max_hp": 110, "type": "water", "evolves_at": 999, "evolves_to": None},
        "Squirtle": {"color": (60, 160, 230), "speed": 1.5, "points": 30, "catch_rate": 0.55, "max_hp": 65, "type": "water", "evolves_at": 16, "evolves_to": "Wartortle"},
        "Wartortle": {"color": (40, 130, 200), "speed": 1.6, "points": 50, "catch_rate": 0.35, "max_hp": 90, "type": "water", "evolves_at": 36, "evolves_to": "Blastoise"},
        "Blastoise": {"color": (20, 90, 160), "speed": 1.7, "points": 95, "catch_rate": 0.20, "max_hp": 130, "type": "water", "evolves_at": 999, "evolves_to": None},
        "Psyduck": {"color": (230, 210, 60), "speed": 1.8, "points": 35, "catch_rate": 0.60, "max_hp": 55, "type": "water", "evolves_at": 33, "evolves_to": "Golduck"},
        "Golduck": {"color": (40, 100, 200), "speed": 2.4, "points": 75, "catch_rate": 0.30, "max_hp": 105, "type": "water", "evolves_at": 999, "evolves_to": None},
        "Poliwag": {"color": (80, 120, 220), "speed": 1.6, "points": 25, "catch_rate": 0.65, "max_hp": 50, "type": "water", "evolves_at": 25, "evolves_to": "Poliwrath"},
        "Poliwrath": {"color": (30, 60, 150), "speed": 2.1, "points": 65, "catch_rate": 0.30, "max_hp": 115, "type": "water", "evolves_at": 999, "evolves_to": None},
        "Charmander": {"color": (240, 110, 40), "speed": 2.0, "points": 25, "catch_rate": 0.50, "max_hp": 55, "type": "fire", "evolves_at": 16, "evolves_to": "Charmeleon"},
        "Charmeleon": {"color": (220, 70, 20), "speed": 2.4, "points": 50, "catch_rate": 0.35, "max_hp": 85, "type": "fire", "evolves_at": 36, "evolves_to": "Charizard"},
        "Charizard": {"color": (200, 50, 10), "speed": 3.1, "points": 110, "catch_rate": 0.15, "max_hp": 135, "type": "fire", "evolves_at": 999, "evolves_to": None},
        "Magmar": {"color": (220, 80, 40), "speed": 2.3, "points": 50, "catch_rate": 0.35, "max_hp": 85, "type": "fire", "evolves_at": 999, "evolves_to": None},
        "Snorlax": {"color": (60, 90, 130), "speed": 1.0, "points": 80, "catch_rate": 0.25, "max_hp": 160, "type": "normal", "evolves_at": 999, "evolves_to": None},
        "Mew": {"color": (255, 140, 200), "speed": 3.5, "points": 120, "catch_rate": 0.15, "max_hp": 120, "type": "psychic", "evolves_at": 999, "evolves_to": None},
        "Dragonite": {"color": (230, 160, 50), "speed": 3.0, "points": 100, "catch_rate": 0.20, "max_hp": 140, "type": "dragon", "evolves_at": 999, "evolves_to": None},
        "Arcanine": {"color": (210, 100, 30), "speed": 3.2, "points": 90, "catch_rate": 0.22, "max_hp": 125, "type": "fire", "evolves_at": 999, "evolves_to": None}
    }

    # Método construtor que inicializa uma nova instância de Pokémon selvagem no mapa
    def __init__(self, spawn_center=pygame.math.Vector3(0, 0, 0), min_lvl=1, max_lvl=10, allowed_names=None):
        # Verifica se a lista de nomes permitidos foi fornecida; caso contrário, define um valor padrão
        if allowed_names is None:
            allowed_names = ["Pikachu"]
        
        # Sorteia aleatoriamente o nome do Pokémon dentre as espécies permitidas na ilha
        self.name = random.choice(allowed_names)
        # Sorteia aleatoriamente o nível do Pokémon dentro da faixa permitida para a ilha
        self.level = random.randint(min_lvl, max_lvl)
        
        # Executa o método para verificar e aplicar evolução natural com base no nível sorteado
        self.check_natural_evolution()

        # Recupera as estatísticas base do dicionário utilizando o nome atualizado do Pokémon
        stats = PokemonEntity.BASE_STATS[self.name]
        # Determina aleatoriamente se o Pokémon é Shiny com uma chance de 5%
        self.is_shiny = random.random() < 0.05
        # Define a cor especial dourada se for Shiny, ou a cor padrão da espécie caso contrário
        self.color = (255, 215, 0) if self.is_shiny else stats["color"]
        # Define a velocidade de movimento, aplicando um bônus de 20% caso seja Shiny
        self.speed = stats["speed"] * (1.2 if self.is_shiny else 1.0)
        # Define os pontos concedidos, multiplicando por 3 caso seja Shiny
        self.points = stats["points"] * (3 if self.is_shiny else 1)
        # Define a taxa base de captura do Pokémon
        self.catch_rate = stats["catch_rate"]
        # Calcula o HP máximo somando a base com o bônus proporcional ao nível atual
        self.max_hp = stats["max_hp"] + (self.level * 2)
        # Define o HP atual do Pokémon igual ao seu HP máximo inicial
        self.hp = self.max_hp
        # Define o tipo elementar do Pokémon
        self.poke_type = stats["type"]

        # Sorteia uma coordenada X ao redor do centro de geração (spawn)
        x = spawn_center.x + random.uniform(-40, 40)
        # Sorteia uma coordenada Z ao redor do centro de geração (spawn)
        z = spawn_center.z + random.uniform(-40, 40)
        # Define a posição tridimensional inicial do Pokémon mantendo a altura (Y) fixa rente ao chão
        self.pos = pygame.math.Vector3(x, 0.5, z)

        # Sorteia um ângulo inicial aleatório em radianos para definir a direção de movimento
        angle = random.uniform(0, math.pi * 2)
        # Cria um vetor unitário de direção baseado no ângulo sorteado
        self.dir = pygame.math.Vector3(math.cos(angle), 0, math.sin(angle))
        # Define um temporizador aleatório para controlar a troca de direção do movimento
        self.walk_timer = random.uniform(1, 4)

    # Método que verifica se o Pokémon atinge o nível necessário para evoluir naturalmente na natureza
    def check_natural_evolution(self):
        # Loop contínuo para permitir múltiplas evoluções consecutivas se o nível for muito alto
        while True:
            # Recupera as estatísticas base da espécie atual
            stats = PokemonEntity.BASE_STATS[self.name]
            # Verifica se o nível atual atinge o requisito de evolução e se existe uma forma evoluída cadastrada
            if self.level >= stats["evolves_at"] and stats["evolves_to"] is not None:
                # Atualiza o nome do Pokémon para a sua próxima forma evoluída
                self.name = stats["evolves_to"]
            else:
                # Interrompe o loop caso não atinja os requisitos de evolução
                break

    # Atualiza a movimentação autônoma e aleatória do Pokémon selvagem pelo mapa
    def update(self, dt):
        # Decrementa o temporizador de caminhada utilizando o delta tempo (dt)
        self.walk_timer -= dt
        # Verifica se o temporizador esgotou para sortear uma nova direção de movimento
        if self.walk_timer <= 0:
            # Sorteia um novo ângulo aleatório
            angle = random.uniform(0, math.pi * 2)
            # Atualiza o vetor de direção com base no novo ângulo
            self.dir = pygame.math.Vector3(math.cos(angle), 0, math.sin(angle))
            # Reinicia o temporizador com um novo valor aleatório de tempo
            self.walk_timer = random.uniform(2, 5)

        # Move a posição do Pokémon adicionando o vetor de direção multiplicado pela velocidade e dt
        self.pos += self.dir * self.speed * dt
        # Garante que a altura (Y) do Pokémon permaneça constante no chão
        self.pos.y = 0.5

# Classe responsável por gerenciar os atributos, experiência, entradas e movimentação do jogador
class Player:
    # Método construtor que inicializa a posição, nível, experiência e estados do jogador
    def __init__(self):
        # Define a posição tridimensional inicial do jogador no centro do mundo
        self.pos = pygame.math.Vector3(0.0, 0.0, 0.0)
        # Define o nível inicial do jogador
        self.level = 1
        # Define a quantidade inicial de pontos de experiência (XP)
        self.xp = 0
        # Define a quantidade inicial de XP necessária para alcançar o próximo nível
        self.xp_to_next = 100
        # Define o nível inicial da melhoria de foco de mira do jogador
        self.focus_upgrade = 0
        # Define o raio inicial de alcance de interação com os Pokémon no mapa
        self.interaction_range = 8.5
        # Inicializa a flag booleana que indica se o jogador está se movimentando
        self.is_moving = False
        # Inicializa a flag booleana que indica se o jogador está correndo
        self.is_running = False
        # Inicializa a flag booleana que indica se o jogador está montado na bicicleta
        self.on_bike = False
        
        # Dicionário contendo os perks (vantagens passivas) melhoráveis do jogador
        self.perks = {
            "luck_charm": 0,    
            "stamina_boost": 0, 
            "magnet": 0         
        }

    # Adiciona pontos de experiência ao jogador e gerencia o processo de subida de nível
    def add_xp(self, amount):
        # Adiciona a quantidade informada ao total de XP atual do jogador
        self.xp += amount
        # Inicializa a flag local para indicar se houve subida de nível
        leveled_up = False
        # Loop para processar múltiplos níveis caso a quantidade de XP ganha seja muito alta
        while self.xp >= self.xp_to_next:
            # Subtrai o limite de XP atual do total acumulado
            self.xp -= self.xp_to_next
            # Incrementa em 1 o nível atual do jogador
            self.level += 1
            # Aumenta a exigência de XP para o próximo nível em 35% de forma exponencial
            self.xp_to_next = int(self.xp_to_next * 1.35)
            # Atualiza o raio de interação do jogador com base no novo nível e perks ativos
            self.interaction_range = 8.5 + (self.level * 0.25) + (self.perks["magnet"] * 1.5)
            # Marca a flag como verdadeira indicando que o jogador subiu de nível
            leveled_up = True
        # Retorna o valor booleano indicando se o jogador subiu de nível
        return leveled_up

    # Processa os comandos de teclado do usuário para mover o jogador e verificar colisões com obstáculos
    def handle_input(self, dt, obstacles):
        # Obtém o estado atual de todas as teclas pressionadas no teclado
        keys = pygame.key.get_pressed()
        # Define a velocidade base de deslocamento (maior caso esteja na bicicleta)
        base_speed = 26.0 if self.on_bike else 13.0
        # Verifica se alguma das teclas de Shift esquerdo ou direito está pressionada para correr
        self.is_running = (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])
        # Define o multiplicador de stamina/velocidade caso esteja correndo
        stamina_mult = 1.45 if self.is_running else 1.0
        # Calcula a velocidade final de movimento multiplicando a base pelo modificador
        speed = base_speed * stamina_mult

        # Cria um vetor de movimento zerado no espaço tridimensional
        move = pygame.math.Vector3(0, 0, 0)
        # Adiciona deslocamento para frente caso pressione W ou Seta para Cima
        if keys[pygame.K_w] or keys[pygame.K_UP]: move.z += 1
        # Adiciona deslocamento para trás caso pressione S ou Seta para Baixo
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: move.z -= 1
        # Adiciona deslocamento para a esquerda caso pressione A ou Seta para Esquerda
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: move.x -= 1
        # Adiciona deslocamento para a direita caso pressione D ou Seta para Direita
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: move.x += 1

        # Verifica se o vetor de movimento possui comprimento maior que zero (indicando tecla pressionada)
        self.is_moving = move.length_squared() > 0
        # Processa a movimentação apenas se houver teclas de direção pressionadas
        if self.is_moving:
            # Normaliza o vetor de movimento para evitar velocidade maior em diagonais
            move = move.normalize()
            # Calcula a próxima posição futura prevista do jogador no mapa
            next_pos = self.pos + move * speed * dt

            # Assume inicialmente que o movimento é livre de colisões
            can_move = True
            # Itera por cada obstáculo presente no cenário para verificar colisão
            for obs in obstacles:
                # Compara a distância entre a próxima posição prevista do jogador e o raio do obstáculo
                if (next_pos - obs["pos"]).length() < obs["radius"]:
                    # Impede o movimento caso a distância seja menor que o raio de colisão
                    can_move = False
                    break

            # Atualiza efetivamente a posição do jogador caso nenhuma colisão tenha ocorrido
            if can_move:
                # Atribui a nova posição calculada ao jogador
                self.pos = next_pos

# Classe principal que coordena toda a lógica do jogo Safari, estados, telas e salvamentos
class SafariGameEngine:
    # Método construtor que inicializa o motor do jogo, jogador, ilhas, inventário e estados
    def __init__(self):
        # Armazena a largura atual da tela de exibição
        self.w = SCREEN_WIDTH
        # Armazena a altura atual da tela de exibição
        self.h = SCREEN_HEIGHT

        # Instancia o objeto do jogador utilizando a classe Player
        self.player = Player()
        # Instancia o objeto da câmera virtual 3D passando as dimensões da tela
        self.camera = VirtualCamera3D(self.w, self.h)

        # Define o ID da ilha atual em que o jogador se encontra (começa na ilha 1)
        self.current_island = 1
        # Inicializa a lista de ilhas desbloqueadas contendo inicialmente apenas a primeira ilha
        self.unlocked_islands = [1]

        # Inicializa a lista vazia que armazenará os Pokémon selvagens gerados no mapa
        self.pokemons = []
        # Inicializa a lista vazia que armazenará os elementos de cenário da ilha
        self.environment = []
        
        # Dicionário estruturado contendo os dados da missão diária ativa do jogador
        self.active_quest = {"target": "Pikachu", "goal": 3, "progress": 0, "reward": 150, "completed": False}
        # Chama o método para gerar uma nova missão inicial aleatória
        self.generate_new_quest()

        # Chama o método para popular os dados, Pokémon e objetos da ilha inicial
        self._initialize_island_data()

        # Define o estado inicial do jogo como exploração livre do mapa
        self.state = "EXPLORE"
        # Inicializa a pontuação de capturas do jogador com zero
        self.score = 0
        # Inicializa a quantidade de moedas iniciais do jogador com 80
        self.coins = 80

        # Inicializa o ponteiro temporal do ciclo de dia e noite
        self.time_of_day = 0.0
        # Inicializa o fator de escuridão/noite com zero
        self.night_factor = 0.0
        # Cria uma lista contendo instâncias do sistema de chuva para a ilha atual
        self.rain_drops = [RainSystem(self.w, self.h) for _ in range(140)]

        # Cria uma superfície gráfica dedicada para desenhar a sombra elíptica das entidades
        self.shadow_surf = pygame.Surface((220, 110), pygame.SRCALPHA)
        # Loop para desenhar gradientes concêntricos simulando o efeito de sombreamento suave
        for i in range(15):
            alpha = int(100 * (1.0 - i / 15.0))
            pygame.draw.ellipse(self.shadow_surf, (0, 0, 0, alpha), (i, i // 2, 220 - i * 2, 110 - i))

        # Dicionário contendo o inventário inicial de Pokébolas e itens de captura do jogador
        self.inventory = {
            "Pokébola": {"count": 20, "bonus": 0.0, "color": (230, 40, 40)},
            "Super Ball": {"count": 8, "bonus": 0.20, "color": (40, 110, 240)},
            "Ultra Ball": {"count": 3, "bonus": 0.40, "color": (250, 190, 20)},
            "Master Ball": {"count": 1, "bonus": 1.00, "color": (160, 32, 240)}
        }
        # Define a Pokébola padrão selecionada inicialmente como a Pokébola básica
        self.selected_ball = "Pokébola"
        # Inicializa o dicionário da Pokédex registrando contadores zerados de vistos e capturados para cada espécie
        self.pokedex = {p_name: {"seen": 0, "caught": 0} for p_name in PokemonEntity.BASE_STATS.keys()}

        # Inicializa a variável de batalha indicando que nenhum Pokémon está sendo combatido no momento
        self.battle_pokemon = None
        # Inicializa o temporizador da barra de mira da batalha
        self.aim_timer = 0.0
        # Define a velocidade inicial de oscilação da mira na batalha
        self.aim_speed = 3.0
        # Define a posição horizontal inicial da mira no centro da tela
        self.aim_x = self.w // 2

        # Define o estado inicial da animação de arremesso da Pokébola como ocioso (IDLE)
        self.ball_state = "IDLE"
        # Inicializa o temporizador de voo da Pokébola no ar
        self.ball_air_timer = 0.0
        # Inicializa o temporizador de balanço da Pokébola após atingir o Pokémon
        self.shake_timer = 0.0
        # Inicializa o contador de vezes que a Pokébola balançou durante a tentativa de captura
        self.shake_count = 0
        # Define a posição inicial de lançamento da Pokébola na parte inferior da tela de batalha
        self.ball_start_pos = pygame.math.Vector2(self.w // 2, self.h - 100)
        # Define a posição alvo inicial para onde a Pokébola será arremessada
        self.ball_target_pos = pygame.math.Vector2(self.w // 2, self.h // 2)
        # Define a posição atual da Pokébola igualando-se à posição de início
        self.ball_current_pos = pygame.math.Vector2(self.ball_start_pos)
        # Define a posição alvo onde o sprite do Pokémon é desenhado na tela de batalha
        self.poke_target_pos = pygame.math.Vector2(self.w // 2, self.h // 2 + 20)

        # Define a mensagem de texto inicial exibida no log da interface de batalha
        self.battle_log = "Um Pokémon selvagem apareceu!"

        # Inicializa a lista vazia para armazenar partículas ativas na tela
        self.particles = []
        # Inicializa a string de texto para mensagens flutuantes na tela como vazia
        self.message_text = ""
        # Inicializa o temporizador de exibição das mensagens flutuantes com zero
        self.message_timer = 0.0
        # Inicializa a lista de áreas clicáveis da interface da loja
        self.shop_rects = []
        # Inicializa a lista de áreas clicáveis do menu de seleção de ilhas
        self.island_rects = []

        # Tenta carregar o arquivo de salvamento persistente existente ao iniciar o motor
        self.load_persistence()

    # Gera uma nova missão diária aleatória com base nas espécies permitidas na ilha atual
    def generate_new_quest(self):
        # Obtém as configurações da ilha atual a partir do dicionário global de ilhas
        isl = ISLAND_CONFIGS[self.current_island]
        # Sorteia aleatoriamente um Pokémon dentre os permitidos na ilha para ser o alvo da missão
        poke_choice = random.choice(isl["allowed_pokemons"])
        # Sorteia a quantidade alvo de capturas necessárias para completar a missão (entre 2 e 5)
        target_count = random.randint(2, 5)
        # Calcula a recompensa em moedas multiplicando a quantidade alvo por 60
        reward_gold = target_count * 60
        # Define o dicionário da nova missão ativa com todos os seus parâmetros atualizados
        self.active_quest = {
            "target": poke_choice,
            "goal": target_count,
            "progress": 0,
            "reward": reward_gold,
            "completed": False
        }

    # Inicializa e popula os dados, listas de Pokémon e elementos de cenário da ilha atual
    def _initialize_island_data(self):
        # Recupera as configurações da ilha atual
        isl = ISLAND_CONFIGS[self.current_island]
        # Gera uma lista contendo 35 instâncias de Pokémon selvagens espalhados pela ilha
        self.pokemons = [
            PokemonEntity(self.player.pos, isl["min_poke_lvl"], isl["max_poke_lvl"], isl["allowed_pokemons"]) 
            for _ in range(35)
        ]
        # Gera os elementos de ambiente e obstáculos procedurais específicos do tipo de ilha
        self.environment = self._generate_environment(isl["env_type"])

    # Alterna o modo de exibição entre tela cheia e janela redimensionável de 1280x720
    def toggle_fullscreen(self):
        global screen, IS_FULLSCREEN, SCREEN_WIDTH, SCREEN_HEIGHT
        # Inverte o valor booleano atual da flag de tela cheia
        IS_FULLSCREEN = not IS_FULLSCREEN
        # Verifica se o modo ativado deve ser tela cheia
        if IS_FULLSCREEN:
            # Restaura a largura e altura para os valores máximos do monitor atual
            SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
            # Recria a janela do Pygame em modo tela cheia com buffer duplo
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN | pygame.DOUBLEBUF)
        else:
            # Define uma resolução padrão em modo janela (1280x720)
            SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
            # Recria a janela do Pygame em modo janela com buffer duplo
            screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)

        # Atualiza as variáveis de largura e altura da instância do motor do jogo
        self.w, self.h = SCREEN_WIDTH, SCREEN_HEIGHT
        # Atualiza as dimensões na câmera virtual 3D
        self.camera.resize(self.w, self.h)
        # Recria o sistema de gotas de chuva ajustando para a nova resolução de tela
        self.rain_drops = [RainSystem(self.w, self.h) for _ in range(140)]
        # Recalcula a posição inicial de arremesso da Pokébola com base na nova altura da tela
        self.ball_start_pos = pygame.math.Vector2(self.w // 2, self.h - 100)
        # Recalcula a posição alvo do Pokémon na tela de batalha
        self.poke_target_pos = pygame.math.Vector2(self.w // 2, self.h // 2 + 20)

    # Gera de forma procedural os elementos de cenário (árvores, rochas, etc.) espalhados pelo mapa
    def _generate_environment(self, env_type):
        # Inicializa a lista que armazenará os objetos gerados no cenário
        objs = []
        # Loop para gerar 140 elementos principais de vegetação (árvores ou palmeiras)
        for _ in range(140):
            # Sorteia uma coordenada X aleatória em uma grande área ao redor do mapa
            x = random.uniform(-160, 160)
            # Sorteia uma coordenada Z aleatória
            z = random.uniform(-160, 160)
            # Garante que os objetos não spawnem exatamente em cima da posição inicial do jogador
            if abs(x) > 4 or abs(z) > 4:
                # Adiciona o dicionário do objeto de cenário à lista com tipo, posição, altura e raio de colisão
                objs.append({"type": env_type, "pos": pygame.math.Vector3(x, 0, z), "h": random.uniform(5.5, 8.5), "radius": 1.4})

        # Loop para gerar 50 elementos secundários de rochas espalhados pelo mapa
        for _ in range(50):
            # Sorteia coordenada X aleatória
            x = random.uniform(-160, 160)
            # Sorteia coordenada Z aleatória
            z = random.uniform(-160, 160)
            # Evita gerar rochas muito perto do centro inicial do jogador
            if abs(x) > 5 or abs(z) > 5:
                # Adiciona o objeto de rocha à lista com seu respectivo raio de colisão
                objs.append({"type": "ROCK", "pos": pygame.math.Vector3(x, 0, z), "radius": random.uniform(1.6, 2.6)})

        # Retorna a lista completa com todos os objetos gerados para o ambiente
        return objs

    # Salva todos os dados importantes de progresso do jogador em um arquivo JSON local
    def save_persistence(self):
        # Cria um dicionário estruturado contendo todos os dados e estatísticas atuais
        data = {
            "level": self.player.level,
            "xp": self.player.xp,
            "coins": self.coins,
            "score": self.score,
            "inventory": self.inventory,
            "pokedex": self.pokedex,
            "current_island": self.current_island,
            "unlocked_islands": self.unlocked_islands,
            "perks": self.player.perks
        }
        # Abre o arquivo JSON de salvamento no modo de escrita e grava os dados estruturados formatados
        with open("savegame_tcc_v4.json", "w") as f:
            json.dump(data, f)

    # Carrega os dados de progresso salvos anteriormente a partir do arquivo JSON local, caso exista
    def load_persistence(self):
        # Verifica se o arquivo de salvamento do jogo existe no diretório atual
        if os.path.exists("savegame_tcc_v4.json"):
            # Tenta abrir e ler o arquivo de salvamento de forma segura
            try:
                with open("savegame_tcc_v4.json", "r") as f:
                    # Carrega o conteúdo JSON decodificando para um dicionário em Python
                    data = json.load(f)
                    # Restaura o nível salvo do jogador, ou mantém o padrão (1) caso ausente
                    self.player.level = data.get("level", 1)
                    # Restaura a experiência salva do jogador
                    self.player.xp = data.get("xp", 0)
                    # Restaura a quantidade de moedas salvas
                    self.coins = data.get("coins", 80)
                    # Restaura a pontuação de capturas do jogador
                    self.score = data.get("score", 0)
                    # Restaura o inventário salvo de itens e Pokébolas
                    self.inventory = data.get("inventory", self.inventory)
                    # Restaura o progresso registrado na Pokédex
                    self.pokedex = data.get("pokedex", self.pokedex)
                    # Restaura a última ilha em que o jogador estava jogando
                    self.current_island = data.get("current_island", 1)
                    # Restaura a lista de ilhas que já foram desbloqueadas
                    self.unlocked_islands = data.get("unlocked_islands", [1])
                    # Restaura os perks passivos adquiridos pelo jogador
                    self.player.perks = data.get("perks", self.player.perks)
                    # Reinicializa os dados e Pokémon da ilha restaurada
                    self._initialize_island_data()
            # Captura qualquer erro de leitura ou arquivo corrompido de forma silenciosa
            except Exception:
                pass

    # Exibe uma mensagem flutuante temporária na interface do usuário por um determinado tempo
    def display_message(self, text, duration=2.5):
        # Atribui o texto da mensagem à variável interna do motor
        self.message_text = text
        # Define o tempo de duração que a mensagem ficará visível na tela
        self.message_timer = duration

    # Calcula e retorna a quantidade total de todas as Pokébolas somadas presentes no inventário
    def total_balls(self):
        # Soma a contagem numérica de cada tipo de Pokébola armazenada no inventário
        return sum(b["count"] for b in self.inventory.values())

    # Gerencia a lógica de viagem para outra ilha ou o desbloqueio dela caso ainda não tenha sido adquirida
    def change_island(self, island_id):
        # Recupera as configurações da ilha selecionada através do seu ID
        info = ISLAND_CONFIGS[island_id]
        # Verifica se o ID da ilha já consta na lista de ilhas desbloqueadas pelo jogador
        if island_id in self.unlocked_islands:
            # Atualiza o ID da ilha atual para a selecionada
            self.current_island = island_id
            # Reinicializa os dados, obstáculos e Pokémon da nova ilha
            self._initialize_island_data()
            # Exibe uma mensagem informando que viajou com sucesso
            self.display_message(f"Viajou para a {info['name']}!")
            # Retorna o estado do jogo para a exploração livre do mapa
            self.state = "EXPLORE"
        else:
            # Verifica se o nível do jogador é menor que o exigido para entrar na ilha
            if self.player.level < info["min_lvl"]:
                # Exibe mensagem de aviso sobre o nível mínimo necessário
                self.display_message(f"Requer Nível {info['min_lvl']}!")
            # Verifica se o jogador possui moedas suficientes para pagar o custo de desbloqueio
            elif self.coins < info["cost"]:
                # Exibe mensagem de aviso informando que faltam moedas
                self.display_message(f"Requer {info['cost']} Moedas!")
            else:
                # Subtrai o custo de moedas do total do jogador
                self.coins -= info["cost"]
                # Adiciona o ID da nova ilha à lista de ilhas desbloqueadas
                self.unlocked_islands.append(island_id)
                # Define a ilha atual como a recém-desbloqueada
                self.current_island = island_id
                # Inicializa os dados da ilha recém-desbloqueada
                self._initialize_island_data()
                # Exibe mensagem de sucesso informando que a ilha foi desbloqueada
                self.display_message(f"{info['name']} Desbloqueada!")
                # Salva o progresso atualizado no arquivo JSON persistente
                self.save_persistence()
                # Retorna o estado do jogo para a exploração
                self.state = "EXPLORE"

    # Processa as compras de itens, Pokébolas ou melhorias de status realizadas pelo jogador na loja
    def process_purchase(self, item_num):
        # Verifica se o item escolhido é o pacote de Pokébolas básicas (número 1) e se há moedas suficientes (20)
        if item_num == 1 and self.coins >= 20:
            # Subtrai 20 moedas do total do jogador
            self.coins -= 20
            # Adiciona 5 unidades de Pokébolas básicas ao inventário
            self.inventory["Pokébola"]["count"] += 5
            # Toca um efeito sonoro de confirmação de compra
            SoundManager.play_tone(600, 0.15)
            # Exibe mensagem de sucesso na tela
            self.display_message("+5 Pokébolas Compradas!")
        # Verifica se o item escolhido é o pacote de Super Balls (número 2) e se há 50 moedas
        elif item_num == 2 and self.coins >= 50:
            # Subtrai 50 moedas
            self.coins -= 50
            # Adiciona 3 unidades de Super Ball ao inventário
            self.inventory["Super Ball"]["count"] += 3
            # Toca efeito sonoro de compra
            SoundManager.play_tone(700, 0.15)
            # Exibe mensagem de sucesso
            self.display_message("+3 Super Balls Compradas!")
        # Verifica se o item escolhido é o pacote de Ultra Balls (número 3) custando 100 moedas
        elif item_num == 3 and self.coins >= 100:
            # Subtrai 100 moedas
            self.coins -= 100
            # Adiciona 2 unidades de Ultra Ball ao inventário
            self.inventory["Ultra Ball"]["count"] += 2
            # Toca som de compra
            SoundManager.play_tone(800, 0.15)
            # Exibe mensagem de sucesso
            self.display_message("+2 Ultra Balls Compradas!")
        # Verifica se o item escolhido é a Master Ball (número 4) custando 300 moedas
        elif item_num == 4 and self.coins >= 300:
            # Subtrai 300 moedas
            self.coins -= 300
            # Adiciona 1 unidade de Master Ball ao inventário do jogador
            self.inventory["Master Ball"]["count"] += 1
            # Toca som especial de compra de item raro
            SoundManager.play_tone(950, 0.2)
            # Exibe mensagem de sucesso
            self.display_message("1x Master Ball Adquirida!")
        # Verifica se o item escolhido é a melhoria de mira de precisão (número 5)
        elif item_num == 5:
            # Calcula o custo progressivo da melhoria de mira baseado no nível atual de melhoria
            cost = (self.player.focus_upgrade + 1) * 55
            # Verifica se o jogador possui moedas suficientes para pagar o custo calculado
            if self.coins >= cost:
                # Subtrai o custo em moedas
                self.coins -= cost
                # Incrementa o nível de melhoria de foco do jogador
                self.player.focus_upgrade += 1
                # Toca som de melhoria bem-sucedida
                SoundManager.play_tone(900, 0.15)
                # Exibe mensagem informando o upgrade
                self.display_message("Precisão de Mira Aumentada!")
        # Verifica se o item escolhido é o amuleto da sorte (número 6)
        elif item_num == 6:
            # Calcula o custo progressivo do amuleto da sorte
            cost = (self.player.perks["luck_charm"] + 1) * 120
            # Verifica se há moedas suficientes
            if self.coins >= cost:
                # Subtrai as moedas correspondentes
                self.coins -= cost
                # Incrementa o nível do perk amuleto da sorte
                self.player.perks["luck_charm"] += 1
                # Toca som de confirmação
                SoundManager.play_tone(1000, 0.15)
                # Exibe mensagem de sucesso
                self.display_message("Amuleto da Sorte Evoluído!")

    # Inicia o modo de batalha contra um Pokémon selvagem específico selecionado no mapa
    def initiate_battle(self, pokemon):
        # Verifica se o total de Pokébolas disponíveis no inventário é zero ou menor
        if self.total_balls() <= 0:
            # Exibe mensagem de alerta informando que está sem Pokébolas
            self.display_message("SEM POKÉBOLAS! Visite a Loja [M].")
            return

        # Verifica se a Pokébola atualmente selecionada está esgotada (quantidade zero)
        if self.inventory[self.selected_ball]["count"] <= 0:
            # Percorre todo o inventário para encontrar automaticamente outra Pokébola disponível
            for bname, bdata in self.inventory.items():
                if bdata["count"] > 0:
                    # Define a nova Pokébola disponível como a selecionada atualmente
                    self.selected_ball = bname
                    break

        # Atribui o Pokémon passado por parâmetro como o alvo da batalha atual
        self.battle_pokemon = pokemon
        # Incrementa o contador de "vistos" para essa espécie na Pokédex do jogador
        self.pokedex[pokemon.name]["seen"] += 1
        # Altera o estado global do jogo para o modo de batalha (BATTLE)
        self.state = "BATTLE"
        # Toca um som de alerta indicando o início do combate
        SoundManager.play_tone(350, 0.2)

        # Calcula a diferença de nível entre o Pokémon selvagem e o jogador
        level_diff = self.battle_pokemon.level - self.player.level
        # Calcula a velocidade base de oscilação da mira, subtraindo bônus da melhoria de foco
        base_speed = 3.0 - (self.player.focus_upgrade * 0.35)
        # Define a velocidade final da mira limitando entre 1.0 e 12.0 com base na diferença de nível
        self.aim_speed = max(1.0, min(12.0, base_speed + (level_diff * 0.2)))
        # Define a frase inicial exibida no log de texto da batalha
        self.battle_log = f"Um {pokemon.name} selvagem (Lv.{pokemon.level}) apareceu!"
        # Reseta os parâmetros de mira e arremesso para o estado inicial
        self.reset_aiming()

    # Reseta as variáveis de estado da mira e da Pokébola para o início de uma nova tentativa de arremesso
    def reset_aiming(self):
        # Define o estado da Pokébola como ocioso (IDLE)
        self.ball_state = "IDLE"
        # Reseta o temporizador de voo da Pokébola
        self.ball_air_timer = 0.0
        # Reseta o temporizador de balanço da Pokébola
        self.shake_timer = 0.0
        # Reseta o contador de balanços da Pokébola
        self.shake_count = 0
        # Retorna a posição atual da Pokébola para a base de lançamento na parte inferior
        self.ball_current_pos = pygame.math.Vector2(self.ball_start_pos)

    # Executa o arremesso da Pokébola selecionada caso o jogador pressione o botão correspondente
    def throw_pokeball(self):
        # Impede o arremesso caso a Pokébola já não esteja no estado ocioso
        if self.ball_state != "IDLE": return
        # Verifica se a Pokébola selecionada está esgotada no inventário
        if self.inventory[self.selected_ball]["count"] <= 0:
            # Exibe mensagem informando que faltam unidades daquele tipo de bola
            self.display_message(f"Sem {self.selected_ball}s!")
            return

        # Decrementa em 1 a quantidade da Pokébola selecionada no inventário do jogador
        self.inventory[self.selected_ball]["count"] -= 1
        # Altera o estado da Pokébola para em voo (AIR)
        self.ball_state = "AIR"
        # Reseta o temporizador de voo da bola
        self.ball_air_timer = 0.0
        # Define a posição alvo final do arremesso baseada na posição horizontal atual da mira
        self.ball_target_pos = pygame.math.Vector2(self.aim_x, self.poke_target_pos.y)
        # Toca som característico de arremesso de Pokébola
        SoundManager.play_tone(500, 0.1)
        # Atualiza o log de texto informando que a Pokébola foi arremessada
        self.battle_log = f"Você arremessou uma {self.selected_ball}!"

    # Resolve a lógica matemática de acerto da mira, dano e cálculo de taxa de sucesso de captura do Pokémon
    def resolve_capture_logic(self):
        # Calcula a distância absoluta entre a posição onde a bola caiu e o centro exato da mira
        dist = abs(self.ball_target_pos.x - (self.w // 2))

        # Verifica se o lançamento caiu dentro da faixa aceitável de acerto (38 pixels)
        if dist <= 38:
            # Define o bônus de precisão baseado em quão perto do centro exato o jogador acertou
            accuracy_bonus = 0.40 if dist <= 12 else 0.20
            # Recupera o bônus específico associado ao tipo de Pokébola utilizada
            ball_bonus = self.inventory[self.selected_ball]["bonus"]

            # Inicializa o bônus de tipo elemental com zero
            type_bonus = 0.0
            # Concede um pequeno bônus de captura caso o tipo elementar corresponda a certas categorias
            if self.battle_pokemon.poke_type in ["water", "fire", "electric"]:
                type_bonus = 0.08

            # Sorteia uma quantidade de dano aleatório causado pela Pokébola ao acertar o Pokémon
            damage = random.randint(30, 55)
            # Reduz o HP atual do Pokémon garantindo que nunca fique abaixo de zero
            self.battle_pokemon.hp = max(0, self.battle_pokemon.hp - damage)
            # Calcula o fator de proporção do HP perdido em relação ao HP máximo do Pokémon
            hp_factor = 1.0 - (self.battle_pokemon.hp / self.battle_pokemon.max_hp)

            # Calcula a chance final de sucesso somando a taxa base, bônus de HP, precisão e tipo da bola
            final_chance = self.battle_pokemon.catch_rate + (hp_factor * 0.4) + accuracy_bonus + ball_bonus + type_bonus
            
            # Garante chance de 100% caso utilize a Master Ball ou o HP do Pokémon tenha chegado a zero
            if self.selected_ball == "Master Ball" or self.battle_pokemon.hp <= 0:
                final_chance = 1.0

            # Sorteia se a captura foi bem-sucedida comparando um número aleatório com a chance final calculada
            self.catch_success = (random.random() < final_chance)

            # Altera o estado da Pokébola para balançando (SHAKING), iniciando a sequência de animação
            self.ball_state = "SHAKING"
            # Reseta o temporizador de balanço
            self.shake_timer = 0.0
            # Reseta o contador de balanços
            self.shake_count = 0
            # Atualiza o log de texto informando que a Pokébola está balançando
            self.battle_log = "A Pokébola balança..."
        else:
            # Exibe mensagem informando que o lançamento foi errado
            self.display_message("Lançamento Errado!")
            # Atualiza o log de texto da batalha
            self.battle_log = "O lançamento falhou e passou longe!"
            # Reseta a mira para permitir nova tentativa
            self.reset_aiming()

    # Finaliza o processo de captura após a conclusão dos balanços da Pokébola na tela de batalha
    def finalize_capture(self):
        # Verifica se o resultado da captura foi bem-sucedido
        if self.catch_success:
            # Incrementa em 1 a pontuação geral de capturas do jogador
            self.score += 1
            
            # Calcula a quantidade de XP ganha com base no nível do Pokémon capturado e se era Shiny
            earned_xp = self.battle_pokemon.level * 18 + (50 if self.battle_pokemon.is_shiny else 10)
            # Adiciona o XP ao jogador e verifica se ele subiu de nível
            leveled_up = self.player.add_xp(earned_xp)

            # Incrementa o contador de "capturados" para essa espécie específica na Pokédex
            self.pokedex[self.battle_pokemon.name]["caught"] += 1
            # Calcula a quantidade de moedas ganhas com base nos pontos e nível do Pokémon
            earned_coins = self.battle_pokemon.points + (self.battle_pokemon.level * 3)

            # Adiciona as moedas ganhas ao total do jogador
            self.coins += earned_coins
            # Recompensa o jogador adicionando 2 Pokébolas básicas de volta ao inventário
            self.inventory["Pokébola"]["count"] += 2

            # Verifica se a missão ativa ainda não foi concluída e se o Pokémon capturado corresponde ao alvo da missão
            if not self.active_quest["completed"] and self.active_quest["target"] == self.battle_pokemon.name:
                # Incrementa o progresso da missão em 1
                self.active_quest["progress"] += 1
                # Verifica se o progresso atingiu ou ultrapassou a meta exigida pela missão
                if self.active_quest["progress"] >= self.active_quest["goal"]:
                    # Marca a missão como concluída
                    self.active_quest["completed"] = True
                    # Adiciona a recompensa em moedas da missão ao total do jogador
                    self.coins += self.active_quest["reward"]
                    # Exibe mensagem comemorativa de conclusão da missão
                    self.display_message(f"Missão Concluída! +{self.active_quest['reward']} Moedas")

            # Define uma string especial indicando se o Pokémon capturado era Shiny
            shiny_str = " SHINY!" if self.battle_pokemon.is_shiny else "!"
            # Define uma string indicando subida de nível caso o jogador tenha evoluído de nível
            lvl_up_str = " | SUBIU DE NÍVEL DO JOGADOR!" if leveled_up else ""
            # Exibe a mensagem de sucesso detalhada da captura na tela
            self.display_message(f"Capturou {self.battle_pokemon.name}{shiny_str} (+{earned_xp} XP){lvl_up_str}")
            # Toca um som especial comemorativo de captura bem-sucedida
            SoundManager.play_tone(880, 0.3)

            # Gera 50 partículas visuais comemorativas estourando no centro da tela
            for _ in range(50):
                self.particles.append(Particle(self.w//2, self.h//2, COLOR_ACCENT, random.uniform(-5, 5), random.uniform(-5, 5), 1.4))

            # Remove o Pokémon capturado da lista ativa de Pokémon da ilha
            if self.battle_pokemon in self.pokemons:
                self.pokemons.remove(self.battle_pokemon)
            
            # Recupera as configurações da ilha atual para gerar um novo Pokémon substituto
            isl = ISLAND_CONFIGS[self.current_island]
            # Adiciona um novo Pokémon gerado proceduralmente à lista para substituir o capturado
            self.pokemons.append(PokemonEntity(self.player.pos, isl["min_poke_lvl"], isl["max_poke_lvl"], isl["allowed_pokemons"]))

            # Salva automaticamente o progresso atualizado no arquivo JSON
            self.save_persistence()
            # Retorna o estado do jogo para o modo de exploração livre
            self.state = "EXPLORE"
        else:
            # Exibe mensagem informando que o Pokémon escapou da bola, mostrando o HP restante
            self.display_message(f"Escapou! HP restante: {self.battle_pokemon.hp}/{self.battle_pokemon.max_hp}")
            # Atualiza o log de texto da batalha
            self.battle_log = f"O {self.battle_pokemon.name} escapou da Pokébola!"
            
            # Sorteia uma chance de 35% do Pokémon fugir correndo após escapar da Pokébola
            if random.random() < 0.35:
                # Exibe mensagem informando que o Pokémon selvagem fugiu correndo
                self.display_message(f"O {self.battle_pokemon.name} selvagem fugiu correndo!")
                # Remove o Pokémon que fugiu da lista ativa do mapa
                if self.battle_pokemon in self.pokemons:
                    self.pokemons.remove(self.battle_pokemon)
                # Recupera as configurações da ilha atual
                isl = ISLAND_CONFIGS[self.current_island]
                # Gera um novo Pokémon substituto no mapa
                self.pokemons.append(PokemonEntity(self.player.pos, isl["min_poke_lvl"], isl["max_poke_lvl"], isl["allowed_pokemons"]))
                # Retorna o estado do jogo para a exploração
                self.state = "EXPLORE"
            else:
                # Caso não fuja, reseta apenas a mira para permitir tentar arremessar novamente
                self.reset_aiming()

# Método central de atualização lógica do jogo, executado a cada quadro com base no delta tempo (dt)
    def update(self, dt):
        # Decrementa o temporizador de mensagens flutuantes caso esteja ativo
        if self.message_timer > 0:
            self.message_timer -= dt

        # Avança o tempo global do ciclo de dia e noite continuamente com base no dt
        self.time_of_day = (self.time_of_day + dt * 0.008) % 1.0
        # Calcula o fator de escuridão da noite (night_factor) utilizando uma função senoidal contínua
        self.night_factor = (math.sin(self.time_of_day * math.pi * 2 - math.pi / 2) + 1.0) / 2.0

        # Recupera as configurações da ilha atual
        isl = ISLAND_CONFIGS[self.current_island]
        # Atualiza as posições das gotas de chuva caso a ilha atual tenha chuva ativada
        if isl["rain"]:
            for drop in self.rain_drops:
                drop.update(dt)

        # Atualiza e limpa as partículas visuais ativas cuja vida útil tenha esgotado
        for p in self.particles[:]:
            p.update(dt)
            if p.lifetime <= 0:
                self.particles.remove(p)

        # Executa a lógica específica do estado de exploração livre do mapa
        if self.state == "EXPLORE":
            # Filtra os objetos do ambiente que possuem raio de colisão ativo
            obstacles = [obj for obj in self.environment if obj.get("radius", 0) > 0]
            # Processa os inputs de movimento do jogador passando os obstáculos para colisão
            self.player.handle_input(dt, obstacles)
            # Atualiza a posição e o balanço da câmera virtual 3D com base no jogador
            self.camera.update(self.player.pos, self.player.is_moving, dt, self.player.is_running)

            # Atualiza a movimentação autônoma de cada Pokémon selvagem presente no mapa
            for poke in self.pokemons:
                poke.update(dt)
                # Reposiciona o Pokémon caso ele se afaste demais da posição atual do jogador
                if (poke.pos - self.player.pos).length() > 95:
                    poke.pos.x = self.player.pos.x + random.uniform(-50, 50)
                    poke.pos.z = self.player.pos.z + random.uniform(-50, 50)

            # Reposiciona elementos de cenário que fiquem muito distantes do jogador para otimizar o mundo aberto
            for obj in self.environment:
                if (obj["pos"] - self.player.pos).length() > 140:
                    obj["pos"].x = self.player.pos.x + random.uniform(-120, 120)
                    obj["pos"].z = self.player.pos.z + random.uniform(-120, 120)

        # Executa a lógica específica do estado de batalha
        elif self.state == "BATTLE":
            # Controla a oscilação da barra de mira caso o estado da bola seja ocioso (IDLE)
            if self.ball_state == "IDLE":
                # Incrementa o temporizador de mira baseado na velocidade calculada
                self.aim_timer += dt * self.aim_speed
                # Define os limites esquerdo e direito da barra de movimento da mira na tela
                min_x, max_x = self.w * 0.2, self.w * 0.8
                # Calcula a coordenada X atual da mira utilizando uma função senoidal suave entre os limites
                self.aim_x = min_x + (math.sin(self.aim_timer) + 1.0) / 2.0 * (max_x - min_x)

            # Controla a animação de voo da Pokébola pelo ar até atingir o alvo
            elif self.ball_state == "AIR":
                # Incrementa o temporizador de voo da bola
                self.ball_air_timer += dt * 2.2
                # Verifica se o voo da bola chegou ao fim (1.0)
                if self.ball_air_timer >= 1.0:
                    self.ball_air_timer = 1.0
                    # Resolve a lógica de captura ao término do voo
                    self.resolve_capture_logic()
                else:
                    # Interpola linearmente a posição atual da bola entre a largada e o alvo
                    self.ball_current_pos = self.ball_start_pos.lerp(self.ball_target_pos, self.ball_air_timer)
                    # Adiciona um arco parabólico vertical subtraindo o valor senoidal da altura
                    self.ball_current_pos.y -= math.sin(self.ball_air_timer * math.pi) * 140

            # Controla a animação de balanço da Pokébola após tentar capturar o Pokémon
            elif self.ball_state == "SHAKING":
                # Incrementa o temporizador de balanço
                self.shake_timer += dt
                # Verifica se passou o intervalo de tempo para cada balanço (0.5 segundos)
                if self.shake_timer >= 0.5:
                    self.shake_timer = 0.0
                    self.shake_count += 1
                    # Toca um som curto a cada balanço da bola
                    SoundManager.play_tone(300, 0.05)
                    # Verifica se completou os 3 balanços necessários para finalizar a captura
                    if self.shake_count >= 3:
                        self.finalize_capture()

    # Aplica sombreamento e mistura de cores nas entidades baseado na distância (dz) e no ciclo de dia/noite
    def get_shaded_color(self, base_color, dz):
        # Recupera as configurações da ilha atual
        isl = ISLAND_CONFIGS[self.current_island]
        # Calcula o fator de neblina (fog) com base na profundidade (dz) do objeto na tela
        fog_factor = min(1.0, max(0.0, (dz - 10.0) / 80.0))
        # Calcula a cor do céu atual interpolada entre dia e noite
        sky_color = lerp_color(isl["sky_day"], isl["sky_night"], self.night_factor)
        # Cria uma mescla da cor do céu com a cor de neblina específica da ilha
        fog_blend = lerp_color(sky_color, isl["fog_color"], 0.4)
        
        # Aplica o escurecimento na cor base do objeto proporcionalmente ao fator da noite
        lit_color = lerp_color(base_color, (base_color[0]*0.2, base_color[1]*0.2, base_color[2]*0.3), self.night_factor)
        # Retorna a cor final misturada com a neblina de acordo com a distância (dz)
        return lerp_color(lit_color, fog_blend, fog_factor)

    # Desenha a sombra elíptica projetada no chão abaixo das entidades do jogo
    def draw_shadow(self, sx, sy, width, height):
        # Redimensiona a superfície padrão de sombra com base nas dimensões informadas com segurança
        scaled = pygame.transform.scale(self.shadow_surf, (max(1, int(width)), max(1, int(height))))
        # Desenha a sombra redimensionada na tela centralizada na posição especificada
        screen.blit(scaled, (sx - width // 2, sy - height // 2))

    # Desenha o minimapa do radar no canto superior direito da tela de exploração
    def draw_minimap(self):
        # Define o tamanho padrão do minimapa quadrado
        map_size = 150
        # Calcula a coordenada X do minimapa alinhada à direita da tela
        map_x = self.w - map_size - 20
        # Define a coordenada Y superior do minimapa
        map_y = 70

        # Cria uma superfície gráfica temporária com suporte a transparência para o minimapa
        surf = pygame.Surface((map_size, map_size), pygame.SRCALPHA)
        # Preenche o fundo do minimapa com uma cor escura semitransparente
        surf.fill((15, 25, 20, 215))
        # Desenha a borda retangular ao redor do minimapa
        pygame.draw.rect(surf, COLOR_ACCENT, (0, 0, map_size, map_size), 2, border_radius=8)

        # Calcula o ponto central exato do minimapa
        center = map_size // 2
        # Define o fator de escala de distância do radar
        scale = 1.6

        # Desenha um ponto azul representando a posição central do jogador no minimapa
        pygame.draw.circle(surf, (80, 160, 255), (center, center), 5)

        # Itera por cada Pokémon presente no mapa para exibições de pontos no radar
        for poke in self.pokemons:
            # Calcula a diferença de coordenadas em relação ao jogador e aplica a escala
            dx = (poke.pos.x - self.player.pos.x) * scale
            dz = (poke.pos.z - self.player.pos.z) * scale
            # Mapeia para as coordenadas 2D relativas ao centro do minimapa
            px, py = int(center + dx), int(center - dz)

            # Verifica se o ponto está dentro dos limites visíveis de dentro do minimapa
            if 3 <= px <= map_size - 3 and 3 <= py <= map_size - 3:
                # Define a cor do ponto (amarelo se for Shiny, vermelho para comum)
                col = COLOR_SHINY if poke.is_shiny else (235, 65, 65)
                # Desenha o ponto indicativo do Pokémon no minimapa
                pygame.draw.circle(surf, col, (px, py), 3)

        # Copia a superfície final do minimapa para a tela principal do jogo
        screen.blit(surf, (map_x, map_y))

    # Desenha o sprite gráfico detalhado do jogador na tela durante a exploração 3D
    def draw_player(self, sx, sy, scale, dz):
        # Calcula o tamanho proporcional do jogador baseado na escala de distância (dz)
        s = max(10, int(26 * scale / 25))
        # Desenha a sombra elíptica abaixo dos pés do jogador
        self.draw_shadow(sx, sy, s * 2.8, s * 1.2)

        # Obtém as cores sombreadas e ajustadas para a roupa, calça, pele, boné e sapatos do jogador
        shirt_col = self.get_shaded_color((35, 120, 240), dz)
        pants_col = self.get_shaded_color((40, 50, 70), dz)
        skin_col = self.get_shaded_color((255, 210, 170), dz)
        cap_col = self.get_shaded_color((230, 40, 40), dz)
        shoe_col = self.get_shaded_color((60, 60, 60), dz)

        # Calcula o deslocamento das pernas para animar os passos caso o jogador esteja se movimentando
        leg_offset = int(math.sin(self.camera.walk_timer) * 4) if self.player.is_moving else 0
        # Desenha a perna esquerda do jogador
        pygame.draw.rect(screen, pants_col, (sx - s//3 - 2, sy - s//2, s//3, s//2 + leg_offset), border_radius=2)
        # Desenha a perna direita do jogador
        pygame.draw.rect(screen, pants_col, (sx + 1, sy - s//2, s//3, s//2 - leg_offset), border_radius=2)
        
        # Desenha o sapato esquerdo
        pygame.draw.rect(screen, shoe_col, (sx - s//3 - 4, sy + leg_offset, s//3 + 2, 4))
        # Desenha o sapato direito
        pygame.draw.rect(screen, shoe_col, (sx, sy - leg_offset, s//3 + 2, 4))

        # Desenha o tronco/camisa do jogador
        pygame.draw.rect(screen, shirt_col, (sx - s//2, sy - s * 1.3, s, s * 0.8), border_radius=4)

        # Desenha a cabeça do jogador
        pygame.draw.circle(screen, skin_col, (sx, sy - s * 1.6), s // 2)
        # Desenha o formato do boné na cabeça do jogador
        pygame.draw.arc(screen, cap_col, (sx - s//2, sy - s * 1.9, s, s), 0, math.pi, max(2, s//4))
        # Desenha a aba frontal do boné
        pygame.draw.rect(screen, cap_col, (sx, sy - s * 1.75, s * 0.6, 3))

        # Verifica se o jogador está montado na bicicleta para desenhar o veículo adicional
        if self.player.on_bike:
            # Desenha a roda traseira da bicicleta
            pygame.draw.circle(screen, COLOR_BLACK, (sx - s, sy - s//3), s//2, 2)
            # Desenha a roda dianteira da bicicleta
            pygame.draw.circle(screen, COLOR_BLACK, (sx + s, sy - s//3), s//2, 2)
            # Desenha o quadro principal da bicicleta
            pygame.draw.line(screen, COLOR_ACCENT, (sx - s, sy - s//3), (sx + s, sy - s//3), 3)

    # Desenha o sprite procedural característico de cada espécie de Pokémon na tela
    def draw_pokemon_sprite(self, sx, sy, scale, poke, dz):
        # Calcula o tamanho proporcional do Pokémon baseado na escala
        s = max(12, int(28 * scale / 25))
        # Desenha a sombra sob o Pokémon
        self.draw_shadow(sx, sy, s * 3.0, s * 1.3)

        # Obtém as cores do corpo e o tom mais escuro do Pokémon com sombreamento aplicado
        body_col = self.get_shaded_color(poke.color, dz)
        darker_col = self.get_shaded_color((max(0, poke.color[0]-50), max(0, poke.color[1]-50), max(0, poke.color[2]-50)), dz)

        # Adiciona partículas de brilho contínuas ao redor caso o Pokémon seja Shiny
        if poke.is_shiny and random.random() < 0.35:
            self.particles.append(Particle(sx + random.uniform(-s, s), sy - random.uniform(0, s*2), COLOR_SHINY, 0, -1.2, 0.4))

        # Desenha formas geométricas específicas customizadas para cada espécie de Pokémon
        if poke.name == "Eevee":
            pygame.draw.polygon(screen, body_col, [(sx - s*0.9, sy - s*1.8), (sx - s*0.4, sy - s*1.1), (sx - s*0.1, sy - s*1.4)])
            pygame.draw.polygon(screen, body_col, [(sx + s*0.9, sy - s*1.8), (sx + s*0.4, sy - s*1.1), (sx + s*0.1, sy - s*1.4)])
            pygame.draw.ellipse(screen, body_col, (sx - s*0.9, sy - s*1.2, s*1.8, s*1.3))
            pygame.draw.circle(screen, COLOR_WHITE, (sx, sy - s*0.5), s*0.5)
        elif poke.name in ["Pikachu", "Raichu"]:
            pygame.draw.polygon(screen, body_col, [(sx - s*0.8, sy - s*1.8), (sx - s*0.3, sy - s*1.1), (sx - s*0.1, sy - s*1.4)])
            pygame.draw.polygon(screen, body_col, [(sx + s*0.8, sy - s*1.8), (sx + s*0.3, sy - s*1.1), (sx + s*0.1, sy - s*1.4)])
            pygame.draw.ellipse(screen, body_col, (sx - s, sy - s*1.2, s*2, s*1.3))
            pygame.draw.circle(screen, (240, 50, 50), (sx - s*0.5, sy - s*0.6), max(2, s//4))
            pygame.draw.circle(screen, (240, 50, 50), (sx + s*0.5, sy - s*0.6), max(2, s//4))
        elif poke.name in ["Bulbasaur", "Ivysaur", "Venusaur"]:
            pygame.draw.ellipse(screen, (70, 150, 90), (sx - s*0.6, sy - s*1.6, s*1.2, s*0.9))
            pygame.draw.ellipse(screen, body_col, (sx - s*1.1, sy - s*1.1, s*2.2, s*1.2))
        elif poke.name in ["Squirtle", "Wartortle", "Blastoise", "Psyduck", "Golduck", "Poliwag", "Poliwrath", "Vaporeon"]:
            pygame.draw.circle(screen, body_col, (sx, sy - s*0.8), s)
            pygame.draw.ellipse(screen, darker_col, (sx - s*0.7, sy - s*0.5, s*1.4, s*0.7))
        elif poke.name in ["Charmander", "Charmeleon", "Charizard", "Magmar", "Arcanine"]:
            pygame.draw.ellipse(screen, body_col, (sx - s*0.9, sy - s*1.3, s*1.8, s*1.4))
            pygame.draw.polygon(screen, (255, 140, 0), [(sx + s*0.8, sy - s*0.5), (sx + s*1.5, sy - s*1.1), (sx + s*1.1, sy - s*0.2)])
        else:
            pygame.draw.ellipse(screen, body_col, (sx - s*1.2, sy - s*1.4, s*2.4, s*1.5))
            pygame.draw.circle(screen, body_col, (sx, sy - s*1.5), s*0.7)

        # Desenha os olhos detalhados no rosto do Pokémon
        pygame.draw.circle(screen, COLOR_BLACK, (sx - s//3, sy - s*0.8), max(2, s//5))
        pygame.draw.circle(screen, COLOR_BLACK, (sx + s//3, sy - s*0.8), max(2, s//5))
        pygame.draw.circle(screen, COLOR_WHITE, (sx - s//3 - 1, sy - s*0.8 - 1), max(1, s//10))
        pygame.draw.circle(screen, COLOR_WHITE, (sx + s//3 - 1, sy - s*0.8 - 1), max(1, s//10))

    # Desenha o sprite circular detalhado de uma Pokébola na tela (usado na batalha)
    def draw_pokeball_sprite(self, sx, sy, radius, btype="Pokébola"):
        # Recupera a cor específica do tipo de Pokébola no inventário
        col = self.inventory[btype]["color"]
        # Desenha o círculo principal da metade superior da Pokébola
        pygame.draw.circle(screen, col, (sx, sy), radius)
        # Desenha a metade inferior branca da Pokébola cobrindo a parte de baixo
        pygame.draw.rect(screen, COLOR_WHITE, (sx - radius, sy, radius * 2, radius))
        # Desenha o contorno circular preto ao redor da Pokébola
        pygame.draw.circle(screen, COLOR_WHITE, (sx, sy), radius, 2)
        # Desenha a linha divisória preta horizontal central da Pokébola
        pygame.draw.line(screen, COLOR_BLACK, (sx - radius, sy), (sx + radius, sy), 3)
        # Desenha o botão central circular preto da Pokébola
        pygame.draw.circle(screen, COLOR_BLACK, (sx, sy), max(3, radius // 3))
        # Desenha o detalhe interno branco do botão central
        pygame.draw.circle(screen, COLOR_WHITE, (sx, sy), max(1, radius // 5))

    # Desenha a interface gráfica completa da tela da loja do jogo
    def draw_shop_screen(self):
        # Preenche o fundo da tela com uma cor escura sólida
        screen.fill((20, 25, 35))
        # Define o retângulo principal do painel central da loja
        shop_rect = pygame.Rect(self.w//2 - 380, self.h//2 - 320, 760, 640)
        # Desenha o retângulo preenchido do painel da loja
        pygame.draw.rect(screen, COLOR_PANEL, shop_rect, border_radius=15)
        # Desenha a borda amarela ao redor do painel da loja
        pygame.draw.rect(screen, COLOR_ACCENT, shop_rect, 3, border_radius=15)

        # Renderiza o título principal da loja
        title = FONT_TITLE.render("LOJA SAFARI DE ITENS E MELHORIAS", True, COLOR_ACCENT)
        screen.blit(title, (self.w//2 - title.get_width()//2, shop_rect.y + 20))

        # Renderiza o texto informando a quantidade de moedas atuais do jogador
        coins_txt = FONT_BODY.render(f"Suas Moedas: {self.coins} 🪙", True, COLOR_WHITE)
        screen.blit(coins_txt, (self.w//2 - coins_txt.get_width()//2, shop_rect.y + 55))

        # Calcula o custo atualizado da melhoria de foco de mira
        focus_cost = (self.player.focus_upgrade + 1) * 55
        # Calcula o custo atualizado do amuleto da sorte
        charm_cost = (self.player.perks["luck_charm"] + 1) * 120
        # Lista contendo todas as opções de itens e melhorias disponíveis para compra na loja
        items = [
            (1, "[1] 5x POKÉBOLA (Básica)", "Custo: 20 Moedas", "Taxa de captura padrão."),
            (2, "[2] 3x SUPER BALL (+20% Chance)", "Custo: 50 Moedas", "Taxa melhorada para pokémons médios."),
            (3, "[3] 2x ULTRA BALL (+40% Chance)", "Custo: 100 Moedas", "Alta eficiência para raros e fortes."),
            (4, "[4] 1x MASTER BALL (100% Captura)", "Custo: 300 Moedas", "Captura garantida sem falhas!"),
            (5, "[5] MIRA DE PRECISÃO (Foco +1)", f"Custo: {focus_cost} Moedas", "Reduz a velocidade da mira."),
            (6, "[6] AMULETO DA SORTE (Shiny+)", f"Custo: {charm_cost} Moedas", "Melhora bônus passivo de raros.")
        ]

        # Reseta a lista de retângulos clicáveis da loja
        self.shop_rects = []
        start_y = shop_rect.y + 95
        # Obtém a posição atual do cursor do mouse na tela
        mouse_pos = pygame.mouse.get_pos()

        # Itera por cada item da lista para desenhar suas respectivas caixas e textos
        for num, name, cost, desc in items:
            # Define o retângulo clicável para a linha do item atual
            item_rect = pygame.Rect(shop_rect.x + 30, start_y, 700, 72)
            # Armazena o retângulo e o número do item na lista de rects clicáveis
            self.shop_rects.append((item_rect, num))

            # Verifica se o mouse está sobre o retângulo do item (efeito hover)
            is_hover = item_rect.collidepoint(mouse_pos)
            bg_color = (40, 55, 70) if is_hover else (30, 40, 50)

            # Desenha o fundo da caixa do item
            pygame.draw.rect(screen, bg_color, item_rect, border_radius=8)
            # Desenha a borda da caixa do item, destacando caso o mouse esteja em cima
            pygame.draw.rect(screen, COLOR_ACCENT if is_hover else (65, 80, 100), item_rect, 1, border_radius=8)

            # Renderiza os textos de nome, custo e descrição do item
            t_name = FONT_BODY.render(name, True, COLOR_ACCENT)
            t_cost = FONT_BODY.render(cost, True, (46, 204, 113))
            t_desc = FONT_SMALL.render(desc, True, (190, 190, 190))

            # Posiciona e desenha os textos dentro da caixa do item
            screen.blit(t_name, (item_rect.x + 15, item_rect.y + 10))
            screen.blit(t_cost, (item_rect.x + 480, item_rect.y + 10))
            screen.blit(t_desc, (item_rect.x + 15, item_rect.y + 38))
            start_y += 80

        # Renderiza o texto de instrução para sair da loja
        exit_txt = FONT_BODY.render("Pressione [M] ou [ESC] para Voltar", True, COLOR_WHITE)
        screen.blit(exit_txt, (self.w//2 - exit_txt.get_width()//2, shop_rect.y + 590))

    # Desenha a interface gráfica do menu de seleção e desbloqueio de ilhas
    def draw_islands_menu(self):
        # Preenche o fundo da tela com cor escura
        screen.fill((18, 22, 30))
        # Define o retângulo do painel central do menu de ilhas
        panel = pygame.Rect(self.w//2 - 350, self.h//2 - 270, 700, 540)
        # Desenha o painel e sua borda amarela de destaque
        pygame.draw.rect(screen, COLOR_PANEL, panel, border_radius=12)
        pygame.draw.rect(screen, COLOR_ACCENT, panel, 2, border_radius=12)

        # Renderiza o título do menu de ilhas
        title = FONT_TITLE.render("SELEÇÃO DE ILHAS SAFARI", True, COLOR_ACCENT)
        screen.blit(title, (self.w//2 - title.get_width()//2, panel.y + 20))

        # Reseta a lista de retângulos clicáveis de ilhas
        self.island_rects = []
        y = panel.y + 80
        # Obtém a posição atual do mouse
        mouse_pos = pygame.mouse.get_pos()

        # Itera por cada ilha cadastrada no dicionário global de configurações
        for i_id, info in ISLAND_CONFIGS.items():
            # Define o retângulo do card da ilha atual
            card = pygame.Rect(panel.x + 30, y, 640, 85)
            # Armazena o card e o ID da ilha na lista de áreas clicáveis
            self.island_rects.append((card, i_id))

            # Verifica se a ilha já foi desbloqueada pelo jogador
            unlocked = i_id in self.unlocked_islands
            # Verifica se o mouse está em cima do card (hover)
            is_hover = card.collidepoint(mouse_pos)
            bg_col = (40, 60, 50) if unlocked else (35, 35, 40)
            if is_hover: bg_col = (55, 80, 70) if unlocked else (50, 45, 55)

            # Desenha o fundo e a borda do card da ilha
            pygame.draw.rect(screen, bg_col, card, border_radius=8)
            pygame.draw.rect(screen, COLOR_ACCENT if unlocked else (90, 90, 90), card, 1, border_radius=8)

            # Renderiza o texto com o nome da ilha e a faixa de nível dos Pokémon dela
            t_name = FONT_BODY.render(f"{info['name']} (Nível: {info['min_poke_lvl']} - {info['max_poke_lvl']})", True, COLOR_WHITE)
            screen.blit(t_name, (card.x + 15, card.y + 15))

            # Verifica se a ilha está desbloqueada para exibir o status correspondente
            if unlocked:
                status_txt = "LOCAL ATUAL" if i_id == self.current_island else "VIAJAR"
                t_status = FONT_BODY.render(status_txt, True, COLOR_HP)
                screen.blit(t_status, (card.x + 490, card.y + 25))
            else:
                # Exibe os requisitos de nível e custo de moedas caso a ilha esteja bloqueada
                t_req = FONT_SMALL.render(f"Requer: Nível {info['min_lvl']} | Custo: {info['cost']} Moedas", True, COLOR_HP_BG)
                screen.blit(t_req, (card.x + 15, card.y + 48))

            y += 100

        # Renderiza o texto para sair do menu de ilhas
        exit_txt = FONT_BODY.render("Pressione [I] ou [ESC] para Voltar", True, COLOR_WHITE)
        screen.blit(exit_txt, (self.w//2 - exit_txt.get_width()//2, panel.y + 480))

    # Desenha a interface da Pokédex exibindo o progresso de capturas e informações de evolução dos Pokémon
    def draw_pokedex(self):
        # Preenche o fundo da tela
        screen.fill((18, 22, 30))
        # Define o painel central da Pokédex
        panel = pygame.Rect(self.w//2 - 400, self.h//2 - 320, 800, 640)
        # Desenha o painel com borda amarela
        pygame.draw.rect(screen, COLOR_PANEL, panel, border_radius=12)
        pygame.draw.rect(screen, COLOR_ACCENT, panel, 2, border_radius=12)

        # Renderiza o título da Pokédex
        title = FONT_TITLE.render("POKÉDEX SAFARI & EVOLUÇÕES", True, COLOR_ACCENT)
        screen.blit(title, (self.w//2 - title.get_width()//2, panel.y + 20))

        y = panel.y + 70
        # Itera por cada espécie de Pokémon registrada na Pokédex do jogador
        for name, data in self.pokedex.items():
            # Define o retângulo da linha de registro da espécie
            card = pygame.Rect(panel.x + 40, y, 720, 42)
            pygame.draw.rect(screen, (30, 40, 55), card, border_radius=8)
            
            # Recupera as informações de evolução do Pokémon nas estatísticas base
            evo_info = PokemonEntity.BASE_STATS[name]
            evo_text = f"Evolui Lv.{evo_info['evolves_at']}" if evo_info['evolves_to'] else "Forma Final"
            
            # Renderiza os textos informando nome, quantidade vistos, capturados e dados de evolução
            t_name = FONT_BODY.render(name, True, COLOR_WHITE)
            t_seen = FONT_SMALL.render(f"Vistos: {data['seen']}", True, (170, 190, 210))
            t_caught = FONT_SMALL.render(f"Capturados: {data['caught']}", True, COLOR_HP)
            t_evo = FONT_SMALL.render(evo_text, True, COLOR_ACCENT)

            # Posiciona e desenha as informações na linha do card
            screen.blit(t_name, (card.x + 15, card.y + 10))
            screen.blit(t_seen, (card.x + 220, card.y + 12))
            screen.blit(t_caught, (card.x + 360, card.y + 12))
            screen.blit(t_evo, (card.x + 540, card.y + 12))
            y += 46

        # Renderiza o texto para retornar ao jogo
        exit_txt = FONT_BODY.render("Pressione [P] ou [ESC] para Voltar ao Jogo", True, COLOR_WHITE)
        screen.blit(exit_txt, (self.w//2 - exit_txt.get_width()//2, panel.y + 590))

    # Desenha a interface completa da tela de batalha contra o Pokémon selvagem
    def draw_battle_screen(self):
        # Recupera as configurações da ilha atual para definir as cores de céu e chão da batalha
        isl = ISLAND_CONFIGS[self.current_island]
        bg_sky = lerp_color(isl["sky_day"], isl["sky_night"], self.night_factor)
        # Preenche o fundo da tela de batalha com a cor do céu interpolada pelo ciclo de dia/noite
        screen.fill(bg_sky)
        
        ground_col = lerp_color(isl["ground_day"], isl["ground_night"], self.night_factor)
        # Desenha a elipse representando o chão da arena de batalha
        pygame.draw.ellipse(screen, ground_col, (self.w//2 - 320, self.h//2 - 60, 640, 380))

        poke = self.battle_pokemon
        center_x, center_y = int(self.poke_target_pos.x), int(self.poke_target_pos.y)

        # Desenha o sprite do Pokémon na arena caso a bola não esteja no estado de balanço final
        if self.ball_state != "SHAKING":
            self.draw_pokemon_sprite(center_x, center_y, 90.0, poke, dz=10.0)

        # Desenha a barra de mira oscilante caso o estado da bola esteja ocioso (IDLE)
        if self.ball_state == "IDLE":
            bar_y = self.h - 170
            min_x, max_x = int(self.w * 0.2), int(self.w * 0.8)
            # Desenha a barra de fundo vermelha da mira
            pygame.draw.rect(screen, (180, 40, 40), (min_x, bar_y - 8, max_x - min_x, 16), border_radius=8)
            # Desenha a zona central verde de acerto perfeito da mira
            pygame.draw.rect(screen, (46, 204, 113), (self.w//2 - 35, bar_y - 8, 70, 16), border_radius=4)

            # Desenha o cursor indicador da mira se movendo sobre a barra
            aim_x_int = int(self.aim_x)
            pygame.draw.line(screen, COLOR_WHITE, (aim_x_int, center_y - 110), (aim_x_int, bar_y + 15), 2)
            pygame.draw.circle(screen, COLOR_ACCENT, (aim_x_int, bar_y), 12)

        # Define as coordenadas atuais da Pokébola na tela de batalha
        bx, by = int(self.ball_current_pos.x), int(self.ball_current_pos.y)
        # Adiciona tremor aleatório à Pokébola caso esteja no estado de balanço (SHAKING)
        if self.ball_state == "SHAKING":
            bx += random.randint(-4, 4)
            by = center_y

        # Calcula o raio e desenha o sprite da Pokébola na tela de batalha
        ball_r = 22 if self.ball_state == "IDLE" else max(10, int(22 * (1.0 - self.ball_air_timer * 0.5)))
        self.draw_pokeball_sprite(bx, by, ball_r, self.selected_ball)

        # Define o retângulo do painel de informações do Pokémon rival na batalha
        card_rect = pygame.Rect(self.w//2 - 180, 35, 360, 105)
        pygame.draw.rect(screen, COLOR_PANEL, card_rect, border_radius=10)

        # Renderiza o nome e nível do Pokémon rival na batalha
        shiny_lbl = " ★ SHINY" if poke.is_shiny else ""
        name_txt = FONT_BODY.render(f"{poke.name} (Lv.{poke.level}){shiny_lbl}", True, COLOR_SHINY if poke.is_shiny else COLOR_WHITE)
        screen.blit(name_txt, (card_rect.x + 15, card_rect.y + 8))

        # Desenha a barra de vida (HP) atual do Pokémon rival
        hp_ratio = poke.hp / poke.max_hp
        pygame.draw.rect(screen, COLOR_HP_BG, (card_rect.x + 15, card_rect.y + 42, 330, 16), border_radius=4)
        pygame.draw.rect(screen, COLOR_HP, (card_rect.x + 15, card_rect.y + 42, int(330 * hp_ratio), 16), border_radius=4)

        # Renderiza a mensagem do log de texto atual da batalha
        log_txt = FONT_SMALL.render(self.battle_log, True, COLOR_ACCENT)
        screen.blit(log_txt, (card_rect.x + 15, card_rect.y + 72))

        # Renderiza as instruções de atalhos e a bola selecionada na parte inferior da tela de batalha
        sel_txt = FONT_SMALL.render("[1-4] Selecionar Bola | [ESPAÇO] Arremessar", True, COLOR_WHITE)
        screen.blit(sel_txt, (30, self.h - 70))
        cur_ball = FONT_BODY.render(f"Bola Selecionada: {self.selected_ball} ({self.inventory[self.selected_ball]['count']})", True, COLOR_ACCENT)
        screen.blit(cur_ball, (30, self.h - 40))

    # Método central de renderização gráfica que desenha a tela correspondente ao estado atual do jogo
    def draw(self):
        # Verifica se o estado atual é a loja para desenhar sua tela específica
        if self.state == "SHOP":
            self.draw_shop_screen()
        # Verifica se o estado é o menu de seleção de ilhas
        elif self.state == "ISLANDS":
            self.draw_islands_menu()
        # Verifica se o estado é a visualização da Pokédex
        elif self.state == "POKEDEX":
            self.draw_pokedex()
        # Verifica se o estado é o modo de batalha
        elif self.state == "BATTLE":
            self.draw_battle_screen()
        # Caso contrário, renderiza o mundo aberto 3D de exploração livre
        else:
            # Recupera as configurações da ilha atual
            isl = ISLAND_CONFIGS[self.current_island]
            sky_col = lerp_color(isl["sky_day"], isl["sky_night"], self.night_factor)
            ground_col = lerp_color(isl["ground_day"], isl["ground_night"], self.night_factor)

            # Preenche o fundo da tela com a cor do céu e desenha o chão a partir da linha do horizonte
            screen.fill(sky_col)
            horizon_y = int(self.h // 3.2 + (self.camera.offset_y - self.camera.base_offset_y) * 10)
            pygame.draw.rect(screen, ground_col, (0, horizon_y, self.w, self.h - horizon_y))

            # Inicializa a fila de renderização (ordenada por profundidade para efeito painter's algorithm)
            render_queue = []
            # Projeta e adiciona o jogador à fila de renderização caso esteja visível
            proj = self.camera.project(self.player.pos)
            if proj: render_queue.append(("PLAYER", proj, self.player.pos))

            # Projeta e adiciona cada Pokémon selvagem à fila de renderização
            for poke in self.pokemons:
                proj = self.camera.project(poke.pos)
                if proj: render_queue.append(("POKEMON", proj, poke))

            # Projeta e adiciona cada elemento de cenário à fila de renderização
            for obj in self.environment:
                proj = self.camera.project(obj["pos"])
                if proj: render_queue.append(("ENV", proj, obj))

            # Ordena a fila de renderização pelo valor de profundidade (dz) em ordem decrescente (do mais longe para o mais perto)
            render_queue.sort(key=lambda item: item[1][2], reverse=True)

            # Itera por cada item ordenado na fila para desenhá-los corretamente na ordem de profundidade 3D
            for item_type, proj, data in render_queue:
                sx, sy, dz, scale = proj
                # Desenha o jogador
                if item_type == "PLAYER":
                    self.draw_player(sx, sy, scale, dz)
                # Desenha o Pokémon selvagem e seu nome flutuante caso o jogador esteja próximo o suficiente
                elif item_type == "POKEMON":
                    poke = data
                    self.draw_pokemon_sprite(sx, sy, scale, poke, dz)
                    if (poke.pos - self.player.pos).length() < self.player.interaction_range:
                        lbl_col = self.get_shaded_color(COLOR_WHITE, dz)
                        lbl = FONT_SMALL.render(f"{poke.name} (Lv.{poke.level})", True, lbl_col)
                        screen.blit(lbl, (sx - lbl.get_width()//2, sy - int(42 * scale / 25)))
                # Desenha os elementos específicos do ambiente (árvores, palmeiras, rochas, cristais)
                elif item_type == "ENV":
                    obj = data
                    if obj["type"] == "TREE":
                        h = int(obj["h"] * scale / 16)
                        w = max(5, int(12 * scale / 22))
                        self.draw_shadow(sx, sy, w * 3.5, w * 1.5)
                        trunk_col = self.get_shaded_color((95, 55, 30), dz)
                        leaves_col = self.get_shaded_color((30, 115, 40), dz)
                        leaves_top = self.get_shaded_color((40, 145, 55), dz)
                        pygame.draw.rect(screen, trunk_col, (sx - w//2, sy - h, w, h), border_radius=2)
                        pygame.draw.circle(screen, leaves_col, (sx, sy - h), int(w * 2.2))
                        pygame.draw.circle(screen, leaves_top, (sx - w//2, sy - h - w//2), int(w * 1.5))
                        pygame.draw.circle(screen, leaves_top, (sx + w//2, sy - h - w//2), int(w * 1.5))
                    elif obj["type"] == "PALM":
                        h = int(obj["h"] * scale / 16)
                        w = max(4, int(10 * scale / 22))
                        self.draw_shadow(sx, sy, w * 3.5, w * 1.5)
                        trunk_col = self.get_shaded_color((130, 100, 50), dz)
                        leaves_col = self.get_shaded_color((35, 150, 55), dz)
                        pygame.draw.rect(screen, trunk_col, (sx - w//2, sy - h, w, h))
                        pygame.draw.ellipse(screen, leaves_col, (sx - w*2.8, sy - h - w*1.2, w*5.6, w*2.4))
                        pygame.draw.ellipse(screen, leaves_col, (sx - w*2.2, sy - h - w*2.2, w*4.4, w*2.2))
                    elif obj["type"] == "LAVA_ROCK":
                        r = max(5, int(obj["radius"] * 9 * scale / 22))
                        self.draw_shadow(sx, sy, r * 2.6, r * 1.3)
                        rock_col = self.get_shaded_color((50, 50, 55), dz)
                        lava_col = self.get_shaded_color((250, 80, 20), dz)
                        pygame.draw.circle(screen, rock_col, (sx, sy - r//3), r)
                        pygame.draw.circle(screen, lava_col, (sx, sy - r//3), r // 2)
                    elif obj["type"] == "CRYSTAL":
                        r = max(5, int(obj["radius"] * 8 * scale / 22))
                        self.draw_shadow(sx, sy, r * 2.2, r * 1.1)
                        crystal_col = self.get_shaded_color((170, 90, 230), dz)
                        pygame.draw.polygon(screen, crystal_col, [(sx, sy - r*2.5), (sx - r, sy), (sx + r, sy)])
                    elif obj["type"] == "ROCK":
                        r = max(5, int(obj["radius"] * 9 * scale / 22))
                        self.draw_shadow(sx, sy, r * 2.6, r * 1.3)
                        rock_col = self.get_shaded_color((110, 110, 120), dz)
                        pygame.draw.circle(screen, rock_col, (sx, sy - r//3), r)

            # Desenha o sistema de chuva na tela caso a ilha atual tenha chuva ativada
            if isl["rain"]:
                for drop in self.rain_drops:
                    drop.draw(screen, self.night_factor)

            # Desenha o minimapa do radar e o painel superior da interface (HUD)
            self.draw_minimap()
            self._draw_hud()

        # Desenha todas as partículas ativas presentes no mundo
        for p in self.particles:
            p.draw(screen)

        # Desenha a mensagem flutuante temporária na tela caso o temporizador esteja ativo
        if self.message_timer > 0:
            msg_surface = FONT_TITLE.render(self.message_text, True, COLOR_ACCENT)
            rect = msg_surface.get_rect(center=(self.w // 2, 105))
            bg_rect = rect.inflate(40, 14)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((10, 15, 20, 230))
            screen.blit(bg_surface, bg_rect.topleft)
            pygame.draw.rect(screen, COLOR_ACCENT, bg_rect, 2, border_radius=6)
            screen.blit(msg_surface, rect)

    # Desenha o painel superior da interface de usuário (HUD) na tela de exploração
    def _draw_hud(self):
        # Cria uma superfície semitransparente para a barra superior do HUD
        hud_surface = pygame.Surface((self.w, 52), pygame.SRCALPHA)
        hud_surface.fill(COLOR_PANEL)
        screen.blit(hud_surface, (0, 0))

        # Define strings descritivas para montaria e nome da ilha
        bike_str = " (Bicicleta)" if self.player.on_bike else ""
        isl_name = ISLAND_CONFIGS[self.current_island]["name"]
        
        # Renderiza o texto do nível atual do jogador
        txt_lvl = FONT_BODY.render(f"Lv.{self.player.level}{bike_str}", True, COLOR_WHITE)
        
        # Desenha a barra de progresso de experiência (XP) do jogador
        xp_w = 110
        xp_ratio = min(1.0, self.player.xp / self.player.xp_to_next)
        pygame.draw.rect(screen, (40, 50, 65), (140, 18, xp_w, 14), border_radius=3)
        pygame.draw.rect(screen, COLOR_XP, (140, 18, int(xp_w * xp_ratio), 14), border_radius=3)
        txt_xp = FONT_SMALL.render(f"XP: {int(self.player.xp)}/{self.player.xp_to_next}", True, COLOR_WHITE)

        # Renderiza os textos informando total de bolas, pontuação, moedas e nome da ilha atual
        txt_balls = FONT_BODY.render(f"Bolas: {self.total_balls()}", True, COLOR_WHITE)
        txt_score = FONT_BODY.render(f"Capturas: {self.score}", True, COLOR_WHITE)
        txt_coins = FONT_BODY.render(f"Moedas: {self.coins} 🪙", True, COLOR_ACCENT)
        txt_isl = FONT_BODY.render(f"Local: {isl_name}", True, COLOR_SHINY)

        # Posiciona e desenha cada elemento de texto do HUD na barra superior
        screen.blit(txt_lvl, (20, 14))
        screen.blit(txt_xp, (148, 17))
        screen.blit(txt_balls, (270, 14))
        screen.blit(txt_score, (410, 14))
        screen.blit(txt_coins, (570, 14))
        screen.blit(txt_isl, (730, 14))

        # Renderiza as informações de progresso da missão diária ativa no canto superior direito
        quest_info = f"Missão: Capturar {self.active_quest['goal']}x {self.active_quest['target']} ({self.active_quest['progress']}/{self.active_quest['goal']})"
        txt_quest = FONT_SMALL.render(quest_info, True, (255, 180, 50))
        screen.blit(txt_quest, (self.w - 380, 16))

        # Renderiza a barra inferior com todos os atalhos de teclado disponíveis para o jogador
        txt_controls = FONT_SMALL.render("[WASD] Mover | [SHIFT] Correr | [B] Bicicleta | [F] Tela Cheia | [ESPAÇO] Batalha | [M] Loja | [I] Ilhas | [P] Pokédex", True, COLOR_WHITE)
        screen.blit(txt_controls, (20, self.h - 25))

    # Método principal que executa o loop infinito de execução do jogo a 60 FPS
    def run(self):
        # Define a flag de controle do loop principal como verdadeira
        running = True
        # Loop principal do jogo executado continuamente quadro a quadro
        while running:
            # Calcula o delta tempo (dt) em segundos a cada quadro, limitando a taxa de atualização a 60 FPS
            dt = clock.tick(60) / 1000.0

            # Captura e processa todos os eventos gerados pelo usuário (teclado e mouse)
            for event in pygame.event.get():
                # Verifica se o evento é o fechamento da janela do jogo
                if event.type == pygame.QUIT:
                    running = False

                # Verifica se ocorreu um clique com o botão esquerdo do mouse
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = pygame.mouse.get_pos()
                    # Processa cliques caso o jogo esteja na tela da loja
                    if self.state == "SHOP":
                        for rect, item_num in self.shop_rects:
                            if rect.collidepoint(pos):
                                self.process_purchase(item_num)
                    # Processa cliques caso o jogo esteja no menu de seleção de ilhas
                    elif self.state == "ISLANDS":
                        for rect, i_id in self.island_rects:
                            if rect.collidepoint(pos):
                                self.change_island(i_id)

                # Verifica se alguma tecla do teclado foi pressionada
                elif event.type == pygame.KEYDOWN:
                    # Verifica se a tecla pressionada foi ESC para fechar menus ou sair do jogo
                    if event.key == pygame.K_ESCAPE:
                        if self.state in ["BATTLE", "SHOP", "POKEDEX", "ISLANDS"]:
                            self.state = "EXPLORE"
                        else:
                            running = False

                    # Verifica se a tecla F foi pressionada para alternar o modo de tela cheia
                    elif event.key == pygame.K_f:
                        self.toggle_fullscreen()

                    # Verifica se a tecla B foi pressionada para montar ou desmontar da bicicleta na exploração
                    elif event.key == pygame.K_b and self.state == "EXPLORE":
                        self.player.on_bike = not self.player.on_bike
                        self.display_message("Montaria Alterada!" if self.player.on_bike else "A pé.")

                    # Verifica se a tecla M foi pressionada para abrir ou fechar a loja
                    elif event.key == pygame.K_m:
                        if self.state == "EXPLORE": self.state = "SHOP"
                        elif self.state == "SHOP": self.state = "EXPLORE"

                    # Verifica se a tecla I foi pressionada para abrir ou fechar o menu de ilhas
                    elif event.key == pygame.K_i:
                        if self.state == "EXPLORE": self.state = "ISLANDS"
                        elif self.state == "ISLANDS": self.state = "EXPLORE"

                    # Verifica se a tecla P foi pressionada para abrir ou fechar a Pokédex
                    elif event.key == pygame.K_p:
                        if self.state == "EXPLORE": self.state = "POKEDEX"
                        elif self.state == "POKEDEX": self.state = "EXPLORE"

                    # Processa os atalhos específicos caso o jogo esteja no modo de batalha
                    elif self.state == "BATTLE":
                        if event.key in [pygame.K_1, pygame.K_KP1]: self.selected_ball = "Pokébola"
                        elif event.key in [pygame.K_2, pygame.K_KP2]: self.selected_ball = "Super Ball"
                        elif event.key in [pygame.K_3, pygame.K_KP3]: self.selected_ball = "Ultra Ball"
                        elif event.key in [pygame.K_4, pygame.K_KP4]: self.selected_ball = "Master Ball"
                        elif event.key == pygame.K_SPACE: self.throw_pokeball()

                    # Processa a tecla ESPAÇO no modo de exploração para iniciar batalha com o Pokémon mais próximo
                    elif event.key == pygame.K_SPACE and self.state == "EXPLORE":
                        closest = None
                        closest_dist = float("inf")
                        # Percorre todos os Pokémon para encontrar o mais próximo do jogador
                        for poke in self.pokemons:
                            d = (self.player.pos - poke.pos).length()
                            if d < closest_dist:
                                closest_dist = d
                                closest = poke

                        # Inicia a batalha caso o Pokémon mais próximo esteja dentro do raio de interação permitido
                        if closest and closest_dist <= self.player.interaction_range:
                            self.initiate_battle(closest)
                        else:
                            self.display_message("Aproxime-se de um Pokémon!", 1.2)

            # Executa o método de atualização lógica do motor passando o delta tempo
            self.update(dt)
            # Executa o método de renderização gráfica na tela
            self.draw()
            # Atualiza o buffer de exibição da tela exibindo os gráficos processados no monitor
            pygame.display.flip()

        # Encerra o Pygame de forma limpa ao sair do loop principal
        pygame.quit()
        # Encerra o processo do sistema operacional de forma segura
        sys.exit()

# Bloco condicional padrão em Python que verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    # Instancia a classe principal do motor do jogo SafariGameEngine
    game = SafariGameEngine()
    # Executa o método run para iniciar o loop principal do jogo
    game.run()
