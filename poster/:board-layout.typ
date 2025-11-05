#import "@preview/cetz:0.4.2"

#set page(width: auto, height: auto, margin: 0in)

#align(center, cetz.canvas(length: 12pt, padding: 6pt, {
  import cetz.draw: *

  content((0, 0), (4, -3), block(width: 100%, height: 100%, stroke: 1pt + black, radius: 10%, outset: (y: -10%), align(
    center + horizon,
  )[]))
  content((0, -3), (4, -7), block(width: 100%, height: 100%, stroke: 1pt + black, radius: 10%, outset: (y: -10%), align(
    center + horizon,
  )[]))
  content((0, -7), (4, -10), block(
    width: 100%,
    height: 100%,
    stroke: 1pt + black,
    radius: 10%,
    outset: (y: -10%),
    align(
      center + horizon,
    )[],
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
