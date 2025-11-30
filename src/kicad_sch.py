"""
KiCad schematic (.kicad_sch) parser.

Extracts components, wires, junctions, and labels from KiCad schematics.
"""

from dataclasses import dataclass, field
from typing import Optional
import math

from sexpr import parse, get, get_all, get_value, SExpr


@dataclass
class Point:
    x: float
    y: float

    def __hash__(self):
        return hash((round(self.x, 4), round(self.y, 4)))

    def __eq__(self, other):
        if not isinstance(other, Point):
            return False
        return (round(self.x, 4) == round(other.x, 4) and
                round(self.y, 4) == round(other.y, 4))


@dataclass
class Pin:
    number: str
    name: str
    x: float  # Relative to symbol origin
    y: float
    angle: float  # Pin angle in degrees (0=right, 90=up, 180=left, 270=down)
    pin_type: str  # input, output, bidirectional, passive, power_in, etc.


@dataclass
class LibSymbol:
    """Symbol definition from lib_symbols section."""
    lib_id: str
    pins: list[Pin] = field(default_factory=list)
    is_power: bool = False


@dataclass
class Component:
    """A placed component instance."""
    lib_id: str
    reference: str
    value: str
    footprint: str
    x: float
    y: float
    angle: float  # Rotation in degrees
    mirror: Optional[str]  # None, 'x', or 'y'
    unit: int
    dnp: bool
    uuid: str
    pins: dict[str, Point] = field(default_factory=dict)  # pin_number -> absolute position


@dataclass
class Wire:
    """A wire segment."""
    points: list[Point]
    uuid: str


@dataclass
class Junction:
    """A junction point where wires connect."""
    x: float
    y: float
    uuid: str


@dataclass
class Label:
    """A net label (local, global, or hierarchical)."""
    name: str
    x: float
    y: float
    angle: float
    label_type: str  # 'local', 'global', 'hierarchical'
    uuid: str


@dataclass
class Schematic:
    """Parsed KiCad schematic."""
    title: str
    lib_symbols: dict[str, LibSymbol] = field(default_factory=dict)
    components: list[Component] = field(default_factory=list)
    wires: list[Wire] = field(default_factory=list)
    junctions: list[Junction] = field(default_factory=list)
    labels: list[Label] = field(default_factory=list)


def parse_schematic(filepath: str) -> Schematic:
    """Parse a KiCad schematic file."""
    with open(filepath, 'r') as f:
        text = f.read()

    expr = parse(text)
    return parse_schematic_expr(expr)


def parse_schematic_expr(expr: SExpr) -> Schematic:
    """Parse schematic from S-expression."""
    if not isinstance(expr, list) or expr[0] != 'kicad_sch':
        raise ValueError("Not a valid KiCad schematic")

    sch = Schematic(title='')

    # Parse title block
    title_block = get(expr, 'title_block')
    if title_block:
        sch.title = get_value(title_block, 'title') or ''

    # Parse library symbols
    lib_symbols = get(expr, 'lib_symbols')
    if lib_symbols:
        for sym_expr in get_all(lib_symbols, 'symbol'):
            lib_sym = parse_lib_symbol(sym_expr)
            if lib_sym:
                sch.lib_symbols[lib_sym.lib_id] = lib_sym

    # Parse component instances
    for sym_expr in get_all(expr, 'symbol'):
        comp = parse_component(sym_expr, sch.lib_symbols)
        if comp:
            sch.components.append(comp)

    # Parse wires
    for wire_expr in get_all(expr, 'wire'):
        wire = parse_wire(wire_expr)
        if wire:
            sch.wires.append(wire)

    # Parse junctions
    for junc_expr in get_all(expr, 'junction'):
        junc = parse_junction(junc_expr)
        if junc:
            sch.junctions.append(junc)

    # Parse labels
    for label_expr in get_all(expr, 'label'):
        label = parse_label(label_expr, 'local')
        if label:
            sch.labels.append(label)

    for label_expr in get_all(expr, 'global_label'):
        label = parse_label(label_expr, 'global')
        if label:
            sch.labels.append(label)

    for label_expr in get_all(expr, 'hierarchical_label'):
        label = parse_label(label_expr, 'hierarchical')
        if label:
            sch.labels.append(label)

    return sch


