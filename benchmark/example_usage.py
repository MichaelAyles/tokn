"""
Example usage of the AI scorer for TOKN circuits.
Demonstrates both single circuit and batch scoring.
"""

from ai_scorer import ai_score_circuit, AIScoreResult

# Example 1: Score a single circuit programmatically
def example_single_score():
    """Score a single TOKN circuit."""

    prompt = "Design a 555 timer astable multivibrator LED blinker circuit"

    tokn = """# TOKN v1
title: 555 Timer LED Blinker

components[6]{ref,type,value,fp,x,y,w,h,a}:
  U1,NE555,NE555,DIP-8,100,100,20,15,0
  R1,R,10k,0805,80,90,7.62,0,90
  R2,R,10k,0805,80,110,7.62,0,90
  R3,R,330,0805,130,95,7.62,0,90
  C1,CP,10u,0805,90,120,0,7.62,0
  D1,LED,LED,LED-5MM,145,95,7.62,0,180

pins{U1}[8]:
  1,GND
  2,TRIG
  3,OUT
  4,RESET
  5,CTRL
  6,THRS
  7,DISCH
  8,VCC

nets[6]{name,pins}:
  +5V,"R1.1,U1.4,U1.8"
  GND,"C1.2,U1.1"
  OUT,"D1.1,R3.2,U1.3"
  N1,"C1.1,R2.2,U1.2,U1.6"
  N2,"R1.2,R2.1,U1.7"
  N3,"D1.2,R3.1"

wires[8]{net,pts}:
  +5V,"80 85,95 85"
  +5V,"95 85,100 85,100 92"
  GND,"90 127,100 127,100 108"
  OUT,"112 100,130 100,130 95"
  N1,"90 115,95 115,95 102"
  N2,"80 95,95 95,95 99"
  N3,"145 95,135 95"
  GND,"130 100,130 127,90 127"
"""

    print("Scoring single circuit...")
    print("=" * 60)

    # Note: This will fail without a valid API key
    # For demonstration, we'll show the expected structure
    try:
        result = ai_score_circuit(prompt, tokn)
        print_score_result(result)
    except Exception as e:
        print(f"Error (expected if no API key): {e}")
        print("\nExpected result structure:")
        example_result = AIScoreResult(
            functionality_score=85,
            completeness_score=60,
            correctness_score=80,
            best_practices_score=70,
            overall_score=76.75,
            issues=[
                "Missing decoupling capacitor on U1 VCC pin",
                "Control pin (CTRL) should have 0.01uF cap to GND",
                "Missing bulk capacitor on power supply"
            ],
            suggestions=[
                "Add 0.1uF ceramic cap between U1 pin 8 and pin 1",
                "Add 0.01uF cap from U1 pin 5 to GND for noise immunity",
                "Add 100uF electrolytic cap at power entry for stability"
            ],
            explanation="Functional 555 astable circuit but missing standard decoupling and filtering capacitors."
        )
        print_score_result(example_result)


def print_score_result(result: AIScoreResult):
    """Pretty print an AI score result."""
    print(f"\nOverall Score: {result.overall_score:.1f}/100")
    print(f"\nDetailed Scores:")
    print(f"  Functionality:  {result.functionality_score:3d}/100")
    print(f"  Completeness:   {result.completeness_score:3d}/100")
    print(f"  Correctness:    {result.correctness_score:3d}/100")
    print(f"  Best Practices: {result.best_practices_score:3d}/100")

    print(f"\nExplanation:")
    print(f"  {result.explanation}")

    if result.issues:
        print(f"\nIssues Found ({len(result.issues)}):")
        for i, issue in enumerate(result.issues, 1):
            print(f"  {i}. {issue}")

    if result.suggestions:
        print(f"\nSuggestions ({len(result.suggestions)}):")
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"  {i}. {suggestion}")


# Example 2: Analyze score distribution
def example_score_analysis():
    """Analyze AI scores from a batch run."""
    import json
    from pathlib import Path

    # This assumes you've already run batch scoring
    scores_file = Path(__file__).parent / "ai_scores_detailed.jsonl"

    if not scores_file.exists():
        print(f"\nScore file not found: {scores_file}")
        print("Run batch scoring first:")
        print("  python benchmark/ai_scorer.py --input results_results.jsonl --output ai_scores.json")
        return

    print("\nAnalyzing AI scores...")
    print("=" * 60)

    with open(scores_file) as f:
        results = [json.loads(line) for line in f]

    # Calculate statistics
    scores = [r['ai_score'] for r in results if r['ai_score']['overall_score'] > 0]

    print(f"Total circuits scored: {len(scores)}")
    print(f"\nAverage Scores:")
    print(f"  Overall:        {sum(s['overall_score'] for s in scores) / len(scores):.1f}/100")
    print(f"  Functionality:  {sum(s['functionality_score'] for s in scores) / len(scores):.1f}/100")
    print(f"  Completeness:   {sum(s['completeness_score'] for s in scores) / len(scores):.1f}/100")
    print(f"  Correctness:    {sum(s['correctness_score'] for s in scores) / len(scores):.1f}/100")
    print(f"  Best Practices: {sum(s['best_practices_score'] for s in scores) / len(scores):.1f}/100")

    # Find best and worst
    best = max(results, key=lambda r: r['ai_score']['overall_score'])
    worst = min(results, key=lambda r: r['ai_score']['overall_score'])

    print(f"\nBest Circuit ({best['ai_score']['overall_score']:.1f}/100):")
    print(f"  Prompt: {best['prompt'][:60]}...")
    print(f"  {best['ai_score']['explanation'][:100]}...")

    print(f"\nWorst Circuit ({worst['ai_score']['overall_score']:.1f}/100):")
    print(f"  Prompt: {worst['prompt'][:60]}...")
    print(f"  {worst['ai_score']['explanation'][:100]}...")

    # Common issues
    all_issues = []
    for r in results:
        all_issues.extend(r['ai_score']['issues'])

    print(f"\nTotal issues found: {len(all_issues)}")
    print(f"Most common issue types:")
    issue_keywords = {}
    for issue in all_issues:
        if 'decoupling' in issue.lower():
            issue_keywords['Decoupling capacitors'] = issue_keywords.get('Decoupling capacitors', 0) + 1
        elif 'power' in issue.lower() or 'vcc' in issue.lower() or 'gnd' in issue.lower():
            issue_keywords['Power connections'] = issue_keywords.get('Power connections', 0) + 1
        elif 'resistor' in issue.lower():
            issue_keywords['Resistor values'] = issue_keywords.get('Resistor values', 0) + 1
        elif 'pin' in issue.lower():
            issue_keywords['Pin connections'] = issue_keywords.get('Pin connections', 0) + 1

    for keyword, count in sorted(issue_keywords.items(), key=lambda x: -x[1])[:5]:
        print(f"  {keyword}: {count}")


if __name__ == '__main__':
    print("AI Scorer Example Usage")
    print("=" * 60)

    # Example 1: Score single circuit
    example_single_score()

    # Example 2: Analyze batch results
    example_score_analysis()
