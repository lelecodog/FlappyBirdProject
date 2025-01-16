import pygame
import os
import random
import sys
import json

# Constantes globais
TELA_LARGURA = 800
TELA_ALTURA = 800

# Inicialização do pygame
pygame.init()

# Carregar imagens
IMAGEM_CANO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'pipe.png')))
IMAGEM_CHAO = pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'base.png')))
IMAGEM_BACKGROUND = pygame.transform.scale(pygame.image.load(os.path.join('imgs', 'bg.png')), (TELA_LARGURA, TELA_ALTURA))
IMAGENS_PASSARO = [
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join('imgs', 'bird3.png'))),
]

# fonte pontos
pygame.font.init()
FONTE_PONTOS = pygame.font.SysFont('arial', 50)
FONTE_MENU = pygame.font.SysFont('arial', 30)

JOGADORES = ['ALEX', 'ARTHUR']

# Objetos do jogo
class Passaro:
    IMGS = IMAGENS_PASSARO
    # animações da rotação
    ROTACAO_MAXIMA = 25
    VELOCIDADE_ROTACAO = 20
    TEMPO_ANIMACAO = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angulo = 0
        self.velocidade = 0
        self.altura = self.y
        self.tempo = 0
        self.contagem_imagem = 0
        self.imagem = self.IMGS[0]

    def pular(self):
        self.velocidade = -10.5
        self.tempo = 0
        self.altura = self.y

    def mover(self):
        #calcular deslocamento
        self.tempo += 1
        deslocamento = 1.5 * (self.tempo**2) + self.velocidade * self.tempo

        #restringir deslocamento
        if deslocamento > 16  :
            deslocamento = 16
        elif deslocamento < 0:
            deslocamento -= 2

        self.y += deslocamento

        #angulo passaro
        if deslocamento < 0 or self.y < (self.altura + 50):
            if self.angulo < self.ROTACAO_MAXIMA:
                self.angulo = self.ROTACAO_MAXIMA
        else:
            if self.angulo > -90:
                self.angulo -= self.VELOCIDADE_ROTACAO

    def desenhar(self, tela):
        #definar qual img do passaro usar
        self.contagem_imagem += 1

        if self.contagem_imagem < self.TEMPO_ANIMACAO:
            self.imagem = self.IMGS[0]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 2:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 3:
            self.imagem = self.IMGS[2]
        elif self.contagem_imagem < self.TEMPO_ANIMACAO * 4:
            self.imagem = self.IMGS[1]
        elif self.contagem_imagem >= self.TEMPO_ANIMACAO * 4 + 1:
            self.imagem = self.IMGS[0]
            self.contagem_imagem = 0

        #quando passaro estiver caindo nao bater asa
        if self.angulo <= -80:
            self.imagem = self.IMGS[1]
            self.contagem_imagem = self.TEMPO_ANIMACAO * 2

        #desenhar a img
        imagem_rotacionada = pygame.transform.rotate(self.imagem, self.angulo)
        posicao_centro_imagem = self.imagem.get_rect(topleft=(self.x, self.y)).center
        retangulo = imagem_rotacionada.get_rect(center=posicao_centro_imagem)
        tela.blit(imagem_rotacionada, retangulo.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.imagem)

class Cano:
    DITANCIA = 300
    VELOCIDADE = 5

    def __init__(self, x):
        self.x = x
        self.altura = 0
        self.pos_topo = 0
        self.pos_base = 0
        self.CANO_TOPO = pygame.transform.flip(IMAGEM_CANO, False, True)
        self.CANO_BASE = IMAGEM_CANO
        self.passou = False
        self.definir_altura()

    def definir_altura(self):
        self.altura = random.randrange(50, 450)
        self.pos_topo = self.altura - self.CANO_TOPO.get_height()
        self.pos_base = self.altura + self.DITANCIA

    def mover(self):
        self.x -= self.VELOCIDADE

    def desenhar(self, tela):
        tela.blit(self.CANO_TOPO, (self.x, self.pos_topo))
        tela.blit(self.CANO_BASE, (self.x, self.pos_base))

    def colidir(self, passaro):
        passaro_mask = passaro.get_mask()
        topo_mask = pygame.mask.from_surface(self.CANO_TOPO)
        base_mask = pygame.mask.from_surface(self.CANO_BASE)

        ditancia_topo = (self.x - passaro.x, self.pos_topo - round(passaro.y))
        distancia_base = (self.x - passaro.x, self.pos_base - round(passaro.y))

        topo_ponto = passaro_mask.overlap(topo_mask, ditancia_topo)
        base_ponto = passaro_mask.overlap(base_mask, distancia_base)

        if base_ponto or topo_ponto:
            return True
        else:
            return False

