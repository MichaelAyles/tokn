"""
Benchmark prompts for TOKN generation.

Generates varied natural language prompts from the training data
for testing model performance before and after fine-tuning.
"""

import json
import random
import sqlite3
from pathlib import Path
from dataclasses import dataclass


@dataclass
class BenchmarkPrompt:
    """A benchmark prompt with expected reference output."""
    prompt: str
    prompt_style: str
    reference_tokn: str
    subcircuit_name: str
    subcircuit_tags: list[str]
    subcircuit_components: str
    file_id: int
    file_name: str
    repo: str
    score: float


# Prompt templates for variety
PROMPT_TEMPLATES = {
    'direct_give': [
        "Give me a TOKN circuit for {description}",
        "Give me a {name}",
        "I need a TOKN schematic for {description}",
    ],
    'direct_create': [
        "Create a TOKN circuit for {description}",
        "Create a {name} in TOKN format",
        "Design a {name}",
    ],
    'component_focused': [
        "Design a circuit using {components}",
        "Create a TOKN schematic with {components}",
        "I need a circuit built around {main_component}",
    ],
    'function_focused': [
        "{use_case}",
        "I need to {use_case_lower}",
        "Design a circuit that can {use_case_lower}",
    ],
    'tag_based': [
        "Give me a {tag} circuit",
        "I need a {tag} design in TOKN",
        "Create a {tag} schematic",
    ],
}


def extract_main_component(components_str: str) -> str:
    """Extract the main IC/component from a components string."""
    # Look for U1, IC1, or first parenthetical part number
    parts = components_str.split(',')
    for part in parts:
        part = part.strip()
        if '(' in part:
            # "ESP32-S3-MINI-1U (U1)" -> "ESP32-S3-MINI-1U"
            return part.split('(')[0].strip()
        if part.startswith('U') or part.startswith('IC'):
            return part
    return parts[0].strip() if parts else "component"


def generate_prompt(subcircuit: dict, style: str = None) -> tuple[str, str]:
    """Generate a natural language prompt from subcircuit data."""
    name = subcircuit.get('name', '')
    description = subcircuit.get('description', '')
    components = subcircuit.get('components', '')
    use_case = subcircuit.get('use_case', '')
    tags = subcircuit.get('tags', [])

    # Pick a random style if not specified
    if style is None:
        style = random.choice(list(PROMPT_TEMPLATES.keys()))

    templates = PROMPT_TEMPLATES[style]
    template = random.choice(templates)

    # Build substitution dict
    main_component = extract_main_component(components)
    use_case_lower = use_case.lower().lstrip('for ').lstrip('to ') if use_case else description.lower()[:100]
    tag = random.choice(tags) if tags else 'electronic'

    # Short description (first sentence or truncated)
    short_desc = description.split('.')[0] if description else name
    if len(short_desc) > 80:
        short_desc = short_desc[:77] + '...'

    prompt = template.format(
        name=name,
        description=short_desc,
        components=components[:100] if len(components) > 100 else components,
        main_component=main_component,
        use_case=use_case[:100] if use_case and len(use_case) > 100 else use_case,
        use_case_lower=use_case_lower[:100],
        tag=tag,
    )

    return prompt, style


def load_benchmark_prompts(
    db_path: str,
    min_score: float = 5.0,
    limit: int = 100,
    seed: int = 42
) -> list[BenchmarkPrompt]:
    """Load benchmark prompts from the database."""
    random.seed(seed)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get high-quality files with TOKN
    cursor.execute('''
        SELECT f.id, f.file_name, f.tokn, f.classification_data, f.classification_score,
               r.full_name
        FROM files f
        JOIN repositories r ON f.repo_id = r.id
        WHERE f.tokn IS NOT NULL
          AND f.classification_score >= ?
        ORDER BY f.classification_score DESC
    ''', (min_score,))

    rows = cursor.fetchall()
    conn.close()

    # Build prompts from subcircuits
    all_prompts = []

    for row in rows:
        file_id, file_name, tokn, classification_json, score, repo = row

        try:
            classification = json.loads(classification_json)
            subcircuits = classification.get('subcircuits', [])
        except:
            continue

        for sc in subcircuits:
            # Generate a varied prompt
            prompt_text, style = generate_prompt(sc)

            benchmark = BenchmarkPrompt(
                prompt=prompt_text,
                prompt_style=style,
                reference_tokn=tokn,
                subcircuit_name=sc.get('name', ''),
                subcircuit_tags=sc.get('tags', []),
                subcircuit_components=sc.get('components', ''),
                file_id=file_id,
                file_name=file_name,
                repo=repo,
                score=score,
            )
            all_prompts.append(benchmark)

    # Shuffle and limit
    random.shuffle(all_prompts)
    return all_prompts[:limit]


def export_prompts_jsonl(prompts: list[BenchmarkPrompt], output_path: str):
    """Export prompts to JSONL for benchmarking."""
    with open(output_path, 'w', encoding='utf-8') as f:
        for p in prompts:
            obj = {
                'prompt': p.prompt,
                'prompt_style': p.prompt_style,
                'reference_tokn': p.reference_tokn,
                'metadata': {
                    'subcircuit_name': p.subcircuit_name,
                    'subcircuit_tags': p.subcircuit_tags,
                    'subcircuit_components': p.subcircuit_components,
                    'file_id': p.file_id,
                    'file_name': p.file_name,
                    'repo': p.repo,
                    'score': p.score,
                }
            }
            f.write(json.dumps(obj, ensure_ascii=False) + '\n')

    print(f"Exported {len(prompts)} prompts to {output_path}")


def main():
    base_dir = Path(__file__).parent.parent
    db_path = base_dir / 'data' / 'kicad_repos.db'
    output_path = base_dir / 'benchmark' / 'test_prompts.jsonl'

    print(f"Loading prompts from {db_path}")
    prompts = load_benchmark_prompts(str(db_path), min_score=5.0, limit=200)

    # Show distribution
    styles = {}
    for p in prompts:
        styles[p.prompt_style] = styles.get(p.prompt_style, 0) + 1

    print(f"\nGenerated {len(prompts)} benchmark prompts")
    print("\nPrompt style distribution:")
    for style, count in sorted(styles.items()):
        print(f"  {style}: {count}")

    print("\nSample prompts:")
    for p in prompts[:5]:
        print(f"  [{p.prompt_style}] {p.prompt}")

    export_prompts_jsonl(prompts, str(output_path))


if __name__ == '__main__':
    main()
