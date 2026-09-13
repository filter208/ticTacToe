import copy
import json

import pytest
from pathlib import Path

from main import TicTacToe,TerminalDashboard

def _finish_x_win(game):
    """构造 X 获胜局面，供比分和终局测试复用。"""
    for row, col in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
        assert game.play_move(row, col)["ok"] is True


def _finish_o_win(game):
    """构造 O 获胜局面，供累计比分测试复用。"""
    for row, col in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2), (1, 2)]:
        assert game.play_move(row, col)["ok"] is True


def _finish_draw(game):
    """构造平局局面，供累计比分测试复用。"""
    for row, col in [(0, 0), (0, 1), (0, 2), (1, 1), (1, 0), (1, 2), (2, 1), (2, 0), (2, 2)]:
        assert game.play_move(row, col)["ok"] is True

def test_tc01_01():
    """游戏初始化：验证默认初始化状态。"""
    game = TicTacToe()
    assert game.board == [[" ", " ", " "] for _ in range(3)]
    assert game.current_player == "X"
    assert game.scoreboard() == {"X": 0, "O": 0, "draws": 0}
    assert game.status()["state"] == "playing"

def test_tc01_02():
    """坐标输入验证：验证有效输入的边界值1,1。"""
    assert TicTacToe().validate_input("1,1") == (0, 0)

def test_tc01_03():
    """坐标输入验证：验证有效输入的边界值3,3。"""
    assert TicTacToe().validate_input("3,3") == (2, 2)

def test_tc01_04():
    """坐标输入验证：验证有效输入的中间值。"""
    assert TicTacToe().validate_input("2,2") == (1, 1)

def test_tc01_05():
    """坐标输入验证：验证带空格的输入。"""
    assert TicTacToe().validate_input(" 3 , 1 ") == (2, 0)

def test_tc01_06():
    """坐标输入验证：验证空格分隔的输入。"""
    assert TicTacToe().validate_input("1 2") == (0, 1)

def test_tc01_07():
    """坐标输入验证：验证斜杠分隔的输入。"""
    assert TicTacToe().validate_input("2/3") == (1, 2)

def test_tc01_08():
    """坐标输入验证：验证逗号分隔的输入。"""
    assert TicTacToe().validate_input("1,2") == (0, 1)

def test_tc01_09():
    """坐标输入验证：验证行过小的输入。"""
    assert TicTacToe().validate_input("0,2") is None

def test_tc01_10():
    """坐标输入验证：验证列过小的输入。"""
    assert TicTacToe().validate_input("2,0") is None

def test_tc01_11():
    """坐标输入验证：验证行过大的输入。"""
    assert TicTacToe().validate_input("4,1") is None

def test_tc01_12():
    """坐标输入验证：验证列过大的输入。"""
    assert TicTacToe().validate_input("1,4") is None

def test_tc01_13():
    """坐标输入验证：验证行列过小的输入。"""
    assert TicTacToe().validate_input("0,0") is None

def test_tc01_14():
    """坐标输入验证：验证行列过大的输入。"""
    assert TicTacToe().validate_input("4,4") is None

def test_tc01_15():
    """坐标输入验证：验证字母开头的输入。"""
    assert TicTacToe().validate_input("a,2") is None

def test_tc01_16():
    """坐标输入验证：验证浮点数输入。"""
    assert TicTacToe().validate_input("1.5,3") is None

def test_tc01_17():
    """坐标输入验证：验证单值输入。"""
    assert TicTacToe().validate_input("3") is None

def test_tc01_18():
    """坐标输入验证：验证多值输入。"""
    assert TicTacToe().validate_input("1,2,3") is None

def test_tc01_19():
    """落子与回合控制：验证左上角位置落子。"""
    game = TicTacToe()

    assert game.make_move(0, 0) is True
    assert game.board[0][0] == "X"

def test_tc01_20():
    """落子与回合控制：验证右下角位置由O落子。
    """
    game = TicTacToe()
    game.current_player = "O"

    assert game.make_move(2, 2) is True
    assert game.board[2][2] == "O"

def test_tc01_21():
    """落子与回合控制：验证顶部中间位置落子。"""
    game = TicTacToe()
    assert game.make_move(0, 1) is True
    assert game.board[0][1] == "X"

def test_tc01_22():
    """落子与回合控制：验证中心位置落子。"""
    game = TicTacToe()
    assert game.make_move(1, 1) is True
    assert game.board[1][1] == "X"

