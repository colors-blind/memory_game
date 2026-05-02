# -*- coding: utf-8 -*-
"""
渲染模块 - 负责游戏界面的绘制和动画效果

此模块包含以下功能：
- 坐标转换（棋盘坐标 -> 像素坐标）
- 图标的绘制（形状和汉字）
- 棋盘的整体绘制（支持动态大小）
- 翻牌动画（翻开和覆盖）
- 开场动画（快速预览所有格子）
- 胜利动画（闪烁效果）
- 计时器显示
- 菜单界面绘制（模式选择、棋盘大小选择）
"""

import random
from typing import Callable, List, Optional, Tuple

import pygame

from board import Board, Revealed, calculate_board_margins, create_revealed_state, get_icon, split_every
from config import (
    BACKGROUND_COLOR,
    BOARD_SIZE_LEVELS,
    BOX_COVER_COLOR,
    DEFAULT_BOARD_COLUMNS,
    DEFAULT_BOARD_ROWS,
    FONT_SIZE,
    FPS,
    GAP_SIZE,
    HIGHLIGHT_COLOR,
    MODE_CHINESE,
    MODE_COLOR,
    REVEAL_SPEED,
    TIMER_COLOR,
    TIMER_FONT_SIZE,
    TIMER_POSITION_X,
    TIMER_POSITION_Y,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)

# ============================================
# 全局变量
# ============================================

# 字体对象（用于汉字渲染）
# 在 initialize_font() 函数中初始化
_font: Optional[pygame.font.Font] = None

# 计时器字体对象
_timer_font: Optional[pygame.font.Font] = None


# ============================================
# 字体初始化函数
# ============================================

