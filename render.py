# -*- coding: utf-8 -*-
"""
渲染模块 - 负责游戏界面的绘制和动画效果

此模块包含以下功能：
- 坐标转换（棋盘坐标 -> 像素坐标）
- 图标的绘制（形状和汉字）
- 棋盘的整体绘制
- 翻牌动画（翻开和覆盖）
- 开场动画（快速预览所有格子）
- 胜利动画（闪烁效果）
- 菜单界面绘制（模式选择）
"""

import random
from typing import List, Optional, Tuple

import pygame

from board import Board, Revealed, create_revealed_state, get_icon, split_every
from config import (
    BACKGROUND_COLOR,
    BOARD_COLUMNS,
    BOARD_ROWS,
    BOX_COVER_COLOR,
    BOX_SIZE,
    FONT_OFFSET_X,
    FONT_OFFSET_Y,
    FONT_SIZE,
    FPS,
    GAP_SIZE,
    HIGHLIGHT_COLOR,
    MODE_CHINESE,
    MODE_COLOR,
    REVEAL_SPEED,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    X_MARGIN,
    Y_MARGIN,
)

# ============================================
# 全局变量
# ============================================

# 字体对象（用于汉字渲染）
# 在 initialize_font() 函数中初始化
_font: Optional[pygame.font.Font] = None


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
    
    # 打印系统中包含 "chinese"、"cjk"、"hei"、"song" 等关键字的字体
    # 帮助用户了解系统中有哪些中文字体
    print("检测到的可能支持中文的字体:")
    for font_name in available_fonts:
        lower_name = font_name.lower()
        # 检查字体名称是否包含中文相关的关键字
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
    # 这是更可靠的方法，可以直接找到字体文件的完整路径
    for font_name in chinese_font_names:
        try:
            # 使用 match_font 查找字体文件路径
            # bold=False, italic=False
            font_path = pygame.font.match_font(font_name, bold=False, italic=False)
            
            if font_path:
                print(f"找到字体文件: {font_path}")
                
                # 直接使用字体文件路径创建字体对象
                _font = pygame.font.Font(font_path, FONT_SIZE)
                
                # 测试字体是否支持中文
                test_text = "中文测试"
                metrics = _font.metrics(test_text)
                
                if metrics and all(m is not None for m in metrics):
                    print(f"成功加载字体: {font_name} (路径: {font_path})")
                    return _font
                    
        except Exception as e:
            # 继续尝试下一个字体
            continue
    
    # 方法2: 使用 SysFont 加载（备选方法）
    for font_name in chinese_font_names:
        try:
            # 尝试使用 SysFont 加载字体
            _font = pygame.font.SysFont(font_name, FONT_SIZE, bold=False, italic=False)
            
            # 测试字体是否支持中文
            test_text = "中文测试"
            metrics = _font.metrics(test_text)
            
            if metrics and all(m is not None for m in metrics):
                print(f"成功加载字体: {font_name}")
                return _font
                
        except Exception as e:
            # 继续尝试下一个字体
            continue
    
    # 方法3: 尝试使用常见的字体文件名直接查找
    # 有些字体可能不在系统字体列表中，但在特定路径下
    common_font_files = [
        # Linux 常见字体路径
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/arphic/uming.ttc",
        "/usr/share/fonts/truetype/arphic/ukai.ttc",
        
        # 通用字体名称（让 Pygame 自己查找）
        "wqy-microhei",
        "wqy-zenhei",
        "NotoSansCJKsc",
        "DroidSansFallback",
    ]
    
    print("尝试直接加载常见中文字体文件...")
    for font_path in common_font_files:
        try:
            # 尝试直接加载字体文件
            _font = pygame.font.Font(font_path, FONT_SIZE)
            
            # 测试字体是否支持中文
            test_text = "中文测试"
            metrics = _font.metrics(test_text)
            
            if metrics and all(m is not None for m in metrics):
                print(f"成功加载字体文件: {font_path}")
                return _font
                
        except Exception as e:
            # 继续尝试下一个字体
            continue
    
    # 如果使用名称找不到字体，尝试使用默认字体
    print("警告：未找到支持中文的系统字体，尝试使用默认字体...")
    
    # 尝试使用 pygame.font.get_default_font()
    try:
        default_font_name = pygame.font.get_default_font()
        print(f"Pygame 默认字体: {default_font_name}")
        
        # 尝试使用默认字体名称加载
        _font = pygame.font.SysFont(default_font_name, FONT_SIZE)
        return _font
    except Exception:
        pass
    
    # 最后的备选方案：使用 None 作为字体名称
    # 这会让 Pygame 使用内置的默认字体
    print("使用 Pygame 内置默认字体（可能不支持中文）")
    print("提示：如果中文显示为方块，请安装中文字体")
    print("常见 Linux 中文字体包：")
    print("  - Ubuntu/Debian: sudo apt install fonts-wqy-microhei fonts-noto-cjk")
    print("  - Fedora/RHEL: sudo dnf install wqy-microhei-fonts google-noto-sans-cjk-sc-fonts")
    print("  - Arch: sudo pacman -S wqy-microhei noto-fonts-cjk")
    
    _font = pygame.font.Font(None, FONT_SIZE)
    return _font


