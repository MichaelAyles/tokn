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

    # Draw wires (grouped by net for coloring)
    net_colors = {}
    color_cycle = plt.cm.tab10.colors

    for i, wire in enumerate(sch.wires):
        if wire.net not in net_colors:
            net_colors[wire.net] = color_cycle[len(net_colors) % len(color_cycle)]

        if len(wire.points) >= 2:
            xs = [p[0] for p in wire.points]
            ys = [p[1] for p in wire.points]
            ax.plot(xs, ys, '-', color='blue', linewidth=1.5, zorder=1)
            all_x.extend(xs)
            all_y.extend(ys)

            # Draw junction at wire endpoints
            for x, y in wire.points:
                all_x.append(x)
                all_y.append(y)

    # Find junctions (points where multiple wires meet)
    point_counts = {}
    for wire in sch.wires:
        for pt in wire.points:
            key = (round(pt[0], 2), round(pt[1], 2))
            point_counts[key] = point_counts.get(key, 0) + 1

    for (x, y), count in point_counts.items():
        if count > 1:
            circle = plt.Circle((x, y), 1.0, color='blue', zorder=3)
            ax.add_patch(circle)

    # Draw net labels at first wire endpoint
    net_labeled = set()
    for wire in sch.wires:
        if wire.net not in net_labeled and wire.points:
            x, y = wire.points[-1]  # Label at end of wire
            # Only label named nets (not anonymous N1, N2, etc.)
            if not wire.net.startswith('N') or not wire.net[1:].isdigit():
                color = 'red' if wire.net in ('+5V', '+12V', '+3V3', 'GND', 'VCC', 'VDD') else 'green'
                ax.annotate(wire.net, (x, y), fontsize=7, color=color,
                           xytext=(3, -3), textcoords='offset points', zorder=5)
            net_labeled.add(wire.net)

    # Draw components
    for comp in sch.components:
        if comp.x != 0 or comp.y != 0:
            all_x.append(comp.x)
            all_y.append(comp.y)
            draw_tokn_component(ax, comp)

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


def draw_tokn_component(ax, comp):
    """Draw a TOKN component symbol."""
    x, y = comp.x, comp.y
    comp_type = comp.type
    w, h = comp.w, comp.h
    angle = comp.a

    # For 2-pin components (R, C), use angle directly
    # angle=0 means horizontal body, angle=90 means vertical body
    if comp_type in ('R', 'C', 'CP'):
        is_vertical = (angle % 180) == 90
    else:
        # For ICs, use pin spread to determine orientation
        if h > w + 0.1:
            is_vertical = True
        elif w > h + 0.1:
            is_vertical = False
        else:
            is_vertical = (angle % 180) == 90

    # Draw based on component type
    if comp_type == 'R':
        # Simple resistor rectangle
        if is_vertical:
            rect = patches.FancyBboxPatch(
                (x - 1.5, y - 4), 3, 8,
                boxstyle="round,pad=0.02",
                facecolor='white',
                edgecolor='black',
                linewidth=1.5,
                zorder=2
            )
            ax.add_patch(rect)
            ax.annotate(comp.ref, (x - 3, y), fontsize=8, fontweight='bold',
                        ha='right', va='center', zorder=5)
            ax.annotate(comp.value, (x + 3, y), fontsize=7,
                        ha='left', va='center', zorder=5, color='gray')
        else:
            rect = patches.FancyBboxPatch(
                (x - 4, y - 1.5), 8, 3,
                boxstyle="round,pad=0.02",
                facecolor='white',
                edgecolor='black',
                linewidth=1.5,
                zorder=2
            )
            ax.add_patch(rect)
            ax.annotate(comp.ref, (x, y - 3), fontsize=8, fontweight='bold',
                        ha='center', va='top', zorder=5)
            ax.annotate(comp.value, (x, y + 3), fontsize=7,
                        ha='center', va='bottom', zorder=5, color='gray')
    elif comp_type == 'C' or comp_type == 'CP':
        # Simple capacitor symbol
        if is_vertical:
            ax.plot([x, x], [y - 4, y - 0.5], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x, x], [y + 0.5, y + 4], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x - 3, x + 3], [y - 0.5, y - 0.5], 'k-', linewidth=2, zorder=2)
            ax.plot([x - 3, x + 3], [y + 0.5, y + 0.5], 'k-', linewidth=2, zorder=2)
            ax.annotate(comp.ref, (x - 5, y), fontsize=8, fontweight='bold',
                        ha='right', va='center', zorder=5)
            ax.annotate(comp.value, (x + 5, y), fontsize=7,
                        ha='left', va='center', zorder=5, color='gray')
        else:
            ax.plot([x - 4, x - 0.5], [y, y], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x + 0.5, x + 4], [y, y], 'k-', linewidth=1.5, zorder=2)
            ax.plot([x - 0.5, x - 0.5], [y - 3, y + 3], 'k-', linewidth=2, zorder=2)
            ax.plot([x + 0.5, x + 0.5], [y - 3, y + 3], 'k-', linewidth=2, zorder=2)
            ax.annotate(comp.ref, (x, y - 5), fontsize=8, fontweight='bold',
                        ha='center', va='top', zorder=5)
            ax.annotate(comp.value, (x, y + 5), fontsize=7,
                        ha='center', va='bottom', zorder=5, color='gray')
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

        # Labels above and below the box
        ax.annotate(comp.ref, (x, rect_y - 2), fontsize=8, fontweight='bold',
                    ha='center', va='bottom', zorder=5)
        ax.annotate(comp.value, (x, rect_y + height + 2), fontsize=7,
                    ha='center', va='top', zorder=5, color='gray')


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