def parse_lib_symbol(expr: SExpr) -> Optional[LibSymbol]:
    """Parse a library symbol definition."""
    if not isinstance(expr, list) or len(expr) < 2:
        return None

    lib_id = expr[1]
    if not isinstance(lib_id, str):
        return None

    # Check if it's a power symbol
    is_power = get(expr, 'power') is not None

    # Find all pins - they're in subsymbols like "SymName_1_1"
    pins = []
    for sub_sym in get_all(expr, 'symbol'):
        if isinstance(sub_sym, list) and len(sub_sym) > 1:
            # Parse pins within subsymbol
            for pin_expr in get_all(sub_sym, 'pin'):
                pin = parse_pin(pin_expr)
                if pin:
                    pins.append(pin)

    return LibSymbol(lib_id=lib_id, pins=pins, is_power=is_power)


def parse_pin(expr: SExpr) -> Optional[Pin]:
    """Parse a pin definition from a library symbol."""
    if not isinstance(expr, list) or len(expr) < 3:
        return None

    # Format: (pin TYPE STYLE (at X Y ANGLE) (length L) (name "NAME" ...) (number "NUM" ...))
    pin_type = expr[1] if len(expr) > 1 else 'passive'

    at = get(expr, 'at')
    if not at or len(at) < 4:
        return None

    x = float(at[1])
    y = float(at[2])
    angle = float(at[3]) if len(at) > 3 else 0

    name_expr = get(expr, 'name')
    name = name_expr[1] if name_expr and len(name_expr) > 1 else ''

    number_expr = get(expr, 'number')
    number = number_expr[1] if number_expr and len(number_expr) > 1 else ''

    return Pin(number=str(number), name=str(name), x=x, y=y, angle=angle, pin_type=str(pin_type))


def parse_component(expr: SExpr, lib_symbols: dict[str, LibSymbol]) -> Optional[Component]:
    """Parse a component instance."""
    if not isinstance(expr, list):
        return None

    lib_id_expr = get(expr, 'lib_id')
    if not lib_id_expr or len(lib_id_expr) < 2:
        return None
    lib_id = lib_id_expr[1]

    at = get(expr, 'at')
    if not at or len(at) < 3:
        return None
    x = float(at[1])
    y = float(at[2])
    angle = float(at[3]) if len(at) > 3 else 0

    # Check for mirror
    mirror = None
    mirror_expr = get(expr, 'mirror')
    if mirror_expr and len(mirror_expr) > 1:
        mirror = mirror_expr[1]

    unit = 1
    unit_expr = get(expr, 'unit')
    if unit_expr and len(unit_expr) > 1:
        unit = int(unit_expr[1])

    dnp = False
    dnp_expr = get(expr, 'dnp')
    if dnp_expr and len(dnp_expr) > 1:
        dnp = dnp_expr[1] == 'yes'

    uuid = ''
    uuid_expr = get(expr, 'uuid')
    if uuid_expr and len(uuid_expr) > 1:
        uuid = uuid_expr[1]

    # Extract properties
    reference = ''
    value = ''
    footprint = ''

    for prop in get_all(expr, 'property'):
        if len(prop) >= 3:
            prop_name = prop[1]
            prop_value = prop[2]
            if prop_name == 'Reference':
                reference = prop_value
            elif prop_name == 'Value':
                value = prop_value
            elif prop_name == 'Footprint':
                footprint = prop_value

    comp = Component(
        lib_id=lib_id,
        reference=reference,
        value=value,
        footprint=footprint,
        x=x, y=y,
        angle=angle,
        mirror=mirror,
        unit=unit,
        dnp=dnp,
        uuid=uuid
    )

    # Calculate absolute pin positions
    # Try lib_name first (for renamed symbols), then fall back to lib_id
    lib_name_expr = get(expr, 'lib_name')
    lib_name = lib_name_expr[1] if lib_name_expr and len(lib_name_expr) > 1 else None

    lookup_key = lib_name if lib_name and lib_name in lib_symbols else lib_id
    if lookup_key in lib_symbols:
        lib_sym = lib_symbols[lookup_key]
        for pin in lib_sym.pins:
            abs_pos = transform_pin(pin.x, pin.y, x, y, angle, mirror)
            comp.pins[pin.number] = abs_pos

    return comp