def initialize_font() -> pygame.font.Font:
    """
    初始化 Pygame 字体系统，获取支持中文的字体。
    
    此函数会尝试多种方式获取支持中文的字体：
    1. 首先列出系统中所有可用的字体
    2. 尝试常见的中文字体名称
    3. 使用字体文件名进行尝试
    4. 最后使用默认字体作为备选
    
    返回:
        初始化后的字体对象
    
    注意:
        此函数应该在 pygame.init() 之后调用
    """
    global _font
    
    # 如果已经初始化过，直接返回
    if _font is not None:
        return _font
    
    # 确保 Pygame 字体模块已初始化
    if not pygame.font.get_init():
        pygame.font.init()
    
    # 获取系统中所有可用的字体名称（用于调试）
    available_fonts = pygame.font.get_fonts()
    print(f"系统可用字体数量: {len(available_fonts)}")
    
    # 按优先级排序的中文字体名称列表
    # 包含不同操作系统和不同地区的常见中文字体
    chinese_font_names = [
        # Linux 系统常见中文字体
        "wenquanyimicrohei",      # 文泉驿微米黑
        "wenquanyi zen hei",       # 文泉驿正黑
        "notosanscjksc",           # Noto Sans CJK SC
        "notosanscjktc",           # Noto Sans CJK TC
        "notosanscjkjp",           # Noto Sans CJK JP
        "notoserifcjksc",          # Noto Serif CJK SC
        "droidsansfallback",       # Droid Sans Fallback
        "ukai",                    # UKai
        "uming",                   # Uming
        "arplumingtw",             # AR PL UMing TW
        "arplumingcn",             # AR PL UMing CN
        "arplukaitw",              # AR PL UKai TW
        "arplukaicn",              # AR PL UKai CN
        
        # Windows 系统常见中文字体
        "microsoftyahei",          # 微软雅黑
        "microsoftjhenghei",       # 微软正黑体
        "simhei",                  # 黑体
        "simsun",                  # 宋体
        "simkai",                  # 楷体
        "simli",                   # 隶书
        "simsunb",                 # 宋体-ExtB
        "nsimsun",                 # 新宋体
        "fangsong",                # 仿宋
        "youyuan",                 # 幼圆
        
        # macOS 系统常见中文字体
        "pingfangsc",              # 苹方-简
        "pingfangtc",              # 苹方-繁
        "pingfanghk",              # 苹方-港
        "heitisc",                 # 黑体-简
        "heititc",                 # 黑体-繁
        "stheitisc",               # 华文黑体-简
        "stheititc",               # 华文黑体-繁
        "stsong",                  # 华文宋体
        "stkaiti",                 # 华文楷体
        "stfangsong",              # 华文仿宋
        "applemyungjo",            # AppleMyungjo
        
        # 其他常见中文字体
        "wqy-microhei",            # 文泉驿微米黑（另一种命名方式）
        "wqy-zenhei",              # 文泉驿正黑（另一种命名方式）
        "sourcehansanscn",         # 思源黑体
        "sourcehanserifcn",        # 思源宋体
    ]
    
    # 打印系统中包含中文相关关键字的字体
    print("检测到的可能支持中文的字体:")
    for font_name in available_fonts:
        lower_name = font_name.lower()
        chinese_keywords = [
            "chinese", "cjk", "sc", "tc", "cn", "tw", "hk",
            "hei", "song", "kai", "fang", "ming", "yuan",
            "yahei", "jheng", "ping", "st", "arpl", "wqy",
            "noto", "droid", "ukai", "uming", "sourcehan",
            "wenquanyi", "micro", "zen",
        ]
        for keyword in chinese_keywords:
            if keyword in lower_name:
                print(f"  - {font_name}")
                break
    
    # 尝试使用 SysFont 加载中文字体
    print("正在尝试加载中文字体...")
    
    # 方法1: 使用 match_font 查找字体文件路径
    for font_name in chinese_font_names:
        try:
            font_path = pygame.font.match_font(font_name, bold=False, italic=False)
            
            if font_path:
                print(f"找到字体文件: {font_path}")
                
                _font = pygame.font.Font(font_path, FONT_SIZE)
                
                # 测试字体是否支持中文
                test_text = "中文测试"
                metrics = _font.metrics(test_text)
                
                if metrics and all(m is not None for m in metrics):
                    print(f"成功加载字体: {font_name} (路径: {font_path})")
                    return _font
                    
        except Exception:
            continue
    
    # 方法2: 使用 SysFont 加载（备选方法）
    for font_name in chinese_font_names:
        try:
            _font = pygame.font.SysFont(font_name, FONT_SIZE, bold=False, italic=False)
            
            test_text = "中文测试"
            metrics = _font.metrics(test_text)
            
            if metrics and all(m is not None for m in metrics):
                print(f"成功加载字体: {font_name}")
                return _font
                
        except Exception:
            continue
    
    # 方法3: 尝试使用常见的字体文件名直接查找
    common_font_files = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
    ]
    
    print("尝试直接加载常见中文字体文件...")
    for font_path in common_font_files:
        try:
            _font = pygame.font.Font(font_path, FONT_SIZE)
            
            test_text = "中文测试"
            metrics = _font.metrics(test_text)
            
            if metrics and all(m is not None for m in metrics):
                print(f"成功加载字体文件: {font_path}")
                return _font
                
        except Exception:
            continue
    
    # 如果使用名称找不到字体，尝试使用默认字体
    print("警告：未找到支持中文的系统字体，尝试使用默认字体...")
    
    try:
        default_font_name = pygame.font.get_default_font()
        print(f"Pygame 默认字体: {default_font_name}")
        
        _font = pygame.font.SysFont(default_font_name, FONT_SIZE)
        return _font
    except Exception:
        pass
    
    # 最后的备选方案：使用 None 作为字体名称
    print("使用 Pygame 内置默认字体（可能不支持中文）")
    print("提示：如果中文显示为方块，请安装中文字体")
    print("常见 Linux 中文字体包：")
    print("  - Ubuntu/Debian: sudo apt install fonts-wqy-microhei fonts-noto-cjk")
    print("  - Fedora/RHEL: sudo dnf install wqy-microhei-fonts google-noto-sans-cjk-sc-fonts")
    print("  - Arch: sudo pacman -S wqy-microhei noto-fonts-cjk")
    
    _font = pygame.font.Font(None, FONT_SIZE)
    return _font