def test_tc01_23():
    """落子与回合控制：验证已占用单元格落子。"""
    game = TicTacToe()
    game.make_move(1, 1)
    before = [row[:] for row in game.board]

    assert game.make_move(1, 1) is False
    assert game.board == before

def test_tc01_24():
    """落子与回合控制：验证连续落子路径。"""
    game = TicTacToe()

    assert game.make_move(0, 0) is True
    game.current_player = "O"
    assert game.make_move(1, 1) is True
    assert game.board[0][0] == "X"
    assert game.board[1][1] == "O"

def test_tc01_25():
    """落子与回合控制：验证重复落子保持原状态。"""
    game = TicTacToe()
    game.make_move(0, 0)

    assert game.make_move(0, 0) is False
    assert game.board[0][0] == "X"

def test_tc01_26():
    """落子与回合控制：验证不同玩家标记正确性。"""
    game = TicTacToe()
    game.make_move(2, 2)
    game.current_player = "O"
    game.make_move(0, 0)

    assert game.board[2][2] == "X"
    assert game.board[0][0] == "O"

def test_tc01_27(capsys):
    """棋盘显示：验证空棋盘输出。"""
    TicTacToe().print_board()
    assert capsys.readouterr().out == " | | \n-----\n | | \n-----\n | | \n"

def test_tc01_28(capsys):
    """棋盘显示：验证部分填充棋盘输出。"""
    game = TicTacToe()
    game.board = [["X", "X", "X"], ["O", "O", " "], [" ", " ", " "]]
    game.print_board()
    assert capsys.readouterr().out == "X|X|X\n-----\nO|O| \n-----\n | | \n"

def test_tc01_29(capsys):
    """棋盘显示：验证混合状态棋盘输出。"""
    game = TicTacToe()
    game.board = [["X", "O", "X"], ["O", " ", "O"], ["X", " ", "O"]]
    game.print_board()
    assert capsys.readouterr().out == "X|O|X\n-----\nO| |O\n-----\nX| |O\n"

def test_tc01_30(capsys):
    """棋盘显示：验证棋盘全满输出。"""
    game = TicTacToe()
    game.board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", "O"]]
    game.print_board()
    assert capsys.readouterr().out == "X|O|X\n-----\nO|X|O\n-----\nO|X|O\n"

def test_tc01_31(capsys):
    """棋盘显示：验证棋盘分隔线数量。"""
    TicTacToe().print_board()
    assert capsys.readouterr().out.count("-----") == 2

def test_tc01_32():
    """胜负与胜利线路判定：测试行胜利条件。"""
    game = TicTacToe()
    game.board = [["X", "X", "X"], ["O", " ", " "], ["O", " ", " "]]
    assert game.check_winner() == "X"

def test_tc01_33():
    """胜负与胜利线路判定：测试列胜利条件。"""
    game = TicTacToe()
    game.board = [["X", "O", " "], ["X", " ", " "], ["X", " ", " "]]
    assert game.check_winner() == "X"

def test_tc01_34():
    """胜负与胜利线路判定：测试对角线胜利条件。"""
    game = TicTacToe()
    game.board = [["X", "O", " "], ["O", "X", " "], [" ", " ", "X"]]
    assert game.check_winner() == "X"

def test_tc01_35():
    """胜负与胜利线路判定：测试无人胜利状态。"""
    game = TicTacToe()
    game.board = [["X", "O", " "], ["O", "X", " "], [" ", " ", " "]]
    assert game.check_winner() is None

def test_tc01_36():
    """平局与终局判定：满棋盘且存在胜利条件。"""
    game = TicTacToe()
    game.board = [["X", "O", "X"], ["O", "X", "O"], ["X", "X", "O"]]
    assert game.check_draw() is False

def test_tc01_37():
    """平局与终局判定：满棋盘且平局。"""
    game = TicTacToe()
    game.board = [["X", "O", "X"], ["X", "X", "O"], ["O", "X", "O"]]
    assert game.check_draw() is True

def test_tc01_38():
    """重新开局：验证新局保留累计比分。"""
    game = TicTacToe()
    _finish_x_win(game)
    game.reset(keep_scores=True)
    assert game.board == [[" ", " ", " "] for _ in range(3)]
    assert game.current_player == "X"
    assert game.scoreboard()["X"] == 1

