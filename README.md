# 井字棋运行说明

这是一个命令行井字棋程序，支持双人对战、人机对战、悔棋、比分统计和棋局存档。

## 文件

| 文件 | 作用 |
| --- | --- |
| `main.py` | 程序主体，也是测试代码默认导入的文件。 |
| `main_fixed.py` | 修复后的程序主体，可单独运行。 |
| `test_tc01.py` | TC01 自动化测试代码。 |

## 环境

- Python 3.10 或更高版本
- 测试需要 `pytest`

安装测试依赖：

```bash
python -m pip install pytest
```

## 运行

运行主体：

```bash
python main.py
```

运行修复后的主体：

```bash
python main_fixed.py
```

启动后输入 `1` 进入双人对战，输入 `2`、`ai` 或 `人机` 进入人机对战。人机难度可选 `easy`、`medium`、`hard`。

## 操作

输入行、列坐标落子，范围均为 `1` 至 `3`，例如 `1,3`。也支持 `1 3` 和 `1/3`。

| 命令 | 作用 |
| --- | --- |
| `help` / `h` | 查看帮助 |
| `undo` / `u` | 撤销最近一步 |
| `new` / `reset` | 开始新局，保留比分 |
| `stats` / `score` | 查看比分 |
| `save 文件名` | 保存棋局 |
| `load 文件名` | 加载棋局 |
| `difficulty easy/medium/hard` | 设置 AI 难度 |
| `mode human` / `mode ai` | 切换对战模式 |
| `quit` / `exit` / `q` | 退出程序 |

## 测试

测试代码默认测试 `main.py`：

```bash
python -m pytest -q test_tc01.py
```
