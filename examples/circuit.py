import pyrtl

import pyrtlsweeper

a = pyrtl.Input(bitwidth=1, name="a")
b = pyrtl.Input(bitwidth=1, name="b")
c = pyrtl.Output(bitwidth=1, name="c")
d = pyrtl.Output(bitwidth=1, name="d")

c <<= ~(~a | ~b)
d <<= a | b

if __name__ == "__main__":
    pyrtlsweeper.set_logging(True)
    with open("circuit.mine", "w") as f:
        pyrtlsweeper.and_not_loop(f)
