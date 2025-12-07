# KiCad Schematic Generation Research

This document captures research findings on programmatically generating KiCad schematic files (`.kicad_sch`), gathered during development of the TOKN decoder.

## File Format Overview

KiCad v6+ uses S-expression format for schematic files. The basic structure is:

```lisp
(kicad_sch
  (version 20231120)
  (generator "generator_name")
  (generator_version "1.0")
  (uuid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
  (paper "A4")

  (title_block
    (title "Schematic Title")
  )

  (lib_symbols
    ; Symbol definitions
  )

  ; Junctions, wires, labels, symbols...
)
```

## Key Sections

### 1. lib_symbols

Contains symbol definitions that are referenced by symbol instances. Each unique component type needs a definition here.

```lisp
(lib_symbols
  (symbol "Device:R"
    (pin_numbers (hide yes))
    (pin_names (offset 0))
    (property "Reference" "R" ...)
    (property "Value" "R" ...)
    (symbol "R_0_1"
      ; Graphics (rectangles, polylines)
    )
    (symbol "R_1_1"
      ; Pins
      (pin passive line
        (at 0 3.81 270)
        (length 1.27)
        (name "~" ...)
        (number "1" ...))
    )
  )
)
```

**Important**: The `_0_1` suffix contains graphics, `_1_1` contains pins for unit 1.

### 2. Symbol Instances

Each placed component is a symbol instance referencing a lib_symbol:

```lisp
(symbol
  (lib_id "Device:R")
  (at 168.91 67.31 90)  ; x, y, rotation
  (unit 1)
  (uuid "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
  (property "Reference" "R1" ...)
  (property "Value" "10k" ...)
  (pin "1"
    (uuid "pin-uuid-here"))
  (pin "2"
    (uuid "pin-uuid-here"))
  (instances
    (project ""
      (path ""
        (reference "R1")
        (unit 1))))
)
```

**Critical**: Each symbol instance must have `(pin "N" (uuid ...))` entries mapping pin numbers to UUIDs.

### 3. Wires

Wire segments connect components:

```lisp
(wire
  (pts
    (xy 156.21 85.09) (xy 167.64 85.09))
  (stroke (width 0) (type default))
  (uuid "wire-uuid"))
```

### 4. Junctions

Where 3+ wires meet:

```lisp
(junction
  (at 156.21 85.09)
  (diameter 0)
  (color 0 0 0 0)
  (uuid "junction-uuid"))
```

### 5. Power Symbols

Power symbols are special symbols with `(power)` flag:

```lisp
(symbol "power:GND"
  (power)
  (pin_names (offset 0) (hide yes))
  (symbol "GND_0_1"
    (polyline
      (pts (xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27))
      ...))
  (symbol "GND_1_1"
    (pin power_in line
      (at 0 0 270)
      (length 0)
      ...))
)
```

### 6. Global Labels

For named signals:

```lisp
(global_label
  "SIGNAL_NAME"
  (shape input)
  (at 176.53 67.31 180)  ; x, y, rotation
  (effects
    (font (size 1.27 1.27))
    (justify right))
  (uuid "label-uuid")
  (property "Intersheetrefs" "${INTERSHEET_REFS}" ...)
)
```

## Standard Symbol Definitions

### Device:R (Resistor)

```lisp
(symbol "Device:R"
  (pin_numbers (hide yes))
  (pin_names (offset 0))
  (property "Reference" "R" (at 2.032 0 90) ...)
  (property "Value" "R" (at 0 0 90) ...)
  (symbol "R_0_1"
    (rectangle
      (start -1.016 -2.54)
      (end 1.016 2.54)
      (stroke (width 0.254) (type default))
      (fill (type none))))
  (symbol "R_1_1"
    (pin passive line
      (at 0 3.81 270)
      (length 1.27)
      (name "~" ...)
      (number "1" ...))
    (pin passive line
      (at 0 -3.81 90)
      (length 1.27)
      (name "~" ...)
      (number "2" ...)))
)
```

- Pin 1 at y=+3.81 (top), pointing down (270°)
- Pin 2 at y=-3.81 (bottom), pointing up (90°)
- Body: rectangle from (-1.016, -2.54) to (1.016, 2.54)

