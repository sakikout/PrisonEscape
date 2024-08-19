import heapq
import pygame
import time
from member import Member

# Inicializa o Pygame
pygame.init()

# Configurações da tela
width, height = 420, 420
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Prison Escape")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (112,128,144)
GREEN = (34,139,34)
RED = (255, 0, 0)
BLUE = (28, 82, 152)
BROWN = (144,95,53)

# Tamanho da célula
cell_size = 10
# Inicializa a fonte para desenhar o texto
font = pygame.font.Font(None, 20)


# Representação dos custos dos terrenos
terrain_cost = {
    'A': 1,  # Asfalto
    'T': 3,  # Terra
    'G': 5,  # Grama
    'P': 10, # Paralelepípedo
    'E': float('inf')  # Edifícios (intransitável)
}

# Função para ler o mapa a partir de um arquivo
def read_map(filename):
    valid_chars = {'A', 'T', 'G', 'P', 'E'} 
    with open(filename, 'r') as file:
        mapa = []
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            for char in line:
                if char not in valid_chars:
                    raise ValueError(f"ERROR: Caracter inválido '{char}' na linha {line_num}.")
            mapa.append(list(line))
            
    return mapa
    


# Função heurística (distância de Manhattan)
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

# Algoritmo A*
def a_star_search(start, goal, mapa):
    open_list = [] # fila de prioridade para os nós que precisam ser explorados
    heapq.heappush(open_list, (0, start)) # adiciona o nó inicial com prioridade 0 ( f(n) = 0 )
    path = {}  # de onde veio cada nó
    cost = {start: 0} # custo

    while open_list:
        current = heapq.heappop(open_list)[1] # remove o nó com a menor prioridade

        if current == goal: # se o nó atual for o objetivo, quebra a iteração e retorna o caminho
            break

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]: # iterando sobre quatro possíveis movimentos (esquerda, direita, cima, baixo)
            neighbor = (current[0] + dx, current[1] + dy) # calculando as coordenadas do nó vizinho baseado na posição atual e no movimento (dx,dy)
            if 0 <= neighbor[0] < 42 and 0 <= neighbor[1] < 42 and mapa[neighbor[0]][neighbor[1]] != 'E': # verificando se o vizinho está dentro dos limites do mapa e se não é um edifício
                new_cost = cost[current] + terrain_cost[mapa[neighbor[0]][neighbor[1]]] # calculando o novo custo para chegar ao vizinho
                if neighbor not in cost or new_cost < cost[neighbor]: # verificando se o vizinho não foi visitado ainda ou se o novo custo é menor que o custo registrado para chegar ao vizinho
                    cost[neighbor] = new_cost # atualiza o custo acumulado para chegar ao vizinho
                    priority = new_cost + heuristic(goal, neighbor) # f(n) = g(n) + h(n)
                    heapq.heappush(open_list, (priority, neighbor)) # adiciona o vizinho à lista com a prioridade calculada
                    path[neighbor] = current # adiciona o vizinho ao caminho

    return path, cost

# Função para reconstruir o caminho
def reconstruct_path(came_from, start, goal):
    current = goal # o fim vira o início
    path = [] # irá armazenar o caminho reconstruído
    while current != start:
        if current not in came_from: # Rick chegou em uma posição que não deveria ser acessada
            raise ValueError(f"ERRO: {current} não está em uma área viável do mapa.")
        path.append(current)
        current = came_from[current]
    path.append(start) # adiciona o começo para o caminho
    path.reverse() # inverte para que o caminho fique do inicio ao fim de novo
    return path

# Ordena os membros pela distância até Rick
def sort_members_by_distance(rick_position, members_positions):
    sorted_members = sorted(members_positions, key=lambda member: heuristic(rick_position, member.getCoordinates()))
    return sorted_members


# Desenha o mapa
def draw_map(mapa, path, current_position, members_positions, message, total_cost, final_message):
    for y, row in enumerate(mapa):
        for x, cell in enumerate(row):
            color = WHITE
            if cell == 'A':
                color = GRAY
            elif cell == 'T':
                color = BROWN
            elif cell == 'G':
                color = GREEN
            elif cell == 'P':
                color = WHITE
            elif cell == 'E':
                color = BLUE
            pygame.draw.rect(screen, color, (x * cell_size, y * cell_size, cell_size, cell_size))
    
    # Desenha o caminho
    for x, y in path:
        pygame.draw.rect(screen, BLACK, (y * cell_size, x * cell_size, cell_size, cell_size))
    
    # Desenha o personagem na posição atual
    pygame.draw.rect(screen, (255, 255, 0), (current_position[1] * cell_size, current_position[0] * cell_size, cell_size, cell_size))
    
    # Desenha os membros
    for member in members_positions:
        pos = member.getCoordinates()
        pygame.draw.rect(screen, member.getColor(), (pos[1] * cell_size, pos[0] * cell_size, cell_size, cell_size))

     # Adiciona texto na tela
    text = font.render(f'Posição atual: {current_position}', True, WHITE)
    screen.blit(text, (10, height - 20))  # Posiciona o texto no canto inferior

     # Adiciona o texto da mensagem
    if message:
        text = font.render(message, True, WHITE)
        screen.blit(text, (10, 5))  # Posiciona o texto no canto superior

    # Adiciona o texto do custo total
    if total_cost is not None:
        cost_text = font.render(f'Custo total: {total_cost}', True, BLACK)
        screen.blit(cost_text, (width * 0.7, height - 40))  # Posiciona o texto no canto inferior

    # Adiciona a mensagem final
    if final_message:
        final_text = font.render(final_message, True, WHITE)
        screen.blit(final_text,  (280, height - 20))  # Posiciona o texto acima da mensagem de custo


