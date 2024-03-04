import pygame
import threading
import time
import random
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        original_image = pygame.image.load("nata.png").convert()
        original_image.set_colorkey(WHITE)
        self.image = pygame.transform.scale(original_image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.speed_x = 0
        self.speed_y = 0

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("ange.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(0, SCREEN_HEIGHT - self.rect.height)
        self.speed_x = random.randint(-3, 3)
        self.speed_y = random.randint(-3, 3)

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speed_x = -self.speed_x
        if self.rect.top < 0 or self.rect.bottom > SCREEN_HEIGHT:
            self.speed_y = -self.speed_y

def generar_enemigos(enemigos, all_sprites, barrier, notify_event, semaforo):
    while True:
        time.sleep(random.uniform(1, 3))
        enemigo = Enemy()
        enemigo.rect.x = random.randint(0, SCREEN_WIDTH - enemigo.rect.width)
        enemigo.rect.y = random.randint(0, SCREEN_HEIGHT - enemigo.rect.height)
        enemigos.add(enemigo)
        all_sprites.add(enemigo)
        barrier.wait()  

        if notify_event.is_set():
            semaforo.acquire() 
            print("Se ha generado un nuevo enemigo")
            semaforo.release()
            notify_event.clear()  

def tarea_back(id_hilo, semaforo):
    while True:
        time.sleep(random.uniform(2, 5))
        semaforo.acquire()
       # print(f"Hilo cooperativo back {id_hilo} ejecutándose.")
        semaforo.release()

def tarea_front(id_hilo, semaforo):
    while True:
        time.sleep(random.uniform(2, 5))
        semaforo.acquire()
       # print(f"Hilo cooperativo front {id_hilo} ejecutándose.")
        semaforo.release()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NATAKONG")


  # Definir el tamaño del rectángulo
    rect_width = 100
    rect_height = 100

    # Definir la posición del rectángulo (en este caso, la esquina superior derecha)
    rect_x = SCREEN_WIDTH - rect_width
    rect_y = 0



    background = pygame.image.load("Back.jpg").convert()
    background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    all_sprites = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    barrier = threading.Barrier(2)
    semaforo = threading.Semaphore(1)
    notify_event = threading.Event()

    hilo_generar_enemigos = threading.Thread(target=generar_enemigos, args=(enemigos, all_sprites, barrier, notify_event, semaforo))
    hilo_generar_enemigos.daemon = True
    hilo_generar_enemigos.start()

    hilo_back = threading.Thread(target=tarea_back, args=(1, semaforo))
    hilo_back.daemon = True
    hilo_back.start()

    hilos_front = []
    for i in range(2):
        hilo_front = threading.Thread(target=tarea_front, args=(i, semaforo))
        hilo_front.daemon = True
        hilo_front.start()
        hilos_front.append(hilo_front)

    font = pygame.font.Font(None, 36)
    contador = 0
    linea_y = SCREEN_HEIGHT // 2 
    tiempo_maximo = 30  
    tiempo_inicio = time.time()

    clock = pygame.time.Clock()
    running = True
    nivel_completado = False  
    avanzar_nivel = False  
    while running:
        tiempo_transcurrido = time.time() - tiempo_inicio
        tiempo_restante = max(tiempo_maximo - tiempo_transcurrido, 0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.speed_x = -5
                elif event.key == pygame.K_RIGHT:
                    player.speed_x = 5
                elif event.key == pygame.K_UP:
                    player.speed_y = -5
                elif event.key == pygame.K_DOWN:
                    player.speed_y = 5
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.speed_x = 0
                elif event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                    player.speed_y = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if nivel_completado:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if 100 <= mouse_x <= 200 and 150 <= mouse_y <= 180:
                        avanzar_nivel = True

        hits = pygame.sprite.spritecollide(player, enemigos, True)
        if hits:
            contador += 1
            if contador >= 5 and not nivel_completado:
                nivel_completado = True
                ventana_fin_juego()

            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            new_enemy = Enemy()
            new_enemy.rect.x = random.randint(0, SCREEN_WIDTH - new_enemy.rect.width)
            new_enemy.rect.y = random.randint(0, SCREEN_HEIGHT - new_enemy.rect.height)
            enemigos.add(new_enemy)
            all_sprites.add(new_enemy)

        for enemy in enemigos:
            if enemy.rect.top <= rect_height and rect_width <= enemy.rect.bottom:
                enemigos.remove(enemy)
                all_sprites.remove(enemy)
                time.sleep(1)
                new_enemy = Enemy()
                new_enemy.rect.x = random.randint(0, SCREEN_WIDTH - new_enemy.rect.width)
                new_enemy.rect.y = random.randint(0, SCREEN_HEIGHT - new_enemy.rect.height)
                enemigos.add(new_enemy)
                all_sprites.add(new_enemy)

        screen.blit(background, (0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        pygame.draw.rect(
            screen, WHITE, (rect_x, rect_y, rect_width, rect_height))

        x_pos = 10
        y_pos = 10

        texto_contador = font.render(f"Nivel 2", True, BLUE)
        screen.blit(texto_contador, (x_pos, y_pos))

        x_pos += texto_contador.get_width() + 10 

        texto_contador = font.render(f"Enemigos eliminados: {contador}", True, WHITE)
        screen.blit(texto_contador, (x_pos, y_pos))

        x_pos += texto_contador.get_width() + 10 

        texto_tiempo = font.render(f"Tiempo restante: {int(tiempo_restante)}", True, GREEN)
        screen.blit(texto_tiempo, (x_pos, y_pos))

        pygame.display.flip()

        if tiempo_transcurrido >= tiempo_maximo and not nivel_completado:
            mostrar_mensaje_tiempo_agotado()
            ventana_fin_juego()

        if avanzar_nivel:
            pygame.quit()
            ventana_fin_juego()

        clock.tick(60)

def ventana_fin_juego():
    pygame.init()
    fin_juego = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Fin del juego")
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    pygame.quit()
                    sys.exit()

        fin_juego.fill(WHITE)
        texto = font.render("Fin del juego", True, WHITE)
        fin_juego.blit(texto, (50, 50))
        texto_continuar = font.render("Presiona Enter para salir", True, WHITE)
        fin_juego.blit(texto_continuar, (10, 100))

        pygame.display.flip()

def mostrar_mensaje_tiempo_agotado():
    pygame.init()
    tiempo_agotado = pygame.display.set_mode((300, 200))
    pygame.display.set_caption("Tiempo Agotado")
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    running = False

        tiempo_agotado.fill(WHITE)
        texto = font.render("Tiempo Agotado", True, BLACK)
        tiempo_agotado.blit(texto, (50, 50))
        texto_continuar = font.render("Presiona Enter para continuar", True, WHITE)
        tiempo_agotado.blit(texto_continuar, (10, 100))

        pygame.display.flip()

if __name__ == "__main__":
    main()
