"""TC_02 test suite designed from scratch for the current main.py project.

The function names intentionally retain the test-case IDs so that each
automated result can be traced back to the AI test-case list.
"""

import copy
import json

import pytest

from main import TerminalDashboard, TicTacToe


def _win_for_x(game: TicTacToe) -> None:
    for move in [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]:
        assert game.play_move(*move)["ok"] is True


def _win_for_o(game: TicTacToe) -> None:
    for move in [(0, 0), (1, 0), (0, 1), (1, 1), (2, 2), (1, 2)]:
        assert game.play_move(*move)["ok"] is True


def _draw(game: TicTacToe) -> None:
    moves = [
        (0, 0), (0, 1), (0, 2),
        (1, 1), (1, 0), (1, 2),
        (2, 1), (2, 0), (2, 2),
    ]
    for move in moves:
        assert game.play_move(*move)["ok"] is True


def test_tc_02_01_initial_state():
    game = TicTacToe()

    assert game.board == [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
    assert game.current_player == "X"
    assert game.scoreboard() == {"X": 0, "O": 0, "draws": 0}
    assert game.status()["state"] == "playing"


def test_tc_02_02_reset_keeps_scores():
    game = TicTacToe()
    _win_for_x(game)

    game.reset(keep_scores=True)

    assert game.board == [[" ", " ", " "] for _ in range(3)]
    assert game.current_player == "X"
    assert game.scoreboard() == {"X": 1, "O": 0, "draws": 0}


def test_tc_02_03_reset_clears_scores():
    game = TicTacToe()
    _win_for_x(game)

    game.reset(keep_scores=False)

    assert game.scoreboard() == {"X": 0, "O": 0, "draws": 0}
    assert game.status()["state"] == "playing"


def test_tc_02_04_valid_ai_difficulties():
    game = TicTacToe()

    for difficulty in ("easy", "medium", "hard"):
        game.set_difficulty(difficulty)
        assert game.difficulty == difficulty


def test_tc_02_05_invalid_difficulty_preserves_previous_value():
    game = TicTacToe(difficulty="easy")

    for invalid in ("expert", "", None):
        with pytest.raises(ValueError):
            game.set_difficulty(invalid)
        assert game.difficulty == "easy"


def test_tc_02_06_valid_mode_switches():
    game = TicTacToe()

    game.set_mode("human", "O")
    assert game.mode == "human"
    game.set_mode("ai", "O")
    assert game.mode == "ai"
    assert game.ai_player == "O"
    game.set_mode("ai", "X")
    assert game.ai_player == "X"


def test_tc_02_07_invalid_mode_and_ai_marker():
    game = TicTacToe()
    before = game.snapshot()

    with pytest.raises(ValueError):
        game.set_mode("arcade", "O")
    with pytest.raises(ValueError):
        game.set_mode("ai", "A")

    assert game.snapshot() == before


def test_tc_02_08_valid_coordinate_formats():
    game = TicTacToe()

    assert game.validate_input("1,1") == (0, 0)
    assert game.validate_input("2/3") == (1, 2)
    assert game.validate_input("1 2") == (0, 1)
    assert game.validate_input(" 3 , 1 ") == (2, 0)


def test_tc_02_09_coordinate_boundaries():
    game = TicTacToe()

    for value in ("0,1", "4,1", "1,0", "1,4"):
        assert game.validate_input(value) is None


def test_tc_02_10_invalid_coordinate_structures():
    game = TicTacToe()

    for value in ("a,1", "1.5,2", "1", "1,2,3", None):
        assert game.validate_input(value) is None


def test_tc_02_11_coordinate_command_parsing():
    game = TicTacToe()

    assert game.parse_command("2/3") == ("move", (1, 2))
    assert game.parse_command("1,2") == ("move", (0, 1))


def test_tc_02_12_command_alias_parsing():
    game = TicTacToe()

    assert game.parse_command("h") == ("help", None)
    assert game.parse_command("u") == ("undo", None)
    assert game.parse_command("q") == ("quit", None)
    assert game.parse_command("score") == ("stats", None)
    assert game.parse_command("reset") == ("new", None)
    assert game.parse_command("level hard") == ("difficulty", "hard")


def test_tc_02_13_parameterized_commands():
    game = TicTacToe()

    assert game.parse_command("save match.json") == ("save", "match.json")
    assert game.parse_command("load match.json") == ("load", "match.json")
    assert game.parse_command("difficulty hard") == ("difficulty", "hard")


def test_tc_02_14_invalid_commands_and_missing_arguments():
    game = TicTacToe()

    for command in ("", "unknown", "save", "load", "mode"):
        assert game.parse_command(command) == ("invalid", None)


def test_tc_02_15_low_level_move_succeeds():
    game = TicTacToe()

    assert game.make_move(0, 0) is True
    assert game.board[0][0] == "X"
    assert len(game.move_history) == 1


def test_tc_02_16_low_level_move_does_not_switch_turn():
    game = TicTacToe()

    game.make_move(0, 0)
    game.make_move(1, 1)

    assert game.current_player == "X"
    assert game.board[0][0] == "X"
    assert game.board[1][1] == "X"


def test_tc_02_17_low_level_move_rejects_occupied_and_invalid_positions():
    game = TicTacToe()
    game.make_move(0, 0)
    before = game.snapshot()

    for row, col in ((0, 0), (-1, 0), (3, 0), (0, 3)):
        assert game.make_move(row, col) is False
    assert game.snapshot() == before


def test_tc_02_18_complete_turn_switches_player():
    game = TicTacToe()

    result = game.play_move(0, 0)

    assert result["ok"] is True
    assert result["player"] == "X"
    assert result["status"]["state"] == "playing"
    assert game.current_player == "O"


def test_tc_02_19_complete_turn_rejects_invalid_input_without_mutation():
    game = TicTacToe()
    game.play_move(0, 0)
    before = game.snapshot()

    for row, col in ((0, 0), (3, 0), (True, 0)):
        result = game.play_move(row, col)
        assert result["ok"] is False
    assert game.snapshot() == before


def test_tc_02_20_terminal_game_rejects_follow_up_move():
    game = TicTacToe()
    _win_for_x(game)

    result = game.play_move(2, 2)

    assert result["ok"] is False
    assert result["reason"] == "game_over"


def test_tc_02_21_row_winner():
    game = TicTacToe()
    game.board = [["X", "X", "X"], ["O", " ", " "], ["O", " ", " "]]

    assert game.check_winner() == "X"


def test_tc_02_22_column_winner():
    game = TicTacToe()
    game.board = [["O", "X", " "], ["O", " ", " "], ["O", " ", " "]]

    assert game.check_winner() == "O"


def test_tc_02_23_diagonal_winner_and_line():
    game = TicTacToe()
    game.board = [["X", "O", " "], ["O", "X", " "], [" ", " ", "X"]]

    assert game.check_winner() == "X"
    assert game.status()["line"] == ((0, 0), (1, 1), (2, 2))


def test_tc_02_24_no_winner():
    game = TicTacToe()
    game.board = [["X", "O", " "], ["O", "X", " "], [" ", " ", " "]]

    assert game.check_winner() is None


def test_tc_02_25_full_board_draw():
    game = TicTacToe()
    game.board = [["X", "O", "X"], ["X", "X", "O"], ["O", "X", "O"]]

    assert game.check_draw() is True
    assert game.status()["state"] == "draw"


def test_tc_02_26_full_board_with_winner_is_not_draw():
    game = TicTacToe()
    game.board = [["X", "X", "X"], ["O", "O", "X"], ["O", "X", "O"]]

    assert game.check_draw() is False
    assert game.status()["state"] == "won"


def test_tc_02_27_undo_restores_normal_turn():
    game = TicTacToe()
    game.play_move(0, 0)
    game.play_move(1, 1)

    assert game.undo() is True
    assert game.board[1][1] == game.EMPTY
    assert game.current_player == "O"
    assert len(game.move_history) == 1


def test_tc_02_28_undo_unavailable():
    empty = TicTacToe()
    assert empty.undo() is False

    disabled = TicTacToe(allow_undo=False)
    disabled.play_move(0, 0)
    assert disabled.undo() is False
    assert disabled.board[0][0] == "X"


def test_tc_02_29_undo_terminal_move_rolls_back_score():
    game = TicTacToe()
    _win_for_x(game)
    assert game.scoreboard()["X"] == 1

    game.undo()

    assert game.scoreboard()["X"] == 0


def test_tc_02_30_score_accumulation_and_clear():
    game = TicTacToe()
    _win_for_x(game)
    game.reset(keep_scores=True)
    _win_for_o(game)
    game.reset(keep_scores=True)
    _draw(game)

    assert game.scoreboard() == {"X": 1, "O": 1, "draws": 1}
    game.reset(keep_scores=False)
    assert game.scoreboard() == {"X": 0, "O": 0, "draws": 0}


def test_tc_02_31_easy_returns_legal_move_without_mutating_board():
    game = TicTacToe(difficulty="easy", seed=7)
    game.board[0][0] = "X"
    game.board[1][1] = "O"
    before = copy.deepcopy(game.board)

    move = game.choose_ai_move("O")

    assert move in game.available_moves()
    assert game.board == before


def test_tc_02_32_easy_chooses_last_available_position():
    game = TicTacToe(difficulty="easy", seed=7)
    game.board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", " "]]

    assert game.choose_ai_move("O") == (2, 2)


def test_tc_02_33_medium_takes_own_immediate_win():
    game = TicTacToe(difficulty="medium")
    game.board = [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]]
    game.current_player = "O"

    assert game.choose_ai_move("O") == (0, 2)


