"""
TOKN validation suite.

Validates generated TOKN for:
1. Syntactic validity - parses correctly
2. Semantic validity - sensible connections
3. Completeness - required elements present
4. Round-trip - can decode back to KiCad
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tokn_parser import parse_tokn, ToknSchematic


@dataclass
class ValidationResult:
    """Result of validating a TOKN document."""
    valid: bool = True
    syntax_valid: bool = True
    semantic_valid: bool = True
    complete: bool = True
    roundtrip_valid: bool = True

    syntax_errors: list[str] = field(default_factory=list)
    semantic_errors: list[str] = field(default_factory=list)
    semantic_warnings: list[str] = field(default_factory=list)
    completeness_warnings: list[str] = field(default_factory=list)
    roundtrip_errors: list[str] = field(default_factory=list)

    # Metrics
    component_count: int = 0
    net_count: int = 0
    wire_count: int = 0
    pin_section_count: int = 0

    def score(self) -> float:
        """Calculate a 0-1 validity score."""
        if not self.syntax_valid:
            return 0.0

        score = 1.0

        # Deduct for semantic errors
        score -= len(self.semantic_errors) * 0.1

        # Deduct less for warnings
        score -= len(self.semantic_warnings) * 0.02
        score -= len(self.completeness_warnings) * 0.02

        # Deduct for roundtrip failures
        if not self.roundtrip_valid:
            score -= 0.2

        return max(0.0, min(1.0, score))


def validate_syntax(tokn_text: str) -> tuple[bool, list[str], Optional[ToknSchematic]]:
    """Validate TOKN syntax - does it parse?"""
    errors = []

    # Check header
    if not tokn_text.strip().startswith('# TOKN v1'):
        errors.append("Missing '# TOKN v1' header")

    # Try to parse
    try:
        doc = parse_tokn(tokn_text)
        return True, errors, doc
    except Exception as e:
        errors.append(f"Parse error: {str(e)}")
        return False, errors, None


def validate_semantics(doc: ToknSchematic) -> tuple[bool, list[str], list[str]]:
    """Validate semantic correctness of connections."""
    errors = []
    warnings = []

    # Build component reference set
    component_refs = {c.ref for c in doc.components}

    # Check nets reference valid components
    # Note: net.pins is list of (ref, pin_num) tuples
    for net in doc.nets:
        for ref, pin_num in net.pins:
            if ref not in component_refs:
                errors.append(f"Net '{net.name}': References unknown component '{ref}'")

    # Check for floating power pins on ICs
    ic_refs = {c.ref for c in doc.components if c.ref.startswith('U') or c.ref.startswith('IC')}

    # Get all connected pins for ICs
    ic_connected_pins = {}
    for net in doc.nets:
        for ref, pin in net.pins:
            if ref in ic_refs:
                if ref not in ic_connected_pins:
                    ic_connected_pins[ref] = set()
                ic_connected_pins[ref].add(pin)

    # Check pin sections for ICs
    # Note: pins_section is list of ToknPin with .num and .name
    for ref, pins_section in doc.pins.items():
        if ref in ic_refs:
            connected = ic_connected_pins.get(ref, set())
            pin_nums = {str(p.num) for p in pins_section}

            # Check for common power pin names that should be connected
            for p in pins_section:
                pin_name_upper = p.name.upper()
                is_power = any(pwr in pin_name_upper for pwr in ['VCC', 'VDD', 'GND', 'VSS', 'VEE'])

                if is_power and str(p.num) not in connected:
                    warnings.append(f"IC '{ref}' pin {p.num} ({p.name}) appears to be power but is unconnected")

    # Check for nets with only one pin (may be intentional for interfaces)
    for net in doc.nets:
        if len(net.pins) == 1:
            # Only warn if it's an anonymous net (not an interface signal)
            if net.name.startswith('N') and net.name[1:].isdigit():
                warnings.append(f"Net '{net.name}' has only one connection")

    # Check wire nets exist
    wire_nets = {w.net for w in doc.wires}
    defined_nets = {n.name for n in doc.nets}
    for wire_net in wire_nets:
        if wire_net not in defined_nets:
            errors.append(f"Wire references undefined net '{wire_net}'")

    valid = len(errors) == 0
    return valid, errors, warnings


def validate_completeness(doc: ToknSchematic) -> list[str]:
    """Check for common completeness issues."""
    warnings = []

    # Check for decoupling caps near ICs
    ic_refs = [c.ref for c in doc.components if c.ref.startswith('U') or c.ref.startswith('IC')]
    cap_refs = [c.ref for c in doc.components if c.ref.startswith('C')]

    if ic_refs and not cap_refs:
        warnings.append("No capacitors found - ICs typically need decoupling caps")

    # Check for power nets
    power_nets = [n.name for n in doc.nets if n.name in ['+5V', '+3V3', '+12V', 'VCC', 'VDD', '+3.3V', '+5VD']]
    gnd_nets = [n.name for n in doc.nets if 'GND' in n.name.upper()]

    if ic_refs and not power_nets:
        warnings.append("No power supply nets found for ICs")

    if ic_refs and not gnd_nets:
        warnings.append("No ground nets found for ICs")

    # Check components have positions
    for c in doc.components:
        if c.x == 0 and c.y == 0:
            warnings.append(f"Component '{c.ref}' at origin (0,0) - may be unplaced")

    return warnings


def validate_roundtrip(doc: ToknSchematic) -> tuple[bool, list[str]]:
    """Test if TOKN can be decoded back to KiCad."""
    errors = []

    try:
        from tokn_decoder import decode_tokn

        # This will raise if it fails
        kicad_sch = decode_tokn(doc)

        # Basic validation of output
        if not kicad_sch or len(kicad_sch) < 100:
            errors.append("Decoded KiCad schematic is too short")
            return False, errors

        if '(kicad_sch' not in kicad_sch:
            errors.append("Decoded output doesn't look like KiCad schematic")
            return False, errors

        return True, errors

    except ImportError:
        # Decoder not available
        return True, ["Decoder not available - skipping roundtrip test"]
    except Exception as e:
        errors.append(f"Roundtrip decode failed: {str(e)}")
        return False, errors


def validate_tokn(tokn_text: str, check_roundtrip: bool = False) -> ValidationResult:
    """Full validation of a TOKN document."""
    result = ValidationResult()

    # 1. Syntax validation
    syntax_valid, syntax_errors, doc = validate_syntax(tokn_text)
    result.syntax_valid = syntax_valid
    result.syntax_errors = syntax_errors

    if not syntax_valid or doc is None:
        result.valid = False
        return result

    # Collect metrics
    result.component_count = len(doc.components)
    result.net_count = len(doc.nets)
    result.wire_count = len(doc.wires)
    result.pin_section_count = len(doc.pins)

    # 2. Semantic validation
    semantic_valid, semantic_errors, semantic_warnings = validate_semantics(doc)
    result.semantic_valid = semantic_valid
    result.semantic_errors = semantic_errors
    result.semantic_warnings = semantic_warnings

    # 3. Completeness check
    result.completeness_warnings = validate_completeness(doc)
    result.complete = len(result.completeness_warnings) == 0

    # 4. Roundtrip test (optional, slower)
    if check_roundtrip:
        roundtrip_valid, roundtrip_errors = validate_roundtrip(doc)
        result.roundtrip_valid = roundtrip_valid
        result.roundtrip_errors = roundtrip_errors

    # Overall validity
    result.valid = result.syntax_valid and result.semantic_valid

    return result


def validate_file(file_path: str, check_roundtrip: bool = False) -> ValidationResult:
    """Validate a TOKN file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tokn_text = f.read()
    return validate_tokn(tokn_text, check_roundtrip)