def get_timer_font() -> pygame.font.Font:
    """
    获取计时器专用的字体对象。
    
    返回:
        用于计时器显示的字体对象
    """
    global _timer_font
    
    if _timer_font is not None:
        return _timer_font
    
    # 初始化字体
    initialize_font()
    
    # 尝试使用支持中文的字体
    try:
        # 使用系统字体
        _timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)
    except Exception:
        _timer_font = pygame.font.Font(None, TIMER_FONT_SIZE)
    
    return _timer_font


# ============================================
# 坐标转换函数（动态版本）
# ============================================

def create_left_top_calculator(
    x_margin: int,
    y_margin: int,
    box_size: int,
    gap_size: int = GAP_SIZE,
) -> Callable[[int, int], Tuple[int, int]]:
    """
    创建一个用于计算格子左上角坐标的函数。
    
    由于不同棋盘大小有不同的边距和格子尺寸，我们使用闭包来封装这些参数。
    
    参数:
        x_margin: 左侧边距
        y_margin: 顶部边距
        box_size: 格子尺寸
        gap_size: 格子间距
    
    返回:
        一个函数，接收 (box_x, box_y) 并返回 (left, top)
    
    示例:
        >>> calc = create_left_top_calculator(70, 65, 40, 10)
        >>> calc(0, 0)
        (70, 65)
        >>> calc(1, 0)
        (120, 65)
    """
    def left_top_of_box(box_x: int, box_y: int) -> Tuple[int, int]:
        """
        根据棋盘格子坐标计算其左上角的像素坐标。
        
        参数:
            box_x: 格子的列索引（从 0 开始）
            box_y: 格子的行索引（从 0 开始）
        
        返回:
            (left, top) 元组，表示格子左上角的像素坐标
        """
        return (
            x_margin + box_x * (box_size + gap_size),
            y_margin + box_y * (box_size + gap_size),
        )
    
    return left_top_of_box


# ============================================
# 图标绘制函数
# ============================================

def draw_icon(
    surface: pygame.Surface,
    shape_or_char: str,
    color: Tuple[int, int, int],
    box_x: int,
    box_y: int,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    mode: str = MODE_COLOR,
):
    """
    在指定格子位置绘制图标。
    
    支持两种模式：
    - 颜色模式：绘制预定义的几何形状
    - 汉字模式：绘制汉字字符
    
    参数:
        surface: Pygame 绘制表面
        shape_or_char: 形状标识（颜色模式）或汉字字符（汉字模式）
        color: 图标颜色
        box_x: 格子的列索引
        box_y: 格子的行索引
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        mode: 绘制模式
    """
    if mode == MODE_CHINESE:
        _draw_chinese_icon(surface, shape_or_char, color, box_x, box_y, left_top_func, box_size)
    else:
        _draw_shape_icon(surface, shape_or_char, color, box_x, box_y, left_top_func, box_size)


