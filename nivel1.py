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
        self.image = pygame.transform.scale(original_image, (65, 65))
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
        self.image = pygame.transform.scale(self.image, (65, 65))
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

# Función para generar enemigos


def generar_enemigos(enemigos, all_sprites, barrier1, barrier2, notify_event, notify_event2):
    while True:
        time.sleep(random.uniform(1, 3))
        enemigo = Enemy()
        enemigo.rect.x = random.randint(0, SCREEN_WIDTH - enemigo.rect.width)
        enemigo.rect.y = random.randint(0, SCREEN_HEIGHT - enemigo.rect.height)
        enemigos.add(enemigo)
        all_sprites.add(enemigo)
        barrier1.wait()

        if notify_event.is_set():
            enemigo = Enemy()
            enemigo.rect.x = random.randint(
                0, SCREEN_WIDTH - enemigo.rect.width)
            enemigo.rect.y = random.randint(
                0, SCREEN_HEIGHT - enemigo.rect.height)
            enemigos.add(enemigo)
            all_sprites.add(enemigo)
            notify_event.clear()

            notify_event2.set()

        barrier2.wait()


def tarea_front(id_hilo, semaforo):
    while True:
        time.sleep(random.uniform(2, 5))
        semaforo.acquire()
        semaforo.release()


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("NATAKONG")
    background = pygame.image.load("Back.jpg").convert()
    background = pygame.transform.scale(
        background, (SCREEN_WIDTH, SCREEN_HEIGHT))

    all_sprites = pygame.sprite.Group()
    enemigos = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    barrier1 = threading.Barrier(2)
    barrier2 = threading.Barrier(2)

    semaforo = threading.Semaphore(1)

    notify_event = threading.Event()
    notify_event2 = threading.Event()

    hilo_generar_enemigos = threading.Thread(target=generar_enemigos, args=(
        enemigos, all_sprites, barrier1, barrier2, notify_event, notify_event2))
    hilo_generar_enemigos.daemon = True
    hilo_generar_enemigos.start()

    hilos_front = []
    for i in range(2):
        hilo_front = threading.Thread(target=tarea_front, args=(i, semaforo))
        hilo_front.daemon = True
        hilo_front.start()
        hilos_front.append(hilo_front)

    font = pygame.font.Font(None, 36)
    contador = 0



    # Definir el tamaño del rectángulo
    rect_width = 100
    rect_height = 100

    # Definir la posición del rectángulo (en este caso, la esquina superior derecha)
    rect_x = SCREEN_WIDTH - rect_width
    rect_y = 0

    tiempo_maximo = 60  # Tiempo del nivel
    tiempo_inicio = time.time()

    clock = pygame.time.Clock()
    running = True
    nivel_completado = False  # Indica si el nivel ha sido completado
    avanzar_nivel = False  # Indica si el jugador quiere avanzar al nivel 2
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
                ventana_nivel_completado()

            player.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

            new_enemy = Enemy()
            new_enemy.rect.x = random.randint(
                0, SCREEN_WIDTH - new_enemy.rect.width)
            new_enemy.rect.y = random.randint(
                0, SCREEN_HEIGHT - new_enemy.rect.height)
            enemigos.add(new_enemy)
            all_sprites.add(new_enemy)

        for enemy in enemigos:
            if enemy.rect.right >= rect_height and rect_width:
                enemigos.remove(enemy)
                all_sprites.remove(enemy)
                time.sleep(1)
                new_enemy = Enemy()
                new_enemy.rect.x = random.randint(
                    0, SCREEN_WIDTH - new_enemy.rect.width)
                new_enemy.rect.y = random.randint(
                    0, SCREEN_HEIGHT - new_enemy.rect.height)
                enemigos.add(new_enemy)
                all_sprites.add(new_enemy)

        screen.blit(background, (0, 0))

        all_sprites.update()
        all_sprites.draw(screen)

        # Dibujar el rectángulo en lugar de la línea
        pygame.draw.rect(
            screen, WHITE, (rect_x, rect_y, rect_width, rect_height))

        texto_contador = font.render(f"Nivel 1", True, BLUE)
        screen.blit(texto_contador, (10, 10))
        texto_contador = font.render(
            f"Enemigos eliminados: {contador}", True, WHITE)
        screen.blit(texto_contador, (10, 50))

        texto_tiempo = font.render(
            f"Tiempo restante: {int(tiempo_restante)}", True, WHITE)
        screen.blit(texto_tiempo, (10, 90))

        pygame.display.flip()

        if tiempo_transcurrido >= tiempo_maximo and not nivel_completado:
            mostrar_mensaje_tiempo_agotado()

        if avanzar_nivel:
            pygame.quit()
            import nivel_2  # Cargar el archivo del nivel 2
            nivel_2.main()  # Ejecutar la función main del nivel 2

        clock.tick(60)


def ventana_nivel_completado():
    pygame.init()
    nivel_completado = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Nivel Completado")
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

        nivel_completado.fill(WHITE)
        texto = font.render("Nivel 1 Completado", True, WHITE)
        nivel_completado.blit(texto, (50, 50))
        texto_continuar = font.render(
            "Presiona Enter para continuar", True, WHITE)
        nivel_completado.blit(texto_continuar, (10, 100))

        pygame.display.flip()

    pygame.quit()
    import nivel_2
    nivel_2.main()


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

        tiempo_agotado.fill(BLACK)
        texto = font.render("Tiempo Agotado", True, BLACK)
        tiempo_agotado.blit(texto, (50, 50))
        texto_continuar = font.render(
            "Presiona Enter para continuar", True, BLACK)
        tiempo_agotado.blit(texto_continuar, (10, 100))

        pygame.display.flip()


if __name__ == "__main__":
    main()