# ============================================
# 坐标转换函数
# ============================================

def left_top_of_box(box_x: int, box_y: int) -> Tuple[int, int]:
    """
    根据棋盘格子坐标计算其左上角的像素坐标。
    
    棋盘坐标从 (0, 0) 开始，对应左上角的第一个格子。
    像素坐标用于 Pygame 的绘制函数。
    
    参数:
        box_x: 格子的列索引（从 0 开始）
        box_y: 格子的行索引（从 0 开始）
    
    返回:
        (left, top) 元组，表示格子左上角的像素坐标
    
    示例:
        >>> left_top_of_box(0, 0)
        (70, 65)  # 取决于 X_MARGIN 和 Y_MARGIN 的值
        
        >>> left_top_of_box(1, 0)
        (120, 65)  # 70 + 40 + 10 = 120
    
    计算逻辑:
        left = X_MARGIN + box_x * (BOX_SIZE + GAP_SIZE)
        top = Y_MARGIN + box_y * (BOX_SIZE + GAP_SIZE)
    """
    return (
        box_x * (BOX_SIZE + GAP_SIZE) + X_MARGIN,
        box_y * (BOX_SIZE + GAP_SIZE) + Y_MARGIN,
    )


# ============================================
# 图标绘制函数
# ============================================

def draw_icon(
    surface: pygame.Surface,
    shape_or_char: str,
    color: Tuple[int, int, int],
    box_x: int,
    box_y: int,
    mode: str = MODE_COLOR,
):
    """
    在指定格子位置绘制图标。
    
    支持两种模式：
    - 颜色模式：绘制预定义的几何形状
    - 汉字模式：绘制汉字字符
    
    参数:
        surface: Pygame 绘制表面（通常是窗口表面）
        shape_or_char: 形状标识（颜色模式）或汉字字符（汉字模式）
        color: 图标颜色（RGB 元组）
        box_x: 格子的列索引
        box_y: 格子的行索引
        mode: 绘制模式，MODE_COLOR 或 MODE_CHINESE
    
    示例:
        # 颜色模式：绘制一个红色的圆形（形状 'a'）
        >>> draw_icon(surface, 'a', (255, 0, 0), 0, 0, MODE_COLOR)
        
        # 汉字模式：绘制一个红色的'一'字
        >>> draw_icon(surface, '一', (255, 0, 0), 0, 0, MODE_CHINESE)
    """
    if mode == MODE_CHINESE:
        _draw_chinese_icon(surface, shape_or_char, color, box_x, box_y)
    else:
        _draw_shape_icon(surface, shape_or_char, color, box_x, box_y)


