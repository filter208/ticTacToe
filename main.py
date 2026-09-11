"""A testable Tic-Tac-Toe application.

The original public methods are kept for compatibility with the existing
course tests. Newer operations return small dictionaries/booleans instead of
printing, so they can be exercised without a terminal.
"""

from __future__ import annotations

import copy
import json
import random
import re
import unicodedata
from pathlib import Path
from typing import Callable, Optional


class TicTacToe:
    """Manage one 3x3 game and its console presentation."""

    BOARD_SIZE = 3
    EMPTY = " "
    PLAYERS = ("X", "O")
    INPUT_PATTERN = re.compile(r"^\s*([1-3])\s*[,/ ]\s*([1-3])\s*$")

    def __init__(
        self,
        player_names: Optional[dict[str, str]] = None,
        difficulty: str = "easy",
        allow_undo: bool = True,
        seed: Optional[int] = None,
        mode: str = "human",
        ai_player: str = "O",
    ):
        self.allow_undo = bool(allow_undo)
        self.random = random.Random(seed)
        self.player_names = self._normalise_player_names(player_names)
        self.difficulty = "easy"
        self.set_difficulty(difficulty)
        self.mode = "human"
        self.ai_player = "O"
        self.set_mode(mode, ai_player)
        self.scores = {"X": 0, "O": 0, "draws": 0}
        self.board: list[list[str]] = []
        self.current_player = "X"
        self.game_over = False
        self.winner: Optional[str] = None
        self.draw = False
        self.move_history: list[dict[str, int | str]] = []
        self._scored_result: Optional[str] = None
        self.reset(keep_scores=True)

    @staticmethod
    def _normalise_player_names(player_names: Optional[dict[str, str]]) -> dict[str, str]:
        names = {"X": "玩家 X", "O": "玩家 O"}
        if isinstance(player_names, dict):
            for marker in ("X", "O"):
                value = player_names.get(marker)
                if isinstance(value, str) and value.strip():
                    names[marker] = value.strip()
        return names

    def reset(self, keep_scores: bool = True) -> None:
        """Start a new round; optionally clear the match scoreboard."""
        self.board = [[self.EMPTY for _ in range(self.BOARD_SIZE)] for _ in range(self.BOARD_SIZE)]
        self.current_player = "X"
        self.game_over = False
        self.winner = None
        self.draw = False
        self.move_history = []
        self._scored_result = None
        if not keep_scores:
            self.scores = {"X": 0, "O": 0, "draws": 0}

    new_game = reset

    def set_difficulty(self, difficulty: str) -> None:
        """Set AI difficulty to easy, medium, or hard."""
        if not isinstance(difficulty, str) or difficulty.lower() not in {"easy", "medium", "hard"}:
            raise ValueError("difficulty must be easy, medium, or hard")
        self.difficulty = difficulty.lower()

    def set_mode(self, mode: str, ai_player: str = "O") -> None:
        """Set human-vs-human or human-vs-AI mode."""
        if not isinstance(mode, str) or mode.lower() not in {"human", "ai"}:
            raise ValueError("mode must be human or ai")
        if ai_player not in self.PLAYERS:
            raise ValueError("ai_player must be X or O")
        self.mode = mode.lower()
        self.ai_player = ai_player

    def print_board(self) -> None:
        """Print the board in the format used by the original program."""
        print(self.board_as_text(), end="")

    def board_as_text(self) -> str:
        lines: list[str] = []
        for index, row in enumerate(self.board):
            lines.append("|".join(row))
            if index < self.BOARD_SIZE - 1:
                lines.append("-" * 5)
        return "\n".join(lines) + "\n"

    def validate_input(self, input_str):
        """Convert a user coordinate such as ``'2,3'`` to zero-based indices."""
        if not isinstance(input_str, str):
            return None
        match = self.INPUT_PATTERN.match(input_str)
        if not match:
            return None
        row, col = (int(value) - 1 for value in match.groups())
        if 0 <= row < self.BOARD_SIZE and 0 <= col < self.BOARD_SIZE:
            return row, col
        return None

    def parse_command(self, command: str):
        """Parse a move or a CLI command and return ``(name, argument)``."""
        if not isinstance(command, str):
            return "invalid", None
        text = command.strip()
        if not text:
            return "invalid", None
        position = self.validate_input(text)
        if position is not None:
            return "move", position

        parts = text.split(maxsplit=1)
        name = parts[0].lower()
        argument = parts[1].strip() if len(parts) == 2 else None
        aliases = {
            "h": "help",
            "help": "help",
            "u": "undo",
            "undo": "undo",
            "q": "quit",
            "quit": "quit",
            "exit": "quit",
            "stats": "stats",
            "score": "stats",
            "new": "new",
            "reset": "new",
            "save": "save",
            "load": "load",
            "difficulty": "difficulty",
            "level": "difficulty",
            "mode": "mode",
        }
        parsed = aliases.get(name)
        if parsed in {"save", "load", "difficulty", "mode"} and not argument:
            return "invalid", None
        if parsed:
            return parsed, argument
        return "invalid", None

    def available_moves(self) -> list[tuple[int, int]]:
        return [
            (row, col)
            for row in range(self.BOARD_SIZE)
            for col in range(self.BOARD_SIZE)
            if self.board[row][col] == self.EMPTY
        ]

    def _valid_coordinates(self, row, col) -> bool:
        return (
            isinstance(row, int)
            and not isinstance(row, bool)
            and isinstance(col, int)
            and not isinstance(col, bool)
            and 0 <= row < self.BOARD_SIZE
            and 0 <= col < self.BOARD_SIZE
        )

    def make_move(self, row, col) -> bool:
        """Place the current marker without switching turns.

        This low-level method keeps the old contract: callers choose when to
        change ``current_player``. New code should normally use ``play_move``.
        """
        if self.game_over or not self._valid_coordinates(row, col):
            return False
        if self.board[row][col] != self.EMPTY:
            return False
        self.board[row][col] = self.current_player
        self.move_history.append({"row": row, "col": col, "player": self.current_player})
        return True

    def play_move(self, row, col) -> dict[str, object]:
        """Apply a complete turn and return a machine-readable result."""
        if self.game_over:
            return {"ok": False, "reason": "game_over", "status": self.status()}
        if not self._valid_coordinates(row, col):
            return {"ok": False, "reason": "out_of_range", "status": self.status()}
        if self.board[row][col] != self.EMPTY:
            return {"ok": False, "reason": "occupied", "status": self.status()}

        player = self.current_player
        self.make_move(row, col)
        status = self._update_terminal_state()
        if status["state"] == "playing":
            self.current_player = self._other_player(player)
        return {"ok": True, "row": row, "col": col, "player": player, "status": status}

    def _other_player(self, player: str) -> str:
        return "O" if player == "X" else "X"

    @classmethod
    def _winner_for_board(cls, board: list[list[str]]) -> Optional[str]:
        lines = [
            *board,
            *[[board[row][col] for row in range(cls.BOARD_SIZE)] for col in range(cls.BOARD_SIZE)],
            [board[index][index] for index in range(cls.BOARD_SIZE)],
            [board[index][cls.BOARD_SIZE - 1 - index] for index in range(cls.BOARD_SIZE)],
        ]
        for line in lines:
            if line[0] != cls.EMPTY and line.count(line[0]) == cls.BOARD_SIZE:
                return line[0]
        return None

    def _winning_line(self, player: Optional[str] = None) -> Optional[tuple[tuple[int, int], ...]]:
        lines = [
            ((0, 0), (0, 1), (0, 2)),
            ((1, 0), (1, 1), (1, 2)),
            ((2, 0), (2, 1), (2, 2)),
            ((0, 0), (1, 0), (2, 0)),
            ((0, 1), (1, 1), (2, 1)),
            ((0, 2), (1, 2), (2, 2)),
            ((0, 0), (1, 1), (2, 2)),
            ((0, 2), (1, 1), (2, 0)),
        ]
        target = player or self.check_winner()
        if target is None:
            return None
        for line in lines:
            if all(self.board[row][col] == target for row, col in line):
                return line
        return None

    def check_winner(self):
        """Return ``X``/``O`` when a line is complete, otherwise ``None``."""
        return self._winner_for_board(self.board)

    def check_draw(self) -> bool:
        """Return true only for a full board without a winner."""
        return self.check_winner() is None and not self.available_moves()

    def status(self) -> dict[str, object]:
        winner = self.check_winner()
        if winner:
            return {"state": "won", "winner": winner, "line": self._winning_line(winner)}
        if self.check_draw():
            return {"state": "draw", "winner": None, "line": None}
        return {"state": "playing", "winner": None, "line": None}

    def _update_terminal_state(self) -> dict[str, object]:
        result = self.status()
        if result["state"] == "won":
            self.game_over = True
            self.winner = result["winner"]
            self.draw = False
            if self._scored_result is None:
                self.scores[self.winner] += 1
                self._scored_result = self.winner
        elif result["state"] == "draw":
            self.game_over = True
            self.winner = None
            self.draw = True
            if self._scored_result is None:
                self.scores["draws"] += 1
                self._scored_result = "draw"
        return result

    def undo(self) -> bool:
        """Undo the last move and return whether anything was undone."""
        if not self.allow_undo or not self.move_history:
            return False
        move = self.move_history.pop()
        self.board[move["row"]][move["col"]] = self.EMPTY
        self.current_player = move["player"]
        self.game_over = False
        self.winner = None
        self.draw = False
        self._scored_result = None
        return True

    def scoreboard(self) -> dict[str, int]:
        return dict(self.scores)

    def _find_winning_move(self, player: str) -> Optional[tuple[int, int]]:
        for row, col in self.available_moves():
            self.board[row][col] = player
            winner = self.check_winner()
            self.board[row][col] = self.EMPTY
            if winner == player:
                return row, col
        return None

    def choose_ai_move(self, player: Optional[str] = None) -> Optional[tuple[int, int]]:
        """Choose a legal move using the configured AI difficulty."""
        player = player or self.current_player
        if player not in self.PLAYERS or self.game_over:
            return None
        moves = self.available_moves()
        if not moves:
            return None
        if self.difficulty == "easy":
            return self.random.choice(moves)

        winning_move = self._find_winning_move(player)
        if winning_move is not None:
            return winning_move
        opponent = self._other_player(player)
        if self.difficulty == "medium":
            blocking_move = self._find_winning_move(player)
            if blocking_move is not None:
                return blocking_move
            if (1, 1) in moves:
                return 1, 1
            return self.random.choice(moves)

        best_score = -10_000
        best_move = moves[0]
        for move in moves:
            row, col = move
            self.board[row][col] = player
            score = self._minimax(self.board, opponent, player, 0)
            self.board[row][col] = self.EMPTY
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def _minimax(self, board, turn: str, maximising_player: str, depth: int) -> int:
        winner = self._winner_for_board(board)
        if winner == maximising_player:
            return 10 - depth
        if winner == self._other_player(maximising_player):
            return depth - 10
        moves = [
            (row, col)
            for row in range(self.BOARD_SIZE)
            for col in range(self.BOARD_SIZE)
            if board[row][col] == self.EMPTY
        ]
        if not moves:
            return 0
        scores = []
        next_turn = self._other_player(turn)
        for row, col in moves:
            board[row][col] = turn
            scores.append(self._minimax(board, next_turn, maximising_player, depth + 1))
            board[row][col] = self.EMPTY
        return max(scores) if turn == maximising_player else min(scores)

    def snapshot(self) -> dict[str, object]:
        return {
            "board": copy.deepcopy(self.board),
            "current_player": self.current_player,
            "game_over": self.game_over,
            "winner": self.winner,
            "draw": self.draw,
            "move_history": copy.deepcopy(self.move_history),
            "scores": self.scoreboard(),
            "difficulty": self.difficulty,
            "allow_undo": self.allow_undo,
            "player_names": dict(self.player_names),
            "mode": self.mode,
            "ai_player": self.ai_player,
        }

    def _validate_snapshot(self, data: dict[str, object]) -> bool:
        board = data.get("board")
        if not isinstance(board, list) or len(board) != self.BOARD_SIZE:
            return False
        if any(not isinstance(row, list) or len(row) != self.BOARD_SIZE for row in board):
            return False
        if any(cell not in {self.EMPTY, "X", "O"} for row in board for cell in row):
            return False
        if data.get("current_player") not in self.PLAYERS:
            return False
        if data.get("mode", "human") not in {"human", "ai"}:
            return False
        if data.get("ai_player", "O") not in self.PLAYERS:
            return False
        if data.get("difficulty", "easy") not in {"easy", "medium", "hard"}:
            return False
        history = data.get("move_history")
        if not isinstance(history, list):
            return False
        return all(
            isinstance(move, dict)
            and move.get("player") in self.PLAYERS
            and self._valid_coordinates(move.get("row"), move.get("col"))
            for move in history
        )

    def save_game(self, path) -> bool:
        """Save the full round and match state as UTF-8 JSON."""
        if not isinstance(path, (str, Path)) or not str(path).strip():
            return False
        try:
            Path(path).write_text(json.dumps(self.snapshot(), ensure_ascii=False, indent=2), encoding="utf-8")
            return True
        except (OSError, TypeError, ValueError):
            return False

    def load_game(self, path) -> bool:
        """Load a previously saved state transactionally."""
        if not isinstance(path, (str, Path)) or not str(path).strip():
            return False
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return False
        if not isinstance(data, dict) or not self._validate_snapshot(data):
            return False

        self.board = copy.deepcopy(data["board"])
        self.current_player = data["current_player"]
        self.game_over = bool(data.get("game_over", False))
        self.winner = data.get("winner")
        self.draw = bool(data.get("draw", False))
        self.move_history = copy.deepcopy(data["move_history"])
        self.set_difficulty(data.get("difficulty", "easy"))
        self.allow_undo = bool(data.get("allow_undo", True))
        self.player_names = self._normalise_player_names(data.get("player_names"))
        self.set_mode(data.get("mode", "human"), data.get("ai_player", "O"))
        self._scored_result = None
        return True

    def format_scoreboard(self) -> str:
        return f"X: {self.scores['X']} | O: {self.scores['O']} | 平局: {self.scores['draws']}"

    def _help_text(self) -> str:
        return (
            "操作说明：输入行列号落子，例如 1,3；行列范围为 1-3。"
            "命令：help 帮助，undo 悔棋，save <文件> 保存，load <文件> 加载，"
            "stats 计分，difficulty <级别> 调整AI，mode <模式> 切换对战模式，"
            "new 新局，quit 退出。"
        )

    def _configure_session(
        self,
        input_fn: Callable[[], str],
        output_fn: Callable[[str], None],
    ) -> None:
        """Ask for mode and difficulty when the program is launched directly."""
        output_fn("选择对战模式：1=双人对战，2=人机对战（默认 1）")
        try:
            mode_choice = input_fn().strip().lower()
        except (EOFError, StopIteration):
            return
        if mode_choice in {"2", "ai", "人机"}:
            self.set_mode("ai", "O")
            output_fn("选择 AI 难度：easy=简单，medium=中等，hard=困难（默认 easy）")
            try:
                difficulty = input_fn().strip().lower()
            except (EOFError, StopIteration):
                difficulty = "easy"
            if difficulty in {"easy", "medium", "hard"}:
                self.set_difficulty(difficulty)
            else:
                output_fn("难度输入无效，已使用 easy。")
        else:
            self.set_mode("human", "O")

    def run(
        self,
        input_fn: Optional[Callable[[], str]] = None,
        output_fn: Optional[Callable[[str], None]] = None,
        interactive_setup: bool = False,
    ) -> str:
        """Run the console loop; dependency injection makes it testable."""
        input_fn = input_fn or input
        output_fn = output_fn or print
        output_fn("欢迎来到井字棋游戏！输入行列号（1-3），格式如：1,3")
        output_fn("------------------------------------------")
        output_fn(self._help_text())
        if interactive_setup:
            self._configure_session(input_fn, output_fn)

        while True:
            if self.mode == "ai" and self.current_player == self.ai_player and not self.game_over:
                ai_move = self.choose_ai_move(self.ai_player)
                if ai_move is not None:
                    ai_result = self.play_move(*ai_move)
                    output_fn(f"AI（{self.difficulty}）落子：{ai_move[0] + 1},{ai_move[1] + 1}")
                    if not ai_result["ok"]:
                        output_fn("AI 落子失败，请检查当前棋局状态。")
                continue
            self.print_board_to(output_fn)
            if self.game_over:
                result = self.status()
                if result["state"] == "won":
                    output_fn(f"玩家 {result['winner']} 获胜！")
                else:
                    output_fn("游戏结束，平局！")
                return "finished"

            output_fn(f"玩家 {self.current_player} 的回合，请输入行列号：")
            try:
                raw = input_fn()
            except (EOFError, StopIteration):
                return "eof"
            command, argument = self.parse_command(raw)

            if command == "move":
                result = self.play_move(*argument)
                if not result["ok"]:
                    output_fn({"occupied": "该位置已被占用，请重新选择！", "game_over": "本局已结束。"}.get(result["reason"], "无效落子。"))
            elif command == "help":
                output_fn(self._help_text())
            elif command == "undo":
                output_fn("已悔棋。" if self.undo() else "当前没有可悔棋的落子。")
            elif command == "stats":
                output_fn(self.format_scoreboard())
            elif command == "new":
                self.reset(keep_scores=True)
                output_fn("已开始新的一局。")
            elif command == "save":
                output_fn("保存成功。" if self.save_game(argument) else "保存失败。")
            elif command == "load":
                output_fn("加载成功。" if self.load_game(argument) else "加载失败。")
            elif command == "difficulty":
                try:
                    self.set_difficulty(argument)
                    output_fn(f"AI 难度已设置为 {self.difficulty}。")
                except ValueError:
                    output_fn("无效难度，请选择 easy、medium 或 hard。")
            elif command == "mode":
                try:
                    self.set_mode(argument, "O")
                    output_fn("已切换为人机对战。" if self.mode == "ai" else "已切换为双人对战。")
                except ValueError:
                    output_fn("无效模式，请选择 human 或 ai。")
            elif command == "quit":
                output_fn("已退出游戏。")
                return "quit"
            else:
                output_fn("无效输入！输入 help 查看帮助。")

    def print_board_to(self, output_fn: Callable[[str], None]) -> None:
        """Send a board to an injected output function without changing text."""
        for line in self.board_as_text().splitlines():
            output_fn(line)