class Chao:
    VELOCIDADE = 5
    LARGURA = IMAGEM_CHAO.get_width()
    IMAGEM = IMAGEM_CHAO

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.LARGURA

    def mover(self):
        self.x1 -= self.VELOCIDADE
        self.x2 -= self.VELOCIDADE

        if self.x1 + self.LARGURA < 0:
            self.x1 = self.x2 + self.LARGURA
        if self.x2 + self.LARGURA < 0:
            self.x2 = self.x1 + self.LARGURA

    def desenhar(self, tela):
        tela.blit(self.IMAGEM, (self.x1, self.y))
        tela.blit(self.IMAGEM, (self.x2, self.y))

def desenhar_tela(tela, passaros, canos, chao, pontos, level):
    tela.blit(IMAGEM_BACKGROUND, (0, 0))
    for passaro in passaros: # desenhar varios passaros para posteriormente criar IA que zera o jogo
        passaro.desenhar(tela)
    for canos in canos:
        canos.desenhar(tela)

    texto_pontos = FONTE_PONTOS.render(f"pontuação: {pontos}", 1, (255, 255, 255))
    tela.blit(texto_pontos, (TELA_LARGURA - 10 -texto_pontos.get_width(), 10))

    texto_nivel = FONTE_PONTOS.render(f"Nível: {level}", 1, (255, 255, 255))
    tela.blit(texto_nivel, (10, 10))

    chao.desenhar(tela)
    pygame.display.update()

def salvar_pontuacao(jogador, pontos):
    try:
        with open('ranking.json', 'r') as f:
            ranking = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ranking = []

    ranking.append({'Jogador': jogador, 'Pontos': pontos})
    ranking = sorted(ranking, key=lambda x: x['Pontos'], reverse=True)[:10]

    with open('ranking.json', 'w') as f:
        json.dump(ranking, f)

