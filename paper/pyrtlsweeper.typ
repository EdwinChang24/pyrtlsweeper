#import "@preview/charged-ieee:0.1.4": ieee
#import "@preview/cetz:0.4.2"
#import "minesweeper-lib/minesweeper.typ": minesweeper-board

#set page(numbering: "1", header: context {
  if counter(page).get().first() > 1 [
    #set text(size: 8pt)
    _PyRTLSweeper: Automated Transformation of Digital Circuits to Minesweeper Boards_
    #h(1fr)
    November 8, 2025
  ]
})
#show raw: it => {
  set text(font: "DejaVu Sans Mono", size: 8pt)
  it
}

#let board-image(source) = align(center, pad(y: 8pt, block(stroke: 3pt + rgb("757575"), image(source))))

#show: ieee.with(
  title: [
    PyRTLSweeper: Automated Transformation of Digital Circuits to Minesweeper Boards

    #text("November 8, 2025", size: 11pt)
  ],
  authors: (
    (
      name: "Edwin Chang",
      department: [College of Creative Studies],
      organization: [University of California, Santa Barbara],
      email: "edwinchang@ucsb.edu",
    ),
  ),
  abstract: [
    In this paper I describe how to construct a set of digital circuit components in Minesweeper, and how to automate their generation. Then, I discuss an approach for laying out the circuit components on a Minesweeper board to make a circuit described using the Python library #link("https://ucsbarchlab.github.io/PyRTL/")[PyRTL], and automate this as well.
  ],
  bibliography: bibliography("bib.yml"),
)

= Note for outside readers

This is an updated version of a paper I wrote in June as part of a class project in Exploring the Hardware/Software Interface (CMPTGCS 130E Spring 2025) at UC Santa Barbara, taught by Zach Sisco. #footnote[https://ccs.ucsb.edu/courses/2025/spring/exploring-hardwaresoftware-interface]

= Introduction

Anyone reading this paper has probably played Minesweeper before. The player is given a board on which mines are hidden, and must deduce which cells are safe based on the number of mines each safe cell is surrounded with. A useful tool for analyzing Minesweeper boards is David Hill's JSMinesweeper. #footnote[https://davidnhill.github.io/JSMinesweeper/]

PyRTL #footnote[https://ucsbarchlab.github.io/PyRTL/] is a hardware description language created by UC Santa Barbara's ArchLab. #footnote[https://www.arch.cs.ucsb.edu/] Using it, one can write digital circuits in Python with relatively simple syntax and do all sorts of analysis on them.

The goal of this project was to write a Python package that provides an algorithm to produce a Minesweeper board representing a circuit written with PyRTL. Since registers and memories seem to be a difficult task given that they require state preservation, I didn't implement them in this project. In this paper, I go through the necessary components needed to make PyRTLSweeper work, and how I wrote the final algorithm.

= Background

There is prior work on building digital logic circuits in Minesweeper. Kirby703 demonstrated in her 2025 SIGBOVIK paper how she built Minesweeper inside Minesweeper using a repeated logic gate.#super[@ms-in-ms] Richard Kaye wrote a couple papers that used logic circuits in Minesweeper to show that Minesweeper is NP-complete.#super[@np-complete @some-configs] Michiel de Bondt also did work using logic gates to analyze Minesweeper's complexity#super[@comp-complexity], and Seunghoon Lee found improved logical components in a hexagonal variant of Minesweeper.#super[@hexagonal] I drew most of my inspiration for this project from Kirby703's work.

= Board components

== Creating wires

Consider the following board.

#minesweeper-board(
  "00000000000000",
  "01110000001110",
  "02F31111113F20",
  "03FHH1HH1HHF30",
  "02F31111113F20",
  "01110000001110",
  "00000000000000",
)

Given that there are 3 unflagged mines on the board, there are two possible ways in which the mines can be placed: one mine on the left side of each pair of hidden cells or one mine on the right side of each. Note how placing one mine determines the positions of the remaining mines. It follows that we can extend this pattern to be as long as we want, and there will always be exactly two possible sets of mine positions.

#minesweeper-board(
  "00000000000000000000000000000000",
  "01110000000000000000000000001110",
  "02F31111111111111111111111113F20",
  "03FHH1HH1HH1HH1HH1HH1HH1HH1HHF30",
  "02F31111111111111111111111113F20",
  "01110000000000000000000000001110",
  "00000000000000000000000000000000",
)

Since placing one mine on one side determines the mine positions all the way down the chain to the other side, this structure works like a wire.

== Phases

An important thing about wires is that the repeated wire component is repeated every 3 cells. This means that when we put together wires and logic gates, they need to be in the correct phase to connect to each other. Dividing the board into $3 times 3$ squares simplifies constructing boards. For the purposes of my project, I divided the board and placed wires as follows:

