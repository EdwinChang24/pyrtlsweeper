import typing
from io import TextIOWrapper

import pyrtl

from and_not_loop.components import _Crossover, _Split, _WireHorizontal, \
    _WireVertical, _TurnLeftDown, _TurnLeftUp, _TurnRightUp, _TurnRightDown, _Const0, _Const1, _CapLeft, _CapRight, \
    _CircuitComponent, _AndGate, _NotGate, _NopGate
from pyrtlsweeper.logging_ import _log, _error

GATES_WIDTH = 4
"""Width in 3x of the gates block"""


def and_not_loop(file: TextIOWrapper, block: pyrtl.Block = pyrtl.working_block()):
    """
    Runs the `and_not_loop` algorithm to generate a Minesweeper board from the given PyRTL block.
    :param file: The file to write the Minesweeper board to. Should end with `.mine`.
    :param block: The PyRTL block to generate from.
    """
    _log("constructing minesweeper board from block using algorithm: and_not_loop")
    new_block = pyrtl.copy_block(block)
    pyrtl.passes.optimize(update_working_block=False, block=new_block)
    post_synth = pyrtl.passes.synthesize(update_working_block=False, merge_io_vectors=False, block=new_block)
    with pyrtl.set_working_block(post_synth):
        pyrtl.passes.and_inverter_synth()
    pyrtl.passes.optimize(update_working_block=False, block=post_synth)
    # wire_src_dict: [wire] = logic net powering wire
    # wire_sink_dict: [wire] = logic nets taking wire as arg
    wire_src_dict, wire_sink_dict = post_synth.net_connections()
    input_wires: list[pyrtl.Input] = []
    output_wires: list[pyrtl.Output] = []
    for original_io in post_synth.io_map.keys():
        if isinstance(original_io, pyrtl.Input):
            input_wires.extend(typing.cast(list[pyrtl.Input], post_synth.io_map[original_io]))
        if isinstance(original_io, pyrtl.Output):
            output_wires.extend(typing.cast(list[pyrtl.Output], post_synth.io_map[original_io]))
    if not output_wires:
        _error("no output wires found. this is not supported")
    _log(f"{output_wires = }")

    # create the list of logic nets in the correct order
    all_nets = list(post_synth.logic)

    # partition nets into logic vs. outputs
    logic_nets: list[pyrtl.LogicNet] = []
    output_nets: list[pyrtl.LogicNet] = []
    for net in all_nets:
        if any(isinstance(dest, pyrtl.Output) for dest in net.dests):
            if net.op != "w":
                _error(
                    f"logic net {net} has an output as a destination but has an op other than w. this is not supported")
            output_nets.append(net)
        else:
            logic_nets.append(net)
    # sort output_nets to match output_wires
    output_nets.sort(key=lambda n: list(map(lambda w: w.name, output_wires)).index(n.dests[0].name))
    _log(f"{logic_nets = }")

    net_src_dict: dict[pyrtl.LogicNet, list[pyrtl.LogicNet | pyrtl.Input | pyrtl.Const]] = {}
    """Map of logic/output net -> ordered list of nets, inputs, or consts whose outputs are inputs to this net"""

    for net in all_nets:
        srcs: list[pyrtl.LogicNet | pyrtl.Input | pyrtl.Const] = []
        for arg in net.args:
            if isinstance(arg, pyrtl.Input) or isinstance(arg, pyrtl.Const):
                srcs.append(arg)
            else:
                srcs.append(wire_src_dict[arg])
        net_src_dict[net] = srcs
    _log(f"{net_src_dict = }")

    heights: dict[pyrtl.LogicNet | pyrtl.Input, int] = {}
    """Maps an input, logic net, or output to its vertical coordinate position in 3x"""

    curr_height = 0
    for wire in input_wires:
        heights[wire] = curr_height
        curr_height += 1
    for net in logic_nets:
        heights[net] = curr_height
        curr_height += 2 if net.op == "&" else 1
    for net in output_nets:
        heights[net] = curr_height
        curr_height += 1
    total_io_logic_height = curr_height
    """The height in 3x of the inputs, logic nets, and outputs combined"""

    wiring_grid = [[" " for _ in range((total_io_logic_height - len(input_wires)) * 2 + GATES_WIDTH)] for _ in
                   range(total_io_logic_height * 2 - len(input_wires))]
    """
    Grid in 3x for laying out the components. Valid components:
    - space: empty
    - -,|,r,L,J,\,+,T,(,): wiring
    - 1,0: consts
    - &,~,!,w: gates (! means Not gate with offset)
    """

    wire_count = total_io_logic_height - len(input_wires)
    """The total number of wires looping around"""

    _log("drawing inputs")
    for input_index in range(len(input_wires)):
        wiring_grid[input_index][wire_count + GATES_WIDTH - 1] = "("

    _log("drawing gates")
    for logic_net_index, logic_net in enumerate(logic_nets):
        if logic_net.op in ["&", "w"]:
            wiring_grid[heights[logic_net]][wire_count] = logic_net.op
        elif logic_net.op == "~":
            wiring_grid[heights[logic_net]][wire_count] = "~" if logic_net_index % 2 == 0 else "!"
        else:
            _error(f"unsupported logic op {logic_net.op}")

    _log("drawing outputs")
    for output_net in output_nets:
        wiring_grid[heights[output_net]][wire_count] = ")"

    _log("drawing looping wires")
    for wire_index in range(wire_count):
        # horizontal segment going into left side of gate
        for i in range(wire_index):
            wiring_grid[total_io_logic_height - wire_index - 1][wire_count - i - 1] = "-"
        # corner
        wiring_grid[total_io_logic_height - wire_index - 1][wire_count - wire_index - 1] = "r"
        # vertical segment connecting left wire to bottom wire
        for i in range(wire_index * 2):
            wiring_grid[total_io_logic_height - wire_index + i][wire_count - wire_index - 1] = "|"
        # corner
        wiring_grid[total_io_logic_height + wire_index][wire_count - wire_index - 1] = "L"
        # horizontal segment running along the bottom
        for i in range(wire_index * 2 + GATES_WIDTH):
            wiring_grid[total_io_logic_height + wire_index][wire_count - wire_index + i] = "-"
        # corner
        wiring_grid[total_io_logic_height + wire_index][wire_count + GATES_WIDTH + wire_index] = "J"
        # vertical segment on bottom right of gate area, connecting bottom wire upwards until extension of bottom side of gate area
        for i in range(wire_index):
            wiring_grid[total_io_logic_height + i][wire_count + GATES_WIDTH + wire_index] = "|"

    _log("drawing src-sink connections and consts")
    for sink, srcs in net_src_dict.items():
        column_of_first_src = wire_count * 2 + GATES_WIDTH + len(input_wires) - heights[sink] - 1
        for src_index, src in enumerate(srcs):
            if isinstance(src, pyrtl.Const):
                wiring_grid[total_io_logic_height - 1][column_of_first_src - src_index] = "1" if src.val == 1 else "0"
            else:
                src_row = heights[src] + (1 if isinstance(src, pyrtl.LogicNet) and src.op == "&" else 0)
                sink_col = column_of_first_src - src_index
                # horizontal segment coming from right side of gates
                for col in range(wire_count + GATES_WIDTH, sink_col):
                    match wiring_grid[src_row][col]:
                        case " ":
                            wiring_grid[src_row][col] = "-"
                        case "|":
                            wiring_grid[src_row][col] = "+"
                        case "\\":
                            wiring_grid[src_row][col] = "T"
                # corner
                match wiring_grid[src_row][sink_col]:
                    case " ":
                        wiring_grid[src_row][sink_col] = "\\"
                    case "-":
                        wiring_grid[src_row][sink_col] = "T"
                # vertical segment connecting input/gate output to vertical wire below gates
                for row in range(src_row + 1, total_io_logic_height):
                    match wiring_grid[row][sink_col]:
                        case " ":
                            wiring_grid[row][sink_col] = "|"
                        case "-":
                            wiring_grid[row][sink_col] = "+"

    # add padding around wiring_grid
    wiring_grid = ([" " for _ in range(len(wiring_grid[0]) + 2)]
                   + [[" "] + grid_row + [" "] for grid_row in wiring_grid]
                   + [" " for _ in range(len(wiring_grid[0]) + 2)])

    _log("converting to actual grid")

    actual_grid = [[" " for _ in range(len(wiring_grid[0]) * 3)] for _ in range(len(wiring_grid) * 3)]
    for row_index, row in enumerate(wiring_grid):
        for col_index, cell in enumerate(row):
            if cell != " ":
                component: _CircuitComponent | None = None
                match cell:
                    case "-":
                        component = _WireHorizontal()
                    case "|":
                        component = _WireVertical()
                    case "r":
                        component = _TurnRightDown()
                    case "L":
                        component = _TurnRightUp()
                    case "J":
                        component = _TurnLeftUp()
                    case "\\":
                        component = _TurnLeftDown()
                    case "+":
                        component = _Crossover()
                    case "T":
                        component = _Split()
                    case "(":
                        component = _CapLeft()
                    case ")":
                        component = _CapRight()
                    case "1":
                        component = _Const1()
                    case "0":
                        component = _Const0()
                    case "&":
                        component = _AndGate()
                    case "~":
                        component = _NotGate(offset=False)
                    case "!":
                        component = _NotGate(offset=True)
                    case "w":
                        component = _NopGate()
                if component is not None:
                    component.place(actual_grid, (row_index * 3, col_index * 3))
                else:
                    _error(f"unrecognized circuit component {cell}")

    _log("running flag pass")
    for row_i, row in enumerate(actual_grid):
        for col_i, cell in enumerate(row):
            if cell != " " or (row_i == 0 or row_i == len(actual_grid) - 1 or col_i == 0 or col_i == len(row) - 1):
                continue
            num_h = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if actual_grid[row_i + i][col_i + j] == "H":
                        num_h += 1
            if num_h % 2 == 1:
                actual_grid[row_i][col_i] = "F"
    _log("running num pass")
    for row_i, row in enumerate(actual_grid):
        for col_i, cell in enumerate(row):
            if cell != " " and cell != "O":
                continue
            if row_i == 0 or row_i == len(actual_grid) - 1 or col_i == 0 or col_i == len(row) - 1:
                actual_grid[row_i][col_i] = "0"
                continue
            num_h = 0
            num_f = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if actual_grid[row_i + i][col_i + j] == "H":
                        num_h += 1
                    elif actual_grid[row_i + i][col_i + j] == "F":
                        num_f += 1
            actual_grid[row_i][col_i] = str(num_h // 2 + num_f)
    total_flag_count = 0
    total_hidden_count = 0
    for row in actual_grid:
        for cell in row:
            if cell == "F":
                total_flag_count += 1
            elif cell == "H":
                total_hidden_count += 1
    board_metadata = f"{len(actual_grid[0])}x{len(actual_grid)}x{total_flag_count + total_hidden_count // 2}"
    _log(f"writing board: {board_metadata = }")
    file.write(board_metadata + "\n" + "\n".join(map(lambda r: "".join(r), actual_grid)))
