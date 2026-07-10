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

# スペースの直後で分割するパターン（フォールバック分割用）
WHITESPACE_SPLIT_PATTERN = re.compile(r"(?<=\s)")

# 1文の最大長。これを超える「文」は句読点が不足しているとみなし、
# セグメント境界（スペース）で再分割する。
# Whisperは日本語で句読点をほとんど出力しないことがあり、その場合
# 文字起こし全体が1文になって下流のTextTiling（クリップ検出）が機能しなくなる。
# Transcriberはセグメント間にスペースを挿入するため、スペースで再分割すれば
# セグメント相当の粒度が確保できる。
MAX_SENTENCE_LENGTH = 200


def split_japanese_sentences(text: str) -> List[str]:
    """
    日本語テキストを文に分割（モジュールレベル関数）

    文末記号（。！？と改行）を基準に分割し、句読点が不足していて
    文が極端に長くなる場合はスペース境界で再分割します。

    Parameters
    ----------
    text: str
        分割する日本語テキスト

    Returns
    -------
    List[str]
        文のリスト（すべて元の文字列の部分文字列）

    Notes
    -----
    - 元の文字列の部分文字列を返すため、タイムスタンプマッピングが機能します
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
        result = [text] if text.strip() else []

    # フォールバック: 句読点がほとんどない文字起こし（Whisperの日本語出力で
    # 発生しやすい）では1文が極端に長くなる。長すぎる文はスペース境界で再分割する
    refined: List[str] = []
    for sentence in result:
        if len(sentence) > MAX_SENTENCE_LENGTH:
            refined.extend(_split_long_sentence(sentence))
        else:
            refined.append(sentence)

    return refined


def _split_long_sentence(sentence: str) -> List[str]:
    """
    長すぎる文をスペース境界で再分割する

    Parameters
    ----------
    sentence: str
        MAX_SENTENCE_LENGTHを超える文

    Returns
    -------
    List[str]
        再分割された文のリスト（すべて元の文字列の部分文字列）

    Notes
    -----
    - スペースの直後で分割するため、部分文字列性が維持されます
    - スペースが存在しない極端に長い断片は固定長で分割します
    """
    parts = [p for p in WHITESPACE_SPLIT_PATTERN.split(sentence) if p.strip()]
    if not parts:
        return [sentence]

    # スペースでも分割しきれない断片は固定長で分割
    # （境界がどこでも部分文字列性・タイムスタンプマッピングは維持される）
    chunks: List[str] = []
    for part in parts:
        if len(part) > MAX_SENTENCE_LENGTH:
            chunks.extend(
                part[i : i + MAX_SENTENCE_LENGTH]
                for i in range(0, len(part), MAX_SENTENCE_LENGTH)
            )
        else:
            chunks.append(part)
    return chunks


class JapaneseSentenceSplitter:
    """
    日本語専用の文分割クラス

    タイムスタンプのマッピングを維持するため、
    元の文字列と完全に一致する文分割結果を生成します。

    Notes
    -----
    - 文末記号（。！？と改行）を基準に分割します
    - 句読点が不足して文が極端に長くなる場合はスペース境界で再分割します
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
        - 分割仕様の詳細は `split_japanese_sentences` を参照
        """
        return split_japanese_sentences(text)