#minesweeper-board(
  overlay: () => {
    import cetz.draw: *

    grid(
      (0, 0),
      (21, -14),
      step: 3,
      shift: 1,
      stroke: 3pt,
    )
  },
  "000000000000000000000",
  "000000000000000123210",
  "0000000000000001FFF10",
  "00000000000000013H310",
  "00000000000000001H100",
  "011100000011100011100",
  "02F31111113F20001H100",
  "03FHH1HH1HHF30001H100",
  "02F31111113F200011100",
  "01110000001110001H100",
  "00000000000000013H310",
  "0000000000000001FFF10",
  "000000000000000123210",
  "000000000000000000000",
)

With this setup, each $3 times 3$ square can contain a repeatable wire component. Notice how the horizontal wire components have two separated hidden cells within the $3 times 3$ so that touching hidden cells will touch over a border. I'll explain the reason for this later.

== Turns

With wires and phases defined, we can make turn components:

#minesweeper-board(
  "00000000000000000000000000000000000",
  "00000000001110000001110000000000000",
  "00000000002F31111113F20000000000000",
  "00000000013FHH1HH1HHF31000000000000",
  "0000000001F4F211112F4F1000000000000",
  "00000000012H21000012H21000000000000",
  "00000000001H10000001H10000000000000",
  "01110000001110000001110000000001110",
  "02F31111112H10000001H21111111113F20",
  "03FHH1HH1HHH21000012HHH1HH1HH1HHF30",
  "02F3111112F3F100001F3F2111111113F20",
  "01110000011211000011211000000001110",
  "00000000000000000000000000000000000",
)

If you ignore the numbers for now, each turn component is defined by hidden cells and flags contained within a $3 times 3$ square. In fact, these can be tightly packed, so turn components can be directly next to other wire/turn components without interference.

== Crossovers

Possibly the most surprising part of wiring is that it's possible to make wires cross over each other without inteference with a $3 times 3$ component.

#minesweeper-board(
  "00000000000000000000000000000000000000000000",
  "01110000000000000000001110000000000000000000",
  "02F31111111111111111113F20000000000000000000",
  "03FHH1HH1HH1HH1HH1HH1HHF31000000000000000000",
  "02F3111111111111111112F4F1000000000000000000",
  "01110000000000000000012H21000000000000000000",
  "00000000000000000000001H10000000000000000000",
  "00000000001110000000001110000000000000001110",
  "00000000002F31111111112H21111111111111113F20",
  "00000000013FHH1HH1HH1HHHHH1HH1HH1HH1HH1HHF30",
  "0000000001F4F2111111112221111111111111113F20",
  "00000000012H21000000001H10000000000000001110",
  "00000000001H10000000001H10000000000000000000",
  "00000000001110000000001110000000000000000000",
  "00000000001H21111111112H10000000000000000000",
  "00000000012HHH1HH1HH1HHH21000000000000000000",
  "0000000001F3F211111112F3F1000000000000000000",
  "00000000011211000000011211000000000000000000",
  "00000000000000000000000000000000000000000000",
)

This is why the horizontal wire component has two separated hidden cells: so crossovers work. I couldn't find a way to make them work with other horizontal wire phases while keeping the wires centered on the cross axis.

== Splitters

This design takes an input signal from the left and reproduces the signal downwards and to the right.

#minesweeper-board(
  "00000000000000000000",
  "00000012321000000000",
  "0111002FFF2100001110",
  "02F3113FH4F211113F20",
  "03FHH1HH33H3HH1HHF30",
  "02F3112F22F211113F20",
  "01110012H21100001110",
  "00000001H10000000000",
  "00000001110000000000",
  "00000001H10000000000",
  "00000001H10000000000",
  "00000001110000000000",
  "00000001H10000000000",
  "00000013H31000000000",
  "0000001FFF1000000000",
  "00000012321000000000",
  "00000000000000000000",
)

It looks like it takes more than a $3 times 3$ square of space, but as I'll explain in the next section, it only takes one to represent. It might not be very packable though.

== Auto generation

I still haven't talked about how to automate making any of this, which is clearly important to building actual circuitry. I wanted to make these boards viewable in David Hill's JSMinesweeper, so I had to indicate whether each cell in a board is hidden, has a flag, or is open, and its number if open.

My first attempt at scripting the generation of these wires was, for each component, to store the positions of hidden cells and flagged cells within the $3 times 3$ square. A turn, for example, would look like this:

#minesweeper-board(
  "000000000000",
  "000000000F00",
  "0HH0HH0HHF00",
  "00000000F0F0",
  "000000000H00",
  "000000000H00",
  "000000000000",
  "000000000H00",
)

