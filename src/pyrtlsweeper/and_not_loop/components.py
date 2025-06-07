from abc import abstractmethod, ABC


class _CircuitComponent(ABC):
    """
    A circuit component (logic gate or wire section) that can be placed on a Minesweeper board. Generally has a height of 3 cells and a width that is a multiple of 3 cells.
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


class _LogicGate(_CircuitComponent, ABC):
    """
    A logic gate that can be placed on a Minesweeper board.
    There may be any number of inputs and exactly one output.
    All inputs come from the left and are spaced by 3 cells, and the output is at the bottom exiting towards the right.
    The height of the logic gate is determined by the number of inputs.
    """

    @abstractmethod
    def metadata(self) -> tuple[int, int]:
        """
        :return: The metadata for this logic gate in the format (number of inputs, width).
        The width is the number of 3-cell blocks taken by this logic gate.
        """
        pass


class _WireHorizontal(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c] = "H"
        board[r + 1][c + 2] = "H"


class _WireVertical(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c + 1] = "H"


class _CapLeft(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c + 2] = "H"


class _CapRight(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c] = "H"


class _TurnLeftDown(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c] = "H"


class _TurnLeftUp(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c] = "H"
        board[r + 1][c + 1] = "H"


class _TurnRightUp(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c + 1] = "H"
        board[r + 1][c + 2] = "H"


class _TurnRightDown(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r + 1][c + 2] = "H"


class _Crossover(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c] = "H"
        board[r + 1][c + 1] = "H"
        board[r + 1][c + 2] = "H"


class _Split(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 2] = "H"
        board[r + 1][c] = "H"


class _NotGate(_LogicGate):
    def metadata(self) -> tuple[int, int]:
        return 1, 1

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c + 1] = "H"
        board[r + 1][c + 1] = "F"
        board[r + 2][c + 1] = "H"


class _AndGate(_LogicGate):
    def metadata(self) -> tuple[int, int]:
        return 2, 4

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        hidden = [(1, 0), (7, 0), (3, 1), (5, 1), (3, 3), (5, 3), (2, 5), (2, 6), (7, 5), (8, 6), (1, 8), (1, 9),
                  (4, 8), (4, 9), (5, 8), (5, 9), (8, 8), (7, 9), (0, 11), (2, 11), (7, 11)]
        flagged = [(4, 0), (4, 1), (2, 2), (3, 2), (5, 2), (6, 2), (4, 3), (4, 4), (3, 7), (3, 8), (3, 9), (0, 10)]
        opened = [(6, 8), (6, 9)]
        for h in hidden:
            board[r + h[0]][c + h[1]] = "H"
        for f in flagged:
            board[r + f[0]][c + f[1]] = "F"
        for o in opened:
            board[r + o[0]][c + o[1]] = "O"


class _NopGate(_LogicGate):
    def metadata(self) -> tuple[int, int]:
        return 1, 0

    def place(self, board: list[list[str]], coords: tuple[int, int]):
        pass


class _Const1(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c] = "H"
        board[r + 2][c + 2] = "H"
        board[r + 1][c + 2] = "O"


class _Const0(_CircuitComponent):
    def place(self, board: list[list[str]], coords: tuple[int, int]):
        r, c = coords
        board[r][c] = "H"
        board[r + 1][c] = "O"
        board[r + 2][c + 2] = "H"