def test_tc01_39():
    """重新开局：验证新局清空累计比分。"""
    game = TicTacToe()
    _finish_x_win(game)
    game.reset(keep_scores=False)
    assert game.scoreboard() == {"X": 0, "O": 0, "draws": 0}

def test_tc01_40():
    """模式切换：验证双人和人机模式切换。"""
    game = TicTacToe()
    game.set_mode("human")
    assert game.mode == "human"

    game.set_mode("ai", "O")
    assert game.mode == "ai"
    assert game.ai_player == "O"

def test_tc01_41():
    """命令解析：验证命令别名和参数解析。"""
    game = TicTacToe()
    assert game.parse_command("h") == ("help", None)
    assert game.parse_command("score") == ("stats", None)
    assert game.parse_command("save match.json") == ("save", "match.json")
    assert game.parse_command("difficulty hard") == ("difficulty", "hard")

def test_tc01_42():
    """完整回合：验证完整回合切换玩家。"""
    game = TicTacToe()
    result = game.play_move(0, 0)

    assert result["ok"] is True
    assert result["player"] == "X"
    assert result["status"]["state"] == "playing"
    assert game.current_player == "O"

def test_tc01_43():
    """完整回合：验证非法回合输入不改变状态。"""
    game = TicTacToe()
    game.play_move(0, 0)
    before = game.snapshot()

    assert game.play_move(0, 0)["ok"] is False
    assert game.play_move(3, 0)["ok"] is False
    assert game.snapshot() == before

def test_tc01_44():
    """终局保护：验证终局后拒绝继续落子。"""
    game = TicTacToe()
    _finish_x_win(game)
    result = game.play_move(2, 2)

    assert result["ok"] is False
    assert result["reason"] == "game_over"

def test_tc01_45():
    """悔棋：验证普通落子撤销。"""
    game = TicTacToe()
    game.play_move(0, 0)
    game.play_move(1, 1)

    assert game.undo() is True
    assert game.board[1][1] == game.EMPTY
    assert game.current_player == "O"
    assert len(game.move_history) == 1

def test_tc01_46():
    """悔棋：验证禁用悔棋和空棋局。"""
    empty_game = TicTacToe()
    assert empty_game.undo() is False

    disabled_game = TicTacToe(allow_undo=False)
    disabled_game.play_move(0, 0)
    assert disabled_game.undo() is False
    assert disabled_game.board[0][0] == "X"

def test_tc01_47():
    """比分管理：验证比分格式和新局逻辑。"""
    game = TicTacToe()
    _finish_x_win(game)
    assert game.format_scoreboard() == "X: 1 | O: 0 | 平局: 0"

    game.reset(keep_scores=True)
    assert game.scoreboard()["X"] == 1

def test_tc01_48():
    """存档恢复：验证棋局完整保存和恢复。"""
    game = TicTacToe(player_names={"X": "Alice", "O": "Bob"}, difficulty="hard", mode="ai")
    game.play_move(0, 0)
    game.play_move(1, 1)
    path = "./game.json"
    assert game.save_game(path) is True

    restored = TicTacToe()
    assert restored.load_game(path) is True
    assert restored.snapshot() == game.snapshot()

def test_tc01_49():
    """存档加载：验证非法存档不会污染当前状态。"""
    malformed = Path("./malformed.json")
    malformed.write_text("{not-json", encoding="utf-8")
    incomplete = Path("./incomplete.json")
    incomplete.write_text(json.dumps({"board": [["X"]]}), encoding="utf-8")
    game = TicTacToe()
    game.play_move(0, 0)
    before = game.snapshot()

    assert game.load_game(Path("./not-found.json")) is False
    assert game.load_game(malformed) is False
    assert game.load_game(incomplete) is False
    assert game.snapshot() == before

def test_tc01_50():
    """终端界面：验证CLI完成一局并输出终局结果。"""
    game = TicTacToe()
    inputs = iter(["1,1", "1,2", "2,1", "2,2", "3,1"])
    output = []
    result = game.run(input_fn=lambda: next(inputs), output_fn=output.append)

    assert result == "finished"
    assert game.winner == "X"
    assert any("玩家 X 获胜" in line for line in output)