def main():
    """CLI for validating TOKN files."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate TOKN files')
    parser.add_argument('files', nargs='+', help='TOKN files to validate')
    parser.add_argument('--roundtrip', action='store_true', help='Test roundtrip decoding')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all warnings')

    args = parser.parse_args()

    for file_path in args.files:
        print(f"\n{'='*60}")
        print(f"Validating: {file_path}")
        print('='*60)

        result = validate_file(file_path, check_roundtrip=args.roundtrip)

        print(f"\nSyntax valid: {result.syntax_valid}")
        print(f"Semantic valid: {result.semantic_valid}")
        print(f"Complete: {result.complete}")
        if args.roundtrip:
            print(f"Roundtrip valid: {result.roundtrip_valid}")

        print(f"\nMetrics:")
        print(f"  Components: {result.component_count}")
        print(f"  Nets: {result.net_count}")
        print(f"  Wires: {result.wire_count}")
        print(f"  Pin sections: {result.pin_section_count}")

        print(f"\nScore: {result.score():.2f}")

        if result.syntax_errors:
            print(f"\nSyntax errors:")
            for e in result.syntax_errors:
                print(f"  - {e}")

        if result.semantic_errors:
            print(f"\nSemantic errors:")
            for e in result.semantic_errors:
                print(f"  - {e}")

        if args.verbose or not result.valid:
            if result.semantic_warnings:
                print(f"\nSemantic warnings:")
                for w in result.semantic_warnings:
                    print(f"  - {w}")

            if result.completeness_warnings:
                print(f"\nCompleteness warnings:")
                for w in result.completeness_warnings:
                    print(f"  - {w}")


if __name__ == '__main__':
    main()
