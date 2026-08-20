"""Evaluation engine for running prompt evaluations against datasets."""

from sqlalchemy.orm import Session

from promptvault.config import DEFAULT_MODEL_CONFIG
from promptvault.core.providers import get_provider
from promptvault.db import crud

# Built-in cost table (per 1K tokens) - can be overridden by model_config
# Prices as of August 2026
COST_TABLE = {
    # OpenAI
    "gpt-4o": {"input": 0.0025, "output": 0.01},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-4.1": {"input": 0.002, "output": 0.008},
    "gpt-4.1-mini": {"input": 0.0004, "output": 0.0016},
    "gpt-4.1-nano": {"input": 0.0001, "output": 0.0004},
    "gpt-5": {"input": 0.00125, "output": 0.01},
    "gpt-5-mini": {"input": 0.00025, "output": 0.002},
    "gpt-5-nano": {"input": 0.00005, "output": 0.0004},
    "o3": {"input": 0.002, "output": 0.008},
    "o3-mini": {"input": 0.0011, "output": 0.0044},
    "o4-mini": {"input": 0.0011, "output": 0.0044},
    # Anthropic
    "claude-haiku-4-5": {"input": 0.001, "output": 0.005},
    "claude-sonnet-5": {"input": 0.002, "output": 0.01},
    "claude-opus-5": {"input": 0.005, "output": 0.025},
    "claude-opus-4-7": {"input": 0.005, "output": 0.025},
    # Google Gemini
    "gemini-3.7-flash": {"input": 0.00075, "output": 0.00375},
    "gemini-3.6-flash": {"input": 0.00075, "output": 0.00375},
    "gemini-3.5-flash": {"input": 0.0015, "output": 0.009},
    "gemini-3.1-pro": {"input": 0.002, "output": 0.012},
    "gemini-3-flash": {"input": 0.0005, "output": 0.003},
    "gemini-2.5-flash": {"input": 0.00015, "output": 0.0006},
    "gemini-2.5-flash-lite": {"input": 0.0001, "output": 0.0004},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
}


def compute_cost(
    token_usage: dict, model: str, cost_per_1k: dict | None = None
) -> float:
    """Compute cost based on token usage."""
    if cost_per_1k:
        input_cost = (token_usage.get("prompt_tokens", 0) / 1000) * cost_per_1k.get(
            "input", 0
        )
        output_cost = (
            token_usage.get("completion_tokens", 0) / 1000
        ) * cost_per_1k.get("output", 0)
        return round(input_cost + output_cost, 6)

    prices = COST_TABLE.get(model, {"input": 0, "output": 0})
    input_cost = (token_usage.get("prompt_tokens", 0) / 1000) * prices["input"]
    output_cost = (token_usage.get("completion_tokens", 0) / 1000) * prices["output"]
    return round(input_cost + output_cost, 6)


def compute_exact_match(actual: str, expected: str) -> float:
    """Compute exact match score (case-insensitive, stripped)."""
    if actual.strip().lower() == expected.strip().lower():
        return 1.0
    return 0.0


def substitute_variables(content: str, variables: dict) -> str:
    """Substitute variables in prompt content."""
    result = content
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def aggregate_metrics(results: list[dict]) -> dict:
    """Aggregate metrics across all evaluation results."""
    if not results:
        return {}

    successful_results = [r for r in results if r.get("error") is None]
    total = len(results)

    avg_latency = 0
    avg_cost = 0
    total_tokens = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    exact_matches = 0

    for result in successful_results:
        avg_latency += result.get("latency_ms", 0) or 0
        avg_cost += result.get("cost", 0) or 0
        usage = result.get("token_usage", {})
        total_tokens["prompt_tokens"] += usage.get("prompt_tokens", 0)
        total_tokens["completion_tokens"] += usage.get("completion_tokens", 0)
        total_tokens["total_tokens"] += usage.get("total_tokens", 0)
        scores = result.get("scores", {})
        exact_matches += scores.get("exact_match", 0)

    count = len(successful_results) or 1
    return {
        "avg_latency_ms": round(avg_latency / count),
        "avg_cost": round(avg_cost / count, 6),
        "total_tokens": total_tokens,
        "exact_match_rate": round(exact_matches / total, 2) if total > 0 else 0,
        "total_items": total,
        "successful_items": len(successful_results),
        "failed_items": total - len(successful_results),
    }


