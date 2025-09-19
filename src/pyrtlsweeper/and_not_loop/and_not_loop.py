from io import TextIOWrapper

import pyrtl

from and_not_loop.components import _Crossover, _LogicGate, _AndGate, _NotGate, _NopGate, _Split, _WireHorizontal, \
    _WireVertical, _TurnLeftDown, _TurnLeftUp, _TurnRightUp, _TurnRightDown, _Const0, _Const1, _CapLeft, _CapRight
from pyrtlsweeper.logging_ import _log


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
    # logic: set of logic nets with arg and dest wires
    wire_src_dict, wire_sink_dict = post_synth.net_connections()
    inputs: list[tuple[pyrtl.Input, list[pyrtl.Input]]] = []
    input_wires: list[pyrtl.Input] = []
    outputs: list[tuple[pyrtl.Output, list[pyrtl.Output]]] = []
    output_wires: list[pyrtl.Output] = []
    for original_io in post_synth.io_map.keys():
        if isinstance(original_io, pyrtl.Input):
            inputs.append((original_io, post_synth.io_map[original_io]))
            input_wires.extend(post_synth.io_map[original_io])
        if isinstance(original_io, pyrtl.Output):
            outputs.append((original_io, post_synth.io_map[original_io]))
            output_wires.extend(post_synth.io_map[original_io])
    _log(f"{output_wires = }")
    # create the list of logic nets in the correct order
    logic: set[pyrtl.LogicNet] = post_synth.logic
    new_logic_order: list[pyrtl.LogicNet] = []
    # add all nets without an output as a dest to the list
    for net in logic:
        found_output = False
        for dest in net.dests:
            if isinstance(dest, pyrtl.Output):
                found_output = True
                break
        if not found_output:
            new_logic_order.append(net)
    # add all nets with an output as a dest to the list
    output_nets: list[pyrtl.LogicNet] = []
    for net in logic:
        found_output = False
        for dest in net.dests:
            if isinstance(dest, pyrtl.Output):
                found_output = True
                break
        if found_output:
            output_nets.append(net)
    output_nets.sort(key=lambda n: list(map(lambda w: w.name, output_wires)).index(n.dests[0].name))
    new_logic_order.extend(output_nets)
    _log(f"{new_logic_order = }")
    # new_logic_order has all the non-output nets followed by the sorted output nets

    # construct map of logic net -> ordered list of logic nets whose outputs are inputs to the logic net
    net_src_dict: dict[pyrtl.LogicNet, list[pyrtl.LogicNet | pyrtl.Input | pyrtl.Const]] = {}
    for net in logic:
        srcs: list[pyrtl.LogicNet | pyrtl.Input | pyrtl.Const] = []
        for arg in net.args:
            if isinstance(arg, pyrtl.Input) or isinstance(arg, pyrtl.Const):
                srcs.append(arg)
            else:
                srcs.append(wire_src_dict[arg])
        net_src_dict[net] = srcs
    _log(f"{net_src_dict = }")
    # create the map of logic net to coordinate positions in 3x
    # and the list of LogicGates
    logic_gates: list[_LogicGate] = []
    heights: dict[pyrtl.LogicNet, int] = {}
    curr_height = len(input_wires) * 2
    for net in new_logic_order:
        if net.op == "&":
            logic_gates.append(_AndGate())
        elif net.op == "~":
            logic_gates.append(_NotGate())
        elif net.op == "w":
            logic_gates.append(_NopGate())
        heights[net] = curr_height
        curr_height += logic_gates[len(logic_gates) - 1].metadata()[0] * 2
    connections: list[tuple[int, int]] = []  # src height, sink height
    consts: list[tuple[int, bool]] = []
    for sink_net, srcs in net_src_dict.items():
        for i, src in enumerate(srcs):
            if isinstance(src, pyrtl.LogicNet):
                gate: _LogicGate
                if src.op == "&":
                    gate = _AndGate()
                elif src.op == "~":
                    gate = _NotGate()
                else:
                    gate = _NopGate()
                connections.append((heights[src] + gate.metadata()[0] * 2 - 2, heights[sink_net] + 2 * i))
            elif isinstance(src, pyrtl.Input):
                connections.append(
                    (list(map(lambda w: w.name, input_wires)).index(src.name) * 2, heights[sink_net] + 2 * i))
            elif isinstance(src, pyrtl.Const):
                consts.append((heights[sink_net] + 2 * i, src.val == 1))
    _log(f"{consts = }")
    total_grid_height = curr_height * 2 - (len(input_wires) * 2) + 1
    gates_width = max(logic_gates, key=lambda g: g.metadata()[1]).metadata()[1]
    total_grid_width = gates_width + (2 * (curr_height - len(input_wires) * 2)) + 2
    wiring_grid = [[False for _ in range(total_grid_width)] for _ in range(total_grid_height)]
    below_gates_bottom_left = (curr_height + 1, curr_height - len(input_wires) * 2 + 1)
    for i in range(len(input_wires) * 2 + 1, below_gates_bottom_left[0], 2):
        for j in range(1, below_gates_bottom_left[0] - i + 1):
            wiring_grid[i][below_gates_bottom_left[1] - j] = True
        for i1 in range(0, (below_gates_bottom_left[0] - i) * 2 - 1):
            wiring_grid[i + i1][below_gates_bottom_left[1] - (below_gates_bottom_left[0] - i)] = True
        for j in range(below_gates_bottom_left[1] - (below_gates_bottom_left[0] - i),
                       below_gates_bottom_left[1] + gates_width + below_gates_bottom_left[0] - i):
            wiring_grid[below_gates_bottom_left[0] * 2 - i - 2][j] = True
        for i1 in range(below_gates_bottom_left[0], below_gates_bottom_left[0] * 2 - i - 1):
            wiring_grid[i1][below_gates_bottom_left[1] + gates_width + below_gates_bottom_left[0] - i - 1] = True
    for src_height, sink_height in connections:
        for j in range(below_gates_bottom_left[1] + gates_width,
                       below_gates_bottom_left[1] + gates_width + curr_height - sink_height):
            wiring_grid[src_height + 1][j] = True
        for i in range(src_height + 1, below_gates_bottom_left[0] + 1):
            wiring_grid[i][below_gates_bottom_left[1] + gates_width + curr_height - sink_height - 1] = True
    actual_grid = [[" " for _ in range(total_grid_width * 3)] for _ in range(total_grid_height * 3)]
    for row_i, row in enumerate(wiring_grid):
        for col_i, cell in enumerate(row):
            if cell:
                new_coords = (row_i * 3, col_i * 3)
                if wiring_grid[row_i - 1][col_i] and wiring_grid[row_i + 1][col_i] and wiring_grid[row_i][col_i - 1] and \
                    wiring_grid[row_i][col_i + 1]:
                    _Crossover().place(actual_grid, new_coords)
                elif wiring_grid[row_i + 1][col_i] and wiring_grid[row_i][col_i - 1] and wiring_grid[row_i][col_i + 1]:
                    _Split().place(actual_grid, new_coords)
                elif wiring_grid[row_i][col_i - 1] and wiring_grid[row_i + 1][col_i]:
                    _TurnLeftDown().place(actual_grid, new_coords)
                elif wiring_grid[row_i][col_i - 1] and wiring_grid[row_i - 1][col_i]:
                    _TurnLeftUp().place(actual_grid, new_coords)
                elif wiring_grid[row_i][col_i + 1] and wiring_grid[row_i - 1][col_i]:
                    _TurnRightUp().place(actual_grid, new_coords)
                elif wiring_grid[row_i][col_i + 1] and wiring_grid[row_i + 1][col_i]:
                    _TurnRightDown().place(actual_grid, new_coords)
                elif wiring_grid[row_i][col_i - 1] or wiring_grid[row_i][col_i + 1]:
                    _WireHorizontal().place(actual_grid, new_coords)
                elif wiring_grid[row_i - 1][col_i] or wiring_grid[row_i + 1][col_i]:
                    _WireVertical().place(actual_grid, new_coords)
    for i in range(len(input_wires)):
        for j in range(gates_width):
            _CapLeft().place(actual_grid, (i * 6 + 3, below_gates_bottom_left[1] * 3 - 3))
            _WireHorizontal().place(actual_grid, (i * 6 + 3, below_gates_bottom_left[1] * 3 + j * 3))
    placing_gate_height = len(input_wires) * 6 + 3
    for gate in logic_gates:
        gate.place(actual_grid, (placing_gate_height, below_gates_bottom_left[1] * 3))
        for j in range(gate.metadata()[1], gates_width):
            _WireHorizontal().place(actual_grid, (placing_gate_height + gate.metadata()[0] * 6 - 6,
                                                  below_gates_bottom_left[1] * 3 + j * 3))
        placing_gate_height += gate.metadata()[0] * 6
    output_cap_height = 1
    for gate_i in range(len(output_wires)):
        gate_height = logic_gates[-gate_i].metadata()[0]
        _CapRight().place(actual_grid, (below_gates_bottom_left[0] * 3 - 6 * output_cap_height,
                                        below_gates_bottom_left[1] * 3 + gates_width * 3))
        output_cap_height += gate_height
    for const_height, one in consts:
        (_Const1() if one else _Const0()).place(actual_grid, (below_gates_bottom_left[0] * 3 - 3,
                                                              below_gates_bottom_left[1] * 3 + gates_width * 3 + (
                                                                  below_gates_bottom_left[0] - (
                                                                  const_height + 1)) * 3 - 3))
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
