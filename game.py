# -*- coding: utf-8 -*-
"""
游戏主模块 - 负责游戏流程控制和事件处理

此模块是游戏的核心控制中心，包含以下功能：
- 游戏状态管理（菜单状态 / 游戏状态）
- 事件循环和用户输入处理
- 游戏流程控制（开始菜单 -> 游戏主循环 -> 胜利 -> 重新开始）
- 匹配逻辑判断
- 支持两种游戏模式（颜色模式 / 汉字模式）
- 支持汉字模式的三种难度级别

游戏流程:
    1. 显示开始菜单，让用户选择模式和难度
    2. 按空格键或回车键开始游戏
    3. 显示开场动画（快速预览所有格子）
    4. 进入游戏主循环：
       - 等待用户点击格子
       - 翻开第一个格子，记录选择
       - 翻开第二个格子，判断是否匹配
       - 如果匹配：保持翻开状态，检查是否胜利
       - 如果不匹配：等待 1 秒后覆盖两个格子
    5. 胜利后显示胜利动画
    6. 自动重新开始新一局
"""

import pygame
from pygame.locals import (
    K_1,
    K_2,
    K_ESCAPE,
    K_e,
    K_q,
    K_RETURN,
    K_SPACE,
    K_w,
    KEYUP,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    QUIT,
)

