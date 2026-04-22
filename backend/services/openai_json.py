import json
from logging import getLogger

logger = getLogger(__name__)


class OpenAIJSONClient:
    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.model = model
        self.client = OpenAI(api_key=api_key)
        logger.info("OpenAIJSONClient initialized model=%s", self.model)

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.choices[0].message.content or "{}"
        return self._parse_json_content(content)

    def _parse_json_content(self, content: str) -> dict:
        normalized = content.strip()
        if normalized.startswith("```"):
            normalized = normalized.strip("`")
            if normalized.startswith("json"):
                normalized = normalized[4:].strip()
        parsed = json.loads(normalized)
        if not isinstance(parsed, dict):
            raise ValueError("Expected JSON object from OpenAI response")
        return parsed
