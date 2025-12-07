"""
Generate JSONL training data from scraped KiCad schematics.

Pairs TOKN-encoded schematics with their classification descriptions,
scores, and rankings for LLM post-training.
"""

import sys
import os
import json
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from tokn_encoder import convert_file
from kicad_sch import parse_schematic
from connectivity import analyze_connectivity
from tokn_encoder import encode_tokn


@dataclass
class TrainingRecord:
    """A single training record pairing description with TOKN."""
    file_id: int
    file_name: str
    file_path: str
    repo_full_name: str
    repo_url: str
    license: str
    owner: str
    stars: int
    classification_score: float
    subcircuit_name: str
    subcircuit_description: str
    subcircuit_components: str
    subcircuit_use_case: str
    subcircuit_notes: str
    subcircuit_tags: list[str]
    subcircuit_rank: int  # 1-based rank within file
    total_subcircuits: int
    tokn: str


def encode_file_to_tokn(file_path: str) -> Optional[str]:
    """Encode a KiCad schematic file to TOKN format."""
    try:
        sch = parse_schematic(file_path)
        netlist = analyze_connectivity(sch)
        tokn = encode_tokn(sch, netlist)
        return tokn
    except Exception as e:
        print(f"  Error encoding {file_path}: {e}")
        return None


def generate_training_records(db_path: str, base_dir: str) -> list[TrainingRecord]:
    """Generate training records from the database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all files with classifications
    cursor.execute('''
        SELECT f.id, f.file_name, f.file_path, f.local_path, f.classification_data,
               f.classification_score, f.component_count,
               r.full_name, r.url, r.license, r.owner, r.stars
        FROM files f
        JOIN repositories r ON f.repo_id = r.id
        WHERE f.classification_data IS NOT NULL
          AND f.classification_score > 0
          AND f.local_path IS NOT NULL
        ORDER BY f.classification_score DESC
    ''')

    rows = cursor.fetchall()
    records = []

    total = len(rows)
    success = 0
    failed = 0
    no_subcircuits = 0

    for i, row in enumerate(rows):
        file_id, file_name, file_path, local_path, classification_json, \
        score, component_count, repo_full_name, repo_url, license_name, owner, stars = row

        if (i + 1) % 100 == 0:
            print(f"Processing {i + 1}/{total}...")

        # Parse classification
        try:
            classification = json.loads(classification_json)
            subcircuits = classification.get('subcircuits', [])
        except:
            continue

        if not subcircuits:
            no_subcircuits += 1
            continue

        # local_path is relative to project root (e.g., "data\repos\skot\bitaxe\fan.kicad_sch")
        full_local_path = os.path.join(base_dir, local_path) if local_path else None

        if not full_local_path or not os.path.exists(full_local_path):
            failed += 1
            continue

        # Encode to TOKN
        tokn = encode_file_to_tokn(full_local_path)
        if not tokn:
            failed += 1
            continue

        success += 1

        # Create a record for each subcircuit in the file
        for rank, sc in enumerate(subcircuits, 1):
            record = TrainingRecord(
                file_id=file_id,
                file_name=file_name,
                file_path=file_path,
                repo_full_name=repo_full_name,
                repo_url=repo_url,
                license=license_name or 'Unknown',
                owner=owner,
                stars=stars,
                classification_score=score,
                subcircuit_name=sc.get('name', ''),
                subcircuit_description=sc.get('description', ''),
                subcircuit_components=sc.get('components', ''),
                subcircuit_use_case=sc.get('useCase', ''),
                subcircuit_notes=sc.get('notes', ''),
                subcircuit_tags=sc.get('tags', []),
                subcircuit_rank=rank,
                total_subcircuits=len(subcircuits),
                tokn=tokn
            )
            records.append(record)

    print(f"\nSummary:")
    print(f"  Total files: {total}")
    print(f"  Successfully encoded: {success}")
    print(f"  Failed to encode: {failed}")
    print(f"  No subcircuits: {no_subcircuits}")
    print(f"  Total training records: {len(records)}")

    conn.close()
    return records


def records_to_jsonl(records: list[TrainingRecord], output_path: str):
    """Write training records to JSONL format."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            obj = {
                'file': {
                    'id': record.file_id,
                    'name': record.file_name,
                    'path': record.file_path,
                },
                'attribution': {
                    'repo': record.repo_full_name,
                    'url': record.repo_url,
                    'license': record.license,
                    'owner': record.owner,
                    'stars': record.stars,
                },
                'classification': {
                    'score': record.classification_score,
                    'rank': record.subcircuit_rank,
                    'total': record.total_subcircuits,
                    'name': record.subcircuit_name,
                    'description': record.subcircuit_description,
                    'components': record.subcircuit_components,
                    'use_case': record.subcircuit_use_case,
                    'notes': record.subcircuit_notes,
                    'tags': record.subcircuit_tags,
                },
                'tokn': record.tokn,
            }
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"Written {len(records)} records to {output_path}")