def test_tc01_51():
    """终端界面：验证终端界面显示和AI回合。"""
    game = TicTacToe(mode="ai", difficulty="hard")
    game.current_player = "O"
    dashboard = TerminalDashboard(game, colour=False)
    rendered = dashboard.render()
    dashboard._ai_turn()

    assert "T I C  T A C  T O E" in rendered
    assert "MATCH STATUS" in rendered
    assert "COMMANDS" in rendered
    assert len(game.move_history) == 1
    assert game.move_history[0]["player"] == "O"
    assert "AI" in dashboard.message

def test_tc01_52():
    """难度设置：验证三个合法AI难度。"""
    game = TicTacToe()
    for difficulty in ("easy", "medium", "hard"):
        game.set_difficulty(difficulty)
        assert game.difficulty == difficulty


def test_tc01_53():
    """难度设置：验证非法难度抛出异常且保留原值。"""
    game = TicTacToe(difficulty="easy")
    for difficulty in ("expert", "", None):
        with pytest.raises(ValueError):
            game.set_difficulty(difficulty)
        assert game.difficulty == "easy"


def test_tc01_54():
    """模式切换：验证非法模式和AI标记不改变状态。"""
    game = TicTacToe()
    before = game.snapshot()
    with pytest.raises(ValueError):
        game.set_mode("arcade", "O")
    with pytest.raises(ValueError):
        game.set_mode("ai", "A")
    assert game.snapshot() == before


def test_tc01_55():
    """命令解析：验证坐标命令、补充别名和缺失参数。"""
    game = TicTacToe()
    assert game.parse_command("2/3") == ("move", (1, 2))
    assert game.parse_command("1,2") == ("move", (0, 1))
    assert game.parse_command("u") == ("undo", None)
    assert game.parse_command("q") == ("quit", None)
    assert game.parse_command("reset") == ("new", None)
    assert game.parse_command("level hard") == ("difficulty", "hard")
    for command in ("", "unknown", "save", "load", "mode"):
        assert game.parse_command(command) == ("invalid", None)


def test_tc01_56():
    """底层落子：验证历史记录、不自动换人和布尔坐标拒绝。"""
    game = TicTacToe()
    assert game.make_move(0, 0) is True
    assert game.make_move(1, 1) is True
    assert game.current_player == "X"
    assert len(game.move_history) == 2
    before = game.snapshot()
    assert game.make_move(True, 0) is False
    assert game.make_move(-1, 0) is False
    assert game.make_move(3, 0) is False
    assert game.make_move(0, 3) is False
    assert game.snapshot() == before


def test_tc01_57():
    """胜利线路：验证状态包含主对角线坐标。"""
    game = TicTacToe()
    game.board = [["X", "O", " "], ["O", "X", " "], [" ", " ", "X"]]
    assert game.status()["line"] == ((0, 0), (1, 1), (2, 2))


def test_tc01_58():
    """终局悔棋：验证撤销最后一步同时回退比分。"""
    game = TicTacToe()
    _finish_x_win(game)
    assert game.scoreboard()["X"] == 1
    assert game.undo() is True
    assert game.scoreboard()["X"] == 0


def test_tc01_59():
    """比分管理：验证X、O和平局可跨局累计。"""
    game = TicTacToe()
    _finish_x_win(game)
    game.reset(keep_scores=True)
    _finish_o_win(game)
    game.reset(keep_scores=True)
    _finish_draw(game)
    assert game.scoreboard() == {"X": 1, "O": 1, "draws": 1}


def test_tc01_60():
    """简单AI：验证返回合法位置且不修改棋盘。"""
    game = TicTacToe(difficulty="easy", seed=7)
    game.board[0][0], game.board[1][1] = "X", "O"
    before = copy.deepcopy(game.board)
    assert game.choose_ai_move("O") in game.available_moves()
    assert game.board == before


def test_tc01_61():
    """中等AI：验证优先获胜、阻挡和选择中心。"""
    winning = TicTacToe(difficulty="medium")
    winning.board = [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]]
    assert winning.choose_ai_move("O") == (0, 2)

    blocking = TicTacToe(difficulty="medium")
    blocking.board = [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]]
    assert blocking.choose_ai_move("X") == (0, 2)

    centre = TicTacToe(difficulty="medium")
    centre.board[0][0] = "X"
    assert centre.choose_ai_move("O") == (1, 1)


