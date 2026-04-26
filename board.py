import random
from typing import Callable, List, Optional, Tuple

from config import BOARD_COLUMNS, BOARD_ROWS, BOX_SIZE, PAIR_COLORS, PAIR_SHAPES

Icon = Tuple[str, Tuple[int, int, int]]
Board = List[List[Icon]]
Revealed = List[List[bool]]


def create_revealed_state(default: bool) -> Revealed:
    return [[default] * BOARD_ROWS for _ in range(BOARD_COLUMNS)]


def create_board() -> Board:
    icons: List[Icon] = []
    for color in PAIR_COLORS:
        for shape in PAIR_SHAPES:
            icons.append((shape, color))

    random.shuffle(icons)
    picked = icons[: (BOARD_COLUMNS * BOARD_ROWS) // 2] * 2
    random.shuffle(picked)

    board: Board = []
    for x in range(BOARD_COLUMNS):
        column: List[Icon] = []
        for _ in range(BOARD_ROWS):
            column.append(picked.pop(0))
        board.append(column)
    return board


def get_icon(board: Board, box_x: int, box_y: int) -> Icon:
    return board[box_x][box_y]


def split_every(size: int, items: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def get_box_at_pixel(
    x: int, y: int, left_top_getter: Callable[[int, int], Tuple[int, int]]
) -> Tuple[Optional[int], Optional[int]]:
    import pygame

    for box_x in range(BOARD_COLUMNS):
        for box_y in range(BOARD_ROWS):
            left, top = left_top_getter(box_x, box_y)
            rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            if rect.collidepoint(x, y):
                return box_x, box_y
    return None, None


def has_won(revealed: Revealed) -> bool:
    return all(all(column) for column in revealed)
