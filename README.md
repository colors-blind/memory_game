# Memory Game (Pygame)

这是一个基于 Pygame 的翻牌记忆小游戏。  
你需要连续翻开两个格子，找出所有相同的图形与颜色组合。

## 运行方式

1. 安装依赖：

```bash
pip install pygame
```

2. 运行游戏：

```bash
python memorypuzzle_obfuscated.py
```

## 项目结构

```text
memory_game/
├── memorypuzzle_obfuscated.py  # 入口文件（兼容原文件名）
├── game.py                     # 主游戏循环与事件处理
├── board.py                    # 棋盘与配对数据逻辑
├── render.py                   # 绘制与动画逻辑
├── config.py                   # 常量配置
└── README.md
```

## 模块职责说明

- `config.py`：统一管理窗口尺寸、棋盘尺寸、颜色、动画速度等常量。
- `board.py`：负责创建棋盘、管理翻牌状态、判断是否胜利等纯逻辑功能。
- `render.py`：负责绘制图形、翻牌动画、开场动画、通关动画。
- `game.py`：负责游戏流程控制、鼠标事件处理、匹配结果判断与重开逻辑。

## 操作说明

- 鼠标移动：高亮当前可翻开的格子
- 鼠标点击：翻开格子
- `ESC` 或关闭窗口：退出游戏