class EvaluationEngine:
    """Handles evaluation of prompt versions against datasets."""

    def __init__(self, db: Session):
        self.db = db

    def run_evaluation(
        self,
        prompt_name: str,
        dataset_name: str,
        version: int | None = None,
        model_config: dict | None = None,
    ) -> str:
        """Run an evaluation and return the evaluation ID."""

        prompt = crud.get_prompt(self.db, prompt_name)
        if not prompt:
            raise ValueError(f"Prompt '{prompt_name}' not found")

        if version is not None:
            prompt_version = crud.get_prompt_version(self.db, prompt.id, version)
        else:
            prompt_version = crud.get_latest_version(self.db, prompt.id)

        if not prompt_version:
            raise ValueError("Prompt version not found")

        dataset = crud.get_dataset(self.db, dataset_name)
        if not dataset:
            raise ValueError(f"Dataset '{dataset_name}' not found")

        effective_config = {**DEFAULT_MODEL_CONFIG, **(model_config or {})}
        provider_name = effective_config.get("provider", "openai")

        evaluation = crud.create_evaluation(
            self.db,
            prompt_version_id=prompt_version.id,
            dataset_id=dataset.id,
            model_config=effective_config,
        )

        crud.update_evaluation_status(self.db, evaluation.id, "running")

        try:
            provider = get_provider(provider_name)
            results = []

            for item in dataset.items:
                filled_prompt = substitute_variables(
                    prompt_version.content, item.input
                )

                try:
                    response = provider.generate(
                        prompt=filled_prompt,
                        model=effective_config.get("model", "gpt-4.1-mini"),
                        temperature=effective_config.get("temperature", 0.0),
                        max_tokens=effective_config.get("max_tokens", 512),
                    )

                    actual_output = response["content"]
                    scores = {}
                    if item.expected_output:
                        scores["exact_match"] = compute_exact_match(
                            actual_output, item.expected_output
                        )

                    cost = compute_cost(
                        response["token_usage"],
                        effective_config.get("model", "gpt-4o-mini"),
                        effective_config.get("cost_per_1k_tokens"),
                    )

                    result_data = {
                        "dataset_item_id": item.id,
                        "input": item.input,
                        "expected_output": item.expected_output,
                        "actual_output": actual_output,
                        "latency_ms": response["latency_ms"],
                        "token_usage": response["token_usage"],
                        "cost": cost,
                        "scores": scores,
                        "error": None,
                    }
                    results.append(result_data)

                except Exception as e:
                    result_data = {
                        "dataset_item_id": item.id,
                        "input": item.input,
                        "expected_output": item.expected_output,
                        "actual_output": None,
                        "latency_ms": None,
                        "token_usage": {},
                        "cost": None,
                        "scores": {},
                        "error": str(e),
                    }
                    results.append(result_data)

            for result_data in results:
                crud.create_evaluation_result(
                    self.db,
                    evaluation_id=evaluation.id,
                    dataset_item_id=result_data["dataset_item_id"],
                    input_data=result_data["input"],
                    expected_output=result_data["expected_output"],
                    actual_output=result_data["actual_output"],
                    latency_ms=result_data["latency_ms"],
                    token_usage=result_data["token_usage"],
                    cost=result_data["cost"],
                    scores=result_data["scores"],
                    error=result_data["error"],
                )

            metrics = aggregate_metrics(results)
            crud.update_evaluation_status(
                self.db, evaluation.id, "completed", metrics
            )

            return evaluation.id

        except Exception as e:
            crud.update_evaluation_status(self.db, evaluation.id, "failed")
            raise e

    def get_report(self, evaluation_id: str) -> dict | None:
        """Get a full evaluation report."""
        evaluation = crud.get_evaluation(self.db, evaluation_id)
        if not evaluation:
            return None

        prompt_version_id = evaluation.prompt_version_id
        if ":" in prompt_version_id:
            prompt_version_id = prompt_version_id.split(":")[0]

        results = crud.get_evaluation_results(self.db, evaluation_id)

        return {
            "evaluation_id": evaluation.id,
            "status": evaluation.status,
            "model_config": evaluation.model_config,
            "metrics": evaluation.metrics,
            "created_at": evaluation.created_at.isoformat()
            if evaluation.created_at
            else None,
            "completed_at": evaluation.completed_at.isoformat()
            if evaluation.completed_at
            else None,
            "results": [
                {
                    "id": r.id,
                    "input": r.input,
                    "expected_output": r.expected_output,
                    "actual_output": r.actual_output,
                    "latency_ms": r.latency_ms,
                    "token_usage": r.token_usage,
                    "cost": r.cost,
                    "scores": r.scores,
                    "error": r.error,
                }
                for r in results
            ],
        }

    def get_status(self, evaluation_id: str) -> dict | None:
        """Get evaluation status."""
        evaluation = crud.get_evaluation(self.db, evaluation_id)
        if not evaluation:
            return None
        return {
            "evaluation_id": evaluation.id,
            "status": evaluation.status,
            "metrics": evaluation.metrics,
        }

    def compare(
        self, evaluation_id_a: str, evaluation_id_b: str
    ) -> dict | None:
        """Compare two evaluation runs."""
        report_a = self.get_report(evaluation_id_a)
        report_b = self.get_report(evaluation_id_b)

        if not report_a or not report_b:
            return None

        return {
            "evaluation_a": report_a,
            "evaluation_b": report_b,
            "metrics_comparison": {
                key: {
                    "a": report_a["metrics"].get(key),
                    "b": report_b["metrics"].get(key),
                }
                for key in set(list(report_a["metrics"].keys()) + list(report_b["metrics"].keys()))
            },
        }
