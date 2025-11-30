from __future__ import annotations

import csv
import logging
from difflib import SequenceMatcher
import json
from pathlib import Path
from typing import Dict, List, Literal, Sequence

import google.generativeai as genai

from .config import get_settings

logger = logging.getLogger(__name__)


class GeminiChatService:
    def __init__(self) -> None:
        settings = get_settings()
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.settings = settings
        self.dataset: List[Dict[str, str]] = self._load_dataset("./all_data.json")

    @staticmethod
    def _normalize_row(row: Dict[str, object]) -> Dict[str, str]:
        normalized: Dict[str, str] = {}
        for key, value in row.items():
            safe_key = key or "col"
            normalized[safe_key] = GeminiChatService._stringify(value)
        return normalized

    @staticmethod
    def _stringify(value: object) -> str:
        if value is None:
            return ""
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        return json.dumps(value, ensure_ascii=False)

    def _load_dataset(self, data_path: Path) -> List[Dict[str, str]]:
        if not data_path.exists():
            raise FileNotFoundError(f"Source introuvable: {data_path}")

        suffix = data_path.suffix.lower()
        if suffix == ".json":
            return self._load_json(data_path)
        return self._load_csv(data_path)

    def _load_csv(self, csv_path: Path) -> List[Dict[str, str]]:
        entries: List[Dict[str, str]] = []
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                normalized = {
                    (key or f"col_{idx}"): (value or "").strip()
                    for idx, (key, value) in enumerate(row.items())
                }
                if any(normalized.values()):
                    entries.append(normalized)
        if not entries:
            raise ValueError(f"{csv_path} est vide ou non lisible.")
        return entries

    def _load_json(self, json_path: Path) -> List[Dict[str, str]]:
        with open(json_path, encoding="utf-8") as fp:
            payload = json.load(fp)

        if isinstance(payload, list):
            candidates = payload
        elif isinstance(payload, dict):
            list_value = next(
                (value for value in payload.values() if isinstance(value, list)),
                None,
            )
            candidates = list_value if list_value is not None else [payload]
        else:
            raise ValueError("Le JSON doit contenir une liste ou un objet.")

        rows: List[Dict[str, str]] = []
        for item in candidates:
            if isinstance(item, dict):
                normalized = self._normalize_row(item)
                if any(normalized.values()):
                    rows.append(normalized)
        if not rows:
            raise ValueError(f"Aucune entrée exploitable trouvée dans {json_path}")
        return rows

    @staticmethod
    def _row_to_snippet(row: Dict[str, str]) -> str:
        parts = [f"{key}: {value}" for key, value in row.items() if value]
        return " | ".join(parts[:8]) or "[ligne vide]"

    def _score(self, query: str, row: Dict[str, str]) -> float:
        content = " ".join(row.values())
        return SequenceMatcher(None, query.lower(), content.lower()).ratio()

    def _retrieve_context(self, query: str) -> Sequence[Dict[str, str]]:
        ranked = sorted(
            self.dataset,
            key=lambda row: self._score(query, row),
            reverse=True,
        )
        return ranked[: self.settings.max_context_rows]

    def _build_prompt(
        self,
        question: str,
        language: Literal["fr", "ar"],
        context_rows: Sequence[Dict[str, str]],
    ) -> str:
        context_text = "\n\n".join(self._row_to_snippet(row) for row in context_rows)
        return f"""
Tu es un assistant service client bilingue. 
Contexte: tu disposes d'un fichier de données (CSV ou JSON) décrivant des hôpitaux.
Consignes:
- Utilise exclusivement les informations fournies ci-dessous pour répondre.
- Si les données ne couvrent pas la question, dis-le poliment.
- Répond toujours dans la langue demandée: {language}.
- Propose 3 suggestions de questions FAQ dans la même langue (si possible).

Question utilisateur: {question}

Contexte de données:
{context_text}

Format de sortie (JSON):
{{
  "answer": "réponse dans la langue cible",
  "suggested_questions": [
      "question 1",
      "question 2",
      "question 3"
  ]
}}
"""

    def ask(self, question: str, language: Literal["fr", "ar"]) -> dict:
        context_rows = self._retrieve_context(question)
        prompt = self._build_prompt(question, language, context_rows)

        response = self.model.generate_content(prompt)
        structured = response.text or ""

        # La sortie Gemini peut déjà être JSON ou texte libre.
        # On applique un fallback simple si nécessaire.
        try:
            import json

            payload = json.loads(structured)
            answer = payload.get("answer")
            suggestions = payload.get("suggested_questions") or []
            if isinstance(suggestions, str):
                suggestions = [suggestions]
        except Exception:  # noqa: BLE001
            logger.warning("Réponse non JSON, retour brut.")
            answer = structured.strip()
            suggestions = []

        return {
            "answer": answer or "Je n'ai pas trouvé d'information correspondante.",
            "suggested_questions": suggestions[:3],
            "context_used": [self._row_to_snippet(row) for row in context_rows],
        }

