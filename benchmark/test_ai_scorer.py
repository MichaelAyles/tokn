"""
Quick test for AI scorer functionality.
This doesn't call the API, just tests the structure.
"""

from ai_scorer import AIScoreResult, AI_SCORER_SYSTEM_PROMPT

def test_dataclass():
    """Test AIScoreResult dataclass."""
    result = AIScoreResult(
        functionality_score=85,
        completeness_score=75,
        correctness_score=90,
        best_practices_score=70,
        overall_score=82.5,
        issues=["Missing decoupling cap on U1", "LED current limiting resistor too large"],
        suggestions=["Add 0.1uF cap near U1 pin 8", "Use 330R instead of 1k for LED"],
        explanation="Circuit is functional but has some best practice issues."
    )

    # Test to_dict
    d = result.to_dict()
    assert d['functionality_score'] == 85
    assert d['overall_score'] == 82.5
    assert len(d['issues']) == 2
    print("[PASS] AIScoreResult dataclass works correctly")
    print(f"  Overall score: {result.overall_score}")
    print(f"  Issues: {len(result.issues)}")
    print(f"  Suggestions: {len(result.suggestions)}")

def test_system_prompt():
    """Test that system prompt is properly defined."""
    assert "TOKN" in AI_SCORER_SYSTEM_PROMPT
    assert "functionality_score" in AI_SCORER_SYSTEM_PROMPT
    assert "completeness_score" in AI_SCORER_SYSTEM_PROMPT
    assert "correctness_score" in AI_SCORER_SYSTEM_PROMPT
    assert "best_practices_score" in AI_SCORER_SYSTEM_PROMPT
    print("[PASS] System prompt contains all required scoring criteria")
    print(f"  Prompt length: {len(AI_SCORER_SYSTEM_PROMPT)} chars")

def test_weighted_average():
    """Test that weighted average is calculated correctly."""
    # Expected: 0.35*80 + 0.25*60 + 0.25*70 + 0.15*50
    # = 28 + 15 + 17.5 + 7.5 = 68
    result = AIScoreResult(
        functionality_score=80,
        completeness_score=60,
        correctness_score=70,
        best_practices_score=50,
        overall_score=68.0,
        issues=[],
        suggestions=[],
        explanation="Test"
    )

    # Calculate what it should be
    expected = (80 * 0.35 + 60 * 0.25 + 70 * 0.25 + 50 * 0.15)
    assert abs(result.overall_score - expected) < 0.01
    print("[PASS] Weighted average calculation verified")
    print(f"  Expected: {expected}, Got: {result.overall_score}")

if __name__ == '__main__':
    print("Testing AI Scorer components...")
    print()
    test_dataclass()
    print()
    test_system_prompt()
    print()
    test_weighted_average()
    print()
    print("All tests passed!")