### Device:C (Capacitor)

```lisp
(symbol "Device:C"
  (pin_numbers (hide yes))
  (pin_names (offset 0.254))
  (property "Reference" "C" (at 0.635 2.54 0) ...)
  (property "Value" "C" (at 0.635 -2.54 0) ...)
  (symbol "C_0_1"
    (polyline
      (pts (xy -2.032 0.762) (xy 2.032 0.762))
      (stroke (width 0.508) (type default))
      (fill (type none)))
    (polyline
      (pts (xy -2.032 -0.762) (xy 2.032 -0.762))
      ...))
  (symbol "C_1_1"
    (pin passive line
      (at 0 3.81 270)
      (length 2.794)
      (name "~" ...)
      (number "1" ...))
    (pin passive line
      (at 0 -3.81 90)
      (length 2.794)
      (name "~" ...)
      (number "2" ...)))
)
```

- Two horizontal lines representing capacitor plates
- Pin 1 at top, Pin 2 at bottom

## Coordinate System

- **Origin**: Top-left of schematic sheet
- **X axis**: Positive to the right
- **Y axis**: Positive downward (screen coordinates)
- **Units**: Millimeters
- **Grid**: Typically 2.54mm (0.1 inch) spacing
- **Rotation**: Degrees, counter-clockwise (0=right, 90=up, 180=left, 270=down)

## Pin Directions

Pin direction in symbol definition determines which way the pin line extends:

| Angle | Direction | Description |
|-------|-----------|-------------|
| 0     | Right     | Pin extends to the right |
| 90    | Up        | Pin extends upward |
| 180   | Left      | Pin extends to the left |
| 270   | Down      | Pin extends downward |

## Symbol Rotation

When a symbol is placed with rotation, all internal coordinates rotate:

- `(at x y 0)` - No rotation
- `(at x y 90)` - Rotated 90° CCW (symbol faces up)
- `(at x y 180)` - Rotated 180° (symbol upside down)
- `(at x y 270)` - Rotated 270° CCW (symbol faces down)

## UUID Generation

KiCad uses UUIDs extensively. For deterministic output, generate UUIDs from content:

```python
import hashlib

def make_uuid(seed: str) -> str:
    h = hashlib.md5(seed.encode()).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"
```

## Key Findings

### 1. KiCad is Tolerant

From KiCad forum research: "A simple symbol entry is sufficient for instantiating a component" — KiCad auto-generates missing fields and UUIDs when loading files.

Minimal working symbol instance:
```lisp
(symbol
  (lib_id "Transistor_FET:2N7002")
  (at 33.02 38.1 0)
  (unit 1))
```

### 2. lib_symbols Must Match lib_id

Every `(lib_id "X:Y")` in a symbol instance must have a corresponding `(symbol "X:Y" ...)` in lib_symbols.

### 3. Pin UUIDs are Required for Connectivity

Without pin UUIDs in symbol instances, KiCad can't track electrical connections properly.

### 4. Power Symbols Need Special Handling

- Must have `(power)` flag in lib_symbols
- Pin type should be `power_in`
- Pin length is typically 0
- Need proper rotation based on wire direction

## Useful Resources

- [KiCad S-Expression Format Documentation](https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/)
- [kicad-skip](https://github.com/psychogenic/kicad-skip) - Python library for KiCad schematic manipulation
- [SKiDL](https://github.com/devbisme/skidl) - Python schematic description language

## Related Tools

| Tool | Description | Limitations |
|------|-------------|-------------|
| nl2sch | Netlist to KiCad schematic | Template-based, limited symbol support |
| kicad-skip | Python KiCad manipulation | Good for editing, complex for generation |
| SKiDL | Python schematic DSL | KiCad v5 only (as of research date) |

## Lessons Learned

1. **Start simple**: Begin with rectangle symbols and add complexity as needed
2. **Match the original**: Study actual KiCad files to understand exact format
3. **Pin positions matter**: Wire endpoints must align with pin positions
4. **Rotation is tricky**: Symbol rotation affects all internal coordinates
5. **Test incrementally**: Verify KiCad can open files after each change
