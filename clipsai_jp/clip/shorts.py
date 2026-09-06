"""
ショート動画向けのクリップ候補生成・スコアリング・重複抑制。

TextTiling はトピック境界の検出に強い一方、YouTube Shorts のような
15〜60秒の自己完結クリップでは「どの区間が単体で面白いか」を選べない。
本モジュールは文の連続区間から候補を作り、フック・完結性・尺で順位付けする。
"""

from __future__ import annotations

import logging
import re
from typing import Dict, List, Optional, Sequence

logger = logging.getLogger(__name__)

# max_clip_duration がこの値以下ならショート向けパイプラインを使う（auto時）
SHORTS_DURATION_THRESHOLD = 90
# ショート向けで max_clips 未指定のときの件数
SHORTS_DEFAULT_MAX_CLIPS = 8

# YouTube Shorts / Reels で視聴維持しやすい尺
SWEET_SPOT_MIN = 25.0
SWEET_SPOT_MAX = 45.0

# 先頭が接続詞・前の文の続きだとショートとして弱い
_CONTINUATION_START = re.compile(
    r"^(うん。|で、|でも、|そして|はい、では|次は|それは|"
    r"これが|これは文法|一方で|このセクションで|"
    r"さて、ここまで|このお話が|そこで)"
)

# 冒頭フックとして加点する表現
_HOOK_KEYWORDS = (
    "なぜ",
    "実は",
    "大事",
    "ポイント",
    "コツ",
    "絶対",
    "まず",
    "結論",
    "秘訣",
    "おすすめ",
    "これだけは",
    "挫折",
    "エラー",
    "プログラミングやってみたい",
)

# 具体的なアドバイス（シェアされやすい）
_ADVICE_KEYWORDS = (
    "1つ目",
    "2つ目",
    "3つ目",
    "ステップ1",
    "ステップ2",
    "ステップ3",
    "コピー",
    "検索",
    "Python",
    "JavaScript",
    "5分",
    "15分",
)

_COMPLETE_ENDINGS = ("。", "！", "？", "?", "です", "ます", "ましょう", "んです")


def is_shorts_mode(clip_style: str, max_clip_duration: float) -> bool:
    """
    ショート向けパイプラインを使うかどうかを返す。

    Parameters
    ----------
    clip_style: str
        ``auto`` / ``shorts`` / ``longform``
    max_clip_duration: float
        クリップ最大長（秒）

    Returns
    -------
    bool
        ショート向け処理を行う場合は True
    """
    if clip_style == "shorts":
        return True
    if clip_style == "longform":
        return False
    return max_clip_duration <= SHORTS_DURATION_THRESHOLD


def generate_sentence_windows(
    sentences_info: Sequence[Dict],
    min_clip_duration: float,
    max_clip_duration: float,
) -> List[Dict]:
    """
    連続する文から、指定尺に収まるクリップ候補を列挙する。

    Parameters
    ----------
    sentences_info: Sequence[dict]
        ``start_time`` / ``end_time`` / ``start_char`` / ``end_char`` を持つ文情報
    min_clip_duration: float
        最小クリップ長（秒）
    max_clip_duration: float
        最大クリップ長（秒）

    Returns
    -------
    list[dict]
        start_time / end_time / start_char / end_char を持つ候補リスト
    """
    n = len(sentences_info)
    windows: List[Dict] = []
    if n == 0:
        return windows

    for i in range(n):
        start_time = sentences_info[i].get("start_time")
        start_char = sentences_info[i].get("start_char")
        if start_time is None or start_char is None:
            continue
        for j in range(i, n):
            end_time = sentences_info[j].get("end_time")
            end_char = sentences_info[j].get("end_char")
            if end_time is None or end_char is None:
                continue
            duration = end_time - start_time
            if duration < min_clip_duration:
                continue
            if duration > max_clip_duration:
                break
            windows.append(
                {
                    "start_time": float(start_time),
                    "end_time": float(end_time),
                    "start_char": int(start_char),
                    "end_char": int(end_char),
                    "source": "window",
                }
            )
    return windows


def clip_iou(start1: float, end1: float, start2: float, end2: float) -> float:
    """
    2つの時間区間の IoU（0.0-1.0）を返す。

    Parameters
    ----------
    start1, end1, start2, end2: float
        各クリップの開始・終了時刻（秒）

    Returns
    -------
    float
        Intersection over Union
    """
    overlap_start = max(start1, start2)
    overlap_end = min(end1, end2)
    inter = max(0.0, overlap_end - overlap_start)
    union = (end1 - start1) + (end2 - start2) - inter
    if union <= 0:
        return 0.0
    return inter / union


