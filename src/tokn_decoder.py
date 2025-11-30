"""
TOKN decoder - converts TOKN format back to KiCad schematic files.

Design:
- Uses standard Device:R and Device:C symbols for passives
- Creates generic rectangular symbols with proper pins for ICs
- Pin positions inferred from wire endpoints in TOKN
- Deterministic output (same TOKN = same KiCad)
"""

import hashlib
from collections import defaultdict

from tokn_parser import ToknSchematic, ToknWire, parse_tokn_file


def make_uuid(seed: str) -> str:
    """Generate deterministic UUID from seed string."""
    h = hashlib.md5(seed.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def esc(s: str) -> str:
    """Escape string for S-expression."""
    if not s:
        return ''
    return s.replace('\\', '\\\\').replace('"', '\\"')


def decode_tokn(tokn_path: str) -> str:
    """Decode TOKN file and return KiCad schematic S-expression."""
    sch = parse_tokn_file(tokn_path)
    return decode_schematic(sch)


def decode_schematic(sch: ToknSchematic) -> str:
    """Convert ToknSchematic to KiCad S-expression string."""
    lines = []

    # Build component map and pin positions from nets
    comp_map = {c.ref: c for c in sch.components}

    # Collect all wire endpoints per net
    net_wire_points = defaultdict(list)
    for wire in sch.wires:
        for pt in wire.points:
            net_wire_points[wire.net].append(pt)

    # Map (ref, pin_num) -> (x, y) from wire endpoints
    pin_positions = {}
    for net in sch.nets:
        for ref, pin_num in net.pins:
            comp = comp_map.get(ref)
            if not comp:
                continue
            # Find closest wire endpoint to component center
            best_pt = None
            best_dist = float('inf')
            for pt in net_wire_points.get(net.name, []):
                dist = ((pt[0] - comp.x)**2 + (pt[1] - comp.y)**2)**0.5
                if dist < best_dist:
                    best_dist = dist
                    best_pt = pt
            if best_pt:
                pin_positions[(ref, pin_num)] = best_pt

    # Calculate pin positions relative to component center (for lib_symbols)
    # Group pins by component ref
    comp_pins = defaultdict(list)
    for (ref, pin_num), (px, py) in pin_positions.items():
        comp = comp_map[ref]
        # Pin position relative to component center
        rel_x = px - comp.x
        rel_y = py - comp.y
        comp_pins[ref].append((pin_num, rel_x, rel_y))

    # Find junctions (3+ wires meeting at same point)
    point_count = defaultdict(int)
    for wire in sch.wires:
        for pt in wire.points:
            key = (round(pt[0], 2), round(pt[1], 2))
            point_count[key] += 1
    junctions = [pt for pt, count in point_count.items() if count >= 3]

    # Find power symbol locations (terminal points of power nets)
    power_nets = {'GND', '+5V', '+3V3', '+3.3V', '+5VD', '+12V', '+24V', 'VCC', 'VDD', 'VSS'}
    power_symbols = []

    # Get component pin positions as set for excluding from power symbol placement
    comp_pin_set = set((round(x, 2), round(y, 2)) for (x, y) in pin_positions.values())

    # Helper to find wire direction at a terminal point
    def get_wire_direction_at_point(wires, px, py):
        """Returns direction the wire goes FROM this point (0=right, 90=down, 180=left, 270=up)."""
        for w in wires:
            pts = w.points
            for i, pt in enumerate(pts):
                if abs(pt[0] - px) < 0.01 and abs(pt[1] - py) < 0.01:
                    # Found the point, get adjacent point
                    if i == 0 and len(pts) > 1:
                        other = pts[1]
                    elif i == len(pts) - 1 and len(pts) > 1:
                        other = pts[-2]
                    else:
                        continue
                    dx = other[0] - px
                    dy = other[1] - py
                    if abs(dx) > abs(dy):
                        return 0 if dx > 0 else 180  # right or left
                    else:
                        return 90 if dy > 0 else 270  # down or up
        return 0  # default

    for net in sch.nets:
        if net.name not in power_nets and not net.name.startswith('+'):
            continue
        net_wires = [w for w in sch.wires if w.net == net.name]
        net_points = defaultdict(int)
        for w in net_wires:
            for pt in w.points:
                key = (round(pt[0], 2), round(pt[1], 2))
                net_points[key] += 1
        # Terminal points (degree 1) that aren't at component pins
        for pt, count in net_points.items():
            if count == 1 and pt not in comp_pin_set:
                direction = get_wire_direction_at_point(net_wires, pt[0], pt[1])
                power_symbols.append((net.name, pt[0], pt[1], direction))

    # Find global label locations (terminal points of signal nets)
    labels = []
    for net in sch.nets:
        # Skip power nets and anonymous nets
        if net.name in power_nets or net.name.startswith('+') or net.name.startswith('N'):
            continue
        net_wires = [w for w in sch.wires if w.net == net.name]
        net_points = defaultdict(int)
        for w in net_wires:
            for pt in w.points:
                key = (round(pt[0], 2), round(pt[1], 2))
                net_points[key] += 1
        for pt, count in net_points.items():
            if count == 1 and pt not in comp_pin_set:
                direction = get_wire_direction_at_point(net_wires, pt[0], pt[1])
                labels.append((net.name, pt[0], pt[1], direction))

    # Header
    doc_uuid = make_uuid(f"doc_{sch.title}")
    lines.append('(kicad_sch')
    lines.append('  (version 20231120)')
    lines.append('  (generator "tokn_decoder")')
    lines.append('  (generator_version "1.0")')
    lines.append(f'  (uuid "{doc_uuid}")')
    lines.append('  (paper "A4")')
    lines.append('')
    lines.append('  (title_block')
    lines.append(f'    (title "{esc(sch.title)}")')
    lines.append('  )')
    lines.append('')

    # Library symbols
    lines.append('  (lib_symbols')

    # Generate symbol definitions
    emitted_types = set()
    for comp in sch.components:
        lib_id = get_lib_id(comp.type)
        if lib_id in emitted_types:
            continue
        emitted_types.add(lib_id)

        if comp.type == 'R':
            lines.extend(emit_resistor_symbol())
        elif comp.type == 'C':
            lines.extend(emit_capacitor_symbol())
        else:
            # Generic IC - need to collect all pins from all instances of this type
            all_pins = []
            for c in sch.components:
                if c.type == comp.type:
                    pins = comp_pins.get(c.ref, [])
                    for pin_num, rel_x, rel_y in pins:
                        all_pins.append((pin_num, rel_x, rel_y))
            lines.extend(emit_generic_symbol(comp.type, comp.w, comp.h, all_pins))

    # Power symbols
    power_types = set(p[0] for p in power_symbols)
    for ptype in power_types:
        lines.extend(emit_power_symbol(ptype))

    lines.append('  )')  # end lib_symbols
    lines.append('')

    # Junctions
    for i, (jx, jy) in enumerate(junctions):
        lines.append('  (junction')
        lines.append(f'    (at {jx} {jy})')
        lines.append('    (diameter 0)')
        lines.append('    (color 0 0 0 0)')
        lines.append(f'    (uuid "{make_uuid(f"junction_{i}_{jx}_{jy}")}")')
        lines.append('  )')

    # Wires
    for i, wire in enumerate(sch.wires):
        if len(wire.points) < 2:
            continue
        for j in range(len(wire.points) - 1):
            p1, p2 = wire.points[j], wire.points[j+1]
            lines.append('  (wire')
            lines.append('    (pts')
            lines.append(f'      (xy {p1[0]} {p1[1]}) (xy {p2[0]} {p2[1]})')
            lines.append('    )')
            lines.append('    (stroke (width 0) (type default))')
            lines.append(f'    (uuid "{make_uuid(f"wire_{i}_{j}_{p1}_{p2}")}")')
            lines.append('  )')

    # Global labels
    for i, (name, lx, ly, direction) in enumerate(labels):
        # Label points opposite to wire direction (label text faces away from wire)
        # Wire goes right (0) -> label faces left (180), wire goes left (180) -> label faces right (0)
        # Wire goes down (90) -> label faces up (270), wire goes up (270) -> label faces down (90)
        label_angle = (direction + 180) % 360
        # Justify based on label angle
        if label_angle == 0:
            justify = 'left'
        elif label_angle == 180:
            justify = 'right'
        else:
            justify = 'left'  # vertical labels
        lines.append('  (global_label')
        lines.append(f'    "{esc(name)}"')
        lines.append('    (shape input)')
        lines.append(f'    (at {lx} {ly} {label_angle})')
        lines.append('    (effects')
        lines.append('      (font (size 1.27 1.27))')
        lines.append(f'      (justify {justify}))')
        lines.append(f'    (uuid "{make_uuid(f"label_{i}_{name}_{lx}_{ly}")}")')
        lines.append('    (property "Intersheetrefs" "${INTERSHEET_REFS}"')
        lines.append(f'      (at {lx} {ly} 0)')
        lines.append('      (effects (font (size 1.27 1.27)) (hide yes)))')
        lines.append('  )')

    # Component instances
    for i, comp in enumerate(sch.components):
        lib_id = get_lib_id(comp.type)
        pins = comp_pins.get(comp.ref, [])

        lines.append('  (symbol')
        lines.append(f'    (lib_id "{lib_id}")')
        lines.append(f'    (at {comp.x} {comp.y} {int(comp.a)})')
        lines.append('    (unit 1)')
        lines.append('    (exclude_from_sim no)')
        lines.append('    (in_bom yes)')
        lines.append('    (on_board yes)')
        lines.append('    (dnp no)')
        lines.append(f'    (uuid "{make_uuid(f"comp_{i}_{comp.ref}")}")')
        lines.append(f'    (property "Reference" "{comp.ref}"')
        lines.append(f'      (at {comp.x} {comp.y - 5} 0)')
        lines.append('      (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Value" "{esc(comp.value)}"')
        lines.append(f'      (at {comp.x} {comp.y + 5} 0)')
        lines.append('      (effects (font (size 1.27 1.27))))')
        lines.append(f'    (property "Footprint" "{esc(comp.footprint)}"')
        lines.append(f'      (at {comp.x} {comp.y} 0)')
        lines.append('      (effects (font (size 1.27 1.27)) (hide yes)))')
        lines.append('    (property "Datasheet" "~"')
        lines.append(f'      (at {comp.x} {comp.y} 0)')
        lines.append('      (effects (font (size 1.27 1.27)) (hide yes)))')

        # Pin UUIDs
        for pin_num, _, _ in pins:
            lines.append(f'    (pin "{pin_num}"')
            lines.append(f'      (uuid "{make_uuid(f"pin_{comp.ref}_{pin_num}")}")')
            lines.append('    )')

        lines.append('    (instances')
        lines.append('      (project ""')
        lines.append('        (path ""')
        lines.append(f'          (reference "{comp.ref}")')
        lines.append('          (unit 1))))')
        lines.append('  )')

    # Power symbols
    for i, (ptype, px, py, direction) in enumerate(power_symbols):
        is_gnd = ptype in ('GND', 'VSS')
        # Power symbol rotation: symbol pin connects to wire
        # For GND: symbol points down (away from wire), so rotate based on wire direction
        # For VCC: symbol points up (away from wire)
        # Wire goes right (0) -> symbol rotates 90 (pin faces right)
        # Wire goes left (180) -> symbol rotates 270 (pin faces left)
        # Wire goes down (90) -> symbol rotates 0 (pin faces down)
        # Wire goes up (270) -> symbol rotates 180 (pin faces up)
        if direction == 0:  # wire goes right
            angle = 90
        elif direction == 180:  # wire goes left
            angle = 270
        elif direction == 90:  # wire goes down
            angle = 0
        else:  # direction == 270, wire goes up
            angle = 180

        lines.append('  (symbol')
        lines.append(f'    (lib_id "power:{ptype}")')
        lines.append(f'    (at {px} {py} {angle})')
        lines.append('    (unit 1)')
        lines.append('    (exclude_from_sim no)')
        lines.append('    (in_bom yes)')
        lines.append('    (on_board yes)')
        lines.append('    (dnp no)')
        lines.append(f'    (uuid "{make_uuid(f"pwr_{i}_{ptype}_{px}_{py}")}")')
        lines.append(f'    (property "Reference" "#PWR{i+1:02d}"')
        lines.append(f'      (at {px} {py} 0)')
        lines.append('      (effects (font (size 1.27 1.27)) (hide yes)))')
        lines.append(f'    (property "Value" "{ptype}"')
        lines.append(f'      (at {px} {py} 0)')
        lines.append('      (effects (font (size 1.27 1.27))))')
        lines.append('    (property "Footprint" ""')
        lines.append(f'      (at {px} {py} 0)')
        lines.append('      (effects (font (size 1.27 1.27)) (hide yes)))')
        lines.append('    (property "Datasheet" ""')
        lines.append(f'      (at {px} {py} 0)')
        lines.append('      (effects (font (size 1.27 1.27)) (hide yes)))')
        lines.append(f'    (pin "1"')
        lines.append(f'      (uuid "{make_uuid(f"pwr_pin_{i}_{ptype}")}")')
        lines.append('    )')
        lines.append('    (instances')
        lines.append('      (project ""')
        lines.append('        (path ""')
        lines.append(f'          (reference "#PWR{i+1:02d}")')
        lines.append('          (unit 1))))')
        lines.append('  )')

    lines.append(')')
    return '\n'.join(lines)


def get_lib_id(comp_type: str) -> str:
    """Get library ID for component type."""
    if comp_type == 'R':
        return 'Device:R'
    elif comp_type == 'C':
        return 'Device:C'
    else:
        return f'tokn:{comp_type}'


def emit_resistor_symbol() -> list[str]:
    """Emit standard Device:R symbol definition."""
    return [
        '    (symbol "Device:R"',
        '      (pin_numbers (hide yes))',
        '      (pin_names (offset 0))',
        '      (exclude_from_sim no)',
        '      (in_bom yes)',
        '      (on_board yes)',
        '      (property "Reference" "R"',
        '        (at 2.032 0 90)',
        '        (effects (font (size 1.27 1.27))))',
        '      (property "Value" "R"',
        '        (at 0 0 90)',
        '        (effects (font (size 1.27 1.27))))',
        '      (property "Footprint" ""',
        '        (at -1.778 0 90)',
        '        (effects (font (size 1.27 1.27)) (hide yes)))',
        '      (property "Datasheet" "~"',
        '        (at 0 0 0)',
        '        (effects (font (size 1.27 1.27)) (hide yes)))',
        '      (symbol "R_0_1"',
        '        (rectangle',
        '          (start -1.016 -2.54)',
        '          (end 1.016 2.54)',
        '          (stroke (width 0.254) (type default))',
        '          (fill (type none))))',
        '      (symbol "R_1_1"',
        '        (pin passive line',
        '          (at 0 3.81 270)',
        '          (length 1.27)',
        '          (name "~" (effects (font (size 1.27 1.27))))',
        '          (number "1" (effects (font (size 1.27 1.27)))))',
        '        (pin passive line',
        '          (at 0 -3.81 90)',
        '          (length 1.27)',
        '          (name "~" (effects (font (size 1.27 1.27))))',
        '          (number "2" (effects (font (size 1.27 1.27))))))',
        '    )',
    ]


def emit_capacitor_symbol() -> list[str]:
    """Emit standard Device:C symbol definition."""
    return [
        '    (symbol "Device:C"',
        '      (pin_numbers (hide yes))',
        '      (pin_names (offset 0.254))',
        '      (exclude_from_sim no)',
        '      (in_bom yes)',
        '      (on_board yes)',
        '      (property "Reference" "C"',
        '        (at 0.635 2.54 0)',
        '        (effects (font (size 1.27 1.27)) (justify left)))',
        '      (property "Value" "C"',
        '        (at 0.635 -2.54 0)',
        '        (effects (font (size 1.27 1.27)) (justify left)))',
        '      (property "Footprint" ""',
        '        (at 0.9652 -3.81 0)',
        '        (effects (font (size 1.27 1.27)) (hide yes)))',
        '      (property "Datasheet" "~"',
        '        (at 0 0 0)',
        '        (effects (font (size 1.27 1.27)) (hide yes)))',
        '      (symbol "C_0_1"',
        '        (polyline',
        '          (pts (xy -2.032 0.762) (xy 2.032 0.762))',
        '          (stroke (width 0.508) (type default))',
        '          (fill (type none)))',
        '        (polyline',
        '          (pts (xy -2.032 -0.762) (xy 2.032 -0.762))',
        '          (stroke (width 0.508) (type default))',
        '          (fill (type none))))',
        '      (symbol "C_1_1"',
        '        (pin passive line',
        '          (at 0 3.81 270)',
        '          (length 2.794)',
        '          (name "~" (effects (font (size 1.27 1.27))))',
        '          (number "1" (effects (font (size 1.27 1.27)))))',
        '        (pin passive line',
        '          (at 0 -3.81 90)',
        '          (length 2.794)',
        '          (name "~" (effects (font (size 1.27 1.27))))',
        '          (number "2" (effects (font (size 1.27 1.27))))))',
        '    )',
    ]


def emit_generic_symbol(comp_type: str, width: float, height: float, pins: list[tuple[str, float, float]]) -> list[str]:
    """Emit generic rectangular symbol with pins at actual positions."""
    lines = []

    # Use TOKN w/h or calculate from pin positions
    if width > 0 and height > 0:
        half_w = width / 2
        half_h = height / 2
    else:
        # Calculate bounding box from pins
        if pins:
            xs = [rel_x for _, rel_x, _ in pins]
            ys = [rel_y for _, _, rel_y in pins]
            half_w = max(abs(min(xs, default=0)), abs(max(xs, default=0))) + 2.54
            half_h = max(abs(min(ys, default=0)), abs(max(ys, default=0))) + 2.54
        else:
            half_w = 5.08
            half_h = 5.08

    # Deduplicate pins (same pin number from different instances)
    seen_pins = {}
    for pin_num, rel_x, rel_y in pins:
        if pin_num not in seen_pins:
            seen_pins[pin_num] = (rel_x, rel_y)

    # Get reference prefix
    ref_prefix = 'U'
    if comp_type.startswith('MAX') or comp_type.startswith('LM') or comp_type.startswith('TL'):
        ref_prefix = 'IC'

    lines.append(f'    (symbol "tokn:{comp_type}"')
    lines.append('      (exclude_from_sim no)')
    lines.append('      (in_bom yes)')
    lines.append('      (on_board yes)')
    lines.append(f'      (property "Reference" "{ref_prefix}"')
    lines.append(f'        (at {half_w + 2} {-half_h} 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (justify left)))')
    lines.append(f'      (property "Value" "{comp_type}"')
    lines.append(f'        (at {half_w + 2} {-half_h + 2.54} 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (justify left)))')
    lines.append('      (property "Footprint" ""')
    lines.append('        (at 0 0 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append('      (property "Datasheet" "~"')
    lines.append('        (at 0 0 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))')

    # Symbol with rectangle and pins
    lines.append(f'      (symbol "{comp_type}_1_1"')
    lines.append('        (rectangle')
    lines.append(f'          (start {-half_w + 5.08} {-half_h})')
    lines.append(f'          (end {half_w - 5.08} {half_h})')
    lines.append('          (stroke (width 0.254) (type default))')
    lines.append('          (fill (type background)))')

    # Emit pins at their actual positions
    for pin_num, (rel_x, rel_y) in seen_pins.items():
        # Determine pin direction based on position relative to rectangle
        if rel_x < -half_w + 5.08:
            # Pin on left side
            direction = 0  # points right
            pin_x = rel_x
            length = (-half_w + 5.08) - rel_x
        elif rel_x > half_w - 5.08:
            # Pin on right side
            direction = 180  # points left
            pin_x = rel_x
            length = rel_x - (half_w - 5.08)
        elif rel_y < -half_h:
            # Pin on bottom
            direction = 90  # points up
            pin_x = rel_x
            length = (-half_h) - rel_y
        else:
            # Pin on top
            direction = 270  # points down
            pin_x = rel_x
            length = rel_y - half_h

        length = max(abs(length), 2.54)

        lines.append('        (pin passive line')
        lines.append(f'          (at {rel_x} {rel_y} {direction})')
        lines.append(f'          (length {length})')
        lines.append(f'          (name "~" (effects (font (size 1.27 1.27))))')
        lines.append(f'          (number "{pin_num}" (effects (font (size 1.27 1.27)))))')

    lines.append('      )')
    lines.append('    )')

    return lines


def emit_power_symbol(ptype: str) -> list[str]:
    """Emit power symbol definition."""
    is_gnd = ptype in ('GND', 'VSS')
    lines = []

    lines.append(f'    (symbol "power:{ptype}"')
    lines.append('      (power)')
    lines.append('      (pin_numbers (hide yes))')
    lines.append('      (pin_names (offset 0) (hide yes))')
    lines.append('      (exclude_from_sim no)')
    lines.append('      (in_bom yes)')
    lines.append('      (on_board yes)')
    lines.append('      (property "Reference" "#PWR"')
    lines.append('        (at 0 -6.35 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append(f'      (property "Value" "{ptype}"')
    lines.append(f'        (at 0 {-3.81 if is_gnd else 3.556} 0)')
    lines.append('        (effects (font (size 1.27 1.27))))')
    lines.append('      (property "Footprint" ""')
    lines.append('        (at 0 0 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))')
    lines.append('      (property "Datasheet" ""')
    lines.append('        (at 0 0 0)')
    lines.append('        (effects (font (size 1.27 1.27)) (hide yes)))')

    if is_gnd:
        lines.append(f'      (symbol "{ptype}_0_1"')
        lines.append('        (polyline')
        lines.append('          (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))')
        lines.append('          (stroke (width 0) (type default))')
        lines.append('          (fill (type none))))')
    else:
        lines.append(f'      (symbol "{ptype}_0_1"')
        lines.append('        (polyline')
        lines.append('          (pts (xy -0.762 1.27) (xy 0 2.54))')
        lines.append('          (stroke (width 0) (type default))')
        lines.append('          (fill (type none)))')
        lines.append('        (polyline')
        lines.append('          (pts (xy 0 2.54) (xy 0.762 1.27))')
        lines.append('          (stroke (width 0) (type default))')
        lines.append('          (fill (type none)))')
        lines.append('        (polyline')
        lines.append('          (pts (xy 0 0) (xy 0 2.54))')
        lines.append('          (stroke (width 0) (type default))')
        lines.append('          (fill (type none))))')

    lines.append(f'      (symbol "{ptype}_1_1"')
    lines.append('        (pin power_in line')
    lines.append(f'          (at 0 0 {270 if is_gnd else 90})')
    lines.append('          (length 0)')
    lines.append('          (name "~" (effects (font (size 1.27 1.27))))')
    lines.append('          (number "1" (effects (font (size 1.27 1.27))))))')
    lines.append('    )')

    return lines


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python tokn_decoder.py <file.tokn> [output.kicad_sch]")
        sys.exit(1)

    tokn_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else tokn_path.replace('.tokn', '.decoded.kicad_sch')

    result = decode_tokn(tokn_path)
    with open(output_path, 'w') as f:
        f.write(result)

    print(f"Decoded {tokn_path} -> {output_path}")