def mostrar_ranking(tela):
    try:
        with open('ranking.json', 'r') as f:
            ranking = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        ranking = []

    # carregar img e redimensiona-la
    IMAGEM_MENU = pygame.image.load(os.path.join('imgs', 'pygame_powered.png'))
    nova_largura = TELA_LARGURA // 2
    proporcao = IMAGEM_MENU.get_height() / IMAGEM_MENU.get_width()
    nova_altura = int(nova_largura * proporcao)
    IMAGEM_MENU = pygame.transform.scale(IMAGEM_MENU, (nova_largura, nova_altura))

    # Ordenar ranking
    ranking = sorted(ranking, key=lambda x: x.get('pontos', 0), reverse=True)[:10]

    tela.fill((0, 0, 0))
    titulo = FONTE_MENU.render("RANKING PONTUAÇÕES", 1, (0, 255, 0))
    tela.blit(titulo, (TELA_LARGURA // 2 - titulo.get_width() // 2, 50))
    tela.blit(IMAGEM_MENU, ((TELA_LARGURA - nova_largura) // 2, (TELA_ALTURA - nova_altura) // 2 + 100))

    for i, entrada in enumerate(ranking):
        jogador = entrada.get('Jogador', 'Desconhecido')
        pontos = entrada.get('Pontos', 0)
        texto = FONTE_MENU.render(f"{i + 1}. {jogador} - {pontos}", 1, (255, 255, 255))
        tela.blit(texto, (TELA_LARGURA // 2 - texto.get_width() // 2, 100 + i * 30))

    pygame.display.update()
    pygame.time.wait(7000)

def menu():
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    #carregar img e redimensiona-la
    IMAGEM_MENU = pygame.image.load(os.path.join('imgs', 'pygame_powered.png'))
    nova_largura = TELA_LARGURA // 2
    proporcao = IMAGEM_MENU.get_height() / IMAGEM_MENU.get_width()
    nova_altura = int(nova_largura * proporcao)
    IMAGEM_MENU = pygame.transform.scale(IMAGEM_MENU, (nova_largura, nova_altura))

    rodando =True
    while rodando:
        tela.fill((0, 0, 0))
        tela.blit(IMAGEM_MENU, ((TELA_LARGURA - nova_largura) // 2, (TELA_ALTURA - nova_altura) // 2))

        titulo = FONTE_MENU.render("Flappy Bird", 1, (0, 255, 0))
        tela.blit(titulo, (TELA_LARGURA // 2 - titulo.get_width() // 2, 50))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        jogar_texto = FONTE_MENU.render("JOGAR", 1, (0, 255, 0))
        ranking_texto = FONTE_MENU.render("RANKING", 1, (0, 255, 0))

        jogar_rect = jogar_texto.get_rect(center=(TELA_LARGURA // 2, 200))
        ranking_rect = ranking_texto.get_rect(center=(TELA_LARGURA // 2, 300))

        if jogar_rect.collidepoint(mouse_x, mouse_y):
            jogar_texto = FONTE_MENU.render("JOGAR", 1, (255, 255, 0)) # Efeito hover
        if ranking_rect.collidepoint(mouse_x, mouse_y):
            ranking_texto = FONTE_MENU.render("RANKING", 1, (255, 255, 0)) # Efeito hover

        tela.blit(jogar_texto, jogar_rect.topleft)
        tela.blit(ranking_texto, ranking_rect.topleft)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if jogar_rect.collidepoint(mouse_x, mouse_y):
                    selecionar_jogador()
                elif ranking_rect.collidepoint(mouse_x, mouse_y):
                    mostrar_ranking(tela)

def selecionar_jogador():
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    rodando = True
    jogador_selecionado = None
    while rodando:
        tela.fill((0, 0,0))
        titulo = FONTE_MENU.render("Selecione um jogador", 1, (255, 255, 255))
        tela.blit(titulo, (TELA_LARGURA // 2 - titulo.get_width() // 2, 50))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        alex_texto = FONTE_MENU.render("ALEX", 1, (255, 255, 255))
        arthur_texto = FONTE_MENU.render("ARTHUR", 1, (255, 255, 255))

        jogar_rect = alex_texto.get_rect(center=(TELA_LARGURA // 2, 200))
        ranking_rect = arthur_texto.get_rect(center=(TELA_LARGURA // 2, 300))

        if jogar_rect.collidepoint(mouse_x, mouse_y):
            alex_texto = FONTE_MENU.render("ALEX", 1, (255, 255, 0))  # Efeito hover
        if ranking_rect.collidepoint(mouse_x, mouse_y):
            arthur_texto = FONTE_MENU.render("ARTHUR", 1, (255, 255, 0))  # Efeito hover

        tela.blit(alex_texto, jogar_rect.topleft)
        tela.blit(arthur_texto, ranking_rect.topleft)

        pygame.display.update()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if jogar_rect.collidepoint(mouse_x, mouse_y):
                    jogador_selecionado = "ALEX"
                    rodando = False
                elif ranking_rect.collidepoint(mouse_x, mouse_y):
                    jogador_selecionado = "ARTHUR"
                    rodando = False

    if jogador_selecionado:
        main(jogador_selecionado)

def main(jogador):
    passaros = [Passaro(230, 350)]
    chao = Chao(750)
    canos = [Cano(700)]
    tela = pygame.display.set_mode((TELA_LARGURA, TELA_ALTURA))
    pontos = 0
    relogio =pygame.time.Clock()
    level = 1
    velocidade = 5
    rodando = True


    while rodando:
        relogio.tick(30)

        # Interação co usuario
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame. K_SPACE:
                    for passaro in passaros: # desenhar varios passaros para posteriormente criar IA que zera o jogo
                        passaro.pular()

        # mover objetos
        for passaro in passaros:
            passaro.mover()
        chao.mover()

        adicionar_cano = False
        remover_canos = []
        for cano in canos:
            cano.VELOCIDADE = velocidade # atualizar velocidade canos
            chao.VELOCIDADE = velocidade # atualizar velocidade chao
            for i, passaro in enumerate(passaros):
                if cano.colidir(passaro):
                    salvar_pontuacao(jogador, pontos)
                    passaros.pop(i)
                    rodando = False
                    break
                if not cano.passou and passaro.x > cano.x:
                    cano.passou = True
                    adicionar_cano = True
            cano.mover()
            if cano.x + cano.CANO_TOPO.get_width() < 0:
                remover_canos.append(cano)

        if adicionar_cano:
            pontos += 1
            canos.append(Cano(800))
            # incrementar nivel e velocidade a cada 10 pontos
            if pontos % 10 == 0:
                level += 1
                velocidade += 1

        for cano in remover_canos:
            canos.remove(cano)

        for i, passaro in enumerate(passaros):
            if(passaro.y + passaro.imagem.get_height()) > chao.y or passaro.y < 0:
                passaros.pop(i)

        desenhar_tela(tela, passaros, canos, chao, pontos, level)

if __name__ == '__main__':
    menu()
