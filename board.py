# -*- coding: utf-8 -*-
"""
棋盘模块 - 负责棋盘的创建、状态管理和核心逻辑

此模块包含以下功能：
- 创建随机化的游戏棋盘
- 管理格子的翻开状态
- 提供坐标转换和碰撞检测
- 判断游戏是否胜利
- 支持两种游戏模式：颜色模式和汉字模式
"""

import random
from typing import Callable, List, Optional, Tuple

from config import (
    BOARD_COLUMNS,
    BOARD_ROWS,
    BOX_SIZE,
    DIFFICULTY_LEVELS,
    MODE_CHINESE,
    MODE_COLOR,
    PAIR_COLORS,
    PAIR_SHAPES,
)

# ============================================
# 类型定义
# ============================================

# 颜色模式图标类型：(形状标识, RGB颜色元组)
ColorIcon = Tuple[str, Tuple[int, int, int]]
# 汉字模式图标类型：(汉字字符, RGB颜色元组)
ChineseIcon = Tuple[str, Tuple[int, int, int]]
# 统一的图标类型
Icon = Tuple[str, Tuple[int, int, int]]

# 棋盘类型：二维列表，存储每个格子的图标
Board = List[List[Icon]]
# 翻开状态类型：二维列表，存储每个格子是否已翻开
Revealed = List[List[bool]]


# ============================================
# 状态管理函数
# ============================================

def create_revealed_state(default: bool) -> Revealed:
    """
    创建一个初始的翻开状态二维列表。
    
    参数:
        default: 初始状态值（True 表示全部翻开，False 表示全部未翻开）
    
    返回:
        一个 BOARD_COLUMNS x BOARD_ROWS 的二维列表，每个元素都是 default 值
    
    示例:
        >>> create_revealed_state(False)
        [[False, False, ...], [False, False, ...], ...]
    """
    return [[default] * BOARD_ROWS for _ in range(BOARD_COLUMNS)]


# ============================================
# 棋盘创建函数
# ============================================

def create_board(mode: str = MODE_COLOR, difficulty: str = "easy") -> Board:
    """
    创建一个随机化的游戏棋盘。
    
    根据选择的游戏模式创建不同类型的棋盘：
    - 颜色模式：使用形状（a-e）和颜色组合
    - 汉字模式：使用汉字和颜色组合
    
    参数:
        mode: 游戏模式，可选值为 MODE_COLOR 或 MODE_CHINESE
        difficulty: 汉字模式的难度级别，可选值为 "easy"、"medium"、"hard"
    
    返回:
        一个 BOARD_COLUMNS x BOARD_ROWS 的二维棋盘列表，每个元素是一个图标元组
    
    示例:
        # 颜色模式
        >>> board = create_board(MODE_COLOR)
        >>> board[0][0]
        ('a', (255, 0, 0))
        
        # 汉字模式
        >>> board = create_board(MODE_CHINESE, "easy")
        >>> board[0][0]
        ('一', (255, 0, 0))
    """
    if mode == MODE_CHINESE:
        return _create_chinese_board(difficulty)
    else:
        return _create_color_board()


def _create_color_board() -> Board:
    """
    创建颜色模式的棋盘（内部函数）。
    
    颜色模式使用形状（a-e）和颜色的组合作为图标。
    每种组合会出现两次，确保可以配对。
    
    返回:
        随机化的颜色模式棋盘
    
    实现逻辑:
        1. 生成所有可能的形状+颜色组合
        2. 随机打乱并选择需要的数量
        3. 每种组合复制一份（确保配对）
        4. 再次打乱并填充到棋盘
    """
    # 生成所有可能的图标组合：形状 × 颜色
    icons: List[ColorIcon] = []
    for color in PAIR_COLORS:
        for shape in PAIR_SHAPES:
            icons.append((shape, color))
    
    # 随机打乱图标列表
    random.shuffle(icons)
    
    # 计算需要的图标对数
    # 棋盘总格子数必须是偶数，这里 (10列 × 7行) = 70 个格子，需要 35 对
    total_pairs = (BOARD_COLUMNS * BOARD_ROWS) // 2
    
    # 选择需要的图标对，每种复制一份（确保每个图标出现两次）
    picked = icons[:total_pairs] * 2
    
    # 再次打乱，确保随机性
    random.shuffle(picked)
    
    # 填充到二维棋盘列表
    board: Board = []
    for x in range(BOARD_COLUMNS):
        column: List[Icon] = []
        for _ in range(BOARD_ROWS):
            column.append(picked.pop(0))
        board.append(column)
    
    return board


