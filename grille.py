import pygame
rows,cols = 4,6
cell_size = 80


def create_grid(rows, cols):
    return [[0 for _ in range(cols)] for _ in range(rows)]

grid = create_grid(rows, cols)
offset_x = 150
offset_y = 300
def draw_grid(screen, grid, cell_size,offset_x,offset_y):
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            rect = pygame.Rect(offset_x + x * cell_size,
                               offset_y + y * cell_size,
                               cell_size,
                               cell_size)
            pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # contour