def setMap():
    map_name = input("Insira o nome do mapa em txt: ")

    if ".txt" not in map_name:
        map_name += ".txt"

    mapa = read_map(map_name)
    return mapa

def setMembers():
    members = []  # nomes: Carl, Daryl, Glen e Maggie - pos: [(6, 32), (13, 31), (35, 35), (32, 9)]

    num_members = input("Insira o número total de membros para Rick encontrar: ")
    num_members = int(num_members)
    i = 0

    while (i < num_members):
        name = input("Nome do membro: ")
        coord_x = input(f"Insira as coordenadas de {name}:\nX: ")
        coord_y = input("Y: ")
        coord_final = (int(coord_x), int(coord_y))
        new_member = Member(name=name, coordinates=coord_final)
        members.append(new_member)
        i += 1

    return members

def main():
    mapa = setMap()

    coord_x = input("Insira as coordenadas da posição inicial de Rick (x,y):\nX: ")
    coord_y = input("Y: ")
    start = (int(coord_x), int(coord_y)) # inicio do exemplo: (21, 13)

    coord_x = input("Insira as coordenadas da posição final:\nX: ")
    coord_y = input("Y: ")
    end = (int(coord_x), int(coord_y))  # saída do exemplo: (41, 20)

    settings = input("Deseja inserir todos os membros ou escolher o padrão?\n1 - INSERIR MEMBROS\n2 - MEMBROS PADRÃO\nR: ")
    if (int(settings) == 1 or settings.upper() == "SIM"):
        members = setMembers() # nomes: Carl, Daryl, Glen e Maggie - pos: [(6, 32), (13, 31), (35, 35), (32, 9)]
    else:
        members = [
        Member("Carl", (6, 32)),
        Member("Daryl", (13, 31)),
        Member("Glen", (35, 35)),
        Member("Maggie", (32, 9))
    ]
    survivors = sort_members_by_distance(start, members)
    
    total_path = []
    current_start = start
    members_positions = []

    while len(survivors) != 0:
        survivor = survivors.pop(0)
        came_from, cost_so_far = a_star_search(current_start, survivor.getCoordinates(), mapa)
        path = reconstruct_path(came_from, current_start, survivor.getCoordinates())
        total_path.extend(path[1:])  # Evita duplicar o ponto de encontro
        members_positions.append(survivor)
        current_start = survivor.getCoordinates()
        survivors = sort_members_by_distance(current_start, survivors)

    
    came_from, cost_so_far = a_star_search(current_start, end, mapa)
    path = reconstruct_path(came_from, current_start, end)
    total_path.extend(path[1:])

   # Inicializa o Pygame
    running = True
    path_index = 0
    current_position = start
    message = None
    total_cost = None
    final_message = None

    positions = []
    for member in members_positions:
        positions.append(member.getCoordinates())

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if path_index < len(total_path):
            current_position = total_path[path_index]
            path_index += 1

            # Verifica se o personagem chegou a um membro
            if current_position in positions:
                for member in members_positions:
                    if member.getCoordinates() == current_position:
                        message = f"Chegou no membro {member.getName()}"
                        members_positions.remove(member)
                        break
            else:
                message = None

            if current_position == end:
                final_message = "Fim do caminho!"
                total_cost = cost_so_far[end]  # Atualiza o custo total ao final
                path_index = len(total_path)  # Para o loop
        else:
            final_message = "Fim do caminho!"
            total_cost = cost_so_far[end]  # Atualiza o custo total ao final
            pygame.time.wait(2000) 

        screen.fill(WHITE)
        draw_map(mapa, total_path[:path_index], current_position, members_positions, message, total_cost, final_message)
        
        pygame.display.flip()
        time.sleep(0.1)
    
    pygame.quit()

    print(f"Custo total: {total_cost}")

if __name__ == '__main__':
    main()
