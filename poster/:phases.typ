#import "minesweeper-lib/minesweeper.typ": minesweeper-board
#import "@preview/cetz:0.4.2"

#set page(width: auto, height: auto, margin: 0in)

#minesweeper-board(
  overlay: () => {
    import cetz.draw: *

    grid(
      (0, 0),
      (21, -15),
      step: 3,
      shift: (1, 2),
      stroke: 0.2pt,
    )
  },
  "000000000000000000000",
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