class TerminalDashboard:
    """The primary polished terminal UI for the TicTacToe engine."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[96m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"
    GREEN = "\033[92m"
    RED = "\033[91m"

    def __init__(self, game: Optional[TicTacToe] = None, colour: bool = True):
        self.game = game or TicTacToe()
        self.colour = colour
        self.message = "欢迎进入竞技棋局"
        self.round_number = 1

    def paint(self, text: str, colour: str = "") -> str:
        if not self.colour or not colour:
            return text
        return f"{colour}{text}{self.RESET}"

    @staticmethod
    def _visible_width(text: str) -> int:
        plain = re.sub(r"\033\[[0-9;]*m", "", text)
        return sum(2 if unicodedata.east_asian_width(char) in {"W", "F"} else 1 for char in plain)

    def _pad_visible(self, text: str, width: int) -> str:
        return text + " " * max(0, width - self._visible_width(text))

    def _boxed_section(self, title: str, lines: list[str], width: int = 44) -> list[str]:
        prefix = f"╭─ {title} "
        top = prefix + "─" * max(0, width - self._visible_width(prefix) - 1) + "╮"
        body = [f"│{self._pad_visible(line, width - 2)}│" for line in lines]
        bottom = "╰" + "─" * (width - 2) + "╯"
        return [self.paint(top, self.CYAN), *body, self.paint(bottom, self.CYAN)]

    def clear_screen(self, output_fn: Callable[[str], None]) -> None:
        output_fn("\033[2J\033[H" if self.colour else "\n" * 2)

    def _cell(self, value: str) -> str:
        marker = value if value != self.game.EMPTY else "·"
        colour = {"X": self.RED, "O": self.YELLOW}.get(value, self.DIM)
        return self.paint(f"   {marker}   ", colour)

    def render(self) -> str:
        status = self.game.status()
        if status["state"] == "won":
            headline = self.paint(f"玩家 {status['winner']} 获胜", self.GREEN + self.BOLD)
        elif status["state"] == "draw":
            headline = self.paint("本局平局", self.YELLOW + self.BOLD)
        else:
            headline = self.paint(f"轮到玩家 {self.game.current_player}", self.CYAN + self.BOLD)

        mode = "人机对战" if self.game.mode == "ai" else "双人对战"
        title = self.paint("╔══════════════════════════════════════════════════════╗", self.CYAN)
        title += "\n" + self.paint("║                 T I C  T A C  T O E                  ║", self.CYAN + self.BOLD)
        title += "\n" + self.paint("║              TERMINAL ARENA / ROUND %02d               ║" % self.round_number, self.BLUE)
        title += "\n" + self.paint("╚══════════════════════════════════════════════════════╝", self.CYAN)

        board_lines = [
            self.paint("             1       2       3", self.DIM),
            self.paint("         ┌───────┬───────┬───────┐", self.BLUE),
        ]
        for row in range(3):
            board_lines.append(
                self.paint(f"      {row + 1}  │", self.BLUE)
                + "│".join(self._cell(self.game.board[row][col]) for col in range(3))
                + self.paint("│", self.BLUE)
            )
            if row < 2:
                board_lines.append(self.paint("         ├───────┼───────┼───────┤", self.BLUE))
        board_lines.append(self.paint("         └───────┴───────┴───────┘", self.BLUE))

        sidebar = self._boxed_section(
            "MATCH STATUS",
            [
                f"  状态       {headline}",
                f"  模式       {mode}",
                f"  AI 难度    {self.game.difficulty}",
                f"  比分       X {self.game.scores['X']}  /  O {self.game.scores['O']}",
                f"  平局       {self.game.scores['draws']}",
            ],
        )
        sidebar += [""]
        sidebar += self._boxed_section(
            "COMMANDS",
            [
                "  （直接输入坐标）       例如 1,3 / 2 2",
                "  undo       撤销最近一步",
                "  new        开始新局",
                "  save/load  保存或恢复棋局",
                "  stats      查看比分",
                "  difficulty medium",
                "  mode ai / mode human",
            ],
        )

        body = []
        for index in range(max(len(board_lines), len(sidebar))):
            left = board_lines[index] if index < len(board_lines) else ""
            right = sidebar[index] if index < len(sidebar) else ""
            body.append(self._pad_visible(left, 36) + "  " + right)

        footer = self.paint("┌─ EVENT ───────────────────────────────────────────────────────────────┐", self.BLUE)
        footer += f"\n│ {self._pad_visible(self.message, 69)} │"
        footer += "\n" + self.paint("└───────────────────────────────────────────────────────────────────────┘", self.BLUE)
        return title + "\n\n" + "\n".join(body) + "\n\n" + footer

    def _configure(self, input_fn: Callable[[], str], output_fn: Callable[[str], None]) -> None:
        output_fn("选择模式：1=双人对战，2=人机对战（默认 1）")
        try:
            choice = input_fn().strip().lower()
        except (EOFError, StopIteration):
            return
        if choice in {"2", "ai", "人机"}:
            self.game.set_mode("ai", "O")
            output_fn("选择难度：easy / medium / hard（默认 easy）")
            try:
                difficulty = input_fn().strip().lower()
            except (EOFError, StopIteration):
                difficulty = "easy"
            if difficulty in {"easy", "medium", "hard"}:
                self.game.set_difficulty(difficulty)
        else:
            self.game.set_mode("human", "O")

    def _ai_turn(self) -> None:
        if self.game.mode != "ai" or self.game.current_player != self.game.ai_player or self.game.game_over:
            return
        move = self.game.choose_ai_move(self.game.ai_player)
        if move is None:
            return
        result = self.game.play_move(*move)
        self.message = f"AI（{self.game.difficulty}）落子：{move[0] + 1},{move[1] + 1}"
        if not result["ok"]:
            self.message = "AI 落子失败，请检查棋局状态"

    def run(
        self,
        input_fn: Optional[Callable[[], str]] = None,
        output_fn: Optional[Callable[[str], None]] = None,
        interactive_setup: bool = False,
    ) -> str:
        input_fn = input_fn or input
        output_fn = output_fn or print
        if interactive_setup:
            self._configure(input_fn, output_fn)

        while True:
            self.clear_screen(output_fn)
            output_fn(self.render())
            if self.game.game_over:
                output_fn(self.paint("本局结束，输入 new 开始下一局，或 quit 退出。", self.GREEN))
            elif self.game.mode == "ai" and self.game.current_player == self.game.ai_player:
                self._ai_turn()
                continue

            try:
                raw = input_fn().strip()
            except (EOFError, StopIteration):
                return "eof"
            command, argument = self.game.parse_command(raw)

            if command == "move":
                result = self.game.play_move(*argument)
                if result["ok"]:
                    self.message = f"玩家 {result['player']} 落子：{argument[0] + 1},{argument[1] + 1}"
                else:
                    self.message = {"occupied": "目标位置已被占用", "game_over": "本局已经结束"}.get(result["reason"], "坐标无效")
            elif command == "help":
                self.message = "输入坐标落子；命令：undo / new / save 文件 / load 文件 / stats / quit"
            elif command == "undo":
                self.message = "已撤销最近落子" if self.game.undo() else "没有可撤销的落子"
            elif command == "stats":
                self.message = self.game.format_scoreboard()
            elif command == "new":
                self.game.reset(keep_scores=True)
                self.round_number += 1
                self.message = f"第 {self.round_number} 局已开始"
            elif command == "save":
                self.message = "保存成功" if self.game.save_game(argument) else "保存失败"
            elif command == "load":
                self.message = "加载成功" if self.game.load_game(argument) else "加载失败"
            elif command == "difficulty":
                try:
                    self.game.set_difficulty(argument)
                    self.message = f"AI 难度已切换为 {self.game.difficulty}"
                except ValueError:
                    self.message = "难度必须是 easy、medium 或 hard"
            elif command == "mode":
                try:
                    self.game.set_mode(argument, "O")
                    self.message = "已切换为人机对战" if self.game.mode == "ai" else "已切换为双人对战"
                except ValueError:
                    self.message = "模式必须是 human 或 ai"
            elif command == "quit":
                return "quit"
            else:
                self.message = "无法识别该操作，输入 help 查看命令"


if __name__ == "__main__":
    TerminalDashboard().run(interactive_setup=True)