def _draw_shape_icon(
    surface: pygame.Surface,
    shape: str,
    color: Tuple[int, int, int],
    box_x: int,
    box_y: int,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
):
    """
    绘制颜色模式的几何形状图标（内部函数）。
    
    支持的形状：
    - 'a': 圆环（带中心孔的圆形）
    - 'b': 正方形
    - 'c': 菱形（旋转45度的正方形）
    - 'd': 对角线装饰
    - 'e': 椭圆
    - 'f': 三角形
    - 'g': 星形
    
    参数:
        surface: Pygame 绘制表面
        shape: 形状标识 ('a'-'g')
        color: 形状颜色
        box_x: 格子的列索引
        box_y: 格子的行索引
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
    """
    # 获取格子左上角的像素坐标
    left, top = left_top_func(box_x, box_y)
    
    # 计算格子中心坐标
    center_x = left + box_size // 2
    center_y = top + box_size // 2
    
    # 计算比例因子（相对于默认 40 像素的格子）
    scale = box_size / 40.0
    
    if shape == "a":
        # 形状 'a': 圆环
        outer_radius = int(15 * scale)
        inner_radius = int(5 * scale)
        pygame.draw.circle(surface, color, (center_x, center_y), outer_radius)
        pygame.draw.circle(surface, BACKGROUND_COLOR, (center_x, center_y), inner_radius)
        
    elif shape == "b":
        # 形状 'b': 正方形
        margin = int(10 * scale)
        size = int(20 * scale)
        pygame.draw.rect(surface, color, (left + margin, top + margin, size, size))
        
    elif shape == "c":
        # 形状 'c': 菱形
        half_size = box_size // 2
        vertices = (
            (center_x, top),
            (left + box_size - 1, center_y),
            (center_x, top + box_size - 1),
            (left, center_y),
        )
        pygame.draw.polygon(surface, color, vertices)
        
    elif shape == "d":
        # 形状 'd': 对角线装饰
        step = max(2, int(4 * scale))
        for i in range(0, box_size, step):
            pygame.draw.line(surface, color, (left, top + i), (left + i, top))
            pygame.draw.line(
                surface,
                color,
                (left + i, top + box_size - 1),
                (left + box_size - 1, top + i),
            )
            
    elif shape == "e":
        # 形状 'e': 椭圆
        margin_y = int(10 * scale)
        height = int(20 * scale)
        ellipse_rect = (left, top + margin_y, box_size, height)
        pygame.draw.ellipse(surface, color, ellipse_rect)
        
    elif shape == "f":
        # 形状 'f': 三角形
        margin = int(5 * scale)
        vertices = (
            (center_x, top + margin),
            (left + box_size - margin, top + box_size - margin),
            (left + margin, top + box_size - margin),
        )
        pygame.draw.polygon(surface, color, vertices)
        
    elif shape == "g":
        # 形状 'g': 星形（简化版）
        # 绘制一个 X 形
        margin = int(8 * scale)
        pygame.draw.line(
            surface,
            color,
            (left + margin, top + margin),
            (left + box_size - margin, top + box_size - margin),
            max(2, int(3 * scale)),
        )
        pygame.draw.line(
            surface,
            color,
            (left + box_size - margin, top + margin),
            (left + margin, top + box_size - margin),
            max(2, int(3 * scale)),
        )


def _draw_chinese_icon(
    surface: pygame.Surface,
    char: str,
    color: Tuple[int, int, int],
    box_x: int,
    box_y: int,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
):
    """
    绘制汉字模式的汉字图标（内部函数）。
    
    参数:
        surface: Pygame 绘制表面
        char: 要绘制的汉字字符
        color: 汉字颜色
        box_x: 格子的列索引
        box_y: 格子的行索引
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
    """
    # 获取格子左上角的像素坐标
    left, top = left_top_func(box_x, box_y)
    
    # 确保字体已初始化
    font = initialize_font()
    
    # 渲染汉字为图像
    text_surface = font.render(char, True, color)
    
    # 计算文字的居中位置
    # 动态计算偏移量，使文字在不同大小的格子中都能居中
    text_rect = text_surface.get_rect()
    offset_x = (box_size - text_rect.width) // 2
    offset_y = (box_size - text_rect.height) // 2
    
    text_x = left + offset_x
    text_y = top + offset_y
    
    # 绘制文字到表面
    surface.blit(text_surface, (text_x, text_y))


# ============================================
# 棋盘绘制函数
# ============================================

def draw_board(
    surface: pygame.Surface,
    board: Board,
    revealed: Revealed,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    columns: int,
    rows: int,
    mode: str = MODE_COLOR,
):
    """
    绘制整个棋盘。
    
    遍历所有格子，根据翻开状态决定显示内容：
    - 未翻开：显示覆盖色（白色方块）
    - 已翻开：显示图标（形状或汉字）
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        revealed: 翻开状态二维列表
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        columns: 棋盘列数
        rows: 棋盘行数
        mode: 游戏模式
    """
    for box_x in range(columns):
        for box_y in range(rows):
            # 获取格子左上角的像素坐标
            left, top = left_top_func(box_x, box_y)
            
            if not revealed[box_x][box_y]:
                # 格子未翻开：绘制覆盖色（白色方块）
                pygame.draw.rect(surface, BOX_COVER_COLOR, (left, top, box_size, box_size))
            else:
                # 格子已翻开：获取并绘制图标
                shape_or_char, color = get_icon(board, box_x, box_y)
                draw_icon(surface, shape_or_char, color, box_x, box_y, left_top_func, box_size, mode)