from board import create_board, create_revealed_state, get_box_at_pixel, get_icon, has_won
from config import (
    BACKGROUND_COLOR,
    DEFAULT_DIFFICULTY,
    FPS,
    MODE_CHINESE,
    MODE_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from render import (
    cover_boxes_animation,
    draw_board,
    draw_highlight,
    draw_menu,
    game_won_animation,
    initialize_font,
    left_top_of_box,
    reveal_boxes_animation,
    start_game_animation,
)


# ============================================
# 菜单循环函数
# ============================================

def run_menu(surface: pygame.Surface, clock: pygame.time.Clock) -> Tuple[str, str]:
    """
    运行开始菜单，让用户选择游戏模式和难度。
    
    菜单操作:
        - 按 '1'：选择颜色模式
        - 按 '2'：选择汉字模式
        - 按 'Q'：选择简单难度（仅汉字模式）
        - 按 'W'：选择中等难度（仅汉字模式）
        - 按 'E'：选择困难难度（仅汉字模式）
        - 按 空格键 或 回车键：开始游戏
        - 按 ESC 或关闭窗口：退出游戏
    
    参数:
        surface: Pygame 绘制表面
        clock: Pygame 时钟对象
    
    返回:
        (selected_mode, selected_difficulty) 元组
        - selected_mode: MODE_COLOR 或 MODE_CHINESE
        - selected_difficulty: "easy", "medium", 或 "hard"
    
    示例:
        >>> mode, difficulty = run_menu(surface, clock)
        >>> print(mode, difficulty)
        'chinese', 'easy'
    """
    # 初始化默认选择
    selected_mode = MODE_COLOR      # 默认选择颜色模式
    selected_difficulty = DEFAULT_DIFFICULTY  # 默认难度
    
    # 初始化字体（确保菜单能正确显示中文）
    initialize_font()
    
    # 菜单主循环
    while True:
        # 绘制菜单界面
        draw_menu(surface, selected_mode, selected_difficulty)
        
        # 事件处理循环
        for event in pygame.event.get():
            # 处理退出事件
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit
            
            # 处理键盘按键释放事件
            elif event.type == KEYUP:
                # ESC 键：退出游戏
                if event.key == K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
                
                # '1' 键：选择颜色模式
                elif event.key == K_1:
                    selected_mode = MODE_COLOR
                
                # '2' 键：选择汉字模式
                elif event.key == K_2:
                    selected_mode = MODE_CHINESE
                
                # 难度选择（仅在汉字模式下有效）
                elif selected_mode == MODE_CHINESE:
                    # 'Q' 键：选择简单难度
                    if event.key == K_q:
                        selected_difficulty = "easy"
                    # 'W' 键：选择中等难度
                    elif event.key == K_w:
                        selected_difficulty = "medium"
                    # 'E' 键：选择困难难度
                    elif event.key == K_e:
                        selected_difficulty = "hard"
                
                # 空格键 或 回车键：开始游戏
                if event.key == K_SPACE or event.key == K_RETURN:
                    # 返回用户选择，进入游戏主循环
                    return selected_mode, selected_difficulty
        
        # 控制菜单帧率，避免 CPU 占用过高
        clock.tick(FPS)


# ============================================
# 游戏主循环函数
# ============================================

def run_game_loop(
    surface: pygame.Surface,
    clock: pygame.time.Clock,
    mode: str,
    difficulty: str,
):
    """
    运行游戏主循环。
    
    这是游戏的核心部分，处理所有游戏逻辑和用户交互。
    
    参数:
        surface: Pygame 绘制表面
        clock: Pygame 时钟对象
        mode: 游戏模式（MODE_COLOR 或 MODE_CHINESE）
        difficulty: 难度级别（"easy", "medium", "hard"）
    
    游戏逻辑:
        1. 创建随机棋盘
        2. 创建翻开状态（全部未翻开）
        3. 显示开场动画
        4. 进入主循环：
           - 处理鼠标移动：高亮悬停的格子
           - 处理鼠标点击：翻开格子
           - 判断两个格子是否匹配
           - 如果不匹配：等待后重新覆盖
           - 如果匹配：保持翻开，检查是否胜利
           - 如果胜利：显示胜利动画，重新开始
    """
    # ============================================
    # 游戏初始化
    # ============================================
    
    # 创建随机棋盘
    # 根据模式和难度生成不同的棋盘
    board = create_board(mode, difficulty)
    
    # 创建翻开状态列表，初始全部为 False（未翻开）
    revealed = create_revealed_state(False)
    
    # 记录第一个翻开的格子坐标
    # None 表示还没有翻开第一个格子
    # (box_x, box_y) 表示已翻开第一个格子，等待第二个
    first_selection = None
    
    # ============================================
    # 开场动画
    # ============================================
    
    # 填充背景色
    surface.fill(BACKGROUND_COLOR)
    
    # 显示开场动画（快速预览所有格子）
    # 帮助玩家记忆格子位置
    start_game_animation(surface, board, clock, mode)
    
    # ============================================
    # 鼠标位置跟踪
    # ============================================
    
    # 记录鼠标当前位置
    # 用于判断鼠标悬停在哪个格子上
    mouse_x = 0
    mouse_y = 0
    
    # ============================================
    # 游戏主循环
    # ============================================
    
    while True:
        # 标记本轮是否有鼠标点击
        mouse_clicked = False
        
        # 每帧开始时填充背景色
        # 清除上一帧的绘制内容
        surface.fill(BACKGROUND_COLOR)
        
        # 绘制当前棋盘状态
        # 根据 revealed 列表决定显示覆盖色还是图标
        draw_board(surface, board, revealed, mode)
        
        # ============================================
        # 事件处理
        # ============================================
        
        for event in pygame.event.get():
            # 处理退出事件
            if event.type == QUIT:
                pygame.quit()
                raise SystemExit
            
            # 处理键盘按键释放事件
            elif event.type == KEYUP:
                # ESC 键：退出游戏
                if event.key == K_ESCAPE:
                    pygame.quit()
                    raise SystemExit
            
            # 处理鼠标移动事件
            elif event.type == MOUSEMOTION:
                # 更新鼠标位置
                mouse_x, mouse_y = event.pos
            
            # 处理鼠标点击释放事件
            elif event.type == MOUSEBUTTONUP:
                # 更新鼠标位置并标记有点击
                mouse_x, mouse_y = event.pos
                mouse_clicked = True
        
        # ============================================
        # 格子悬停和点击处理
        # ============================================
        
        # 根据鼠标像素坐标获取对应的棋盘格子坐标
        # 如果鼠标不在任何格子上，返回 (None, None)
        box_x, box_y = get_box_at_pixel(mouse_x, mouse_y, left_top_of_box)
        
        # 检查鼠标是否在某个格子上
        if box_x is not None and box_y is not None:
            # 检查该格子是否未翻开
            if not revealed[box_x][box_y]:
                # 鼠标悬停在未翻开的格子上，绘制高亮边框
                # 给玩家视觉反馈，表示可以点击
                draw_highlight(surface, box_x, box_y)
            
            # 检查是否点击了未翻开的格子
            if not revealed[box_x][box_y] and mouse_clicked:
                # ============================================
                # 处理格子翻开
                # ============================================
                
                # 播放翻开动画
                reveal_boxes_animation(surface, board, [(box_x, box_y)], clock, mode)
                
                # 更新翻开状态
                revealed[box_x][box_y] = True
                
                # ============================================
                # 判断是第一次还是第二次选择
                # ============================================
                
                if first_selection is None:
                    # 这是第一次选择
                    # 记录坐标，等待第二次选择
                    first_selection = (box_x, box_y)
                else:
                    # 这是第二次选择
                    # 获取两个格子的图标进行比较
                    icon1 = get_icon(board, first_selection[0], first_selection[1])
                    icon2 = get_icon(board, box_x, box_y)
                    
                    # ============================================
                    # 判断是否匹配
                    # ============================================
                    
                    if icon1 != icon2:
                        # 两个格子不匹配
                        
                        # 等待 1 秒，让玩家看到两个不匹配的图标
                        pygame.time.wait(1000)
                        
                        # 播放覆盖动画，重新隐藏两个格子
                        cover_boxes_animation(
                            surface,
                            board,
                            [first_selection, (box_x, box_y)],
                            clock,
                            mode,
                        )
                        
                        # 更新翻开状态，将两个格子标记为未翻开
                        revealed[first_selection[0]][first_selection[1]] = False
                        revealed[box_x][box_y] = False
                        
                    else:
                        # 两个格子匹配成功！
                        
                        # 检查是否所有格子都已翻开（游戏胜利）
                        if has_won(revealed):
                            # 游戏胜利！
                            
                            # 播放胜利动画
                            game_won_animation(surface, board, mode)
                            
                            # 等待 2 秒，让玩家享受胜利时刻
                            pygame.time.wait(2000)
                            
                            # ============================================
                            # 准备新一局游戏
                            # ============================================
                            
                            # 创建新的随机棋盘
                            board = create_board(mode, difficulty)
                            
                            # 重置翻开状态
                            revealed = create_revealed_state(False)
                            
                            # 绘制新棋盘（全部未翻开）
                            draw_board(surface, board, revealed, mode)
                            pygame.display.update()
                            
                            # 等待 1 秒
                            pygame.time.wait(1000)
                            
                            # 播放新一局的开场动画
                            start_game_animation(surface, board, clock, mode)
                    
                    # 无论是否匹配，重置第一次选择
                    # 准备下一轮的两个格子选择
                    first_selection = None
        
        # ============================================
        # 更新显示和控制帧率
        # ============================================
        
        # 更新窗口显示
        # 将绘制缓冲区的内容显示到屏幕上
        pygame.display.update()
        
        # 控制游戏帧率
        # 确保游戏在不同设备上运行速度一致
        clock.tick(FPS)


# ============================================
# 游戏入口函数
# ============================================

def run_game():
    """
    游戏入口函数。
    
    这是整个游戏的起点，负责：
    1. 初始化 Pygame
    2. 创建游戏窗口
    3. 运行开始菜单
    4. 根据用户选择运行游戏主循环
    
    使用方式:
        >>> from game import run_game
        >>> run_game()
    """
    # ============================================
    # Pygame 初始化
    # ============================================
    
    # 初始化所有 Pygame 模块
    pygame.init()
    
    # 创建时钟对象，用于控制帧率
    clock = pygame.time.Clock()
    
    # 创建游戏窗口
    # 返回一个 Surface 对象，用于所有绘制操作
    surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    
    # 设置窗口标题
    pygame.display.set_caption("Memory Game")
    
    # ============================================
    # 游戏流程控制
    # ============================================
    
    # 先运行开始菜单
    # 获取用户选择的模式和难度
    mode, difficulty = run_menu(surface, clock)
    
    # 运行游戏主循环
    run_game_loop(surface, clock, mode, difficulty)


# ============================================
# 模块入口
# ============================================

if __name__ == "__main__":
    # 当此模块被直接运行时（不是被导入时），启动游戏
    run_game()