def _draw_shape_icon(
    surface: pygame.Surface,
    shape: str,
    color: Tuple[int, int, int],
    box_x: int,
    box_y: int,
):
    """
    绘制颜色模式的几何形状图标（内部函数）。
    
    支持的形状：
    - 'a': 圆环（带中心孔的圆形）
    - 'b': 正方形
    - 'c': 菱形（旋转45度的正方形）
    - 'd': 对角线装饰
    - 'e': 椭圆
    
    参数:
        surface: Pygame 绘制表面
        shape: 形状标识 ('a'-'e')
        color: 形状颜色
        box_x: 格子的列索引
        box_y: 格子的行索引
    """
    # 获取格子左上角的像素坐标
    left, top = left_top_of_box(box_x, box_y)
    
    # 计算格子中心坐标（用于绘制对称图形）
    center_x = left + BOX_SIZE // 2
    center_y = top + BOX_SIZE // 2
    
    if shape == "a":
        # 形状 'a': 圆环
        # 外层实心圆
        pygame.draw.circle(surface, color, (center_x, center_y), 15)
        # 内层用背景色绘制一个小圆，形成圆环效果
        pygame.draw.circle(surface, BACKGROUND_COLOR, (center_x, center_y), 5)
        
    elif shape == "b":
        # 形状 'b': 正方形
        # 计算正方形的位置和大小（居中，边长 20）
        rect_left = left + 10
        rect_top = top + 10
        pygame.draw.rect(surface, color, (rect_left, rect_top, 20, 20))
        
    elif shape == "c":
        # 形状 'c': 菱形
        # 定义四个顶点（顺时针方向）
        # 上顶点、右顶点、下顶点、左顶点
        vertices = (
            (center_x, top),                    # 上
            (left + BOX_SIZE - 1, center_y),   # 右
            (center_x, top + BOX_SIZE - 1),    # 下
            (left, center_y),                   # 左
        )
        pygame.draw.polygon(surface, color, vertices)
        
    elif shape == "d":
        # 形状 'd': 对角线装饰
        # 绘制两组交叉的对角线
        for i in range(0, BOX_SIZE, 4):
            # 从左上到右下的对角线（上半部分）
            pygame.draw.line(surface, color, (left, top + i), (left + i, top))
            # 从右下到左上的对角线（下半部分）
            pygame.draw.line(
                surface,
                color,
                (left + i, top + BOX_SIZE - 1),
                (left + BOX_SIZE - 1, top + i),
            )
            
    elif shape == "e":
        # 形状 'e': 椭圆
        # 计算椭圆的包围矩形
        # 椭圆在垂直方向居中，水平方向占满整个格子
        ellipse_rect = (left, top + 10, BOX_SIZE, 20)
        pygame.draw.ellipse(surface, color, ellipse_rect)


def _draw_chinese_icon(
    surface: pygame.Surface,
    char: str,
    color: Tuple[int, int, int],
    box_x: int,
    box_y: int,
):
    """
    绘制汉字模式的汉字图标（内部函数）。
    
    使用 Pygame 的字体渲染功能绘制汉字。
    汉字会在格子中居中显示。
    
    参数:
        surface: Pygame 绘制表面
        char: 要绘制的汉字字符
        color: 汉字颜色
        box_x: 格子的列索引
        box_y: 格子的行索引
    """
    # 获取格子左上角的像素坐标
    left, top = left_top_of_box(box_x, box_y)
    
    # 确保字体已初始化
    font = initialize_font()
    
    # 渲染汉字为图像
    # antialias=True 表示开启抗锯齿，使文字边缘更平滑
    text_surface = font.render(char, True, color)
    
    # 计算文字的居中位置
    # 文字在格子中的位置 = 格子左上角 + 偏移量
    text_x = left + FONT_OFFSET_X
    text_y = top + FONT_OFFSET_Y
    
    # 绘制文字到表面
    surface.blit(text_surface, (text_x, text_y))


# ============================================
# 棋盘绘制函数
# ============================================