Then, note that whenever open cells are next to hidden cells, it is only for the purpose of 'connecting' the hidden cells together (forcing one to have a mine if the other doesn't and vice versa). Therefore, we have the following formula for computing the number to mark an open cell with:

$
  "cell #" = "adjacent flags" + floor("adjacent hidden cells" / 2)
$

Using this formula, we can fill in the numbers for all the open cells.

Then I realized that most of the flags can be computed on the fly as well. My second (and final) attempt involved storing any of the following for each position in a $3 times 3$:

- A hidden cell
- A required flag
- A required open cell
- Nothing

Then the algorithm becomes as follows:

+ Place all hidden cells, required flags, and required open cells (open cells are differentiated from unknown cells).
+ For each unknown cell, if there is an even number of neighboring cells, make the cell open. Else, place a flag there.
+ Use the above formula to compute the number in each open cell.

The advantage of the second approach is that for the most part, each component only needs to correspond to a set of hidden positions. Required flags and required open cells are only used in some special cases. In the splitter design in the previous section, the splitter component doesn't need to specify where any flags are, only the hiddens. The flags don't even need to be in the $3 times 3$ square to get automatically computed. Since the hidden cells fit in the $3 times 3$, I consider it a $3 times 3$ component.

JSMinesweeper also wants to know how many mines are in a board, in order to analyze it. We calculate this from a final board using a similar formula to the one above:

$
  "total mines" = "total flags" + floor("total hidden cells" / 2)
$

== NOT Gate

We now consider building an inverter. A naive implementation looks like this:

#minesweeper-board(
  "00000000000000000",
  "00000112121100000",
  "111112F3F3F211111",
  "HH1HH3H5H5H3HH1HH",
  "111112F3F3F211111",
  "00000112121100000",
  "00000000000000000",
)

However, there's a problem here. When playing Minesweeper, the game tells you how many mines are left, so the number of mines needs to be constant. In this design, the center hidden cell is a mine in one board state and is safe in the other board state, but the hidden cells on its sides are both mines or both safe. This means that if the number of mines is known, the positions of the mines are determined, which is bad.

Here's the fixed inverter:

#minesweeper-board(
  "00000000000000000",
  "00000012321000000",
  "0000012FFF2100000",
  "111112F6H6F211111",
  "HH1HH3HFFFH3HH1HH",
  "111112F6H6F211111",
  "0000012FFF2100000",
  "00000012321000000",
  "00000000000000000",
)

In this case, the number of mines in each board state is the same, which satisfies our needs. Also note that this makes use of a required flag (the one in the center) because even though it neighbors two hidden cells, those hidden cells shouldn't be connected. The other flags are implicitly placed because they neighbor an odd number of hidden cells. This gate is represented as something like this when scripting:

#minesweeper-board(
  "00000000000000000",
  "00000000H00000000",
  "HH0HH0H0F0H0HH0HH",
  "00000000H00000000",
  "00000000000000000",
)

== AND Gate

The most complex component needed is an AND gate. In theory we could use OR/NAND/NOR gates instead to make logic, but PyRTL provides a nice algorithm to convert everything in a circuit to AND gates. I took the design from Kirby703's paper and modified it to fit my constraints:

#minesweeper-board(
  "00000000000000000000000000",
  "00000000000000001232100000",
  "01110001110001112FFF200000",
  "02F31113F21111F24FHF200000",
  "03FHH1HHF43F222HHF53200000",
  "02F3113F6FF4HH3444HF200000",
  "0111003FHFHF32FFF3FF200000",
  "0000003FF6FF313HH322100000",
  "0111003FHFHF433HH210001110",
  "02F3113F6FF5FFF22F21113F20",
  "03FHH1HHF44FH432H2HH1HHF30",
  "02F31113F22F5H3H3211113F20",
  "011100011112FF3FF100001110",
  "00000000000122222100000000",
  "00000000000000000000000000",
)

This takes up a $4 times 3$ of $3 times 3$ squares. I'm not going to get into how this exactly works, because I don't entirely understand it either. An important thing, though, is that the hidden cell at the far top right may look like an unnecessary dead end, but it's actually necessary to keep the number of mines constant, just like in the NOT gate.

The prior AND gate design has 3-cell spacing between the two inputs, which fits nicely if we want the entire circuit to have spacing between wires and gates. In a further revision, I removed the 3-cell spacing and compressed the design:

#minesweeper-board(
  "00000000000000000000",
  "01111111222233321000",
  "02F32F33FF3FFFFF1000",
  "03FHH4FF5H5H6FH31000",
  "03F6FH4HF5FF5HH32110",
  "03F6FH3HFHFFF3FF4F20",
  "03FHH4F4HHFH5H4HHF30",
  "02F32F3F223F3F213F20",
  "01111121101121101110",
  "00000000000000000000",
)

