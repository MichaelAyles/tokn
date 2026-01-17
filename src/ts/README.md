# TOKN TypeScript Encoder

TypeScript implementation of the TOKN encoder for converting KiCad schematics to the compact TOKN format.

## Installation

```bash
cd src/ts
bun install  # or npm install
```

## Usage

### Basic Usage

```typescript
import { convertToTokn } from './index';
import { readFileSync } from 'fs';

// Read a KiCad schematic file
const schematicText = readFileSync('circuit.kicad_sch', 'utf-8');

// Convert to TOKN format
const tokn = convertToTokn(schematicText);
console.log(tokn);
```

### Step-by-Step Usage

For more control over the conversion process:

```typescript
import { parseSchematic, analyzeConnectivity, encodeTokn } from './index';
import { readFileSync } from 'fs';

const schematicText = readFileSync('circuit.kicad_sch', 'utf-8');

// 1. Parse the KiCad schematic
const schematic = parseSchematic(schematicText);
console.log(`Title: ${schematic.title}`);
console.log(`Components: ${schematic.components.length}`);

// 2. Analyze connectivity to build netlist
const netlist = analyzeConnectivity(schematic);
console.log(`Nets: ${netlist.nets.length}`);

// 3. Encode to TOKN format
const tokn = encodeTokn(schematic, netlist);
```

### CLI Usage

```bash
bun test.ts path/to/schematic.kicad_sch
```

This outputs the TOKN to stdout and writes to `schematic.ts.tokn`.

## API Reference

### Main Functions

| Function | Description |
|----------|-------------|
| `convertToTokn(text: string): string` | One-step conversion from KiCad schematic text to TOKN |
| `parseSchematic(text: string): Schematic` | Parse KiCad schematic into structured data |
| `analyzeConnectivity(sch: Schematic): Netlist` | Build netlist from schematic |
| `encodeTokn(sch: Schematic, netlist: Netlist): string` | Encode to TOKN format |

### Utility Functions

| Function | Description |
|----------|-------------|
| `normalizeType(libId: string): string` | Convert KiCad lib_id to short type code |
| `normalizeFootprint(footprint: string): string` | Convert footprint to shorthand |

### Types

```typescript
interface Schematic {
  title: string;
  libSymbols: Map<string, LibSymbol>;
  components: Component[];
  wires: Wire[];
  junctions: Junction[];
  labels: Label[];
}

interface Netlist {
  nets: Net[];
  components: Component[];
}

interface Net {
  name: string;
  pins: [string, string, string][]; // [ref, pin_number, pin_name]
  wires: WireSegment[];
  isPower: boolean;
}
```

## Output Format

See [TOKN-v1.md](../../spec/TOKN-v1.md) for the full specification.

Example output:

```
# TOKN v1
title: MCP2551 CAN Transceiver

components[5]{ref,type,value,fp,x,y,w,h,a}:
  C60,C,30pf,,123.19,101.60,0.00,7.62,0
  R1,R,1k,,134.62,101.60,0.00,7.62,0
  U1,MCP2551,MCP2551-I-SN,SOIC-8,149.86,85.09,25.40,20.32,0

pins{U1}[8]:
  1,TXD
  2,VSS
  ...

nets[8]{name,pins}:
  +5V,"C61.1,U1.3"
  GND,"C60.2,C61.2,R1.2,U1.2"
  ...

wires[25]{net,pts}:
  +5V,"128.27 57.15,149.86 57.15"
  ...
```

## Compatibility

Output is identical to the Python implementation (`src/tokn_encoder.py`).