# ============================================
# 高亮绘制函数
# ============================================

def draw_highlight(
    surface: pygame.Surface,
    box_x: int,
    box_y: int,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
):
    """
    绘制格子的高亮边框。
    
    当鼠标悬停在未翻开的格子上时，显示一个蓝色边框。
    
    参数:
        surface: Pygame 绘制表面
        box_x: 格子的列索引
        box_y: 格子的行索引
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
    """
    # 获取格子左上角的像素坐标
    left, top = left_top_func(box_x, box_y)
    
    # 计算高亮边框的矩形（向外扩展 5 像素）
    margin = 5
    border_width = 4
    highlight_rect = (
        left - margin,
        top - margin,
        box_size + margin * 2,
        box_size + margin * 2,
    )
    
    # 绘制边框
    pygame.draw.rect(surface, HIGHLIGHT_COLOR, highlight_rect, border_width)


# ============================================
# 计时器绘制函数
# ============================================

def format_time(seconds: float) -> str:
    """
    将秒数格式化为分:秒.毫秒的格式。
    
    参数:
        seconds: 秒数（可以是浮点数）
    
    返回:
        格式化的时间字符串，如 "01:23.456"
    
    示例:
        >>> format_time(83.456)
        '01:23.456'
        >>> format_time(5.5)
        '00:05.500'
    """
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds * 1000) % 1000)
    return f"{minutes:02d}:{secs:02d}.{milliseconds:03d}"


def draw_timer(
    surface: pygame.Surface,
    elapsed_seconds: float,
    is_running: bool = True,
):
    """
    绘制游戏计时器。
    
    在屏幕顶部显示已用时间。
    
    参数:
        surface: Pygame 绘制表面
        elapsed_seconds: 已用时间（秒）
        is_running: 计时器是否正在运行（影响显示颜色）
    """
    # 获取计时器字体
    font = get_timer_font()
    
    # 格式化时间
    time_str = format_time(elapsed_seconds)
    
    # 选择颜色
    if is_running:
        color = TIMER_COLOR
    else:
        # 暂停或结束时使用不同的颜色
        color = (0, 255, 0)  # 绿色
    
    # 渲染时间文本
    text_surface = font.render(f"时间: {time_str}", True, color)
    
    # 绘制到屏幕
    surface.blit(text_surface, (TIMER_POSITION_X, TIMER_POSITION_Y))


def draw_game_info(
    surface: pygame.Surface,
    elapsed_seconds: float,
    remaining_seconds: float,
    time_limit: float,
    board_size_name: str,
    mode_name: str,
):
    """
    绘制游戏信息栏。
    
    显示计时器（剩余时间）、棋盘大小、游戏模式等信息。
    当剩余时间不足时，时间显示为红色警告。
    
    参数:
        surface: Pygame 绘制表面
        elapsed_seconds: 已用时间（秒）
        remaining_seconds: 剩余时间（秒）
        time_limit: 时间限制（秒）
        board_size_name: 棋盘大小名称（如 "中等 (6×6)"）
        mode_name: 游戏模式名称（如 "颜色模式" 或 "汉字模式"）
    """
    # 获取字体
    font = get_timer_font()
    
    # 格式化剩余时间
    time_str = format_time(remaining_seconds)
    
    # 判断剩余时间是否紧急（少于1/5时间或少于30秒）
    urgent_threshold = min(time_limit / 5, 30)
    if remaining_seconds <= urgent_threshold:
        # 紧急状态：显示红色
        time_color = (255, 0, 0)  # 红色
    else:
        # 正常状态：显示白色
        time_color = TIMER_COLOR
    
    # 绘制剩余时间
    time_text = f"剩余: {time_str}"
    time_surface = font.render(time_text, True, time_color)
    surface.blit(time_surface, (TIMER_POSITION_X, TIMER_POSITION_Y))
    
    # 绘制棋盘大小（在右侧）
    size_text = f"难度: {board_size_name}"
    size_surface = font.render(size_text, True, TIMER_COLOR)
    size_x = WINDOW_WIDTH - size_surface.get_width() - TIMER_POSITION_X
    surface.blit(size_surface, (size_x, TIMER_POSITION_Y))
    
    # 绘制模式（在中间）
    mode_text = f"模式: {mode_name}"
    mode_surface = font.render(mode_text, True, TIMER_COLOR)
    mode_x = (WINDOW_WIDTH - mode_surface.get_width()) // 2
    surface.blit(mode_surface, (mode_x, TIMER_POSITION_Y))


