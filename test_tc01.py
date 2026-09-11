import pytest

from main import TicTacToe

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

    修改说明：make_move是底层接口，不负责自动切换玩家，因此在前置条件
    中显式设置current_player为O。
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


