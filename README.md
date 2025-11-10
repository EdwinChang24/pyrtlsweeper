<!--suppress HtmlDeprecatedAttribute -->
<h1 align="center">PyRTLSweeper</h1>

<p align="center">
    <a href="/LICENSE">
        <img src="https://img.shields.io/badge/License-MIT-blue" alt="License: MIT">
    </a>
</p>

**Listen to the talk: [PyRTLSweeper: Automated Transformation of Digital Circuits to Minesweeper Boards](https://youtu.be/34RXtKhsOSs)**

**Also check out [the paper](https://edwinchang.dev/pyrtlsweeper/paper.pdf) and [the poster](https://edwinchang.dev/pyrtlsweeper/poster.pdf).**

PyRTLSweeper is a Python package that takes a circuit written with [PyRTL](https://ucsbarchlab.github.io/PyRTL/) and
produces a Minesweeper board readable by [JSMinesweeper](https://davidnhill.github.io/JSMinesweeper/) that represents
the circuit. The player can designate input cells to be flagged or not flagged, and some output cells are determined to
have a mine or not.

PyRTLSweeper currently does not support registers and memories due to the complexity of state preservation.

To get started with PyRTLSweeper, try editing and running [the example](./examples/circuit.py) with [uv](https://docs.astral.sh/uv/).

## License

[MIT](./LICENSE)
