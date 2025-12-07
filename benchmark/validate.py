"""
TOKN validation suite.

Validates generated TOKN for:
1. Syntactic validity - parses correctly
2. Semantic validity - sensible connections
3. Requirement matching - includes specified components
4. Completeness - required elements present
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

    syntax_errors: list[str] = field(default_factory=list)
    semantic_errors: list[str] = field(default_factory=list)
    semantic_warnings: list[str] = field(default_factory=list)
    completeness_warnings: list[str] = field(default_factory=list)

    # Requirement matching
    requirement_score: float = 1.0  # 0-1 based on how many requirements met
    matched_requirements: list[str] = field(default_factory=list)
    missing_requirements: list[str] = field(default_factory=list)

    # Metrics
    component_count: int = 0
    net_count: int = 0
    wire_count: int = 0
    pin_section_count: int = 0

    def score(self) -> float:
        """Calculate a 0-1 validity score.

        Scoring weights:
        - Syntax valid: gate (0 if fails)
        - Requirement matching: 50% (most important - did you build what was asked?)
        - Semantic correctness: 30% (are connections valid?)
        - Completeness: 20% (best practices)
        """
        if not self.syntax_valid:
            return 0.0

        score = 0.0

        # Requirement matching: 50% of score
        score += 0.5 * self.requirement_score

        # Semantic correctness: 30% of score
        semantic_score = 1.0
        semantic_score -= len(self.semantic_errors) * 0.25  # Each error costs 25%
        semantic_score -= len(self.semantic_warnings) * 0.05
        score += 0.3 * max(0.0, semantic_score)

        # Completeness: 20% of score
        completeness_score = 1.0
        completeness_score -= len(self.completeness_warnings) * 0.1
        score += 0.2 * max(0.0, completeness_score)

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

    # Check pin sections for ICs - power pins MUST be connected (error, not warning)
    for ref, pins_section in doc.pins.items():
        if ref in ic_refs:
            connected = ic_connected_pins.get(ref, set())
            for p in pins_section:
                pin_name_upper = p.name.upper()
                is_power = any(pwr in pin_name_upper for pwr in ['VCC', 'VDD', 'GND', 'VSS', 'VEE'])

                if is_power and str(p.num) not in connected:
                    errors.append(f"IC '{ref}' power pin {p.num} ({p.name}) is unconnected")

    # Check for nets with only one pin
    for net in doc.nets:
        if len(net.pins) == 1:
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

    # Ratio check: should have ~1+ cap per IC
    if ic_refs and cap_refs and len(cap_refs) < len(ic_refs):
        warnings.append(f"Only {len(cap_refs)} caps for {len(ic_refs)} ICs - typically need more decoupling")

    # Check for power nets
    power_nets = [n.name for n in doc.nets if n.name in ['+5V', '+3V3', '+12V', 'VCC', 'VDD', '+3.3V', '+5VD']]
    gnd_nets = [n.name for n in doc.nets if 'GND' in n.name.upper()]

    if ic_refs and not power_nets:
        warnings.append("No power supply nets found for ICs")

    if ic_refs and not gnd_nets:
        warnings.append("No ground nets found for ICs")

    return warnings


def normalize_value(value: str) -> str:
    """Normalize component values for comparison.

    "0.1uF" -> "100nf"
    "10k" -> "10k"
    "4.7uF" -> "4.7uf"
    """
    v = value.lower().strip()
    # Remove common suffixes that don't affect matching
    v = v.replace('ohm', '').replace('ω', '')
    # Normalize micro
    v = v.replace('µ', 'u')
    return v


def normalize_part_number(part: str) -> str:
    """Normalize IC part numbers for comparison.

    "RT9080-33GJ5" -> "rt9080"
    "EMC2101" -> "emc2101"
    """
    p = part.lower().strip()
    # Remove common suffixes/variants
    p = re.sub(r'[-_][a-z0-9]+$', '', p)  # Remove suffix after dash
    p = re.sub(r'[a-z]$', '', p)  # Remove single letter suffix
    return p


def validate_requirements(
    doc: ToknSchematic,
    required_ics: list[str],
    required_components: list[str]
) -> tuple[float, list[str], list[str]]:
    """Check if required components are present in the generated TOKN.

    Returns: (score, matched, missing)
    """
    if not required_components and not required_ics:
        return 1.0, [], []

    matched = []
    missing = []

    # Extract what's in the generated TOKN
    generated_types = set()  # IC part numbers
    generated_values = set()  # Resistor/cap values

    for comp in doc.components:
        # Component type field often has the IC part number
        if comp.type:
            generated_types.add(normalize_part_number(comp.type))
        if comp.value:
            generated_values.add(normalize_value(comp.value))
            # Also add the type if it looks like a part number
            if not comp.value.replace('.', '').replace('-', '').isdigit():
                generated_types.add(normalize_part_number(comp.value))

    # Check ICs (weighted more heavily)
    for ic in required_ics:
        norm_ic = normalize_part_number(ic)
        # Check if any generated type contains this IC
        found = any(norm_ic in gen or gen in norm_ic for gen in generated_types)
        if found:
            matched.append(ic)
        else:
            missing.append(ic)

    # Check other components (values)
    for comp in required_components:
        if comp in required_ics:
            continue  # Already checked

        norm_comp = normalize_value(comp)
        # Check if value is present
        found = any(norm_comp in gen or gen in norm_comp for gen in generated_values)
        if found:
            matched.append(comp)
        else:
            missing.append(comp)

    # Calculate score
    total = len(required_ics) + len([c for c in required_components if c not in required_ics])
    if total == 0:
        return 1.0, matched, missing

    # ICs are worth more (each IC = 2 points, each passive = 1 point)
    ic_points = len([m for m in matched if m in required_ics]) * 2
    passive_points = len([m for m in matched if m not in required_ics])
    max_points = len(required_ics) * 2 + len([c for c in required_components if c not in required_ics])

    score = (ic_points + passive_points) / max_points if max_points > 0 else 1.0

    return score, matched, missing


def validate_tokn(
    tokn_text: str,
    required_ics: list[str] = None,
    required_components: list[str] = None,
) -> ValidationResult:
    """Full validation of a TOKN document."""
    result = ValidationResult()

    required_ics = required_ics or []
    required_components = required_components or []

    # 1. Syntax validation
    syntax_valid, syntax_errors, doc = validate_syntax(tokn_text)
    result.syntax_valid = syntax_valid
    result.syntax_errors = syntax_errors

    if not syntax_valid or doc is None:
        result.valid = False
        result.requirement_score = 0.0
        return result

    # Collect metrics
    result.component_count = len(doc.components)
    result.net_count = len(doc.nets)
    result.wire_count = len(doc.wires)
    result.pin_section_count = len(doc.pins)

    # 2. Requirement matching (most important)
    req_score, matched, missing = validate_requirements(doc, required_ics, required_components)
    result.requirement_score = req_score
    result.matched_requirements = matched
    result.missing_requirements = missing

    # 3. Semantic validation
    semantic_valid, semantic_errors, semantic_warnings = validate_semantics(doc)
    result.semantic_valid = semantic_valid
    result.semantic_errors = semantic_errors
    result.semantic_warnings = semantic_warnings

    # 4. Completeness check
    result.completeness_warnings = validate_completeness(doc)
    result.complete = len(result.completeness_warnings) == 0

    # Overall validity
    result.valid = result.syntax_valid and result.semantic_valid

    return result


def validate_file(file_path: str, **kwargs) -> ValidationResult:
    """Validate a TOKN file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        tokn_text = f.read()
    return validate_tokn(tokn_text, **kwargs)


def main():
    """CLI for validating TOKN files."""
    import argparse

    parser = argparse.ArgumentParser(description='Validate TOKN files')
    parser.add_argument('files', nargs='+', help='TOKN files to validate')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show all warnings')

    args = parser.parse_args()

    for file_path in args.files:
        print(f"\n{'='*60}")
        print(f"Validating: {file_path}")
        print('='*60)

        result = validate_file(file_path)

        print(f"\nSyntax valid: {result.syntax_valid}")
        print(f"Semantic valid: {result.semantic_valid}")
        print(f"Complete: {result.complete}")
        print(f"Requirement score: {result.requirement_score:.2f}")

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