def test_tc_02_34_medium_blocks_opponent_immediate_win():
    game = TicTacToe(difficulty="medium")
    game.board = [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]]
    game.current_player = "X"

    assert game.choose_ai_move("X") == (0, 2)


def test_tc_02_35_medium_prefers_center_without_tactical_threat():
    game = TicTacToe(difficulty="medium")
    game.board[0][0] = "X"
    game.current_player = "O"

    assert game.choose_ai_move("O") == (1, 1)


def test_tc_02_36_hard_takes_own_immediate_win():
    game = TicTacToe(difficulty="hard")
    game.board = [["X", "X", " "], ["O", " ", " "], [" ", "O", " "]]
    game.current_player = "X"

    assert game.choose_ai_move("X") == (0, 2)


def test_tc_02_37_hard_blocks_opponent_immediate_win():
    game = TicTacToe(difficulty="hard")
    game.board = [["O", "O", " "], ["X", " ", " "], [" ", "X", " "]]
    game.current_player = "X"

    assert game.choose_ai_move("X") == (0, 2)


def test_tc_02_38_hard_handles_corner_fork_with_edge_move():
    game = TicTacToe(difficulty="hard")
    game.board = [["X", " ", " "], [" ", "O", " "], [" ", " ", "X"]]
    game.current_player = "O"

    assert game.choose_ai_move("O") in {(0, 1), (1, 0), (1, 2), (2, 1)}


