import os
from dataclasses import dataclass

from backend.services.openai_json import OpenAIJSONClient
from backend.services.policy_evaluation.evaluators import OpenAIPolicyEvaluator


@dataclass(frozen=True)
class PolicyEvaluationSettings:
    openai_api_key: str | None
    model: str

    @classmethod
    def from_env(cls) -> "PolicyEvaluationSettings":
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("OPENAI_POLICY_EVALUATION_MODEL", "gpt-4o-mini"),
        )


def build_policy_evaluator() -> OpenAIPolicyEvaluator:
    settings = PolicyEvaluationSettings.from_env()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is required for policy evaluation")
    client = OpenAIJSONClient(api_key=settings.openai_api_key, model=settings.model)
    return OpenAIPolicyEvaluator(client=client)