def transform_pin(pin_x: float, pin_y: float,
                  comp_x: float, comp_y: float,
                  angle: float, mirror: Optional[str]) -> Point:
    """Transform a pin position from symbol-relative to absolute coordinates.

    KiCad coordinate systems:
    - Schematic: Y increases downward
    - Symbol library: Y increases upward (standard math convention)

    So we need to flip Y when going from symbol to schematic coordinates.
    """
    # Flip Y axis (symbol coords to schematic coords)
    px, py = pin_x, -pin_y

    # Apply mirror
    if mirror == 'x':
        py = -py
    elif mirror == 'y':
        px = -px

    # Apply rotation (in schematic coordinate system)
    rad = math.radians(-angle)  # Negative because Y is flipped
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)

    rx = px * cos_a - py * sin_a
    ry = px * sin_a + py * cos_a

    # Translate to component position
    return Point(comp_x + rx, comp_y + ry)


def parse_wire(expr: SExpr) -> Optional[Wire]:
    """Parse a wire segment."""
    if not isinstance(expr, list):
        return None

    pts = get(expr, 'pts')
    if not pts:
        return None

    points = []
    for xy in get_all(pts, 'xy'):
        if len(xy) >= 3:
            points.append(Point(float(xy[1]), float(xy[2])))

    uuid = ''
    uuid_expr = get(expr, 'uuid')
    if uuid_expr and len(uuid_expr) > 1:
        uuid = uuid_expr[1]

    return Wire(points=points, uuid=uuid) if points else None


def parse_junction(expr: SExpr) -> Optional[Junction]:
    """Parse a junction."""
    if not isinstance(expr, list):
        return None

    at = get(expr, 'at')
    if not at or len(at) < 3:
        return None

    uuid = ''
    uuid_expr = get(expr, 'uuid')
    if uuid_expr and len(uuid_expr) > 1:
        uuid = uuid_expr[1]

    return Junction(x=float(at[1]), y=float(at[2]), uuid=uuid)


def parse_label(expr: SExpr, label_type: str) -> Optional[Label]:
    """Parse a label (local, global, or hierarchical)."""
    if not isinstance(expr, list) or len(expr) < 2:
        return None

    name = expr[1]
    if not isinstance(name, str):
        return None

    at = get(expr, 'at')
    if not at or len(at) < 3:
        return None

    x = float(at[1])
    y = float(at[2])
    angle = float(at[3]) if len(at) > 3 else 0

    uuid = ''
    uuid_expr = get(expr, 'uuid')
    if uuid_expr and len(uuid_expr) > 1:
        uuid = uuid_expr[1]

    return Label(name=name, x=x, y=y, angle=angle, label_type=label_type, uuid=uuid)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        sch = parse_schematic(sys.argv[1])
        print(f"Title: {sch.title}")
        print(f"Library symbols: {len(sch.lib_symbols)}")
        print(f"Components: {len(sch.components)}")
        for c in sch.components:
            print(f"  {c.reference}: {c.lib_id} = {c.value} @ ({c.x}, {c.y}) rot={c.angle}")
            for pin_num, pos in c.pins.items():
                print(f"    Pin {pin_num}: ({pos.x:.2f}, {pos.y:.2f})")
        print(f"Wires: {len(sch.wires)}")
        print(f"Junctions: {len(sch.junctions)}")
        print(f"Labels: {len(sch.labels)}")
        for l in sch.labels:
            print(f"  {l.label_type}: {l.name} @ ({l.x}, {l.y})")
