#import "@preview/cetz:0.4.2"

#let minesweeper-board(padding-x: 16pt, padding-y: 16pt, overlay: () => {}, ..board) = {
  let border-color = rgb("#757575")
  let board-width = calc.max(..board.pos()).len()
  let board-height = board.pos().len()
  place(center + horizon, pad(x: padding-x, y: padding-y, layout(size => {
    cetz.canvas(
      length: calc.min(size.width / board-width, size.height / board-height),
      background: border-color,
      stroke: 3pt + border-color,
      {
        import cetz.draw: *

        for row-i in range(board.pos().len()) {
          for cell-i in range(board.pos().at(row-i).len()) {
            let cell = board.pos().at(row-i).at(cell-i)
            content((cell-i, -row-i), (cell-i + 1, -row-i - 1), image(
              "assets/" + cell + ".png",
            ))
          }
        }

        overlay()
      },
    )
  })))
}