# ============================================
# 动画辅助函数
# ============================================

def _draw_box_covers(
    surface: pygame.Surface,
    board: Board,
    boxes: List[Tuple[int, int]],
    coverage: int,
    clock: pygame.time.Clock,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    mode: str = MODE_COLOR,
):
    """
    绘制带有部分覆盖效果的格子（内部函数）。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        boxes: 要绘制的格子坐标列表
        coverage: 覆盖宽度（像素）
        clock: Pygame 时钟对象
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        mode: 游戏模式
    """
    for box_x, box_y in boxes:
        # 获取格子左上角的像素坐标
        left, top = left_top_func(box_x, box_y)
        
        # 1. 先绘制背景色
        pygame.draw.rect(surface, BACKGROUND_COLOR, (left, top, box_size, box_size))
        
        # 2. 绘制完整的图标
        shape_or_char, color = get_icon(board, box_x, box_y)
        draw_icon(surface, shape_or_char, color, box_x, box_y, left_top_func, box_size, mode)
        
        # 3. 如果需要覆盖，绘制覆盖矩形
        if coverage > 0:
            cover_rect = (left, top, coverage, box_size)
            pygame.draw.rect(surface, BOX_COVER_COLOR, cover_rect)
    
    # 更新显示
    pygame.display.update()
    
    # 控制帧率
    clock.tick(FPS)


# ============================================
# 翻牌动画函数
# ============================================

def reveal_boxes_animation(
    surface: pygame.Surface,
    board: Board,
    boxes: List[Tuple[int, int]],
    clock: pygame.time.Clock,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    mode: str = MODE_COLOR,
):
    """
    翻开格子的动画效果。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        boxes: 要翻开的格子坐标列表
        clock: Pygame 时钟对象
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        mode: 游戏模式
    """
    # 从完全覆盖到完全翻开
    for coverage in range(box_size, (-REVEAL_SPEED) - 1, -REVEAL_SPEED):
        _draw_box_covers(surface, board, boxes, coverage, clock, left_top_func, box_size, mode)


def cover_boxes_animation(
    surface: pygame.Surface,
    board: Board,
    boxes: List[Tuple[int, int]],
    clock: pygame.time.Clock,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    mode: str = MODE_COLOR,
):
    """
    覆盖格子的动画效果。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        boxes: 要覆盖的格子坐标列表
        clock: Pygame 时钟对象
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        mode: 游戏模式
    """
    # 从完全翻开到完全覆盖
    for coverage in range(0, box_size + REVEAL_SPEED, REVEAL_SPEED):
        _draw_box_covers(surface, board, boxes, coverage, clock, left_top_func, box_size, mode)


# ============================================
# 开场动画函数
# ============================================

