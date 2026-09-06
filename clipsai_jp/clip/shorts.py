"""
ショート動画向けのクリップ候補生成・スコアリング・重複抑制。

TextTiling はトピック境界の検出に強い一方、YouTube Shorts のような
15〜60秒の自己完結クリップでは「どの区間が単体で面白いか」を選べない。
本モジュールは文の連続区間から候補を作り、フック・完結性・尺で順位付けする。
"""

from __future__ import annotations

import logging
import math
import re
from typing import Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger(__name__)

# max_clip_duration がこの値以下ならショート向けパイプラインを使う（auto時）
SHORTS_DURATION_THRESHOLD = 90
# ショート向けで max_clips 未指定のときの件数
SHORTS_DEFAULT_MAX_CLIPS = 8

# YouTube Shorts / Reels で視聴維持しやすい尺
SWEET_SPOT_MIN = 25.0
SWEET_SPOT_MAX = 45.0
SWEET_SPOT_TARGET = (SWEET_SPOT_MIN + SWEET_SPOT_MAX) / 2.0
# 文連続ウィンドウの上限。全組み合わせを実体化すると長尺で数百万件になる
MAX_GENERATED_WINDOWS = 512
MAX_OPENING_WINDOWS = 64

# 冒頭フックを優先確保する開始時刻の上限（秒）
OPENING_PRIORITY_START = 15.0

# 先頭が接続詞・前の文の続きだとショートとして弱い
# 「これが」「それは」はフック（「これがポイント」等）にもなるので含めない
_CONTINUATION_START = re.compile(
    r"^(うん。|で、|でも、|そして|はい、では|次は|"
    r"一方で|このセクションで|これは文法|"
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
    "やってみたい",
    "始めれば",
    "知っておきたい",
)

# 番号付きの具体アドバイス。汎用語（言語名など）は加点しすぎない
_ADVICE_KEYWORDS = (
    "1つ目",
    "2つ目",
    "3つ目",
    "ステップ1",
    "ステップ2",
    "ステップ3",
)

_COMPLETE_ENDINGS = ("。", "！", "？", "?", "です", "ます", "ましょう", "んです")
_RANK_INTERNAL_KEYS = ("score", "weight", "_is_opening_hook")


def _has_hook_signal(text: str) -> bool:
    """先頭付近に問いかけまたはフック語があるか。"""
    head = (text or "")[:70]
    if "？" in head or "?" in head:
        return True
    return any(keyword in head for keyword in _HOOK_KEYWORDS)


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


def _window_pre_score(start_time: float, duration: float) -> float:
    """尺と冒頭位置だけで候補を間引くための軽量スコア。"""
    if SWEET_SPOT_MIN <= duration <= SWEET_SPOT_MAX:
        duration_score = 1.2
    else:
        if duration < SWEET_SPOT_MIN:
            dist = SWEET_SPOT_MIN - duration
        else:
            dist = duration - SWEET_SPOT_MAX
        duration_score = max(0.2, 1.0 - dist / 30.0)
    opening = 0.0
    if start_time <= OPENING_PRIORITY_START:
        recency = max(0.0, 1.0 - start_time / OPENING_PRIORITY_START)
        opening = 0.5 + 1.0 * recency
    return duration_score + opening


def _representative_end_indices(
    sentences_info: Sequence[Dict],
    start_index: int,
    start_time: float,
    min_clip_duration: float,
    max_clip_duration: float,
) -> List[int]:
    """1つの開始文につき、尺の代表点（スイートスポットと端）だけ返す。"""
    first_j: Optional[int] = None
    last_j: Optional[int] = None
    best_sweet_j: Optional[int] = None
    best_sweet_dist: Optional[float] = None
    target_end = start_time + SWEET_SPOT_TARGET
    n = len(sentences_info)
    for j in range(start_index, n):
        end_time = sentences_info[j].get("end_time")
        end_char = sentences_info[j].get("end_char")
        if end_time is None or end_char is None:
            continue
        duration = end_time - start_time
        if duration < min_clip_duration:
            continue
        if duration > max_clip_duration:
            break
        if first_j is None:
            first_j = j
        last_j = j
        dist = abs(float(end_time) - target_end)
        if best_sweet_j is None or dist < best_sweet_dist:
            best_sweet_j = j
            best_sweet_dist = dist
    if best_sweet_j is None:
        return []
    chosen = {best_sweet_j}
    if first_j is not None and last_j is not None and first_j != last_j:
        first_end = float(sentences_info[first_j]["end_time"])
        last_end = float(sentences_info[last_j]["end_time"])
        sweet_end = float(sentences_info[best_sweet_j]["end_time"])
        if abs(first_end - sweet_end) >= abs(last_end - sweet_end):
            chosen.add(first_j)
        else:
            chosen.add(last_j)
    return list(chosen)


