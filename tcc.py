import pygame
import sys
import random

# 1. CONFIGURAÇÕES INICIAIS
pygame.init()
pygame.font.init()

LARGURA, ALTURA = 600, 450
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Pokémon: Explorar e Batalhar")

# CORES
BRANCO = (240, 240, 240)
PRETO = (20, 20, 20)
VERDE_GRAMA = (34, 139, 34)
VERDE_MATO_ALTO = (0, 100, 0)
AZUL_JOGADOR = (41, 128, 185)
AMARELO_PIKA = (241, 196, 15)
VERMELHO_CHAR = (231, 76, 60)

FONTE = pygame.font.SysFont("Arial", 20)
relogio = pygame.time.Clock()

# 2. VARIÁVEIS DO JOGO
# Estados do jogo: "MAPA" ou "BATALHA"
estado_jogo = "MAPA"

# Posição do jogador no mapa
jogador_x = 100
jogador_y = 100
velocidade = 5

# Definição do Mato Alto (Onde os Pokémons aparecem)
mato_alto = pygame.Rect(150, 100, 300, 200)

# Status dos Pokémons
vida_max = 100
vida_pika = 100
vida_char = 100
mensagem_batalha = ""

# 3. LOOP PRINCIPAL
rodando = True
while rodando:
    relogio.tick(30) # 30 Quadros por segundo
    
    # --- CAPTURA DE EVENTOS ---
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
            pygame.quit()
            sys.exit()
            
        # Controles se estiver na BATALHA
        if estado_jogo == "BATALHA" and evento.type == pygame.KEYDOWN:
            if vida_char > 0 and vida_pika > 0:
                if evento.key == pygame.K_1: # Atacar
                    dano = random.randint(15, 25)
                    vida_char -= dano
                    mensagem_batalha = f"Pikachu causou {dano} de dano!"
                    
                    # Contra-ataque do rival se ele ainda estiver vivo
                    if vida_char > 0:
                        dano_rival = random.randint(10, 20)
                        vida_pika -= dano_rival
                        mensagem_batalha += f" | Charmander causou {dano_rival} de dano!"
                
                elif evento.key == pygame.K_2: # Fugir
                    estado_jogo = "MAPA"
                    # Teleporta o jogador para fora do mato para não travar num loop de batalha
                    jogador_y += 40 
            
            # Se a batalha acabou, aperta ESPAÇO para voltar ao mapa
            elif evento.key == pygame.K_SPACE:
                if vida_char <= 0:
                    estado_jogo = "MAPA"
                    jogador_y += 40 # Tira do mato
                elif vida_pika <= 0:
                    # Se você perdeu, cura o Pikachu para você poder tentar de novo
                    vida_pika = 100
                    estado_jogo = "MAPA"
                    jogador_x, jogador_y = 100, 100

    # --- LÓGICA DO MODO MAPA ---
    if estado_jogo == "MAPA":
        # Ler teclas pressionadas para andar
        teclas = pygame.key.get_pressed()
        movendo = False
        
        if teclas[pygame.K_LEFT]:
            jogador_x -= velocidade
            movendo = True
        if teclas[pygame.K_RIGHT]:
            jogador_x += velocidade
            movendo = True
        if teclas[pygame.K_UP]:
            jogador_y -= velocidade
            movendo = True
        if teclas[pygame.K_DOWN]:
            jogador_y += velocidade
            movendo = True

        # Criar um retângulo invisível na posição atual do jogador para testar colisão
        rect_jogador = pygame.Rect(jogador_x, jogador_y, 30, 30)
        
        # Se o jogador estiver andando DENTRO do mato alto
        if movendo and mato_alto.colliderect(rect_jogador):
            # 2% de chance a cada passo de achar um Pokémon
            if random.random() < 0.02: 
                estado_jogo = "BATALHA"
                vida_char = 100 # Nasce um Charmander novinho com vida cheia!
                mensagem_batalha = "Um CHARMANDER selvagem apareceu! (1) Atacar ou (2) Fugir"

    # --- DESENHAR NA TELA ---
    tela.fill(PRETO)

    if estado_jogo == "MAPA":
        # Desenha o chão gramado
        tela.fill(VERDE_GRAMA)
        
        # Desenha a zona de Mato Alto
        pygame.draw.rect(tela, VERDE_MATO_ALTO, mato_alto)
        
        # Desenha o Jogador (Quadradinho Azul)
        pygame.draw.rect(tela, AZUL_JOGADOR, (jogador_x, jogador_y, 30, 30))
        
        # Texto de instrução no mapa
        txt_mapa = FONTE.render("Use as SETAS para andar. Entre no mato escuro!", True, BRANCO)
        tela.blit(txt_mapa, (20, 20))

    elif estado_jogo == "BATALHA":
        tela.fill(BRANCO)
        
        # Desenhar Pikachu (Jogador - Amarelo)
        pygame.draw.rect(tela, AMARELO_PIKA, (80, 200, 100, 100))
        txt_pika = FONTE.render(f"PIKACHU: {vida_pika}/{vida_max} HP", True, PRETO)
        tela.blit(txt_pika, (80, 170))
        
        # Desenhar Charmander (Inimigo - Vermelho)
        if vida_char > 0:
            pygame.draw.rect(tela, VERMELHO_CHAR, (420, 200, 100, 100))
            txt_char = FONTE.render(f"CHARMANDER: {vida_char}/{vida_max} HP", True, PRETO)
            tela.blit(txt_char, (420, 170))
        
        # Mostrar mensagens e comandos
        txt_msg = FONTE.render(mensagem_batalha, True, PRETO)
        tela.blit(txt_msg, (30, 340))
        
        # Se alguém desmaiou, mostra aviso para fechar a batalha
        if vida_char <= 0:
            txt_fim = FONTE.render("Você VENCEU! Pressione ESPAÇO para voltar ao mapa.", True, VERDE_MATO_ALTO)
            tela.blit(txt_fim, (30, 380))
        elif vida_pika <= 0:
            txt_fim = FONTE.render("Você PERDEU! Pressione ESPAÇO para reviver no início.", True, VERMELHO_CHAR)
            tela.blit(txt_fim, (30, 380))

    pygame.display.flip()
