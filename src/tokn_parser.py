"""
TOKN parser - reads TOKN format back into data structures.
"""

import re
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ToknComponent:
    ref: str
    type: str
    value: str
    footprint: str = ''
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0  # width (pin spread)
    h: float = 0.0  # height (pin spread)
    a: float = 0.0  # angle in degrees


@dataclass
class ToknNet:
    name: str
    pins: list[tuple[str, str]]  # (ref, pin_number)


@dataclass
class ToknWire:
    net: str
    points: list[tuple[float, float]]


@dataclass
class ToknPin:
    num: str
    name: str


@dataclass
class ToknSchematic:
    title: str = ''
    components: list[ToknComponent] = field(default_factory=list)
    pins: dict[str, list[ToknPin]] = field(default_factory=dict)  # ref -> list of pins
    nets: list[ToknNet] = field(default_factory=list)
    wires: list[ToknWire] = field(default_factory=list)


def parse_tokn(text: str) -> ToknSchematic:
    """Parse TOKN format text into a ToknSchematic."""
    sch = ToknSchematic()
    lines = text.strip().split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines and comments
        if not line or line.startswith('#'):
            i += 1
            continue

        # Title
        if line.startswith('title:'):
            sch.title = line[6:].strip()
            i += 1
            continue

        # Components section
        match = re.match(r'components\[(\d+)\]\{([^}]+)\}:', line)
        if match:
            count = int(match.group(1))
            fields = match.group(2).split(',')
            i += 1
            for _ in range(count):
                if i >= len(lines):
                    break
                row = lines[i].strip()
                if not row or row.startswith('#'):
                    i += 1
                    continue
                values = parse_csv_row(row)
                comp = ToknComponent(
                    ref=values[0] if len(values) > 0 else '',
                    type=values[1] if len(values) > 1 else '',
                    value=values[2] if len(values) > 2 else '',
                    footprint=values[3] if len(values) > 3 else '',
                    x=float(values[4]) if len(values) > 4 and values[4] else 0.0,
                    y=float(values[5]) if len(values) > 5 and values[5] else 0.0,
                    w=float(values[6]) if len(values) > 6 and values[6] else 0.0,
                    h=float(values[7]) if len(values) > 7 and values[7] else 0.0,
                    a=float(values[8]) if len(values) > 8 and values[8] else 0.0,
                )
                sch.components.append(comp)
                i += 1
            continue

        # Pins section - pins{REF}[N]:
        match = re.match(r'pins\{([^}]+)\}\[(\d+)\]:', line)
        if match:
            ref = match.group(1)
            count = int(match.group(2))
            i += 1
            pins_list = []
            for _ in range(count):
                if i >= len(lines):
                    break
                row = lines[i].strip()
                if not row or row.startswith('#'):
                    i += 1
                    continue
                # Check if this is a new section header (not a pin row)
                if re.match(r'(pins|nets|wires|components)\{?', row):
                    break
                values = parse_csv_row(row)
                if len(values) >= 2:
                    pins_list.append(ToknPin(num=values[0], name=values[1]))
                i += 1
            sch.pins[ref] = pins_list
            continue

        # Nets section
        match = re.match(r'nets\[(\d+)\]\{([^}]+)\}:', line)
        if match:
            count = int(match.group(1))
            i += 1
            for _ in range(count):
                if i >= len(lines):
                    break
                row = lines[i].strip()
                if not row or row.startswith('#'):
                    i += 1
                    continue
                values = parse_csv_row(row)
                name = values[0] if len(values) > 0 else ''
                pins_str = values[1] if len(values) > 1 else ''
                pins = parse_pins(pins_str)
                sch.nets.append(ToknNet(name=name, pins=pins))
                i += 1
            continue

        # Wires section
        match = re.match(r'wires\[(\d+)\]\{([^}]+)\}:', line)
        if match:
            count = int(match.group(1))
            i += 1
            for _ in range(count):
                if i >= len(lines):
                    break
                row = lines[i].strip()
                if not row or row.startswith('#'):
                    i += 1
                    continue
                values = parse_csv_row(row)
                net_name = values[0] if len(values) > 0 else ''
                pts_str = values[1] if len(values) > 1 else ''
                points = parse_points(pts_str)
                sch.wires.append(ToknWire(net=net_name, points=points))
                i += 1
            continue

        i += 1

    return sch


def parse_csv_row(row: str) -> list[str]:
    """Parse a CSV row, handling quoted values."""
    values = []
    current = ''
    in_quotes = False

    for char in row:
        if char == '"':
            in_quotes = not in_quotes
        elif char == ',' and not in_quotes:
            values.append(current)
            current = ''
        else:
            current += char

    values.append(current)
    return values


def parse_pins(pins_str: str) -> list[tuple[str, str]]:
    """Parse pins string like 'R1.1,U1.3' into list of (ref, pin) tuples."""
    pins = []
    for pin in pins_str.split(','):
        pin = pin.strip()
        if '.' in pin:
            ref, num = pin.rsplit('.', 1)
            pins.append((ref, num))
    return pins


def parse_points(pts_str: str) -> list[tuple[float, float]]:
    """Parse points string like '128.27 57.15,149.86 57.15' into list of (x, y) tuples."""
    points = []
    for pt in pts_str.split(','):
        pt = pt.strip()
        if ' ' in pt:
            parts = pt.split()
            if len(parts) >= 2:
                try:
                    x = float(parts[0])
                    y = float(parts[1])
                    points.append((x, y))
                except ValueError:
                    pass
    return points


def parse_tokn_file(filepath: str) -> ToknSchematic:
    """Parse a TOKN file."""
    with open(filepath, 'r') as f:
        return parse_tokn(f.read())


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tokn_parser.py <file.tokn>")
        sys.exit(1)

    sch = parse_tokn_file(sys.argv[1])
    print(f"Title: {sch.title}")
    print(f"Components: {len(sch.components)}")
    for c in sch.components:
        print(f"  {c.ref}: {c.type} = {c.value}")
    print(f"Nets: {len(sch.nets)}")
    for n in sch.nets:
        pins = ', '.join(f"{r}.{p}" for r, p in n.pins)
        print(f"  {n.name}: {pins}")
    print(f"Wires: {len(sch.wires)}")
    for w in sch.wires[:5]:
        pts = ' -> '.join(f"({x:.1f},{y:.1f})" for x, y in w.points)
        print(f"  {w.net}: {pts}")
    if len(sch.wires) > 5:
        print(f"  ... and {len(sch.wires) - 5} more")