def _create_chinese_board(difficulty: str = "easy") -> Board:
    """
    创建汉字模式的棋盘（内部函数）。
    
    汉字模式使用汉字和颜色的组合作为图标。
    根据难度级别选择不同的汉字库。
    
    参数:
        difficulty: 难度级别，可选值为 "easy"、"medium"、"hard"
    
    返回:
        随机化的汉字模式棋盘
    
    实现逻辑:
        1. 根据难度选择汉字库
        2. 为每个汉字分配一种颜色
        3. 生成汉字+颜色的组合
        4. 确保每种组合出现两次
        5. 随机打乱并填充到棋盘
    """
    # 根据难度级别获取对应的汉字列表
    chinese_chars = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["easy"])
    
    # 生成汉字和颜色的组合
    # 为了增加变化，我们为每个汉字分配不同的颜色
    icons: List[ChineseIcon] = []
    for char in chinese_chars:
        # 为每个汉字选择一种颜色（循环使用颜色列表）
        color_index = len(icons) % len(PAIR_COLORS)
        color = PAIR_COLORS[color_index]
        icons.append((char, color))
    
    # 计算需要的图标对数
    total_pairs = (BOARD_COLUMNS * BOARD_ROWS) // 2
    
    # 如果汉字数量不够，重复使用汉字
    while len(icons) < total_pairs:
        icons.extend(icons)
    
    # 随机打乱并选择需要的数量
    random.shuffle(icons)
    picked = icons[:total_pairs] * 2
    random.shuffle(picked)
    
    # 填充到二维棋盘列表
    board: Board = []
    for x in range(BOARD_COLUMNS):
        column: List[Icon] = []
        for _ in range(BOARD_ROWS):
            column.append(picked.pop(0))
        board.append(column)
    
    return board


# ============================================
# 棋盘访问函数
# ============================================

def get_icon(board: Board, box_x: int, box_y: int) -> Icon:
    """
    获取棋盘上指定位置的图标。
    
    参数:
        board: 棋盘二维列表
        box_x: 格子的列索引（从 0 开始）
        box_y: 格子的行索引（从 0 开始）
    
    返回:
        图标元组，格式为 (标识, 颜色)
        - 颜色模式：('a', (255, 0, 0))
        - 汉字模式：('一', (255, 0, 0))
    
    示例:
        >>> icon = get_icon(board, 0, 0)
        >>> shape_or_char, color = icon
    """
    return board[box_x][box_y]


# ============================================
# 辅助函数
# ============================================

def split_every(size: int, items: List[Tuple[int, int]]) -> List[List[Tuple[int, int]]]:
    """
    将列表按照指定大小分组。
    
    主要用于开场动画，将格子坐标分成小组进行动画展示。
    
    参数:
        size: 每组的大小
        items: 要分组的坐标列表
    
    返回:
        分组后的二维列表
    
    示例:
        >>> split_every(2, [(0,0), (0,1), (1,0), (1,1)])
        [[(0,0), (0,1)], [(1,0), (1,1)]]
    """
    return [items[i : i + size] for i in range(0, len(items), size)]


# ============================================
# 坐标转换函数
# ============================================

def get_box_at_pixel(
    x: int, y: int, left_top_getter: Callable[[int, int], Tuple[int, int]]
) -> Tuple[Optional[int], Optional[int]]:
    """
    根据像素坐标获取对应的棋盘格子坐标。
    
    用于处理鼠标点击和悬停事件，判断鼠标指向的是哪个格子。
    
    参数:
        x: 像素坐标的 x 值
        y: 像素坐标的 y 值
        left_top_getter: 一个函数，用于根据格子坐标获取其左上角的像素坐标
                        通常传入 render.py 中的 left_top_of_box 函数
    
    返回:
        如果像素坐标在某个格子内，返回 (box_x, box_y)
        如果不在任何格子内，返回 (None, None)
    
    示例:
        >>> # 假设 (100, 100) 像素位置在第 2 列第 1 行的格子内
        >>> get_box_at_pixel(100, 100, left_top_of_box)
        (1, 0)
    """
    import pygame
    
    # 遍历所有格子，检查像素坐标是否在格子范围内
    for box_x in range(BOARD_COLUMNS):
        for box_y in range(BOARD_ROWS):
            # 获取格子左上角的像素坐标
            left, top = left_top_getter(box_x, box_y)
            # 创建矩形对象用于碰撞检测
            rect = pygame.Rect(left, top, BOX_SIZE, BOX_SIZE)
            # 检查像素坐标是否在矩形内
            if rect.collidepoint(x, y):
                return box_x, box_y
    
    # 不在任何格子内
    return None, None


# ============================================
# 游戏状态判断函数
# ============================================

def has_won(revealed: Revealed) -> bool:
    """
    检查游戏是否胜利。
    
    游戏胜利的条件是：所有格子都已翻开。
    
    参数:
        revealed: 翻开状态二维列表
    
    返回:
        True 表示所有格子都已翻开（游戏胜利）
        False 表示还有格子未翻开
    
    示例:
        >>> # 所有格子都翻开了
        >>> revealed = [[True, True, ...], [True, True, ...], ...]
        >>> has_won(revealed)
        True
    """
    # 使用 all() 函数检查所有元素是否都是 True
    # 外层 all() 检查每一列
    # 内层 all() 检查每一行
    return all(all(column) for column in revealed)