def start_game_animation(
    surface: pygame.Surface,
    board: Board,
    clock: pygame.time.Clock,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    columns: int,
    rows: int,
    mode: str = MODE_COLOR,
):
    """
    游戏开始时的开场动画。
    
    快速预览所有格子的位置，帮助玩家记忆。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        clock: Pygame 时钟对象
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        columns: 棋盘列数
        rows: 棋盘行数
        mode: 游戏模式
    """
    # 创建全未翻开的状态
    revealed = create_revealed_state(False, columns, rows)
    
    # 生成所有格子的坐标列表
    boxes = [(x, y) for x in range(columns) for y in range(rows)]
    
    # 随机打乱顺序
    random.shuffle(boxes)
    
    # 分成每组（根据棋盘大小调整每组数量）
    group_size = max(4, min(8, columns * rows // 5))
    grouped = split_every(group_size, boxes)
    
    # 先绘制一次全未翻开的棋盘
    draw_board(surface, board, revealed, left_top_func, box_size, columns, rows, mode)
    
    # 对每组执行翻开-覆盖动画
    for group in grouped:
        reveal_boxes_animation(surface, board, group, clock, left_top_func, box_size, mode)
        cover_boxes_animation(surface, board, group, clock, left_top_func, box_size, mode)


# ============================================
# 胜利动画函数
# ============================================

def game_won_animation(
    surface: pygame.Surface,
    board: Board,
    left_top_func: Callable[[int, int], Tuple[int, int]],
    box_size: int,
    columns: int,
    rows: int,
    mode: str = MODE_COLOR,
):
    """
    游戏胜利时的庆祝动画。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        left_top_func: 计算格子左上角坐标的函数
        box_size: 格子尺寸
        columns: 棋盘列数
        rows: 棋盘行数
        mode: 游戏模式
    """
    # 创建全翻开的状态
    revealed = create_revealed_state(True, columns, rows)
    
    # 定义两种闪烁颜色
    color1 = (100, 100, 100)
    color2 = BACKGROUND_COLOR
    
    # 闪烁 13 次
    for _ in range(13):
        # 交换两种颜色
        color1, color2 = color2, color1
        
        # 填充背景色
        surface.fill(color1)
        
        # 绘制棋盘
        draw_board(surface, board, revealed, left_top_func, box_size, columns, rows, mode)
        
        # 更新显示
        pygame.display.update()
        
        # 等待
        pygame.time.wait(300)


# ============================================
# 菜单绘制函数
# ============================================

def draw_menu(
    surface: pygame.Surface,
    selected_mode: str,
    selected_chinese_difficulty: str,
    selected_board_size: str,
):
    """
    绘制游戏开始菜单。
    
    菜单包含：
    - 游戏标题
    - 模式选择（颜色模式 / 汉字模式）
    - 棋盘大小选择（简单/中等/困难/专家）
    - 汉字难度选择（仅在汉字模式下显示）
    - 开始游戏提示
    
    参数:
        surface: Pygame 绘制表面
        selected_mode: 当前选中的模式
        selected_chinese_difficulty: 当前选中的汉字难度
        selected_board_size: 当前选中的棋盘大小
    """
    # 填充背景色
    surface.fill(BACKGROUND_COLOR)
    
    # 确保字体已初始化
    font = initialize_font()
    
    # 定义颜色
    text_color = (255, 255, 255)
    highlight_color = (0, 255, 0)
    dim_color = (150, 150, 150)
    
    # 计算窗口中心
    center_x = WINDOW_WIDTH // 2
    
    # 当前 Y 坐标
    current_y = 60
    
    # ============================================
    # 1. 绘制标题
    # ============================================
    title_font = pygame.font.Font(None, 56)
    title_text = "记忆翻牌游戏"
    title_surface = title_font.render(title_text, True, text_color)
    title_rect = title_surface.get_rect(centerx=center_x, centery=current_y)
    surface.blit(title_surface, title_rect)
    current_y += 50
    
    # ============================================
    # 2. 绘制模式选择
    # ============================================
    mode_title = "选择游戏模式（按 1 或 2）："
    mode_title_surface = font.render(mode_title, True, text_color)
    mode_title_rect = mode_title_surface.get_rect(centerx=center_x, centery=current_y)
    surface.blit(mode_title_surface, mode_title_rect)
    current_y += 35
    
    # 颜色模式选项
    color_option = "1. 颜色模式 (图形+颜色)"
    color_color = highlight_color if selected_mode == MODE_COLOR else dim_color
    color_surface = font.render(color_option, True, color_color)
    color_rect = color_surface.get_rect(centerx=center_x, centery=current_y)
    surface.blit(color_surface, color_rect)
    current_y += 30
    
    # 汉字模式选项
    chinese_option = "2. 汉字模式 (汉字+颜色)"
    chinese_color = highlight_color if selected_mode == MODE_CHINESE else dim_color
    chinese_surface = font.render(chinese_option, True, chinese_color)
    chinese_rect = chinese_surface.get_rect(centerx=center_x, centery=current_y)
    surface.blit(chinese_surface, chinese_rect)
    current_y += 45
    
    # ============================================
    # 3. 绘制棋盘大小选择
    # ============================================
    size_title = "选择棋盘大小（按 3/4/5/6）："
    size_title_surface = font.render(size_title, True, text_color)
    size_title_rect = size_title_surface.get_rect(centerx=center_x, centery=current_y)
    surface.blit(size_title_surface, size_title_rect)
    current_y += 35
    
    # 获取所有棋盘大小级别
    size_levels = list(BOARD_SIZE_LEVELS.keys())
    size_names = ["简单", "中等", "困难", "专家"]
    size_keys = ["3", "4", "5", "6"]
    
    for i, (level_key, level_info) in enumerate(BOARD_SIZE_LEVELS.items()):
        size_option = f"{size_keys[i]}. {size_names[i]} ({level_info['columns']}×{level_info['rows']})"
        size_color = highlight_color if selected_board_size == level_key else dim_color
        size_surface = font.render(size_option, True, size_color)
        size_rect = size_surface.get_rect(centerx=center_x, centery=current_y)
        surface.blit(size_surface, size_rect)
        current_y += 30
    
    current_y += 15
    
    # ============================================
    # 4. 绘制汉字难度选择（仅在汉字模式下显示）
    # ============================================
    if selected_mode == MODE_CHINESE:
        diff_title = "选择汉字难度（按 Q/W/E）："
        diff_title_surface = font.render(diff_title, True, text_color)
        diff_title_rect = diff_title_surface.get_rect(centerx=center_x, centery=current_y)
        surface.blit(diff_title_surface, diff_title_rect)
        current_y += 35
        
        # 简单难度选项
        easy_option = "Q. 简单 (常用字)"
        easy_color = highlight_color if selected_chinese_difficulty == "easy" else dim_color
        easy_surface = font.render(easy_option, True, easy_color)
        easy_rect = easy_surface.get_rect(centerx=center_x, centery=current_y)
        surface.blit(easy_surface, easy_rect)
        current_y += 30
        
        # 中等难度选项
        medium_option = "W. 中等 (相似字)"
        medium_color = highlight_color if selected_chinese_difficulty == "medium" else dim_color
        medium_surface = font.render(medium_option, True, medium_color)
        medium_rect = medium_surface.get_rect(centerx=center_x, centery=current_y)
        surface.blit(medium_surface, medium_rect)
        current_y += 30
        
        # 困难难度选项
        hard_option = "E. 困难 (生僻字)"
        hard_color = highlight_color if selected_chinese_difficulty == "hard" else dim_color
        hard_surface = font.render(hard_option, True, hard_color)
        hard_rect = hard_surface.get_rect(centerx=center_x, centery=current_y)
        surface.blit(hard_surface, hard_rect)
        current_y += 30
    
    current_y += 25
    
    # ============================================
    # 5. 绘制开始提示
    # ============================================
    start_hint = "按 空格键 或 回车键 开始游戏"
    start_surface = font.render(start_hint, True, text_color)
    start_rect = start_surface.get_rect(centerx=center_x, centery=current_y)
    surface.blit(start_surface, start_rect)
    
    # 更新显示
    pygame.display.update()
