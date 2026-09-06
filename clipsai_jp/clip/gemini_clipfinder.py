"""
Gemini APIを使用したクリップ検出の補助機能（非推奨）。

.. deprecated::
    新規コードでは ``clipsai_jp.clip.llm_clipfinder.LlmClipFinder`` を使い、
    ``provider="openai"`` / ``"anthropic"`` / ``"gemini"`` /
    ``"openai_compatible"`` を指定してください。
"""

# standard library imports
import warnings
from typing import Optional

# current package imports
from .llm_clipfinder import (  # noqa: F401
    CHUNK_OVERLAP,
    SENTENCE_CHAR_LIMIT,
    SENTENCES_PER_CHUNK,
    TEXT_PREVIEW_CHAR_LIMIT,
    LlmClipFinder,
)


class GeminiClipFinder(LlmClipFinder):
    """
    Gemini 専用の薄い互換ラッパー。

    Parameters
    ----------
    api_key: str or None
        Google Gemini APIキー。Noneの場合は環境変数 GEMINI_API_KEY から取得
    model: str
        使用するGeminiモデル名
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
    ) -> None:
        warnings.warn(
            "GeminiClipFinder is deprecated. Use LlmClipFinder("
            "provider='gemini', ...) or ClipFinder(use_llm=True, "
            "llm_provider='openai') to use other models.",
            DeprecationWarning,
            stacklevel=2,
        )
        super().__init__(provider="gemini", api_key=api_key, model=model)