def score_clip_text(
    text: str,
    duration: float,
    min_clip_duration: float,
    max_clip_duration: float,
    start_time: float = None,
) -> float:
    """
    ショートとしての良さ（フック・完結性・尺）を数値化する。

    Parameters
    ----------
    text: str
        クリップの文字起こし
    duration: float
        クリップ長（秒）
    min_clip_duration: float
        許容最小長
    max_clip_duration: float
        許容最大長
    start_time: float or None
        クリップ開始時刻。冒頭フックの加点に使う

    Returns
    -------
    float
        高いほどショート向き
    """
    text = (text or "").strip()
    if not text:
        return -10.0

    score = 0.0

    # 尺: 25-45秒をピークに、許容範囲内なら加点
    if SWEET_SPOT_MIN <= duration <= SWEET_SPOT_MAX:
        score += 1.2
    elif min_clip_duration <= duration <= max_clip_duration:
        # スイートスポットからの距離で減衰
        if duration < SWEET_SPOT_MIN:
            dist = SWEET_SPOT_MIN - duration
        else:
            dist = duration - SWEET_SPOT_MAX
        score += max(0.2, 1.0 - dist / 30.0)
    else:
        score -= 1.0

    head = text[:70]
    if "？" in head or "?" in head:
        score += 0.8
    hook_hits = sum(1 for kw in _HOOK_KEYWORDS if kw in head)
    score += min(0.9, 0.35 * hook_hits)

    if _CONTINUATION_START.match(text):
        score -= 1.0

    # 動画冒頭の問いかけフックはショート向き
    if start_time is not None and start_time <= 1.0 and ("？" in head or "?" in head):
        score += 1.0

    stripped = text.rstrip()
    if stripped.endswith(_COMPLETE_ENDINGS):
        score += 0.4
    else:
        score -= 0.2

    advice_hits = sum(1 for kw in _ADVICE_KEYWORDS if kw in text)
    score += min(0.6, 0.2 * advice_hits)

    # 締めの CTA だけだと単体ショートとして弱い
    if "ここまで一緒に" in text or "最高に嬉しい" in text:
        score -= 0.5

    return score


def snap_clip_to_sentences(
    clip: Dict,
    sentences_info: Sequence[Dict],
) -> Dict:
    """
    クリップの開始・終了を最も近い文境界へスナップする。

    Parameters
    ----------
    clip: dict
        start_time / end_time を持つクリップ
    sentences_info: Sequence[dict]
        文情報リスト

    Returns
    -------
    dict
        文境界に合わせたクリップ（元の dict をコピーして更新）
    """
    if not sentences_info:
        return dict(clip)

    snapped = dict(clip)
    start_time = clip["start_time"]
    end_time = clip["end_time"]

    start_sent = min(
        sentences_info,
        key=lambda s: abs((s.get("start_time") or 0.0) - start_time),
    )
    end_sent = min(
        sentences_info,
        key=lambda s: abs((s.get("end_time") or 0.0) - end_time),
    )

    # 開始は「その時刻以前の文頭」、終了は「その時刻以降の文末」を優先
    earlier_or_eq = [
        s for s in sentences_info if (s.get("start_time") or 0.0) <= start_time + 0.05
    ]
    if earlier_or_eq:
        start_sent = earlier_or_eq[-1]

    later_or_eq = [
        s for s in sentences_info if (s.get("end_time") or 0.0) >= end_time - 0.05
    ]
    if later_or_eq:
        end_sent = later_or_eq[0]

    if start_sent.get("start_time", 0) >= end_sent.get("end_time", 0):
        return dict(clip)

    snapped["start_time"] = float(start_sent["start_time"])
    snapped["end_time"] = float(end_sent["end_time"])
    snapped["start_char"] = int(start_sent["start_char"])
    snapped["end_char"] = int(end_sent["end_char"])
    return snapped


def rank_and_suppress(
    clips: List[Dict],
    transcription_text: str,
    min_clip_duration: float,
    max_clip_duration: float,
    overlap_threshold: float = 0.30,
    max_clips: Optional[int] = None,
) -> List[Dict]:
    """
    スコア順に並べ、大きく重なるクリップを落として多様性を確保する。

    Parameters
    ----------
    clips: list[dict]
        候補クリップ
    transcription_text: str
        文字起こし全文（start_char/end_char で切り出す）
    min_clip_duration: float
        最小クリップ長
    max_clip_duration: float
        最大クリップ長
    overlap_threshold: float
        この IoU 以上なら重複とみなして低い方を捨てる
    max_clips: int or None
        返す最大件数。None なら制限しない

    Returns
    -------
    list[dict]
        スコア降順のクリップ（weight/score は含めない）
    """
    scored: List[Dict] = []
    for clip in clips:
        start = clip.get("start_time", 0.0)
        end = clip.get("end_time", 0.0)
        duration = end - start
        if duration < min_clip_duration or duration > max_clip_duration:
            continue
        start_char = max(0, int(clip.get("start_char", 0)))
        end_char = min(len(transcription_text), int(clip.get("end_char", 0)))
        if end_char <= start_char:
            continue
        text = transcription_text[start_char:end_char]
        item = dict(clip)
        item["score"] = score_clip_text(
            text,
            duration,
            min_clip_duration,
            max_clip_duration,
            start_time=start,
        )
        scored.append(item)

    scored.sort(key=lambda c: c["score"], reverse=True)

    kept: List[Dict] = []
    for clip in scored:
        if any(
            clip_iou(
                clip["start_time"],
                clip["end_time"],
                other["start_time"],
                other["end_time"],
            )
            >= overlap_threshold
            for other in kept
        ):
            continue
        kept.append(clip)
        if max_clips is not None and len(kept) >= max_clips:
            break

    logger.info(
        "Shorts ranking kept %s/%s clips (threshold=%.2f)",
        len(kept),
        len(scored),
        overlap_threshold,
    )
    cleaned = []
    for clip in kept:
        cleaned.append({k: v for k, v in clip.items() if k not in ("score", "weight")})
    return cleaned
