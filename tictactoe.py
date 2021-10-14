from dataclasses import dataclass
from itertools import cycle
from typing import Optional, Union


@dataclass(frozen=True)
class CharSub:
    """A class describing characters to be substituted in a string."""

    indicies: list
    characters: str

    def __post_init__(self):
        if len(self.indicies) != len(self.characters):
            raise ValueError("Arguments with different lengths given.")


@dataclass
class Win:
    """An data class for containing information describing a win."""

    line_name: str
    player_name: Optional[str]
    turn: Optional[int] = None


def substitute_chars(base_string: str, sub: "CharSub") -> str:
    """Returns the supplied string, with characters replaced according to the supplied CharSub object."""
    base_list = list(base_string)
    for i, c in zip(sub.indicies, sub.characters):
        base_list[i] = c
    return "".join(base_list)


def invert_dict(base_dict: dict) -> dict:
    """Inverts the keys and values of a dict, if the values are all unique."""
    keys, vals = base_dict.items()
    if len(set(vals)) != len(keys):
        raise ValueError("Supplied dict does not have unique values.")
    return {v: k for k, v in base_dict.items()}


def rm_format(base_string: str, line_length: int) -> str:
    """Retruns a string with newlines inserted at the end of each line."""
    str_list = list(base_string)
    out_str = ""
    for i, c in enumerate(str_list):
        out_str += c
        if (i + 1) % line_length == 0:
            out_str += "\n"
    return out_str


def rm_coord_from_index(index: int, line_length: int):
    """Returns a (Row, Column) coordinate for a 2D array in row major format."""
    row = index // line_length
    col = index % line_length
    return (row, col)


class TicTacToeGame:

    NULL_CHAR = "-"
    PLAYER_MARKS = "XO"
    STANDARD_MESSAGES = {
        "greeting": "\n\n -----===== Tic Tac Toe =====----- \n\n",
        "draw": "The game ends in a draw.",
        "bad turn": "Please enter a valid turn: ",
    }

    def __init__(self) -> None:
        self.game_state = self.NULL_CHAR * 9
        self.rule_set = Rules
        self.style = BoardStyleLarge
        self.turns = 0
        self.win = None
        self._greet()
        self.player_sequence = cycle(self._setup_players())

    def _setup_players(self) -> tuple:
        players = []
        for mark in self.PLAYER_MARKS:
            players.append(self._get_player_type(mark))
        return tuple(players)

    @staticmethod
    def _get_player_type(player_mark) -> "Player":
        player_types = {
            "human": ConsoleInput,
            "ai": AIInput,
        }

        input_type = input(f"Is player {player_mark} human or AI?: ")
        while input_type.casefold() not in player_types:
            input_type = input(
                f"Please enter 'human' or 'AI' for player {player_mark}: "
            )
        return Player(player_mark, player_types[input_type.casefold()])

    def _greet(self):
        print(self.STANDARD_MESSAGES["greeting"])
        # print(self.style.get_board_string(self.game_state, self.win))

    @classmethod
    def _position_is_playable(cls, board_state: str, turn: str) -> bool:
        """Returns True if the supplied position can be played from the supplied board state, and False otherwise."""
        try:
            index = int(turn) - 1
            assert 0 <= index <= 8
            char = board_state[index]
        except (ValueError, AssertionError):
            return False
        if char == cls.NULL_CHAR:
            return True
        return False

    def _get_valid_turn(self, player: "Player") -> "CharSub":
        turn_str = player.get_turn(
            f"Player {player.mark}, where would you like to play?: "
        )
        while not self._position_is_playable(self.game_state, turn_str):
            turn_str = player.get_turn(self.STANDARD_MESSAGES["bad turn"])
        return CharSub([int(turn_str) - 1], player.mark)

    def _get_next_player(self) -> "Player":
        return next(self.player_sequence)

    def _end_game(self, win: Optional["Win"]) -> None:
        if win:
            print(
                f"Player {win.player_name} wins on turn {self.turns} along {win.line_name.casefold()}!"
            )
        else:
            print(self.STANDARD_MESSAGES["draw"])

    def turn(self) -> None:
        """Carrys out the steps of a turn. If a win condition is found, ends the game."""
        self.turns += 1
        next_player = self._get_next_player()
        turn = self._get_valid_turn(next_player)
        self.game_state = substitute_chars(self.game_state, turn)
        self.win = self.rule_set.evaluate_board(self.game_state)
        print(self.style.get_board_string(self.game_state, self.win))
        if self.win or self.NULL_CHAR not in self.game_state:
            self._end_game(self.win)

    def play(self) -> None:
        print("\n\n")
        print(self.style.get_board_string(self.game_state, self.win))
        while self.NULL_CHAR in self.game_state and self.win is None:
            self.turn()


class Player:
    def __init__(
        self, mark: str, input_source: Union["ConsoleInput", "AIInput"]
    ) -> None:
        self.mark = mark
        self.input_source = input_source

    def get_turn(self, prompt: str) -> str:
        return self.input_source.get_turn_input(prompt)


class ConsoleInput:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_turn_input(prompt=None) -> str:
        prompt = prompt or "Input?: "
        return input(prompt)


class AIInput:
    def __init__(self) -> None:
        pass

    def get_turn_input(self, _):
        pass