def test_tc_02_39_ai_stops_on_invalid_player_full_board_or_game_over():
    game = TicTacToe(difficulty="hard")
    before = copy.deepcopy(game.board)
    assert game.choose_ai_move("A") is None
    assert game.board == before

    game.board = [["X", "O", "X"], ["O", "X", "O"], ["O", "X", "O"]]
    assert game.choose_ai_move("X") is None

    game.reset()
    game.game_over = True
    assert game.choose_ai_move("X") is None


def test_tc_02_40_save_and_load_round_trip(tmp_path):
    path = tmp_path / "round-trip.json"
    source = TicTacToe(player_names={"X": "Alice", "O": "Bob"}, difficulty="hard", mode="ai")
    source.play_move(0, 0)
    source.play_move(1, 1)

    assert source.save_game(path) is True
    restored = TicTacToe()
    assert restored.load_game(path) is True

    assert restored.snapshot() == source.snapshot()


def test_tc_02_41_invalid_save_paths(tmp_path):
    game = TicTacToe()

    assert game.save_game(None) is False
    assert game.save_game("") is False
    assert game.save_game(tmp_path / "missing" / "game.json") is False


def test_tc_02_42_invalid_load_is_transactional(tmp_path):
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{not-json", encoding="utf-8")
    game = TicTacToe()
    game.play_move(0, 0)
    before = game.snapshot()

    assert game.load_game(malformed) is False
    assert game.load_game(tmp_path / "not-found.json") is False
    assert game.snapshot() == before


@pytest.mark.parametrize(
    "payload",
    [
        {"board": [["A", " ", " "], [" ", " ", " "], [" ", " ", " "]]},
        {"board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]], "current_player": "A"},
        {"board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]], "current_player": "X", "mode": "arcade"},
        {"board": [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]], "current_player": "X", "difficulty": "expert"},
    ],
    ids=["invalid-cell", "invalid-current-player", "invalid-mode", "invalid-difficulty"],
)
def test_tc_02_43_invalid_snapshot_fields_are_rejected(tmp_path, payload):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    game = TicTacToe()
    game.play_move(0, 0)
    before = game.snapshot()

    assert game.load_game(path) is False
    assert game.snapshot() == before


def test_tc_02_44_load_restores_match_scores(tmp_path):
    path = tmp_path / "scores.json"
    source = TicTacToe()
    _win_for_x(source)
    assert source.save_game(path) is True

    restored = TicTacToe()
    assert restored.load_game(path) is True
    assert restored.scoreboard()["X"] == 1


def test_tc_02_45_cli_completes_human_game():
    game = TicTacToe()
    inputs = iter(["1,1", "1,2", "2,1", "2,2", "3,1"])
    output = []

    result = game.run(input_fn=lambda: next(inputs), output_fn=output.append)

    assert result == "finished"
    assert game.winner == "X"
    assert any("玩家 X 获胜" in line for line in output)


def test_tc_02_46_cli_switches_difficulty_and_mode():
    game = TicTacToe()
    inputs = iter(["difficulty hard", "mode ai", "quit"])
    output = []

    assert game.run(input_fn=lambda: next(inputs), output_fn=output.append) == "quit"
    assert game.difficulty == "hard"
    assert game.mode == "ai"


def test_tc_02_47_cli_runs_an_automatic_ai_turn():
    game = TicTacToe(mode="ai", difficulty="hard")
    inputs = iter(["1,1", "quit"])
    output = []

    assert game.run(input_fn=lambda: next(inputs), output_fn=output.append) == "quit"
    assert len(game.move_history) == 2
    assert game.move_history[1]["player"] == "O"
    assert any("AI（hard）落子" in line for line in output)


def test_tc_02_48_dashboard_initial_display():
    dashboard = TerminalDashboard(TicTacToe(), colour=False)

    rendered = dashboard.render()

    assert "T I C  T A C  T O E" in rendered
    assert "MATCH STATUS" in rendered
    assert "COMMANDS" in rendered
    assert "1       2       3" in rendered
    assert "轮到玩家 X" in rendered


def test_tc_02_49_dashboard_board_and_status_are_synchronized():
    game = TicTacToe()
    game.board[0][0] = "X"
    game.board[1][1] = "O"
    rendered = TerminalDashboard(game, colour=False).render()

    board_lines = [line for line in rendered.splitlines() if "│" in line]
    assert any("1  │" in line and "X" in line for line in board_lines)
    assert any("2  │" in line and "O" in line for line in board_lines)
    assert "轮到玩家 X" in rendered


def test_tc_02_50_dashboard_triggers_ai_turn():
    game = TicTacToe(mode="ai", difficulty="hard")
    game.current_player = "O"
    dashboard = TerminalDashboard(game, colour=False)

    dashboard._ai_turn()

    assert len(game.move_history) == 1
    assert game.move_history[0]["player"] == "O"
    assert "AI" in dashboard.message