This is a compact, working AND gate design for a board with tightly packed wires and gates.

= Board Layout

== The problem

PyRTL provides nice APIs for analyzing circuits. Given a PyRTL circuit, PyRTL can produce the list of logic gates, list of wires, map of wires to logic gates powering them, and map of wires to logic gates they are input for. Additionally, PyRTL can reduce a circuit to 1-bit wires and logic gates, and further reduce it to only NOT and AND gates.

All we need to do is project the graph of logic gates and wires onto a Minesweeper board using the previously built components.

== Laying out the components

The easiest way, to my knowledge, to project a directed graph onto a board like this is to put all the nodes in a line. Here's what the design roughly looks like (not to scale):

#align(center, cetz.canvas(length: 12pt, padding: 6pt, {
  import cetz.draw: *

  content((0, 0), (4, -3), block(width: 100%, height: 100%, stroke: 1pt + black, radius: 10%, outset: (y: -10%), align(
    center + horizon,
  )[Inputs]))
  content((0, -3), (4, -7), block(width: 100%, height: 100%, stroke: 1pt + black, radius: 10%, outset: (y: -10%), align(
    center + horizon,
  )[Gates]))
  content((0, -7), (4, -10), block(
    width: 100%,
    height: 100%,
    stroke: 1pt + black,
    radius: 10%,
    outset: (y: -10%),
    align(
      center + horizon,
    )[Outputs],
  ))

  // input 1
  line((4, -1), (6, -1), (6, -12), (-2, -12), (-2, -8), (0, -8))
  // input 2
  line((4, -2), (8, -2), (8, -14), (-4, -14), (-4, -5), (0, -5))
  // gate output 1
  line((4, -5), (7, -5), (7, -13), (-3, -13), (-3, -6), (0, -6))
  // gate output 2
  line((4, -6), (9, -6), (9, -15), (-5, -15), (-5, -4), (0, -4))
  // split
  line((5, -6), (5, -11), (-1, -11), (-1, -9), (0, -9))

  mark((0, -4), 0deg, "straight")
  mark((0, -5), 0deg, "straight")
  mark((0, -6), 0deg, "straight")
  mark((0, -8), 0deg, "straight")
  mark((0, -9), 0deg, "straight")
}))

As shown, wires can split off in the top right if multiple gates take a particular wire as an argument.

On the actual Minesweeper board, I originally added $3$-cell spacing between the wires and gates, which are sized with $3 times 3$ units, to make things easier. In a later revision, I compressed the wire and gate designs to tightly pack them without spacing.

== Putting everything together

Using everything discussed before, I wrote a Python script to generate Minesweeper boards from PyRTL circuits. Here's what ```py c <<= a | b``` looks like:

#board-image("images/or-circuit-old.png")

This was with spacing between the wires and gates, which made the boards simpler to build. I later removed the spacing to optimize the board size. Here's what the same circuit looks like with no spacing:

#board-image("images/or-circuit-new.png")

A more complicated circuit, ```py c <<= ~(~a | ~b); d <<= a | b```:

#board-image("images/complex-circuit.png")

Board generation is not deterministic since it depends on ordering within Python sets, but the same graph is represented on each run.

= Results

PyRTLSweeper can generate Minesweeper boards from PyRTL circuits!

Also, the boards turn out to be quite monstrously large. But hey, the circuits work.

= Applications

If you find any, please let me know.

= Future direction

There are a couple ways in which this project may be continued:

- Adding registers/memories (if possible?)
- Making a custom editor/analyzer for circuits, since my web browser does not enjoy analyzing boards with 3000 mines

= Acknowledgements

I thank Zach Sisco for being an awesome teacher during spring quarter; I had a lot of fun working on this project and exploring other weird ways to compute things. I also thank Kirby703 for submitting her work on Minesweeper circuits to SIGBOVIK, as it was among my favorite papers in the conference this year and I learned a lot of this stuff from that paper. In addition, I thank David Hill for creating JSMinesweeper, which I used extensively in this project. Finally, I thank Jonathan Balkind for introducing me to PyRTL, and UCSB's ArchLab for creating PyRTL.

= Appendix: Running the code

The source code is available online at #link("https://github.com/EdwinChang24/pyrtlsweeper")[`https://github.com/EdwinChang24/pyrtlsweeper`]. To try it, clone the repo and run `examples/circuit.py` with a Python runtime (I recommend `uv` #footnote[https://docs.astral.sh/uv/]). It will produce a `.mine` file which you can drag and drop into JSMinesweeper. The main source code is in the `src` directory. If you have any questions, feel free to open an issue on GitHub or email me.
