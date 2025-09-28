from abc import abstractmethod, ABC


class _CircuitComponent(ABC):
    """
    A circuit component (logic gate or wire section) that can be placed on a Minesweeper board. Generally has a size that is a multiple of 3x3.
    """

    @abstractmethod
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        """
        Places this circuit component on the board.
        The following strings may be placed:

        - 'H': This cell should be hidden.
        - 'F': This cell should always be flagged.
        - 'O': This cell should always be open, and the number should be computed later.

        Cells that aren't modified by this method will be autofilled with a number or flag after all components have been placed.

        :param board: The entire board, where the outer list is of rows and the inner list is of columns.
        :param coords: The absolute coordinates (row index, col index) of the top left corner of the region this component should be placed in.
        """
        pass


class _WireHorizontal(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c] = "H"
        board[r + 1][c + 2] = "H"


class _WireVertical(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c + 1] = "H"


class _CapLeft(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c + 2] = "H"


class _CapRight(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c] = "H"


class _TurnLeftDown(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c] = "H"


class _TurnLeftUp(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c] = "H"
        board[r + 1][c + 1] = "H"


class _TurnRightUp(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c + 1] = "H"
        board[r + 1][c + 2] = "H"


class _TurnRightDown(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c + 2] = "H"


class _Crossover(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c] = "H"
        board[r + 1][c + 1] = "H"
        board[r + 1][c + 2] = "H"


class _Split(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c] = "H"


class _NotGate(_CircuitComponent):
    """
    Size in 3x3: height 1, width 4
    The inverter is placed at either the front or the back (putting it in the middle causes collisions with adjacent and gates).

    :param offset: If true, the inverter is placed at the end of the 1x4 instead of the front. This is to prevent collisions between not gates placed next to each other.
    """
    offset: bool

    def __init__(self, offset: bool):
        self.offset = offset

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        wh = _WireHorizontal()
        if self.offset:
            # wires
            wh.place(board, coords)
            wh.place(board, (r, c + 3))
            wh.place(board, (r, c + 6))
            # inverter
            board[r][c + 10] = "H"
            board[r + 2][c + 10] = "H"
            board[r + 1][c + 10] = "F"

        else:
            # inverter
            board[r][c + 1] = "H"
            board[r + 2][c + 1] = "H"
            board[r + 1][c + 1] = "F"
            # wires
            wh.place(board, (r, c + 3))
            wh.place(board, (r, c + 6))
            wh.place(board, (r, c + 9))


class _AndGate(_CircuitComponent):
    """
    Size in 3x3: height 2, width 4
    Has some extra flags in place to avoid collision with adjacent not gates.
    """

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        rows = [
            " F       FFF",
            "H F  H H  H ",
            "FH HF    HH ",
            "FH H H   OF ",
            "H F HH H H H",
            " F       F  "
        ]
        for row_i, row in enumerate(rows):
            for col_i, col in enumerate(row):
                if rows[row_i][col_i] == " ":
                    continue
                else:
                    board[r + row_i][c + col_i] = rows[row_i][col_i]


class _NopGate(_CircuitComponent):
    """Size in 3x3: height 1, width 4"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        wh = _WireHorizontal()
        for i in range(4):
            wh.place(board, (r, c + i * 3))


class _Const1(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 2][c + 1] = "O"


class _Const0(_CircuitComponent):
    """Size: 3x3"""

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "O"
        board[r + 1][c + 1] = "H"
        board[r + 2][c + 2] = "H"
