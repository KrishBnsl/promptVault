"""Tests for the evaluation engine."""


from promptvault.core.evaluation import (
    aggregate_metrics,
    compute_cost,
    compute_exact_match,
    substitute_variables,
)


class TestEvaluationHelpers:
    """Tests for evaluation helper functions."""

    def test_compute_exact_match(self):
        """Test exact match computation."""
        assert compute_exact_match("hello", "hello") == 1.0
        assert compute_exact_match("Hello", "hello") == 1.0
        assert compute_exact_match("hello ", "hello") == 1.0
        assert compute_exact_match("hello", "world") == 0.0

    def test_substitute_variables(self):
        """Test variable substitution in prompts."""
        content = "Hello {name}, welcome to {place}!"
        result = substitute_variables(content, {"name": "Alice", "place": "Wonderland"})
        assert result == "Hello Alice, welcome to Wonderland!"

    def test_substitute_no_variables(self):
        """Test substitution with no variables."""
        content = "Hello world!"
        result = substitute_variables(content, {})
        assert result == "Hello world!"

    def test_compute_cost_with_table(self):
        """Test cost computation using built-in table."""
        token_usage = {"prompt_tokens": 1000, "completion_tokens": 500}
        cost = compute_cost(token_usage, "gpt-4o-mini")
        assert cost > 0

    def test_compute_cost_with_custom_prices(self):
        """Test cost computation with custom prices."""
        token_usage = {"prompt_tokens": 1000, "completion_tokens": 500}
        cost = compute_cost(token_usage, "custom", {"input": 0.001, "output": 0.002})
        assert cost == 0.002

    def test_aggregate_metrics(self):
        """Test metrics aggregation."""
        results = [
            {
                "latency_ms": 100, "cost": 0.01,
                "token_usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
                "scores": {"exact_match": 1.0}, "error": None,
            },
            {
                "latency_ms": 200, "cost": 0.02,
                "token_usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
                "scores": {"exact_match": 0.0}, "error": None,
            },
        ]
        metrics = aggregate_metrics(results)
        assert metrics["avg_latency_ms"] == 150
        assert metrics["avg_cost"] == 0.015
        assert metrics["exact_match_rate"] == 0.5
        assert metrics["total_tokens"]["total_tokens"] == 45

    def test_aggregate_empty_results(self):
        """Test aggregation with empty results."""
        metrics = aggregate_metrics([])
        assert metrics == {}