def test_tc01_62():
    """困难AI：验证获胜、阻挡和角落叉子局面处理。"""
    winning = TicTacToe(difficulty="hard")
    winning.board = [["X", "X", " "], ["O", " ", " "], [" ", "O", " "]]
    assert winning.choose_ai_move("X") == (0, 2)

    blocking = TicTacToe(difficulty="hard")
    blocking.board = [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]]
    assert blocking.choose_ai_move("X") == (0, 2)

    fork = TicTacToe(difficulty="hard")
    fork.board = [["X", " ", " "], [" ", "O", " "], [" ", " ", "X"]]
    assert fork.choose_ai_move("O") in {(0, 1), (1, 0), (1, 2), (2, 1)}


def test_tc01_63():
    """AI边界：验证非法玩家、满棋盘和终局不返回落子。"""
    game = TicTacToe(difficulty="hard")
    before = copy.deepcopy(game.board)
    assert game.choose_ai_move("A") is None
    assert game.board == before
    game.board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", "O"]]
    assert game.choose_ai_move("X") is None
    game.reset()
    game.game_over = True
    assert game.choose_ai_move("X") is None


def test_tc01_64(tmp_path):
    """存档路径：验证空路径和不存在父目录无法保存。"""
    game = TicTacToe()
    assert game.save_game(None) is False
    assert game.save_game("") is False
    assert game.save_game(tmp_path / "missing" / "game.json") is False


def test_tc01_65(tmp_path):
    """存档字段：验证非法单元格、玩家、模式和难度被拒绝。"""
    payloads = [
        {"board": [["A", " ", " "], [" ", " ", " "], [" ", " ", " "]]},
        {"board": [[" ", " ", " "]] * 3, "current_player": "A"},
        {"board": [[" ", " ", " "]] * 3, "current_player": "X", "mode": "arcade"},
        {"board": [[" ", " ", " "]] * 3, "current_player": "X", "difficulty": "expert"},
    ]
    game = TicTacToe()
    game.play_move(0, 0)
    before = game.snapshot()
    for index, payload in enumerate(payloads):
        path = tmp_path / f"invalid-{index}.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        assert game.load_game(path) is False
        assert game.snapshot() == before


def test_tc01_66(tmp_path):
    """存档比分：验证加载后恢复累计比分。"""
    path = tmp_path / "scores.json"
    source = TicTacToe()
    _finish_x_win(source)
    assert source.save_game(path) is True
    restored = TicTacToe()
    assert restored.load_game(path) is True
    assert restored.scoreboard()["X"] == 1


def test_tc01_67():
    """终端界面：验证命令可切换难度和对战模式。"""
    game = TicTacToe()
    inputs, output = iter(["difficulty hard", "mode ai", "quit"]), []
    assert game.run(input_fn=lambda: next(inputs), output_fn=output.append) == "quit"
    assert game.difficulty == "hard"
    assert game.mode == "ai"


def test_tc01_68():
    """终端界面：验证人机模式自动执行AI回合。"""
    game = TicTacToe(mode="ai", difficulty="hard")
    inputs, output = iter(["1,1", "quit"]), []
    assert game.run(input_fn=lambda: next(inputs), output_fn=output.append) == "quit"
    assert len(game.move_history) == 2
    assert game.move_history[1]["player"] == "O"


def test_tc01_69():
    """终端面板：验证显示的棋盘内容和当前状态同步。"""
    game = TicTacToe()
    game.board[0][0], game.board[1][1] = "X", "O"
    rendered = TerminalDashboard(game, colour=False).render()
    board_lines = [line for line in rendered.splitlines() if "│" in line]
    assert any("1  │" in line and "X" in line for line in board_lines)
    assert any("2  │" in line and "O" in line for line in board_lines)
    assert "轮到玩家 X" in rendered


def test_tc01_70():
    """胜负状态：验证O列胜利和满棋盘平局状态。"""
    winning = TicTacToe()
    winning.board = [["O", "X", " "], ["O", " ", " "], ["O", " ", " "]]
    assert winning.check_winner() == "O"

    drawn = TicTacToe()
    drawn.board = [["X", "O", "X"], ["X", "X", "O"], ["O", "X", "O"]]
    assert drawn.status()["state"] == "draw"


def test_tc01_71():
    """简单AI：验证唯一空位必被选择。"""
    game = TicTacToe(difficulty="easy", seed=7)
    game.board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", " "]]
    assert game.choose_ai_move("O") == (2, 2)


def test_tc01_72():
    """终端面板：验证初始界面展示坐标栏。"""
    rendered = TerminalDashboard(TicTacToe(), colour=False).render()
    assert "1       2       3" in rendered
