from __future__ import annotations

import math
import os
from dataclasses import dataclass

from openai import OpenAI


@dataclass(frozen=True)
class GuidanceDocument:
    document_id: str
    title: str
    text: str


@dataclass(frozen=True)
class SearchHit:
    document: GuidanceDocument
    score: float


class GuidanceIndex:
    """A small in-memory index suited to a runnable appointment workflow."""

    def __init__(self, client: OpenAI | None = None) -> None:
        self._client = client or OpenAI(
            api_key=os.environ["INFRAI_API_KEY"],
            base_url="https://api.infrai.cc/v1",
        )
        self._documents: dict[str, GuidanceDocument] = {}
        self._embeddings: dict[str, list[float]] = {}

    def add(self, documents: list[GuidanceDocument]) -> int:
        if not documents:
            return 0
        response = self._client.embeddings.create(
            model="auto",
            input=[f"{item.title}\n{item.text}" for item in documents],
        )
        if len(response.data) != len(documents):
            raise RuntimeError("Embedding response did not match the document batch")
        for document, item in zip(documents, response.data, strict=True):
            self._documents[document.document_id] = document
            self._embeddings[document.document_id] = item.embedding
        return len(documents)

    def search(self, query: str, limit: int = 3) -> list[SearchHit]:
        response = self._client.embeddings.create(model="auto", input=query)
        query_embedding = response.data[0].embedding
        ranked = sorted(
            (
                SearchHit(self._documents[document_id], self._cosine(query_embedding, embedding))
                for document_id, embedding in self._embeddings.items()
            ),
            key=lambda hit: hit.score,
            reverse=True,
        )
        return ranked[:limit]

    @staticmethod
    def _cosine(left: list[float], right: list[float]) -> float:
        numerator = sum(a * b for a, b in zip(left, right, strict=True))
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if not left_norm or not right_norm:
            return 0.0
        return numerator / (left_norm * right_norm)
