import pygame
from pygame.locals import K_ESCAPE, KEYUP, MOUSEBUTTONUP, MOUSEMOTION, QUIT

from board import create_board, create_revealed_state, get_box_at_pixel, get_icon, has_won
from config import BACKGROUND_COLOR, FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from render import (
    cover_boxes_animation,
    draw_board,
    draw_highlight,
    game_won_animation,
    left_top_of_box,
    reveal_boxes_animation,
    start_game_animation,
)


def run_game():
    pygame.init()
    clock = pygame.time.Clock()
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Memory Game")

    board = create_board()
    revealed = create_revealed_state(False)
    first_selection = None

    surface.fill(BACKGROUND_COLOR)
    start_game_animation(surface, board, clock)

    mouse_x = 0
    mouse_y = 0

    while True:
        mouse_clicked = False
        surface.fill(BACKGROUND_COLOR)
        draw_board(surface, board, revealed)

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                pygame.quit()
                raise SystemExit
            elif event.type == MOUSEMOTION:
                mouse_x, mouse_y = event.pos
            elif event.type == MOUSEBUTTONUP:
                mouse_x, mouse_y = event.pos
                mouse_clicked = True

        box_x, box_y = get_box_at_pixel(mouse_x, mouse_y, left_top_of_box)
        if box_x is not None and box_y is not None:
            if not revealed[box_x][box_y]:
                draw_highlight(surface, box_x, box_y)

            if not revealed[box_x][box_y] and mouse_clicked:
                reveal_boxes_animation(surface, board, [(box_x, box_y)], clock)
                revealed[box_x][box_y] = True

                if first_selection is None:
                    first_selection = (box_x, box_y)
                else:
                    icon1 = get_icon(board, first_selection[0], first_selection[1])
                    icon2 = get_icon(board, box_x, box_y)
                    if icon1 != icon2:
                        pygame.time.wait(1000)
                        cover_boxes_animation(surface, board, [first_selection, (box_x, box_y)], clock)
                        revealed[first_selection[0]][first_selection[1]] = False
                        revealed[box_x][box_y] = False
                    elif has_won(revealed):
                        game_won_animation(surface, board)
                        pygame.time.wait(2000)

                        board = create_board()
                        revealed = create_revealed_state(False)
                        draw_board(surface, board, revealed)
                        pygame.display.update()
                        pygame.time.wait(1000)
                        start_game_animation(surface, board, clock)

                    first_selection = None

        pygame.display.update()
        clock.tick(FPS)
