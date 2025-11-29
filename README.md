# TOKN

**Token-Optimised KiCad Notation** — a compact format for representing KiCad schematics, designed for LLM training and generation.

## What is TOKN?

TOKN is a domain-specific format that converts KiCad schematic files (`.kicad_sch`) into a token-efficient representation. It's built on [TOON](https://github.com/toon-format/spec) (Token-Oriented Object Notation).

### Goals

- **Minimise tokens** — strip UUIDs, absolute coordinates, and structural noise
- **Preserve design intent** — component types, values, net connectivity, hierarchy
- **Enable round-trip conversion** — `kicad_sch → TOKN → kicad_sch` produces functionally equivalent schematics
- **Be learnable** — consistent structure for LLM pattern learning

### Example

A KiCad schematic like:

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

Becomes something like:

```toon
components[2]{ref,type,value}:
R1,R,10k
C1,C,100nF

nets[2]{name,pins}:
N1,"R1.2,C1.1"
FILT_OUT,"C1.2"
```

## Status

This project is in the specification phase. See [plan.md](plan.md) for the development roadmap.

## Related

- [TOON Specification](https://github.com/toon-format/spec)
- [TOON Reference Implementation](https://github.com/toon-format/toon)

## License

[MIT](LICENSE)
