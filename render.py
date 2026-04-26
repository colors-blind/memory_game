import random
from typing import List, Tuple

import pygame

from board import Board, Revealed, create_revealed_state, get_icon, split_every
from config import (
    BACKGROUND_COLOR,
    BOARD_COLUMNS,
    BOARD_ROWS,
    BOX_COVER_COLOR,
    BOX_SIZE,
    FPS,
    GAP_SIZE,
    HIGHLIGHT_COLOR,
    REVEAL_SPEED,
    X_MARGIN,
    Y_MARGIN,
)


def left_top_of_box(box_x: int, box_y: int) -> Tuple[int, int]:
    return (
        box_x * (BOX_SIZE + GAP_SIZE) + X_MARGIN,
        box_y * (BOX_SIZE + GAP_SIZE) + Y_MARGIN,
    )


def draw_icon(surface, shape: str, color: Tuple[int, int, int], box_x: int, box_y: int):
    left, top = left_top_of_box(box_x, box_y)
    if shape == "a":
        pygame.draw.circle(surface, color, (left + 20, top + 20), 15)
        pygame.draw.circle(surface, BACKGROUND_COLOR, (left + 20, top + 20), 5)
    elif shape == "b":
        pygame.draw.rect(surface, color, (left + 10, top + 10, 20, 20))
    elif shape == "c":
        pygame.draw.polygon(
            surface,
            color,
            ((left + 20, top), (left + BOX_SIZE - 1, top + 20), (left + 20, top + BOX_SIZE - 1), (left, top + 20)),
        )
    elif shape == "d":
        for i in range(0, BOX_SIZE, 4):
            pygame.draw.line(surface, color, (left, top + i), (left + i, top))
            pygame.draw.line(surface, color, (left + i, top + BOX_SIZE - 1), (left + BOX_SIZE - 1, top + i))
    elif shape == "e":
        pygame.draw.ellipse(surface, color, (left, top + 10, BOX_SIZE, 20))


def draw_board(surface, board: Board, revealed: Revealed):
    for box_x in range(BOARD_COLUMNS):
        for box_y in range(BOARD_ROWS):
            left, top = left_top_of_box(box_x, box_y)
            if not revealed[box_x][box_y]:
                pygame.draw.rect(surface, BOX_COVER_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                shape, color = get_icon(board, box_x, box_y)
                draw_icon(surface, shape, color, box_x, box_y)


def draw_highlight(surface, box_x: int, box_y: int):
    left, top = left_top_of_box(box_x, box_y)
    pygame.draw.rect(surface, HIGHLIGHT_COLOR, (left - 5, top - 5, BOX_SIZE + 10, BOX_SIZE + 10), 4)


def _draw_box_covers(surface, board: Board, boxes: List[Tuple[int, int]], coverage: int, clock):
    for box_x, box_y in boxes:
        left, top = left_top_of_box(box_x, box_y)
        pygame.draw.rect(surface, BACKGROUND_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
        shape, color = get_icon(board, box_x, box_y)
        draw_icon(surface, shape, color, box_x, box_y)
        if coverage > 0:
            pygame.draw.rect(surface, BOX_COVER_COLOR, (left, top, coverage, BOX_SIZE))
    pygame.display.update()
    clock.tick(FPS)


def reveal_boxes_animation(surface, board: Board, boxes: List[Tuple[int, int]], clock):
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED) - 1, -REVEAL_SPEED):
        _draw_box_covers(surface, board, boxes, coverage, clock)


def cover_boxes_animation(surface, board: Board, boxes: List[Tuple[int, int]], clock):
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        _draw_box_covers(surface, board, boxes, coverage, clock)


def start_game_animation(surface, board: Board, clock):
    revealed = create_revealed_state(False)
    boxes = [(x, y) for x in range(BOARD_COLUMNS) for y in range(BOARD_ROWS)]
    random.shuffle(boxes)
    grouped = split_every(8, boxes)

    draw_board(surface, board, revealed)
    for group in grouped:
        reveal_boxes_animation(surface, board, group, clock)
        cover_boxes_animation(surface, board, group, clock)


def game_won_animation(surface, board: Board):
    revealed = create_revealed_state(True)
    color1 = (100, 100, 100)
    color2 = BACKGROUND_COLOR
    for _ in range(13):
        color1, color2 = color2, color1
        surface.fill(color1)
        draw_board(surface, board, revealed)
        pygame.display.update()
        pygame.time.wait(300)
