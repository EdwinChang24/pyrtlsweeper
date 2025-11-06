// adapted from https://github.com/typst/templates/tree/main/charged-ieee

#let template(
  title: [],
  authors: (),
  abstract: none,
  bibliography: none,
  body,
) = {
  set document(title: title, author: authors.map(author => author.name))

  set text(font: "Libertinus Serif", size: 10pt, spacing: .35em)

  set enum(numbering: "1)a)i)")

  show figure: set block(spacing: 15.5pt)
  show figure: set place(clearance: 15.5pt)

  show raw: set text(
    font: "JetBrains Mono NL",
    ligatures: false,
    size: 8pt,
    spacing: 100%,
  )

  set columns(gutter: 12pt)
  set page(
    columns: 2,
    margin: (
      x: (50pt / 216mm) * 100%,
      top: (55pt / 279mm) * 100%,
      bottom: (64pt / 279mm) * 100%,
    ),
  )

  set math.equation(numbering: "(1)")
  show math.equation: set block(spacing: 0.65em)

  // Configure appearance of equation references
  show ref: it => {
    if it.element != none and it.element.func() == math.equation {
      // Override equation references.
      link(it.element.location(), numbering(
        it.element.numbering,
        ..counter(math.equation).at(it.element.location()),
      ))
    } else {
      // Other references as usual.
      it
    }
  }

  set enum(indent: 10pt, body-indent: 9pt)
  set list(indent: 10pt, body-indent: 9pt)

  set heading(numbering: "I.A.a)")
  show heading: it => {
    let levels = counter(heading).get()
    let deepest = if levels != () {
      levels.last()
    } else {
      1
    }

    set text(10pt, weight: 400)
    if it.level == 1 {
      let unnumbered = it.body in ([Acknowledgements], [Appendix: Running the code])
      set align(center)
      set text(11pt)
      show: block.with(above: 15pt, below: 13.75pt, sticky: true)
      show: smallcaps
      if it.numbering != none and not unnumbered {
        numbering("I.", deepest)
        h(7pt, weak: true)
      }
      it.body
    } else if it.level == 2 {
      set text(style: "italic")
      show: block.with(spacing: 10pt, sticky: true)
      if it.numbering != none {
        numbering("A.", deepest)
        h(7pt, weak: true)
      }
      it.body
    }
  }

  show std.bibliography: set text(8pt)
  show std.bibliography: set block(spacing: 0.5em)
  set std.bibliography(title: text(11pt)[References], style: "ieee")

  place(
    top,
    float: true,
    scope: "parent",
    clearance: 30pt,
    {
      {
        set align(center)
        set par(leading: 0.5em)
        set text(size: 24pt)
        block(below: 8.35mm, title)
      }

      set par(leading: 0.6em)
      for i in range(calc.ceil(authors.len() / 3)) {
        let end = calc.min((i + 1) * 3, authors.len())
        let is-last = authors.len() == end
        let slice = authors.slice(i * 3, end)
        grid(
          columns: slice.len() * (1fr,),
          gutter: 12pt,
          ..slice.map(author => align(center, {
            text(size: 11pt, author.name)
            if "department" in author [
              \ #emph(author.department)
            ]
            if "organization" in author [
              \ #emph(author.organization)
            ]
            if "location" in author [
              \ #author.location
            ]
            if "email" in author {
              if type(author.email) == str [
                \ #link("mailto:" + author.email)
              ] else [
                \ #author.email
              ]
            }
          }))
        )

        if not is-last {
          v(16pt, weak: true)
        }
      }
    },
  )

  set par(justify: true, first-line-indent: (amount: 1em, all: true), spacing: 0.5em, leading: 0.5em)

  if abstract != none {
    set par(spacing: 0.45em, leading: 0.45em)
    set text(9pt, weight: 700, spacing: 150%)

    [_Abstract_---#h(weak: true, 0pt)#abstract]

    v(2pt)
  }

  body

  bibliography
}