def records_to_conversation_jsonl(records: list[TrainingRecord], output_path: str):
    """Write training records as conversation pairs for fine-tuning."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for record in records:
            # Build the user prompt from the classification
            user_prompt = f"Design a {record.subcircuit_name}"
            if record.subcircuit_use_case:
                user_prompt += f" for {record.subcircuit_use_case.lower()}"

            # Build assistant response with attribution comment
            assistant_response = f"# TOKN v1\n# Source: {record.repo_full_name} ({record.license})\n"
            assistant_response += f"# Score: {record.classification_score}/10, Subcircuit {record.subcircuit_rank}/{record.total_subcircuits}\n\n"
            assistant_response += record.tokn

            obj = {
                'messages': [
                    {
                        'role': 'system',
                        'content': 'You are an expert electronics design assistant. Generate TOKN format schematics based on user requirements. TOKN is a compact notation for KiCad schematics.'
                    },
                    {
                        'role': 'user',
                        'content': user_prompt
                    },
                    {
                        'role': 'assistant',
                        'content': assistant_response
                    }
                ],
                'metadata': {
                    'file_id': record.file_id,
                    'repo': record.repo_full_name,
                    'license': record.license,
                    'score': record.classification_score,
                    'tags': record.subcircuit_tags,
                }
            }
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"Written {len(records)} conversation records to {output_path}")


def compute_statistics(records: list[TrainingRecord]) -> dict:
    """Compute statistics about the training data."""
    stats = {
        'total_records': len(records),
        'unique_files': len(set(r.file_id for r in records)),
        'unique_repos': len(set(r.repo_full_name for r in records)),
        'score_distribution': {},
        'license_distribution': {},
        'tag_distribution': {},
        'avg_score': 0,
        'avg_subcircuits_per_file': 0,
    }

    scores = [r.classification_score for r in records]
    stats['avg_score'] = sum(scores) / len(scores) if scores else 0

    # Score buckets
    for r in records:
        bucket = int(r.classification_score)
        stats['score_distribution'][bucket] = stats['score_distribution'].get(bucket, 0) + 1

    # License distribution
    for r in records:
        lic = r.license
        stats['license_distribution'][lic] = stats['license_distribution'].get(lic, 0) + 1

    # Tag distribution
    for r in records:
        for tag in r.subcircuit_tags:
            stats['tag_distribution'][tag] = stats['tag_distribution'].get(tag, 0) + 1

    # Sort distributions
    stats['license_distribution'] = dict(sorted(
        stats['license_distribution'].items(), key=lambda x: -x[1]
    )[:20])
    stats['tag_distribution'] = dict(sorted(
        stats['tag_distribution'].items(), key=lambda x: -x[1]
    )[:50])

    # Avg subcircuits per file
    file_subcircuit_counts = {}
    for r in records:
        file_subcircuit_counts[r.file_id] = r.total_subcircuits
    stats['avg_subcircuits_per_file'] = sum(file_subcircuit_counts.values()) / len(file_subcircuit_counts) if file_subcircuit_counts else 0

    return stats


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'kicad_repos.db'
    output_dir = base_dir / 'data' / 'training'

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    print(f"Database: {db_path}")
    print(f"Base directory: {base_dir}")
    print(f"Output directory: {output_dir}")
    print()

    # Generate records
    print("Generating training records...")
    records = generate_training_records(str(db_path), str(base_dir))

    if not records:
        print("No records generated!")
        return

    # Compute statistics
    print("\nComputing statistics...")
    stats = compute_statistics(records)

    # Write outputs
    print("\nWriting outputs...")
    records_to_jsonl(records, str(output_dir / 'training_data.jsonl'))
    records_to_conversation_jsonl(records, str(output_dir / 'training_conversations.jsonl'))

    # Write statistics
    with open(output_dir / 'training_stats.json', 'w') as f:
        json.dump(stats, f, indent=2)

    # Print summary
    print("\n" + "="*60)
    print("TRAINING DATA GENERATION COMPLETE")
    print("="*60)
    print(f"\nTotal training records: {stats['total_records']}")
    print(f"Unique files: {stats['unique_files']}")
    print(f"Unique repos: {stats['unique_repos']}")
    print(f"Average score: {stats['avg_score']:.2f}")
    print(f"Average subcircuits per file: {stats['avg_subcircuits_per_file']:.1f}")

    print("\nScore distribution:")
    for score, count in sorted(stats['score_distribution'].items()):
        print(f"  {score}: {count}")

    print("\nTop 10 licenses:")
    for lic, count in list(stats['license_distribution'].items())[:10]:
        print(f"  {count:5} - {lic}")

    print("\nTop 20 tags:")
    for tag, count in list(stats['tag_distribution'].items())[:20]:
        print(f"  {count:5} - {tag}")


if __name__ == '__main__':
    main()
