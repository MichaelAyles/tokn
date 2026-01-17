/**
 * Test script to compare TypeScript encoder output with Python encoder output.
 */

import { readFileSync, writeFileSync } from 'fs';
import { convertToTokn } from './toknEncoder';

const testFile = process.argv[2] || '../../examples/mcp2551-can-transceiver/schematic.kicad_sch';

console.log(`Reading: ${testFile}`);
const schematicText = readFileSync(testFile, 'utf-8');

console.log('Converting to TOKN...');
const tokn = convertToTokn(schematicText);

console.log('--- TOKN Output ---');
console.log(tokn);

// Also write to a file for comparison
const outputFile = testFile.replace('.kicad_sch', '.ts.tokn');
writeFileSync(outputFile, tokn);
console.log(`\nWritten to: ${outputFile}`);