def _select_bounded_pairs(
    pairs: List[Tuple[float, float, int, int]],
    limit: int,
) -> List[Tuple[float, float, int, int]]:
    """冒頭を残しつつ、開始時刻で層化して件数を上限以内にする。"""
    if len(pairs) <= limit:
        return pairs
    opening = [p for p in pairs if p[1] <= OPENING_PRIORITY_START]
    rest = [p for p in pairs if p[1] > OPENING_PRIORITY_START]
    n_opening = min(len(opening), MAX_OPENING_WINDOWS, limit)
    opening.sort(key=lambda p: p[0], reverse=True)
    selected = opening[:n_opening]
    remaining = limit - len(selected)
    if remaining <= 0 or not rest:
        return selected
    rest.sort(key=lambda p: p[1])
    chunk_size = max(1, math.ceil(len(rest) / remaining))
    for offset in range(0, len(rest), chunk_size):
        group = rest[offset : offset + chunk_size]
        if group:
            selected.append(max(group, key=lambda p: p[0]))
        if len(selected) >= limit:
            break
    return selected[:limit]


def generate_sentence_windows(
    sentences_info: Sequence[Dict],
    min_clip_duration: float,
    max_clip_duration: float,
) -> List[Dict]:
    """
    連続する文から、指定尺に収まるクリップ候補を列挙する。

    開始文ごとに全終了文を実体化せず、尺の代表点だけを残し、
    さらに ``MAX_GENERATED_WINDOWS`` 件へ間引く（冒頭と時間方向の多様性を維持）。

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
    if n == 0:
        return []

    pairs: List[Tuple[float, float, int, int]] = []
    for i in range(n):
        start_time = sentences_info[i].get("start_time")
        start_char = sentences_info[i].get("start_char")
        if start_time is None or start_char is None:
            continue
        start_time_f = float(start_time)
        for j in _representative_end_indices(
            sentences_info,
            i,
            start_time_f,
            min_clip_duration,
            max_clip_duration,
        ):
            end_time = float(sentences_info[j]["end_time"])
            duration = end_time - start_time_f
            pairs.append(
                (
                    _window_pre_score(start_time_f, duration),
                    start_time_f,
                    i,
                    j,
                )
            )

    windows: List[Dict] = []
    for _, _, i, j in _select_bounded_pairs(pairs, MAX_GENERATED_WINDOWS):
        start_time = float(sentences_info[i]["start_time"])
        end_time = float(sentences_info[j]["end_time"])
        windows.append(
            {
                "start_time": start_time,
                "end_time": end_time,
                "start_char": int(sentences_info[i]["start_char"]),
                "end_char": int(sentences_info[j]["end_char"]),
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

    # 動画冒頭のフックは早いほど加点（0秒で +1.5、15秒で +0.5）
    if start_time is not None and start_time <= OPENING_PRIORITY_START:
        if "？" in head or "?" in head or hook_hits:
            recency = max(0.0, 1.0 - start_time / OPENING_PRIORITY_START)
            score += 0.5 + 1.0 * recency

    stripped = text.rstrip()
    if stripped.endswith(_COMPLETE_ENDINGS):
        score += 0.4
    else:
        score -= 0.2

    advice_hits = sum(1 for kw in _ADVICE_KEYWORDS if kw in text)
    score += min(0.35, 0.12 * advice_hits)

    # 締めの CTA だけだと単体ショートとして弱い
    if "ここまで一緒に" in text or "最高に嬉しい" in text:
        score -= 0.5

    return score


def _sentence_start(sentence: Dict) -> Optional[float]:
    start_time = sentence.get("start_time")
    return None if start_time is None else float(start_time)


def _sentence_end(sentence: Dict) -> Optional[float]:
    end_time = sentence.get("end_time")
    return None if end_time is None else float(end_time)


def _has_char_span(sentence: Dict) -> bool:
    return (
        sentence.get("start_char") is not None and sentence.get("end_char") is not None
    )


def _sentences_containing(sentences_info: Sequence[Dict], time: float) -> List[Dict]:
    """時刻が [start_time, end_time] に含まれる文を返す。"""
    containing: List[Dict] = []
    for sentence in sentences_info:
        start_time = _sentence_start(sentence)
        end_time = _sentence_end(sentence)
        if start_time is None or end_time is None:
            continue
        if start_time - 0.05 <= time <= end_time + 0.05:
            containing.append(sentence)
    return containing


def _pick_start_sentence(sentences_info: Sequence[Dict], start_time: float) -> Dict:
    """開始時刻を含む文。無音ギャップなら次の文へ進める。"""
    containing = _sentences_containing(sentences_info, start_time)
    if containing:
        return max(containing, key=lambda s: _sentence_start(s) or 0.0)

    later = [
        s
        for s in sentences_info
        if _sentence_start(s) is not None and _sentence_start(s) >= start_time - 0.05
    ]
    if later:
        return min(later, key=lambda s: _sentence_start(s) or 0.0)

    return min(
        sentences_info,
        key=lambda s: abs((_sentence_start(s) or 0.0) - start_time),
    )


def _pick_end_sentence(sentences_info: Sequence[Dict], end_time: float) -> Dict:
    """終了時刻を含む文。無音ギャップなら前の文へ戻す。"""
    containing = _sentences_containing(sentences_info, end_time)
    if containing:
        return min(containing, key=lambda s: _sentence_end(s) or 0.0)

    earlier = [
        s
        for s in sentences_info
        if _sentence_end(s) is not None and _sentence_end(s) <= end_time + 0.05
    ]
    if earlier:
        return max(earlier, key=lambda s: _sentence_end(s) or 0.0)

    return min(
        sentences_info,
        key=lambda s: abs((_sentence_end(s) or 0.0) - end_time),
    )


def _apply_sentence_span(
    clip: Dict, start_sent: Dict, end_sent: Dict
) -> Optional[Dict]:
    """2文の境界でクリップを更新する。不正なら None。"""
    start_time = _sentence_start(start_sent)
    end_time = _sentence_end(end_sent)
    if start_time is None or end_time is None or start_time >= end_time:
        return None
    if not _has_char_span(start_sent) or not _has_char_span(end_sent):
        return None
    snapped = dict(clip)
    snapped["start_time"] = start_time
    snapped["end_time"] = end_time
    snapped["start_char"] = int(start_sent["start_char"])
    snapped["end_char"] = int(end_sent["end_char"])
    return snapped


def _trim_snapped_to_duration(
    snapped: Dict,
    original: Dict,
    sentences_info: Sequence[Dict],
    min_clip_duration: Optional[float],
    max_clip_duration: Optional[float],
) -> Dict:
    """スナップ後に最大尺を超えたら、文境界のまま収まるよう縮める。"""
    if max_clip_duration is None:
        return snapped

    duration = snapped["end_time"] - snapped["start_time"]
    if duration <= max_clip_duration:
        return snapped

    start_time = snapped["start_time"]
    end_candidates = []
    for sentence in sentences_info:
        end_time = _sentence_end(sentence)
        if end_time is None or not _has_char_span(sentence):
            continue
        candidate_duration = end_time - start_time
        if candidate_duration <= 0 or candidate_duration > max_clip_duration:
            continue
        if min_clip_duration is not None and candidate_duration < min_clip_duration:
            continue
        end_candidates.append(sentence)
    if end_candidates:
        end_sent = max(end_candidates, key=lambda s: _sentence_end(s) or 0.0)
        trimmed = dict(snapped)
        trimmed["end_time"] = float(end_sent["end_time"])
        trimmed["end_char"] = int(end_sent["end_char"])
        return trimmed

    end_time = snapped["end_time"]
    start_candidates = []
    for sentence in sentences_info:
        sentence_start = _sentence_start(sentence)
        if sentence_start is None or not _has_char_span(sentence):
            continue
        candidate_duration = end_time - sentence_start
        if candidate_duration <= 0 or candidate_duration > max_clip_duration:
            continue
        if min_clip_duration is not None and candidate_duration < min_clip_duration:
            continue
        start_candidates.append(sentence)
    if start_candidates:
        start_sent = min(start_candidates, key=lambda s: _sentence_start(s) or 0.0)
        trimmed = dict(snapped)
        trimmed["start_time"] = float(start_sent["start_time"])
        trimmed["start_char"] = int(start_sent["start_char"])
        return trimmed

    original_duration = original["end_time"] - original["start_time"]
    fits_max = original_duration > 0 and original_duration <= max_clip_duration
    fits_min = min_clip_duration is None or original_duration >= min_clip_duration
    if fits_max and fits_min:
        return dict(original)
    return snapped


def snap_clip_to_sentences(
    clip: Dict,
    sentences_info: Sequence[Dict],
    min_clip_duration: Optional[float] = None,
    max_clip_duration: Optional[float] = None,
) -> Dict:
    """
    クリップの開始・終了を最も近い文境界へスナップする。

    開始時刻が文と文の無音ギャップにあるときは次の文頭へ進め、
    終了時刻がギャップにあるときは前の文末へ戻す。スナップで
    ``max_clip_duration`` を超える場合は、フック側（先頭）を優先して縮める。

    Parameters
    ----------
    clip: dict
        start_time / end_time を持つクリップ
    sentences_info: Sequence[dict]
        文情報リスト
    min_clip_duration: float or None
        縮めたあとも維持したい最小尺。None なら制限しない
    max_clip_duration: float or None
        この秒数を超えないよう文境界で縮める。None なら制限しない

    Returns
    -------
    dict
        文境界に合わせたクリップ（元の dict をコピーして更新）
    """
    if not sentences_info:
        return dict(clip)

    start_time = clip["start_time"]
    end_time = clip["end_time"]
    start_sent = _pick_start_sentence(sentences_info, start_time)
    end_sent = _pick_end_sentence(sentences_info, end_time)
    snapped = _apply_sentence_span(clip, start_sent, end_sent)
    if snapped is None:
        return dict(clip)

    return _trim_snapped_to_duration(
        snapped,
        clip,
        sentences_info,
        min_clip_duration,
        max_clip_duration,
    )


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
        スコア降順のクリップ（weight/score は含めない）。
        冒頭フック（開始15秒以内かつ問いかけ/フック語）がある場合は
        1件を確保してから残りを埋める。
    """
    scored: List[Dict] = []
    for clip in clips:
        start = clip.get("start_time", 0.0)
        end = clip.get("end_time", 0.0)
        duration = end - start
        if duration < min_clip_duration or duration > max_clip_duration:
            continue
        raw_start_char = clip.get("start_char")
        raw_end_char = clip.get("end_char")
        if raw_start_char is None or raw_end_char is None:
            continue
        try:
            start_char = max(0, int(raw_start_char))
            end_char = min(len(transcription_text), int(raw_end_char))
        except (TypeError, ValueError):
            continue
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
        item["_is_opening_hook"] = start <= OPENING_PRIORITY_START and _has_hook_signal(
            text
        )
        scored.append(item)

    scored.sort(key=lambda c: c["score"], reverse=True)

    # 番号付きアドバイスが上位を埋め尽くしても、冒頭フックを1枠残す
    opening = next((c for c in scored if c.get("_is_opening_hook")), None)
    kept: List[Dict] = []
    if opening is not None:
        kept.append(opening)

    for clip in scored:
        if opening is not None and clip is opening:
            continue
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

    kept.sort(key=lambda c: c["score"], reverse=True)

    logger.info(
        "Shorts ranking kept %s/%s clips (threshold=%.2f)",
        len(kept),
        len(scored),
        overlap_threshold,
    )
    cleaned = []
    for clip in kept:
        cleaned.append({k: v for k, v in clip.items() if k not in _RANK_INTERNAL_KEYS})
    return cleaned
