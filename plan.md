# TOKN Standard Development Prompt

## Context

You are helping define **TOKN** (Token-Optimised KiCad Notation), a domain-specific format for representing KiCad schematic files (`.kicad_sch`) in a token-efficient way suitable for LLM training and generation.

TOKN is built on top of **TOON** (Token-Oriented Object Notation), a general-purpose compact serialisation format. Before proceeding, familiarise yourself with:

- TOON specification: https://github.com/toon-format/spec
- TOON reference implementation: https://github.com/toon-format/toon

## Goal

Create a lossless (for electrical intent) intermediate representation that:

1. **Minimises tokens** - strips verbose formatting, UUIDs, absolute coordinates, and structural noise
2. **Preserves design intent** - component types, values, net connectivity, hierarchical structure
3. **Enables round-trip conversion** - `kicad_sch → TOKN → kicad_sch` produces functionally equivalent schematics
4. **Is learnable** - structure is consistent enough for an LLM to learn generation patterns from ~4500 examples


## KiCad Schematic Structure (for reference)

KiCad `.kicad_sch` files use S-expressions with these main elements:

```lisp
(kicad_sch
  (version N) (generator "...") (uuid "...")
  (lib_symbols ...)           ; Symbol library cache
  (symbol                     ; Component instances
    (lib_id "...")
    (at X Y angle)
    (uuid "...")
    (property "Reference" "R1" ...)
    (property "Value" "10k" ...)
    (pin "1" (uuid "..."))
    ...)
  (wire                       ; Connections
    (pts (xy X1 Y1) (xy X2 Y2))
    (uuid "..."))
  (label "NET_NAME" (at X Y angle) ...)
  (global_label ...)
  (hierarchical_label ...)
  (junction (at X Y) ...)
  (no_connect (at X Y) ...)
  (sheet ...)                 ; Hierarchical sheets
  ...)
```

## Design Questions to Address

### 1. What to Strip
- UUIDs (regenerate on conversion back)
- Absolute coordinates (use connectivity graph or relative positioning?)
- Wire routing details (just preserve net connectivity?)
- Redundant properties inferrable from symbol library
- Generator metadata, version info

### 2. What to Preserve
- Component types (lib_id or normalised form?)
- Component values and critical properties
- Reference designators
- Net names (labels, global labels)
- Pin assignments
- Hierarchical structure
- Power symbols and their net associations

### 3. Representation Decisions
- How to express connectivity: explicit netlist vs implicit from labels?
- How to handle component variants (same part, different footprint)?
- How to reference standard symbols vs custom symbols?
- How to represent power nets (VCC, GND, etc.)?
- What level of hierarchy to support?

### 4. TOON Mapping
- Which elements map to TOON tabular arrays?
- What's the optimal field ordering for common patterns?
- How to handle variable-property components?

## Deliverables Needed

1. **TOKN Specification Document** - Formal definition of the format
2. **Field Definitions** - What each field means, valid values, optionality
3. **Conversion Rules** - How each KiCad element maps to/from TOKN
4. **Example Corpus** - Hand-converted examples showing the mapping
5. **Edge Cases** - How to handle unusual but valid schematics
6. **Validation Rules** - What makes a TOKN document valid

## Example Direction (strawman, iterate on this)

A simple RC filter might go from:

```lisp
(kicad_sch
  (symbol (lib_id "Device:R") (at 100 50 0) (uuid "abc123")
    (property "Reference" "R1" (at 100 40 0))
    (property "Value" "10k" (at 100 60 0)))
  (symbol (lib_id "Device:C") (at 150 75 90) (uuid "def456")
    (property "Reference" "C1" (at 160 75 0))
    (property "Value" "100nF" (at 140 75 0)))
  (wire (pts (xy 100 60) (xy 100 75) (xy 150 75)))
  (label "FILT_OUT" (at 175 75 0)))
```

To something like:

```toon
components[2]{ref,type,value}:
R1,R,10k
C1,C,100nF

nets[2]{name,pins}:
N1,"R1.2,C1.1"
FILT_OUT,"C1.2"
```

This is just a starting point - the actual format needs careful design.

## Process

1. Start by analysing 5-10 representative circuits from different complexity levels
2. Identify common patterns and variations
3. Draft initial format specification
4. Test round-trip conversion on examples
5. Iterate based on edge cases and token efficiency measurements
6. Document formally

## Success Criteria

- Token count reduction of 50%+ vs raw kicad_sch
- Lossless round-trip for electrical connectivity
- Consistent structure that an LLM can learn
- Human-readable enough for debugging