"""
Gemini APIを使用したクリップ検出の補助機能
公式SDK: google-genai を使用
参考: https://ai.google.dev/gemini-api/docs/quickstart?hl=ja#python
"""
# standard library imports
import json
import logging
import os
import re
from typing import Dict, List, Optional

# 3rd party imports
try:
    from google import genai
except ImportError:
    genai = None

logger = logging.getLogger(__name__)


class GeminiClipFinder:
    """
    Gemini APIを使用してトピックセグメンテーションを補助するクラス

    Gemini API公式SDK (google-genai) を使用
    参考: https://ai.google.dev/gemini-api/docs/quickstart?hl=ja#python
    """

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        """
        Parameters
        ----------
        api_key: str or None
            Google Gemini APIキー。Noneの場合は環境変数 GEMINI_API_KEY から取得
        model: str
            使用するGeminiモデル名
            - "gemini-2.5-flash" (推奨、高速)
            - "gemini-2.5-pro" (高精度、遅い)

        Raises
        ------
        ImportError
            google-genaiパッケージがインストールされていない場合
        ValueError
            APIキーが設定されていない場合
        """
        if genai is None:
            raise ImportError(
                "google-genai package is required for Gemini integration. "
                "Install it with: pip install google-genai"
            )

        if api_key:
            # APIキーが指定された場合は環境変数として設定
            os.environ["GEMINI_API_KEY"] = api_key

        # クライアントは環境変数 GEMINI_API_KEY から自動的に取得
        try:
            self.client = genai.Client()
            self.model_name = model
        except Exception as e:
            raise ValueError(
                f"Failed to initialize Gemini client. "
                f"Make sure GEMINI_API_KEY environment variable is set. Error: {e}"
            )

    def suggest_clip_boundaries(
        self,
        transcription_text: str,
        sentences: List[Dict],
        min_clip_duration: int = 10,
        max_clip_duration: int = 60,
    ) -> List[Dict]:
        """
        Gemini APIを使用してクリップ境界を提案

        Parameters
        ----------
        transcription_text: str
            文字起こしテキスト（最初の4000文字程度を使用）
        sentences: List[Dict]
            センテンス情報のリスト（start_time, end_time, sentence含む）
        min_clip_duration: int
            最小クリップ長（秒）
        max_clip_duration: int
            最大クリップ長（秒）

        Returns
        -------
        List[Dict]
            クリップ境界の提案リスト（start_time, end_time, topic含む）
            エラー時は空リストを返す
        """
        # テキストを適切な長さに切り詰め（Geminiの入力制限を考慮）
        text_preview = transcription_text[:4000]

        # センテンス情報から時間情報を抽出（インデックスも含める）
        sentences_summary = [
            {
                "index": i,
                "start_time": s.get("start_time", 0),
                "end_time": s.get("end_time", 0),
                "sentence": s.get("sentence", "")[:200],  # より長い文を保持
            }
            for i, s in enumerate(sentences[:150])  # より多くの文を考慮
        ]

        prompt = f"""あなたは動画編集の専門家です。以下の動画の文字起こしテキストを分析して、自然なトピック境界を見つけてください。

【文字起こしテキスト】
{text_preview}

【文分割結果（MeCabで日本語最適化済み）】
{json.dumps(sentences_summary, ensure_ascii=False, indent=2)}

【要件】
1. 各クリップは{min_clip_duration}秒以上{max_clip_duration}秒以下であること
2. トピックが明確に変わる箇所を境界として提案
3. 文の途中で分割しないこと（文の境界で分割）
4. 自然な会話の流れを考慮すること
5. 日本語の文構造（主述関係、修飾関係）を考慮すること

【重要な注意点】
- 提供された文分割結果は、MeCabで日本語の文構造を考慮して分割されています
- 各文の境界（start_time, end_time）を尊重してください
- 文の途中で分割すると、不自然な動画分割になります
- 文のインデックス（index）を参考にして、文の境界で分割してください

【出力形式】
JSON配列形式で返答してください:
[
  {{
    "start_time": 開始時間（秒）,
    "end_time": 終了時間（秒）,
    "topic": "トピック名の説明",
    "reason": "この境界を選んだ理由",
    "sentence_indices": [開始文のインデックス, 終了文のインデックス]
  }},
  ...
]

各クリップの start_time と end_time は、提供されたセンテンス情報の start_time と end_time を使用してください。
文のインデックス（index）を参考にして、文の境界で分割してください。
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )

            # レスポンステキストからJSONを抽出
            response_text = response.text
            boundaries = self._parse_json_response(response_text)

            logger.info(f"Gemini suggested {len(boundaries)} clip boundaries")
            return boundaries

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return []

    def _parse_json_response(self, text: str) -> List[Dict]:
        """
        レスポンステキストからJSON配列を抽出・パース

        Parameters
        ----------
        text: str
            Gemini APIのレスポンステキスト

        Returns
        -------
        List[Dict]
            パースされたJSON配列。エラー時は空リスト
        """
        try:
            # コードブロック内のJSONを抽出
            json_match = re.search(r"```(?:json)?\s*(\[[\s\S]*?\])", text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                return json.loads(json_text)

            # JSON配列を直接検索
            json_match = re.search(r"(\[[\s\S]*?\])", text, re.DOTALL)
            if json_match:
                json_text = json_match.group(1)
                return json.loads(json_text)

            # 全体をJSONとして試行
            return json.loads(text)

        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from Gemini response: {e}")
            logger.debug(f"Response text: {text[:500]}")
            return []