def draw_board(
    surface: pygame.Surface,
    board: Board,
    revealed: Revealed,
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
        mode: 游戏模式（决定图标的绘制方式）
    
    绘制流程:
        1. 遍历每一列
        2. 遍历每一行
        3. 检查格子是否已翻开
        4. 根据状态绘制覆盖色或图标
    """
    for box_x in range(BOARD_COLUMNS):
        for box_y in range(BOARD_ROWS):
            # 获取格子左上角的像素坐标
            left, top = left_top_of_box(box_x, box_y)
            
            if not revealed[box_x][box_y]:
                # 格子未翻开：绘制覆盖色（白色方块）
                pygame.draw.rect(surface, BOX_COVER_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
            else:
                # 格子已翻开：获取并绘制图标
                shape_or_char, color = get_icon(board, box_x, box_y)
                draw_icon(surface, shape_or_char, color, box_x, box_y, mode)


# ============================================
# 高亮绘制函数
# ============================================

def draw_highlight(surface: pygame.Surface, box_x: int, box_y: int):
    """
    绘制格子的高亮边框。
    
    当鼠标悬停在未翻开的格子上时，显示一个蓝色边框。
    边框比格子稍大，形成突出显示效果。
    
    参数:
        surface: Pygame 绘制表面
        box_x: 格子的列索引
        box_y: 格子的行索引
    
    绘制效果:
        - 边框向外扩展 5 像素
        - 边框宽度 4 像素
        - 边框颜色为蓝色 (HIGHLIGHT_COLOR)
    """
    # 获取格子左上角的像素坐标
    left, top = left_top_of_box(box_x, box_y)
    
    # 计算高亮边框的矩形
    # 向左和向上扩展 5 像素，宽度和高度各增加 10 像素
    highlight_rect = (
        left - 5,           # 左边界向左扩展 5 像素
        top - 5,            # 上边界向上扩展 5 像素
        BOX_SIZE + 10,      # 宽度增加 10 像素（左右各 5）
        BOX_SIZE + 10,      # 高度增加 10 像素（上下各 5）
    )
    
    # 绘制边框（width=4 表示只绘制边框，不填充）
    pygame.draw.rect(surface, HIGHLIGHT_COLOR, highlight_rect, 4)


# ============================================
# 动画辅助函数
# ============================================

def _draw_box_covers(
    surface: pygame.Surface,
    board: Board,
    boxes: List[Tuple[int, int]],
    coverage: int,
    clock: pygame.time.Clock,
    mode: str = MODE_COLOR,
):
    """
    绘制带有部分覆盖效果的格子（内部函数）。
    
    此函数用于翻牌动画的每一帧绘制。
    通过逐渐改变覆盖宽度，实现翻开/覆盖的动画效果。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        boxes: 要绘制的格子坐标列表 [(box_x, box_y), ...]
        coverage: 覆盖宽度（像素）。0 表示完全翻开，BOX_SIZE 表示完全覆盖
        clock: Pygame 时钟对象（用于控制帧率）
        mode: 游戏模式
    
    绘制流程:
        1. 绘制背景色（清除之前的内容）
        2. 绘制完整的图标
        3. 如果 coverage > 0，绘制覆盖矩形
        4. 更新显示并控制帧率
    """
    for box_x, box_y in boxes:
        # 获取格子左上角的像素坐标
        left, top = left_top_of_box(box_x, box_y)
        
        # 1. 先绘制背景色（清除此格子区域）
        pygame.draw.rect(surface, BACKGROUND_COLOR, (left, top, BOX_SIZE, BOX_SIZE))
        
        # 2. 绘制完整的图标
        shape_or_char, color = get_icon(board, box_x, box_y)
        draw_icon(surface, shape_or_char, color, box_x, box_y, mode)
        
        # 3. 如果需要覆盖，绘制覆盖矩形
        # coverage 表示从左侧开始覆盖的宽度
        if coverage > 0:
            cover_rect = (left, top, coverage, BOX_SIZE)
            pygame.draw.rect(surface, BOX_COVER_COLOR, cover_rect)
    
    # 更新显示
    pygame.display.update()
    
    # 控制帧率（确保动画速度一致）
    clock.tick(FPS)


# ============================================
# 翻牌动画函数
# ============================================

def reveal_boxes_animation(
    surface: pygame.Surface,
    board: Board,
    boxes: List[Tuple[int, int]],
    clock: pygame.time.Clock,
    mode: str = MODE_COLOR,
):
    """
    翻开格子的动画效果。
    
    模拟从左向右掀开覆盖层的效果。
    覆盖宽度从 BOX_SIZE（完全覆盖）逐渐减小到 0（完全翻开）。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        boxes: 要翻开的格子坐标列表
        clock: Pygame 时钟对象
        mode: 游戏模式
    
    动画过程:
        1. coverage = BOX_SIZE（完全覆盖，只看到白色）
        2. coverage 逐渐减小（图标从右侧逐渐露出）
        3. coverage = 0（完全翻开，看到完整图标）
    
    示例:
        >>> # 翻开第 1 列第 1 行的格子
        >>> reveal_boxes_animation(surface, board, [(0, 0)], clock)
    """
    # 从完全覆盖到完全翻开
    # 步长为 -REVEAL_SPEED，表示每次减少 REVEAL_SPEED 像素
    # 终止值为 (-REVEAL_SPEED) - 1，确保能覆盖到 0
    for coverage in range(BOX_SIZE, (-REVEAL_SPEED) - 1, -REVEAL_SPEED):
        _draw_box_covers(surface, board, boxes, coverage, clock, mode)


def cover_boxes_animation(
    surface: pygame.Surface,
    board: Board,
    boxes: List[Tuple[int, int]],
    clock: pygame.time.Clock,
    mode: str = MODE_COLOR,
):
    """
    覆盖格子的动画效果。
    
    模拟从左向右盖上覆盖层的效果。
    覆盖宽度从 0（完全翻开）逐渐增加到 BOX_SIZE（完全覆盖）。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        boxes: 要覆盖的格子坐标列表
        clock: Pygame 时钟对象
        mode: 游戏模式
    
    动画过程:
        1. coverage = 0（完全翻开，看到完整图标）
        2. coverage 逐渐增大（覆盖层从左侧逐渐向右扩展）
        3. coverage = BOX_SIZE（完全覆盖，只看到白色）
    
    用途:
        当玩家翻开的两个格子不匹配时，短暂显示后用此动画重新覆盖
    """
    # 从完全翻开到完全覆盖
    # 终止值为 BOX_SIZE + REVEAL_SPEED，确保能覆盖到 BOX_SIZE
    for coverage in range(0, BOX_SIZE + REVEAL_SPEED, REVEAL_SPEED):
        _draw_box_covers(surface, board, boxes, coverage, clock, mode)


# ============================================
# 开场动画函数
# ============================================

def start_game_animation(
    surface: pygame.Surface,
    board: Board,
    clock: pygame.time.Clock,
    mode: str = MODE_COLOR,
):
    """
    游戏开始时的开场动画。
    
    快速预览所有格子的位置，帮助玩家记忆。
    格子会分组进行翻开-覆盖的动画效果。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        clock: Pygame 时钟对象
        mode: 游戏模式
    
    动画流程:
        1. 创建全未翻开的状态
        2. 生成所有格子的坐标列表并随机打乱
        3. 将坐标分成每组 8 个
        4. 对每组依次执行：
           - 翻开动画（快速显示图标）
           - 覆盖动画（重新隐藏）
    
    设计目的:
        - 让玩家在游戏开始前快速预览所有格子的位置
        - 增加游戏的趣味性和挑战性
        - 分组动画避免一次性显示过多信息
    """
    # 创建全未翻开的状态
    revealed = create_revealed_state(False)
    
    # 生成所有格子的坐标列表
    # 格式: [(0,0), (0,1), ..., (9,6)]
    boxes = [(x, y) for x in range(BOARD_COLUMNS) for y in range(BOARD_ROWS)]
    
    # 随机打乱顺序
    random.shuffle(boxes)
    
    # 分成每组 8 个
    grouped = split_every(8, boxes)
    
    # 先绘制一次全未翻开的棋盘
    draw_board(surface, board, revealed, mode)
    
    # 对每组执行翻开-覆盖动画
    for group in grouped:
        # 快速翻开（预览）
        reveal_boxes_animation(surface, board, group, clock, mode)
        # 快速覆盖（重新隐藏）
        cover_boxes_animation(surface, board, group, clock, mode)


# ============================================
# 胜利动画函数
# ============================================

def game_won_animation(surface: pygame.Surface, board: Board, mode: str = MODE_COLOR):
    """
    游戏胜利时的庆祝动画。
    
    背景色交替闪烁，营造庆祝氛围。
    
    参数:
        surface: Pygame 绘制表面
        board: 棋盘二维列表
        mode: 游戏模式
    
    动画效果:
        - 背景色在两种颜色之间交替切换
        - 棋盘保持显示（所有格子已翻开）
        - 共闪烁 13 次
        - 每次闪烁间隔 300 毫秒
    
    设计目的:
        - 给玩家明确的胜利反馈
        - 营造庆祝氛围
        - 闪烁次数为奇数，确保最终停在背景色上
    """
    # 创建全翻开的状态
    revealed = create_revealed_state(True)
    
    # 定义两种闪烁颜色
    # color1: 深灰色
    # color2: 正常背景色
    color1 = (100, 100, 100)
    color2 = BACKGROUND_COLOR
    
    # 闪烁 13 次（奇数次，确保最后停在背景色）
    for _ in range(13):
        # 交换两种颜色
        color1, color2 = color2, color1
        
        # 填充背景色
        surface.fill(color1)
        
        # 绘制棋盘（所有格子已翻开）
        draw_board(surface, board, revealed, mode)
        
        # 更新显示
        pygame.display.update()
        
        # 等待 300 毫秒
        pygame.time.wait(300)


# ============================================
# 菜单绘制函数
# ============================================

def draw_menu(
    surface: pygame.Surface,
    selected_mode: str,
    selected_difficulty: str,
):
    """
    绘制游戏开始菜单。
    
    菜单包含：
    - 游戏标题
    - 模式选择（颜色模式 / 汉字模式）
    - 难度选择（仅在汉字模式下显示）
    - 开始游戏提示
    
    参数:
        surface: Pygame 绘制表面
        selected_mode: 当前选中的模式 (MODE_COLOR 或 MODE_CHINESE)
        selected_difficulty: 当前选中的难度 ("easy", "medium", "hard")
    
    绘制效果:
        - 选中的选项用亮色高亮显示
        - 未选中的选项用暗色显示
        - 使用不同的 Y 坐标实现垂直布局
    """
    # 填充背景色
    surface.fill(BACKGROUND_COLOR)
    
    # 确保字体已初始化
    font = initialize_font()
    
    # 定义颜色
    text_color = (255, 255, 255)      # 白色（普通文本）
    highlight_color = (0, 255, 0)       # 绿色（选中项）
    dim_color = (150, 150, 150)         # 灰色（未选中项）
    
    # 计算窗口中心（用于居中对齐）
    center_x = WINDOW_WIDTH // 2
    
    # ============================================
    # 1. 绘制标题
    # ============================================
    title_text = "记忆翻牌游戏"
    # 创建大字体（使用默认字体，放大倍数）
    title_font = pygame.font.Font(None, 48)
    title_surface = title_font.render(title_text, True, text_color)
    # 计算居中位置
    title_rect = title_surface.get_rect(centerx=center_x, centery=80)
    surface.blit(title_surface, title_rect)
    
    # ============================================
    # 2. 绘制模式选择标题
    # ============================================
    mode_title = "选择游戏模式："
    mode_title_surface = font.render(mode_title, True, text_color)
    mode_title_rect = mode_title_surface.get_rect(centerx=center_x, centery=160)
    surface.blit(mode_title_surface, mode_title_rect)
    
    # ============================================
    # 3. 绘制颜色模式选项
    # ============================================
    color_option = "1. 颜色模式 (图形+颜色)"
    # 根据是否选中选择颜色
    color_color = highlight_color if selected_mode == MODE_COLOR else dim_color
    color_surface = font.render(color_option, True, color_color)
    color_rect = color_surface.get_rect(centerx=center_x, centery=200)
    surface.blit(color_surface, color_rect)
    
    # ============================================
    # 4. 绘制汉字模式选项
    # ============================================
    chinese_option = "2. 汉字模式 (汉字+颜色)"
    # 根据是否选中选择颜色
    chinese_color = highlight_color if selected_mode == MODE_CHINESE else dim_color
    chinese_surface = font.render(chinese_option, True, chinese_color)
    chinese_rect = chinese_surface.get_rect(centerx=center_x, centery=240)
    surface.blit(chinese_surface, chinese_rect)
    
    # ============================================
    # 5. 绘制难度选择（仅在汉字模式下显示）
    # ============================================
    if selected_mode == MODE_CHINESE:
        # 难度选择标题
        diff_title = "选择难度："
        diff_title_surface = font.render(diff_title, True, text_color)
        diff_title_rect = diff_title_surface.get_rect(centerx=center_x, centery=300)
        surface.blit(diff_title_surface, diff_title_rect)
        
        # 简单难度选项
        easy_option = "Q. 简单 (常用字)"
        easy_color = highlight_color if selected_difficulty == "easy" else dim_color
        easy_surface = font.render(easy_option, True, easy_color)
        easy_rect = easy_surface.get_rect(centerx=center_x, centery=340)
        surface.blit(easy_surface, easy_rect)
        
        # 中等难度选项
        medium_option = "W. 中等 (相似字)"
        medium_color = highlight_color if selected_difficulty == "medium" else dim_color
        medium_surface = font.render(medium_option, True, medium_color)
        medium_rect = medium_surface.get_rect(centerx=center_x, centery=380)
        surface.blit(medium_surface, medium_rect)
        
        # 困难难度选项
        hard_option = "E. 困难 (生僻字)"
        hard_color = highlight_color if selected_difficulty == "hard" else dim_color
        hard_surface = font.render(hard_option, True, hard_color)
        hard_rect = hard_surface.get_rect(centerx=center_x, centery=420)
        surface.blit(hard_surface, hard_rect)
    
    # ============================================
    # 6. 绘制开始提示
    # ============================================
    start_hint = "按 空格键 或 回车键 开始游戏"
    start_surface = font.render(start_hint, True, text_color)
    start_rect = start_surface.get_rect(centerx=center_x, centery=450)
    surface.blit(start_surface, start_rect)
    
    # 更新显示
    pygame.display.update()