class Rules:
    """A class for evaluating the condition of a tic tac toe board."""

    LINES = {
        (0, 1, 2): "Row 1",
        (3, 4, 5): "Row 2",
        (6, 7, 8): "Row 3",
        (0, 3, 6): "Column 1",
        (1, 4, 7): "Column 2",
        (2, 5, 8): "Column 3",
        (0, 4, 8): "Diagonal 1",
        (2, 4, 6): "Diagonal 2",
    }

    def __init__(self) -> None:
        pass

    @classmethod
    def evaluate_board(cls, game_state: str) -> Optional["Win"]:
        """Returns a Win object if a win is found in the supplied game state."""
        line_states = cls._decompose_board(game_state)
        return cls._discover_wins(line_states)

    @staticmethod
    def _extract_line(game_state: str, line_indecies: tuple) -> str:
        """Returns the contents of a specified line from a supplied game state."""
        line_state = ""
        for i in line_indecies:
            line_state += game_state[i]
        return line_state

    @classmethod
    def _decompose_board(cls, game_state: str) -> dict:
        """Converts a supplied game state string to a dict of linestates and their matching names."""
        line_states = {}
        for indecies, name in cls.LINES.items():
            line_state = cls._extract_line(game_state, indecies)
            line_states[line_state] = name
        return line_states

    @classmethod
    def _discover_wins(cls, line_states: dict) -> Optional["Win"]:
        """Checks all of the supplied lines, and returns a Win object describing the win state if a win is found. Returns None otherwise."""
        for line, name in line_states.items():
            if TicTacToeGame.NULL_CHAR not in line and len(set(line)) == 1:
                return Win(name, line[0])
        return None


class BoardStyleLarge:

    _EMPTY_BOARD = (
        "   ┃   ┃   "
        " 1 ┃ 2 ┃ 3 "
        "   ┃   ┃   "
        "━━━╋━━━╋━━━"
        "   ┃   ┃   "
        " 4 ┃ 5 ┃ 6 "
        "   ┃   ┃   "
        "━━━╋━━━╋━━━"
        "   ┃   ┃   "
        " 7 ┃ 8 ┃ 9 "
        "   ┃   ┃   "
    )

    CELL_INDEX_MAP = (
        "111┃222┃333"
        "111┃222┃333"
        "111┃222┃333"
        "━━━╋━━━╋━━━"
        "444┃555┃666"
        "444┃555┃666"
        "444┃555┃666"
        "━━━╋━━━╋━━━"
        "777┃888┃999"
        "777┃888┃999"
        "777┃888┃999"
    )

    CELL_INDICIES = "123456789"
    INDEX_MAP: dict = {x: [] for x in CELL_INDICIES}
    for i, c in enumerate(CELL_INDEX_MAP):
        if c in CELL_INDICIES:
            INDEX_MAP[c].append(i)

    # These lambdas describe the comparison that must be made between the row and column position of
    # an index in the large board to determine whether it needs to be overwritten to display a win line
    _WIN_LINE_LAMBDAS = {
        "Row 1": lambda r, c: r == 1,
        "Row 2": lambda r, c: r == 5,
        "Row 3": lambda r, c: r == 9,
        "Column 1": lambda r, c: c == 1,
        "Column 2": lambda r, c: c == 5,
        "Column 3": lambda r, c: c == 9,
        "Diagonal 1": lambda r, c: r == c,
        "Diagonal 2": lambda r, c: r + c == 10,
    }

    # RULES (these may be off by 1)
    # Column: col is 2, 6 or 10
    # Row: row is 2, 6, or 10
    # diag 1: row == column
    # diag 2: col + row == LINE_LENGTH - 1

    _WIN_CHARS = {
        "Row": "─",
        "Column": "│",
        "Diagonal 1": "╲",
        "Diagonal 2": "╱",
    }

    BIG_MARK = {
        "X": ("╲ ╱ ╳ ╱ ╲"),
        "O": ("╭─╮│ │╰─╯"),
    }

    def __init__(self) -> None:
        pass

    @staticmethod
    def rm_format(output_string: str) -> str:
        """Reuturns the supplied string with newlines inserted at the end of each line."""
        # This board style draws a board that is 11 characters long.
        line_length = 11
        str_list = list(output_string)
        out_str = ""
        for i, c in enumerate(str_list):
            out_str += c
            if (i + 1) % line_length == 0:
                out_str += "\n"
        return out_str

    @classmethod
    def _build_board_string(cls, board_state: str) -> str:
        board_string = cls._EMPTY_BOARD
        for i, c in enumerate(board_state):
            if c is not TicTacToeGame.NULL_CHAR:
                c_sub = CharSub(cls.INDEX_MAP[str(i + 1)], cls.BIG_MARK[c])
                board_string = substitute_chars(board_string, c_sub)
        return board_string

    @classmethod
    def get_board_string(cls, board_state: str, win: Optional["Win"]):
        """Returns a display ready string representeing the supplied board state."""
        board_string = cls._build_board_string(board_state)
        if win is not None:
            board_string = cls._build_win_line_string(board_string, win)
        return cls.rm_format(board_string)

    @classmethod
    def _get_win_character(cls, line_name: str) -> str:
        for line_type, char in cls._WIN_CHARS.items():
            if line_type in line_name:
                return char
        raise ValueError(f"Unhandled line name: {line_name}")

    @classmethod
    def _build_win_line_string(cls, board_string: str, win: "Win") -> str:
        evaluator = cls._WIN_LINE_LAMBDAS[win.line_name]
        win_char = cls._get_win_character(win.line_name)
        indicies = []
        sub_chars = ""
        for i, _ in enumerate(board_string):
            row, col = rm_coord_from_index(i, 11)
            if evaluator(row, col):
                indicies.append(i)
                sub_chars += win_char
        c_sub = CharSub(indicies, sub_chars)
        return substitute_chars(board_string, c_sub)


new_game = TicTacToeGame()
new_game.play()
