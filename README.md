<!--suppress HtmlDeprecatedAttribute -->
<h1 align="center">PyRTLSweeper</h1>

<p align="center">
    <a href="/LICENSE">
        <img src="https://img.shields.io/badge/License-MIT-blue" alt="License: MIT">
    </a>
</p>

**Check out the
paper: [PyRTLSweeper: An attempt at automated transpilation of digital circuits to Minesweeper boards](https://edwinchang.dev/files/pyrtlsweeper.pdf)**

PyRTLSweeper is a Python package that takes a circuit written with [PyRTL](https://ucsbarchlab.github.io/PyRTL/) and
produces a Minesweeper board readable by [JSMinesweeper](https://davidnhill.github.io/JSMinesweeper/) that represents
the circuit. The player can designate input cells to be flagged or not flagged, and some output cells are determined to
have a mine or not.

PyRTLSweeper currently does not support registers and memories due to the complexity of state preservation, and does not
work on all circuits. An XOR circuit in particular seems to produce incorrect results. If you have a solution to either
of these issues, please reach out to me.

To get started with PyRTLSweeper, try editing and running [the example](./examples/circuit.py).

## License

[MIT](./LICENSE)
