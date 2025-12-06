"""
Render KiCad schematics and TOKN files using matplotlib.

Supports side-by-side comparison to verify no data loss.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import tiktoken
from pathlib import Path

from kicad_sch import Schematic, Component, parse_schematic
from tokn_parser import ToknSchematic, parse_tokn_file


def render_kicad(ax, sch: Schematic):
    """Render a KiCad schematic to a matplotlib axes."""
    ax.set_aspect('equal')
    ax.invert_yaxis()

    all_x, all_y = [], []

    # Draw wires
    for wire in sch.wires:
        if len(wire.points) >= 2:
            xs = [p.x for p in wire.points]
            ys = [p.y for p in wire.points]
            ax.plot(xs, ys, 'b-', linewidth=1.5, zorder=1)
            all_x.extend(xs)
            all_y.extend(ys)

    # Draw junctions
    for junc in sch.junctions:
        circle = plt.Circle((junc.x, junc.y), 1.0, color='blue', zorder=3)
        ax.add_patch(circle)
        all_x.append(junc.x)
        all_y.append(junc.y)

    # Draw components
    for comp in sch.components:
        is_power = (comp.lib_id in sch.lib_symbols and
                    sch.lib_symbols[comp.lib_id].is_power)
        draw_component(ax, comp, is_power)
        all_x.append(comp.x)
        all_y.append(comp.y)
        for pin_pos in comp.pins.values():
            all_x.append(pin_pos.x)
            all_y.append(pin_pos.y)

    # Draw labels
    for label in sch.labels:
        color = {'global': 'green', 'local': 'purple', 'hierarchical': 'orange'}.get(label.label_type, 'black')
        ax.plot(label.x, label.y, 's', color=color, markersize=6, zorder=4)
        ax.annotate(label.name, (label.x, label.y), fontsize=8, color=color,
                    xytext=(5, -5), textcoords='offset points', zorder=5)
        all_x.append(label.x)
        all_y.append(label.y)

    # Set limits
    if all_x and all_y:
        margin = 20
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(max(all_y) + margin, min(all_y) - margin)

    ax.set_title(f"KiCad: {sch.title or 'Schematic'}")
    ax.grid(True, alpha=0.3)


def render_tokn(ax, sch: ToknSchematic):
    """Render a TOKN schematic to a matplotlib axes."""
    ax.set_aspect('equal')
    ax.invert_yaxis()

    all_x, all_y = [], []

    # Build map of component pin positions
    pin_positions = {}  # (ref, pin_num) -> (x, y)
    comp_map = {c.ref: c for c in sch.components}

    # For ICs with pin definitions, calculate positions using standard dual-inline layout
    for comp in sch.components:
        if comp.ref in sch.pins and comp.type not in ('R', 'C', 'CP', 'L', 'D'):
            pin_defs = sch.pins[comp.ref]
            num_pins = len(pin_defs)
            if num_pins == 0:
                continue

            # Use component dimensions or defaults
            half_w = comp.w / 2 if comp.w > 0 else 10.16
            half_h = comp.h / 2 if comp.h > 0 else max(num_pins * 1.27, 7.62)

            # Standard dual-inline layout: pins 1-N/2 on left, N/2+1 to N on right
            pins_per_side = (num_pins + 1) // 2
            pin_spacing = (half_h * 2 - 5.08) / max(pins_per_side - 1, 1)

            sorted_pins = sorted(pin_defs, key=lambda p: int(p.num) if p.num.isdigit() else 0)
            for i, pin in enumerate(sorted_pins):
                pin_idx = int(pin.num) if pin.num.isdigit() else i + 1
                if pin_idx <= pins_per_side:
                    # Left side: pin 1 at top, going down
                    rel_x = -half_w
                    rel_y = -half_h + 2.54 + (pin_idx - 1) * pin_spacing
                else:
                    # Right side: pin N/2+1 at bottom, going up
                    right_idx = pin_idx - pins_per_side
                    rel_x = half_w
                    rel_y = half_h - 2.54 - (right_idx - 1) * pin_spacing

                pin_positions[(comp.ref, pin.num)] = (comp.x + rel_x, comp.y + rel_y)

    # For passives and components without pin defs, use net-based positions
    net_wire_points = {}  # net_name -> list of all wire endpoints
    for wire in sch.wires:
        if wire.net not in net_wire_points:
            net_wire_points[wire.net] = []
        for pt in wire.points:
            net_wire_points[wire.net].append(pt)

    for net in sch.nets:
        wire_points = net_wire_points.get(net.name, [])
        for ref, pin_num in net.pins:
            # Skip if already have position from pin defs
            if (ref, pin_num) in pin_positions:
                continue
            if ref in comp_map and wire_points:
                comp = comp_map[ref]
                # Find the wire point closest to this component's center
                best_pt = None
                best_dist = float('inf')
                for pt in wire_points:
                    dist = ((pt[0] - comp.x) ** 2 + (pt[1] - comp.y) ** 2) ** 0.5
                    if dist < best_dist:
                        best_dist = dist
                        best_pt = pt
                if best_pt:
                    pin_positions[(ref, pin_num)] = best_pt

    # Build set of points that are connected to components (wire endpoints near component bounds)
    component_connected_points = set()
    for comp in sch.components:
        # Get component bounding box with small tolerance
        # Use actual pin spread + small margin, not a large minimum
        half_w = comp.w / 2 + 2
        half_h = comp.h / 2 + 2
        # For ICs with significant size, ensure minimum bounds
        if comp.type not in ('R', 'C', 'CP', 'L', 'D'):
            half_w = max(half_w, 5)
            half_h = max(half_h, 5)
        for wire in sch.wires:
            for pt in wire.points:
                px, py = pt
                # Check if point is within or near the component bounds
                if (comp.x - half_w <= px <= comp.x + half_w and
                    comp.y - half_h <= py <= comp.y + half_h):
                    component_connected_points.add((round(px, 2), round(py, 2)))

    # Count wire connections at each point
    point_counts = {}
    for wire in sch.wires:
        for pt in wire.points:
            key = (round(pt[0], 2), round(pt[1], 2))
            point_counts[key] = point_counts.get(key, 0) + 1

    # Points where wires connect (for label placement logic)
    wire_connected_points = {pt for pt, count in point_counts.items() if count >= 2}
    # Points needing junction dots (3+ connections, not simple corners)
    junction_dots = {pt for pt, count in point_counts.items() if count >= 3}

    # Draw wires
    for wire in sch.wires:
        if len(wire.points) >= 2:
            xs = [p[0] for p in wire.points]
            ys = [p[1] for p in wire.points]
            ax.plot(xs, ys, '-', color='blue', linewidth=1.5, zorder=1)
            all_x.extend(xs)
            all_y.extend(ys)

    # Draw junctions (only for 3+ wire connections, not corners)
    for (x, y) in junction_dots:
        circle = plt.Circle((x, y), 1.0, color='blue', zorder=3)
        ax.add_patch(circle)

    # Draw net labels at ALL unconnected wire ends
    # Power nets get power symbols, signal nets get green square + label
    power_nets = {'+5V', '+12V', '+3V3', '+3.3V', 'GND', 'VCC', 'VDD', 'VSS', 'VBAT'}

    for wire in sch.wires:
        if not wire.points:
            continue

        # Only label named nets (not anonymous N1, N2, etc.)
        if wire.net.startswith('N') and wire.net[1:].isdigit():
            continue

        is_power = wire.net in power_nets

        # Find the unconnected endpoint
        first_pt = (round(wire.points[0][0], 2), round(wire.points[0][1], 2))
        last_pt = (round(wire.points[-1][0], 2), round(wire.points[-1][1], 2))

        first_connected = first_pt in component_connected_points or first_pt in wire_connected_points
        last_connected = last_pt in component_connected_points or last_pt in wire_connected_points

        # Prefer the unconnected end; if both are unconnected or both connected, use first
        if not first_connected and last_connected:
            label_pt = wire.points[0]
            other_pt = wire.points[1] if len(wire.points) > 1 else wire.points[0]
        elif first_connected and not last_connected:
            label_pt = wire.points[-1]
            other_pt = wire.points[-2] if len(wire.points) > 1 else wire.points[-1]
        elif not first_connected and not last_connected:
            label_pt = wire.points[0]
            other_pt = wire.points[1] if len(wire.points) > 1 else wire.points[0]
        else:
            # Both connected - skip labeling this wire
            continue

        x, y = label_pt
        ox, oy = other_pt

        # Determine text alignment based on wire direction
        dx = x - ox
        dy = y - oy

        if is_power:
            # Draw power symbol - 50% smaller
            if wire.net == 'GND':
                # GND symbol - downward pointing (3 horizontal lines)
                ax.plot([x - 1.5, x + 1.5], [y, y], 'r-', linewidth=1.5, zorder=4)
                ax.plot([x - 1, x + 1], [y + 0.75, y + 0.75], 'r-', linewidth=1.5, zorder=4)
                ax.plot([x - 0.5, x + 0.5], [y + 1.5, y + 1.5], 'r-', linewidth=1.5, zorder=4)
            else:
                # VCC/+5V symbol - upward pointing triangle
                triangle = plt.Polygon([(x, y - 1.5), (x - 1.5, y + 0.5), (x + 1.5, y + 0.5)],
                                       fill=False, edgecolor='red', linewidth=1.5, zorder=4)
                ax.add_patch(triangle)
                ax.annotate(wire.net, (x, y - 2), fontsize=5, color='red',
                           ha='center', va='bottom', zorder=5)
        else:
            # Signal net - green square marker + text label
            ax.plot(x, y, 's', color='green', markersize=5, zorder=4)

            if abs(dx) > abs(dy):
                # Horizontal wire
                if dx > 0:
                    ha, text_offset = 'left', (5, 0)
                else:
                    ha, text_offset = 'right', (-5, 0)
                va = 'center'
            else:
                # Vertical wire
                if dy > 0:
                    va, text_offset = 'top', (0, 5)
                else:
                    va, text_offset = 'bottom', (0, -5)
                ha = 'center'

            ax.annotate(wire.net, (x, y), fontsize=7, color='green',
                       xytext=text_offset, textcoords='offset points',
                       ha=ha, va=va, zorder=5)

    # Draw components
    for comp in sch.components:
        if comp.x != 0 or comp.y != 0:
            all_x.append(comp.x)
            all_y.append(comp.y)
            # Get pin positions for this component
            comp_pins = {pin: pos for (ref, pin), pos in pin_positions.items() if ref == comp.ref}
            draw_tokn_component(ax, comp, comp_pins)

    # Show stats
    ax.text(0.02, 0.98, f"Components: {len(sch.components)}\nNets: {len(sch.nets)}\nWires: {len(sch.wires)}",
            transform=ax.transAxes, fontsize=8, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Set limits
    if all_x and all_y:
        margin = 20
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(max(all_y) + margin, min(all_y) - margin)

    ax.set_title(f"TOKN: {sch.title or 'Schematic'}")
    ax.grid(True, alpha=0.3)


def draw_component(ax, comp: Component, is_power: bool):
    """Draw a component symbol."""
    if is_power:
        marker = '^' if 'V' in comp.value or '+' in comp.value else 'v'
        ax.plot(comp.x, comp.y, marker, color='red', markersize=10, zorder=4)
        ax.annotate(comp.value, (comp.x, comp.y), fontsize=7, color='red',
                    xytext=(3, 3), textcoords='offset points', zorder=5)
        return

    comp_type = comp.lib_id.split(':')[-1].split('_')[0] if ':' in comp.lib_id else comp.lib_id

    if comp.pins:
        pin_xs = [p.x for p in comp.pins.values()]
        pin_ys = [p.y for p in comp.pins.values()]
        min_x, max_x = min(pin_xs), max(pin_xs)
        min_y, max_y = min(pin_ys), max(pin_ys)
        padding = 2
        width = max(max_x - min_x, 8) + padding * 2
        height = max(max_y - min_y, 4) + padding * 2
        rect_x = min_x - padding
        rect_y = min_y - padding
    else:
        width, height = 10, 6
        rect_x = comp.x - width / 2
        rect_y = comp.y - height / 2

    if comp_type == 'R':
        draw_resistor(ax, comp)
    elif comp_type == 'C':
        draw_capacitor(ax, comp)
    else:
        rect = patches.FancyBboxPatch(
            (rect_x, rect_y), width, height,
            boxstyle="round,pad=0.02",
            facecolor='lightyellow',
            edgecolor='black',
            linewidth=1.5,
            zorder=2
        )
        ax.add_patch(rect)

    for pin_pos in comp.pins.values():
        ax.plot(pin_pos.x, pin_pos.y, 'ko', markersize=3, zorder=3)

    ax.annotate(comp.reference, (comp.x, comp.y - 3), fontsize=8, fontweight='bold',
                ha='center', va='bottom', zorder=5)
    ax.annotate(comp.value, (comp.x, comp.y + 3), fontsize=7,
                ha='center', va='top', zorder=5, color='gray')


def draw_resistor(ax, comp: Component):
    """Draw a resistor symbol."""
    if len(comp.pins) >= 2:
        pins = list(comp.pins.values())
        p1, p2 = pins[0], pins[1]
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        length = np.sqrt(dx*dx + dy*dy)

        if length > 0:
            ux, uy = dx/length, dy/length
            px, py = -uy, ux
            n_zigs = 4
            zig_height = 2
            points = [(p1.x, p1.y)]

            for i in range(n_zigs * 2):
                t = (i + 1) / (n_zigs * 2 + 1)
                base_x = p1.x + dx * t
                base_y = p1.y + dy * t
                offset = zig_height * (1 if i % 2 == 0 else -1)
                points.append((base_x + px * offset, base_y + py * offset))

            points.append((p2.x, p2.y))
            xs, ys = zip(*points)
            ax.plot(xs, ys, 'k-', linewidth=1.5, zorder=2)


def draw_capacitor(ax, comp: Component):
    """Draw a capacitor symbol."""
    if len(comp.pins) >= 2:
        pins = list(comp.pins.values())
        p1, p2 = pins[0], pins[1]
        mx = (p1.x + p2.x) / 2
        my = (p1.y + p2.y) / 2
        dx = p2.x - p1.x
        dy = p2.y - p1.y
        length = np.sqrt(dx*dx + dy*dy)

        if length > 0:
            ux, uy = dx/length, dy/length
            px, py = -uy, ux
            gap = 1.5
            plate_len = 4

            ax.plot([p1.x, mx - ux*gap], [p1.y, my - uy*gap], 'k-', linewidth=1.5, zorder=2)
            ax.plot([p2.x, mx + ux*gap], [p2.y, my + uy*gap], 'k-', linewidth=1.5, zorder=2)
            ax.plot([mx - ux*gap - px*plate_len, mx - ux*gap + px*plate_len],
                    [my - uy*gap - py*plate_len, my - uy*gap + py*plate_len],
                    'k-', linewidth=2, zorder=2)
            ax.plot([mx + ux*gap - px*plate_len, mx + ux*gap + px*plate_len],
                    [my + uy*gap - py*plate_len, my + uy*gap + py*plate_len],
                    'k-', linewidth=2, zorder=2)


def draw_tokn_component(ax, comp, pin_positions=None):
    """Draw a TOKN component symbol.

    Args:
        ax: matplotlib axes
        comp: component object with x, y, w, h, type, ref, value, a
        pin_positions: dict mapping pin number (str) to (x, y) position
    """
    if pin_positions is None:
        pin_positions = {}

    x, y = comp.x, comp.y
    comp_type = comp.type
    w, h = comp.w, comp.h
    angle = comp.a

    # Determine orientation from pin spread (w, h)
    # h > w means pins are spread vertically -> vertical component
    # w > h means pins are spread horizontally -> horizontal component
    if h > w + 0.1:
        is_vertical = True
        pin_spread = h
    elif w > h + 0.1:
        is_vertical = False
        pin_spread = w
    else:
        # Square or no spread - use angle as fallback
        is_vertical = (angle % 180) == 90
        pin_spread = max(w, h)

    # Draw based on component type
    if comp_type == 'R':
        # Resistor - 50% smaller body with lead wires to pin positions
        body_half = 2  # half-length of resistor body
        body_width = 0.75  # half-width of resistor body
        if is_vertical:
            pin1_y = y - pin_spread / 2  # top pin
            pin2_y = y + pin_spread / 2  # bottom pin
            # Lead wires from pins to body
            ax.plot([x, x], [pin1_y, y - body_half], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x, x], [y + body_half, pin2_y], 'k-', linewidth=1.5, zorder=2)
            # Body
            rect = patches.FancyBboxPatch(
                (x - body_width, y - body_half), body_width * 2, body_half * 2,
                boxstyle="round,pad=0.02",
                facecolor='white',
                edgecolor='black',
                linewidth=1.5,
                zorder=2
            )
            ax.add_patch(rect)
            ax.annotate(comp.ref, (x - 2, y), fontsize=7, fontweight='bold',
                        ha='right', va='center', zorder=5)
            ax.annotate(comp.value, (x + 2, y), fontsize=6,
                        ha='left', va='center', zorder=5, color='gray')
        else:
            pin1_x = x - pin_spread / 2  # left pin
            pin2_x = x + pin_spread / 2  # right pin
            # Lead wires from pins to body
            ax.plot([pin1_x, x - body_half], [y, y], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x + body_half, pin2_x], [y, y], 'k-', linewidth=1.5, zorder=2)
            # Body
            rect = patches.FancyBboxPatch(
                (x - body_half, y - body_width), body_half * 2, body_width * 2,
                boxstyle="round,pad=0.02",
                facecolor='white',
                edgecolor='black',
                linewidth=1.5,
                zorder=2
            )
            ax.add_patch(rect)
            ax.annotate(comp.ref, (x, y - 2), fontsize=7, fontweight='bold',
                        ha='center', va='top', zorder=5)
            ax.annotate(comp.value, (x, y + 2), fontsize=6,
                        ha='center', va='bottom', zorder=5, color='gray')
    elif comp_type == 'C' or comp_type == 'CP':
        # Capacitor - 50% smaller plates with lead wires
        plate_width = 1.5  # half-width of plates
        gap = 0.4  # gap between plates
        if is_vertical:
            pin1_y = y - pin_spread / 2  # top pin
            pin2_y = y + pin_spread / 2  # bottom pin
            # Lead wires from pins to plates
            ax.plot([x, x], [pin1_y, y - gap], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x, x], [y + gap, pin2_y], 'k-', linewidth=1.5, zorder=2)
            # Plates
            ax.plot([x - plate_width, x + plate_width], [y - gap, y - gap], 'k-', linewidth=2, zorder=2)
            ax.plot([x - plate_width, x + plate_width], [y + gap, y + gap], 'k-', linewidth=2, zorder=2)
            # Labels
            ax.annotate(comp.ref, (x - 2, y), fontsize=7, fontweight='bold',
                        ha='right', va='bottom', zorder=5)
            ax.annotate(comp.value, (x - 2, y), fontsize=6,
                        ha='right', va='top', zorder=5, color='gray')
        else:
            pin1_x = x - pin_spread / 2  # left pin
            pin2_x = x + pin_spread / 2  # right pin
            # Lead wires from pins to plates
            ax.plot([pin1_x, x - gap], [y, y], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x + gap, pin2_x], [y, y], 'k-', linewidth=1.5, zorder=2)
            # Plates
            ax.plot([x - gap, x - gap], [y - plate_width, y + plate_width], 'k-', linewidth=2, zorder=2)
            ax.plot([x + gap, x + gap], [y - plate_width, y + plate_width], 'k-', linewidth=2, zorder=2)
            # Labels
            ax.annotate(comp.ref, (x, y - 2), fontsize=7, fontweight='bold',
                        ha='right', va='bottom', zorder=5)
            ax.annotate(comp.value, (x, y - 2), fontsize=6,
                        ha='left', va='bottom', zorder=5, color='gray')
    elif comp_type in ('QNPN', 'QPNP', 'NMOS', 'PMOS') or comp_type.startswith('BSS') or comp_type.startswith('2N'):
        # Transistor - draw circle with leads to actual pin positions
        body_size = 2
        # Draw circle for body
        circle = plt.Circle((x, y), body_size, fill=False, edgecolor='black', linewidth=1.5, zorder=2)
        ax.add_patch(circle)

        # Draw leads to each pin position
        for pin_num, (px, py) in pin_positions.items():
            # Draw line from component center to pin position
            # But stop at the circle edge
            dx, dy = px - x, py - y
            dist = (dx**2 + dy**2) ** 0.5
            if dist > 0:
                # Start point on circle edge
                edge_x = x + dx / dist * body_size
                edge_y = y + dy / dist * body_size
                ax.plot([edge_x, px], [edge_y, py], 'k-', linewidth=1.5, zorder=2)
                # Pin dot and number
                ax.plot(px, py, 'ko', markersize=2, zorder=3)
                # Position pin number on opposite side from component center
                offset_x = 1.5 if px > x else -1.5
                offset_y = 1 if py > y else -1
                ha = 'left' if px > x else 'right'
                va = 'top' if py > y else 'bottom'
                ax.annotate(pin_num, (px + offset_x, py + offset_y), fontsize=5,
                           ha=ha, va=va, zorder=5, color='#666666')

        # Labels
        ax.annotate(comp.ref, (x + 3, y - 2), fontsize=6, fontweight='bold',
                    ha='left', va='center', zorder=5)
        ax.annotate(comp.value, (x + 3, y + 2), fontsize=5,
                    ha='left', va='center', zorder=5, color='gray')
    elif comp_type.startswith('NCV') or comp_type.startswith('LM') or 'REG' in comp_type.upper() or '317' in comp_type or '7805' in comp_type:
        # Voltage regulator (3-pin) - draw as small rectangle with leads to actual pin positions
        reg_w = 4
        reg_h = 3
        rect = patches.FancyBboxPatch(
            (x - reg_w/2, y - reg_h/2), reg_w, reg_h,
            boxstyle="round,pad=0.02",
            facecolor='white',
            edgecolor='black',
            linewidth=1.5,
            zorder=2
        )
        ax.add_patch(rect)

        # Draw leads to each pin position
        for pin_num, (px, py) in pin_positions.items():
            # Find the closest edge point on the rectangle
            # Clamp to rectangle bounds
            edge_x = max(x - reg_w/2, min(x + reg_w/2, px))
            edge_y = max(y - reg_h/2, min(y + reg_h/2, py))
            # If inside, push to nearest edge
            if x - reg_w/2 < px < x + reg_w/2 and y - reg_h/2 < py < y + reg_h/2:
                # Point is inside - find nearest edge
                to_left = px - (x - reg_w/2)
                to_right = (x + reg_w/2) - px
                to_top = py - (y - reg_h/2)
                to_bot = (y + reg_h/2) - py
                min_dist = min(to_left, to_right, to_top, to_bot)
                if min_dist == to_left:
                    edge_x = x - reg_w/2
                elif min_dist == to_right:
                    edge_x = x + reg_w/2
                elif min_dist == to_top:
                    edge_y = y - reg_h/2
                else:
                    edge_y = y + reg_h/2
            else:
                # Point is outside - determine which edge to connect from
                if px <= x - reg_w/2:
                    edge_x = x - reg_w/2
                    edge_y = max(y - reg_h/2, min(y + reg_h/2, py))
                elif px >= x + reg_w/2:
                    edge_x = x + reg_w/2
                    edge_y = max(y - reg_h/2, min(y + reg_h/2, py))
                elif py <= y - reg_h/2:
                    edge_y = y - reg_h/2
                    edge_x = max(x - reg_w/2, min(x + reg_w/2, px))
                else:
                    edge_y = y + reg_h/2
                    edge_x = max(x - reg_w/2, min(x + reg_w/2, px))
            ax.plot([edge_x, px], [edge_y, py], 'k-', linewidth=1.5, zorder=2)
            # Pin dot and number
            ax.plot(px, py, 'ko', markersize=2, zorder=3)
            offset_x = 1.5 if px > x else -1.5
            offset_y = 1 if py > y else -1
            ha = 'left' if px > x else 'right'
            va = 'top' if py > y else 'bottom'
            ax.annotate(pin_num, (px + offset_x, py + offset_y), fontsize=5,
                       ha=ha, va=va, zorder=5, color='#666666')

        # Labels
        ax.annotate(comp.ref, (x, y - reg_h/2 - 1), fontsize=6, fontweight='bold',
                    ha='center', va='bottom', zorder=5)
        ax.annotate(comp.value, (x, y), fontsize=4,
                    ha='center', va='center', zorder=5, color='gray')
    else:
        # Generic IC/component box - use stored width/height
        # Small padding so box edges align with trace connections
        padding = 1
        width = max(w + padding * 2, 10)
        height = max(h + padding * 2, 6)
        rect_x = x - width / 2
        rect_y = y - height / 2

        rect = patches.FancyBboxPatch(
            (rect_x, rect_y), width, height,
            boxstyle="round,pad=0.02",
            facecolor='lightyellow',
            edgecolor='black',
            linewidth=1.5,
            zorder=2
        )
        ax.add_patch(rect)

        # Draw pin numbers
        for pin_num, (px, py) in pin_positions.items():
            # Determine which side of the component this pin is on
            is_left = px < x - width / 4
            is_right = px > x + width / 4
            is_top = py < y - height / 4
            is_bottom = py > y + height / 4

            if is_left:
                # Left side - text inside, right of pin
                ha, va = 'left', 'center'
                offset_x, offset_y = 1.5, 0
            elif is_right:
                # Right side - text inside, left of pin
                ha, va = 'right', 'center'
                offset_x, offset_y = -1.5, 0
            elif is_top:
                # Top side - text below pin (inside component)
                ha, va = 'center', 'top'
                offset_x, offset_y = 0, 1.5
            elif is_bottom:
                # Bottom side - text above pin (inside component)
                ha, va = 'center', 'bottom'
                offset_x, offset_y = 0, -1.5
            else:
                # Center (shouldn't happen)
                ha, va = 'center', 'center'
                offset_x, offset_y = 0, 0

            # Draw small dot at pin position
            ax.plot(px, py, 'ko', markersize=2, zorder=3)
            # Draw pin number
            ax.annotate(pin_num, (px + offset_x, py + offset_y), fontsize=5,
                       ha=ha, va=va, zorder=5, color='#666666')

        # Reference above the box, value centered inside the box
        ax.annotate(comp.ref, (x, rect_y - 1), fontsize=7, fontweight='bold',
                    ha='center', va='bottom', zorder=5)
        ax.annotate(comp.value, (x, y), fontsize=6,
                    ha='center', va='center', zorder=5, color='gray')


# Use cl100k_base encoding (used by GPT-4, Claude, etc.)
_tokenizer = None

def count_tokens(text: str) -> int:
    """Count tokens using tiktoken (cl100k_base encoding)."""
    global _tokenizer
    if _tokenizer is None:
        _tokenizer = tiktoken.get_encoding("cl100k_base")
    return len(_tokenizer.encode(text))


def get_file_stats(filepath: str) -> dict:
    """Get file statistics."""
    with open(filepath, 'r') as f:
        content = f.read()

    lines = content.count('\n') + (1 if content and not content.endswith('\n') else 0)
    size = len(content.encode('utf-8'))
    tokens = count_tokens(content)

    return {
        'size': size,
        'lines': lines,
        'tokens': tokens,
    }


def render_comparison(kicad_path: str, tokn_path: str, output_path: str = None, show: bool = True):
    """Render KiCad and TOKN side by side for comparison."""
    # Create figure with space for stats table
    fig = plt.figure(figsize=(20, 12))

    # Create grid: 2 columns for schematics, full width for stats
    gs = fig.add_gridspec(2, 2, height_ratios=[4, 1], hspace=0.3)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax_table = fig.add_subplot(gs[1, :])
    ax_table.axis('off')

    # Parse and render KiCad
    kicad_sch = parse_schematic(kicad_path)
    render_kicad(ax1, kicad_sch)

    # Parse and render TOKN
    tokn_sch = parse_tokn_file(tokn_path)
    render_tokn(ax2, tokn_sch)

    # Calculate stats
    kicad_stats = get_file_stats(kicad_path)
    tokn_stats = get_file_stats(tokn_path)

    # Count components (excluding power symbols for KiCad)
    kicad_components = len([c for c in kicad_sch.components
                           if not (c.lib_id in kicad_sch.lib_symbols and
                                  kicad_sch.lib_symbols[c.lib_id].is_power)])
    tokn_components = len(tokn_sch.components)

    kicad_nets = len(set())  # KiCad doesn't have explicit net list
    tokn_nets = len(tokn_sch.nets)

    kicad_wires = len(kicad_sch.wires)
    tokn_wires = len(tokn_sch.wires)

    # Build stats table
    def fmt_diff(kicad_val, tokn_val):
        diff = tokn_val - kicad_val
        sign = '+' if diff > 0 else ''
        return f'{sign}{diff}'

    def fmt_pct(kicad_val, tokn_val):
        if kicad_val == 0:
            return 'N/A'
        pct = ((tokn_val - kicad_val) / kicad_val) * 100
        sign = '+' if pct > 0 else ''
        return f'{sign}{pct:.1f}%'

    # Table data
    headers = ['Metric', 'KiCad', 'TOKN', 'Diff', '% Change']
    data = [
        ['Components', str(kicad_components), str(tokn_components),
         fmt_diff(kicad_components, tokn_components), fmt_pct(kicad_components, tokn_components)],
        ['Nets', '-', str(tokn_nets), '-', '-'],
        ['Wires', str(kicad_wires), str(tokn_wires),
         fmt_diff(kicad_wires, tokn_wires), fmt_pct(kicad_wires, tokn_wires)],
        ['File Size (bytes)', f"{kicad_stats['size']:,}", f"{tokn_stats['size']:,}",
         fmt_diff(kicad_stats['size'], tokn_stats['size']), fmt_pct(kicad_stats['size'], tokn_stats['size'])],
        ['Lines', f"{kicad_stats['lines']:,}", f"{tokn_stats['lines']:,}",
         fmt_diff(kicad_stats['lines'], tokn_stats['lines']), fmt_pct(kicad_stats['lines'], tokn_stats['lines'])],
        ['Tokens', f"{kicad_stats['tokens']:,}", f"{tokn_stats['tokens']:,}",
         fmt_diff(kicad_stats['tokens'], tokn_stats['tokens']), fmt_pct(kicad_stats['tokens'], tokn_stats['tokens'])],
    ]

    # Create table
    table = ax_table.table(
        cellText=data,
        colLabels=headers,
        cellLoc='center',
        loc='center',
        colWidths=[0.2, 0.2, 0.2, 0.2, 0.2]
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)

    # Style header row
    for i in range(len(headers)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', fontweight='bold')

    # Style data rows with alternating colors
    for i in range(1, len(data) + 1):
        color = '#D9E2F3' if i % 2 == 0 else 'white'
        for j in range(len(headers)):
            table[(i, j)].set_facecolor(color)

    # Highlight reduction cells in green
    for i, row in enumerate(data, 1):
        if row[4] != '-' and row[4] != 'N/A' and row[4].startswith('-'):
            table[(i, 3)].set_facecolor('#C6EFCE')
            table[(i, 4)].set_facecolor('#C6EFCE')

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {output_path}")

    if show:
        plt.show()

    return fig


def render_single(input_path: str, output_path: str = None, show: bool = True):
    """Render a single file (auto-detect format)."""
    fig, ax = plt.subplots(1, 1, figsize=(16, 12))

    if input_path.endswith('.kicad_sch'):
        sch = parse_schematic(input_path)
        render_kicad(ax, sch)
    elif input_path.endswith('.tokn'):
        sch = parse_tokn_file(input_path)
        render_tokn(ax, sch)
    else:
        raise ValueError(f"Unknown file type: {input_path}")

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved to {output_path}")

    if show:
        plt.show()

    return fig


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python render.py <schematic.kicad_sch> [output.png]  - Render KiCad schematic")
        print("  python render.py <file.tokn> [output.png]           - Render TOKN file")
        print("  python render.py --compare <schematic.kicad_sch> <file.tokn> [output.png]")
        sys.exit(1)

    if sys.argv[1] == '--compare':
        if len(sys.argv) < 4:
            print("Usage: python render.py --compare <schematic.kicad_sch> <file.tokn> [output.png]")
            sys.exit(1)
        kicad_path = sys.argv[2]
        tokn_path = sys.argv[3]
        output = sys.argv[4] if len(sys.argv) > 4 else None
        render_comparison(kicad_path, tokn_path, output, show=(output is None))
    else:
        input_path = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else None
        render_single(input_path, output, show=(output is None))
