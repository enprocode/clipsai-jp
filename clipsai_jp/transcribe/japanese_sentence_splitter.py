"""
日本語専用の文分割モジュール（MeCab使用）

日本語テキストを文に分割します。
タイムスタンプのマッピングを維持するため、元の文字列と完全に一致する
文分割結果を生成します。
"""

import logging
import re
from typing import List, Optional

try:
    import MeCab  # type: ignore

    MECAB_AVAILABLE = True
except ImportError:
    MECAB_AVAILABLE = False
    MeCab = None  # type: ignore

logger = logging.getLogger(__name__)

# 日本語の文末記号: 。！？、改行
# （読点「、」は文の区切りではないため含めない）
SENTENCE_ENDINGS_PATTERN = re.compile(r"(?<=[。！？\n])")


class JapaneseSentenceSplitter:
    """
    日本語専用の文分割クラス

    タイムスタンプのマッピングを維持するため、
    元の文字列と完全に一致する文分割結果を生成します。

    Notes
    -----
    - 文末記号（。！？と改行）を基準に分割します
    - 元の文字列の部分文字列をそのまま返すため、空白文字も保持されます
    - MeCabは初期化時の環境検証に使用します（辞書が正しく設定されているかの確認）
    """

    def __init__(self, mecab_dict_path: Optional[str] = None):
        """
        Parameters
        ----------
        mecab_dict_path: str or None
            MeCab辞書のパス（Noneの場合はデフォルト辞書を使用）

        Raises
        ------
        ImportError
            MeCabがインストールされていない場合
        RuntimeError
            MeCabの初期化に失敗した場合
        """
        if not MECAB_AVAILABLE:
            raise ImportError(
                "MeCab is not installed. Install it with: " "pip install mecab"
            )

        # MeCabの初期化
        mecab_options = ""
        if mecab_dict_path:
            mecab_options = f"-d {mecab_dict_path}"

        try:
            # mecabパッケージの場合、オプションなしで初期化を試みる
            # （設定ファイルは自動検出される）
            if mecab_options:
                self.mecab = MeCab.Tagger(mecab_options)
            else:
                self.mecab = MeCab.Tagger()

            # 初期化テスト
            test_result = self.mecab.parse("テスト")
            if not test_result:
                raise RuntimeError("MeCab initialization test failed")
        except Exception as e:
            logger.error(f"Failed to initialize MeCab: {e}")
            raise RuntimeError(f"MeCab initialization failed: {e}")

    def split_sentences(self, text: str) -> List[str]:
        """
        日本語テキストを文に分割

        元の文字列と完全に一致する文分割結果を返すため、
        文末記号（。！？と改行）を基準に分割します。

        Parameters
        ----------
        text: str
            分割する日本語テキスト

        Returns
        -------
        List[str]
            文のリスト（元の文字列の部分文字列）

        Notes
        -----
        - 元の文字列の部分文字列を返すため、タイムスタンプマッピングが機能します
        - 空白文字も保持されます
        - 空白のみの文は除外されます
        """
        if not text:
            return []

        # 文末記号の直後で分割（元の文字列の部分文字列をそのまま保持する）
        parts = SENTENCE_ENDINGS_PATTERN.split(text)

        # 空・空白のみの文を除去
        # strip()は判定のみに使い、結果には元の部分文字列をそのまま保持
        result = [s for s in parts if s.strip()]

        # 結果が空の場合は、元のテキストをそのまま返す（strip()は使わない）
        if not result:
            return [text] if text.strip() else []

        return result
