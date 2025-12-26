"""
動画からクリップを見つけるサンプルコード

このサンプルでは、動画を文字起こしして、そのトランスクリプトから
自動的にクリップを見つける方法を示します。

詳細な使用方法については、doc/SAMPLE_CODE.mdを参照してください。
"""
# 標準ライブラリ
import json
import logging
import os

# サードパーティライブラリ
# .envファイルから環境変数を読み込む（オプション）
# python-dotenvパッケージが必要: pip install python-dotenv
try:
    from dotenv import load_dotenv  # type: ignore

    # サンプルディレクトリの.envファイルを読み込む
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    load_dotenv(env_path)
except ImportError:
    # python-dotenvがインストールされていない場合は環境変数のみを使用
    pass

# ローカルパッケージ
from clipsai_jp import ClipFinder, Transcriber, MediaEditor, AudioVideoFile

# logging設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def format_time_srt(seconds: float) -> str:
    """
    SRT形式の時間フォーマット（HH:MM:SS,mmm）

    Parameters
    ----------
    seconds: float
        秒数

    Returns
    -------
    str
        SRT形式の時間文字列（HH:MM:SS,mmm）
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


def format_time_vtt(seconds: float) -> str:
    """
    VTT形式の時間フォーマット（HH:MM:SS.mmm）

    Parameters
    ----------
    seconds: float
        秒数

    Returns
    -------
    str
        VTT形式の時間文字列（HH:MM:SS.mmm）
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}.{millis:03d}"


def main() -> None:
    """動画からクリップを見つけるメイン処理"""
    video_file_path = os.path.join(os.path.dirname(__file__), "test.mp4")

    # ファイル存在確認
    if not os.path.exists(video_file_path):
        logger.error(f"動画ファイルが見つかりません: {video_file_path}")
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_file_path}")

    # 出力ディレクトリ（必要に応じて変更してください）
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"出力ディレクトリの作成に失敗しました: {e}")
        raise

    # 元の動画ファイル名からベース名を取得（拡張子を除く）
    video_basename = os.path.splitext(os.path.basename(video_file_path))[0]

    # 1. トランスクリプターを作成して動画を文字起こし
    logger.info("動画を文字起こししています...")
    transcriber = Transcriber()
    transcription = transcriber.transcribe(audio_file_path=video_file_path)

    # 文字起こし結果を保存（元のファイル名を使用）
    logger.info("文字起こし結果を保存しています...")
    # JSON形式で保存（タイムスタンプ情報を含む）
    json_file = transcription.store_as_json_file(
        os.path.join(output_dir, f"{video_basename}_transcription.json")
    )
    logger.info(f"  JSON形式: {json_file.path}")

    # テキスト形式で保存
    text_file_path = os.path.join(output_dir, f"{video_basename}_transcription.txt")
    try:
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(transcription.text)
        logger.info(f"  テキスト形式: {text_file_path}")
    except IOError as e:
        logger.error(f"ファイル書き込みエラー: {e}")
        raise

    # 2. クリップファインダーを作成してクリップを見つける
    logger.info("\nクリップを検索しています...")

    # デフォルト設定（15秒〜15分のクリップ）
    # clipfinder = ClipFinder()

    # ショート動画（最大60秒）向けの設定例:
    # clipfinder = ClipFinder(
    #     min_clip_duration=10,      # 最小10秒
    #     max_clip_duration=60,      # 最大60秒（ショート動画）
    #     cutoff_policy="average",   # "high"（厳しい）→ "average"（標準）→ "low"（緩い）
    #     embedding_model="japanese",  # 日本語最適化モデル（精度向上）
    # )

    # より高精度なモデルを使用する場合:
    # clipfinder = ClipFinder(
    #     min_clip_duration=10,
    #     max_clip_duration=60,
    #     cutoff_policy="average",
    #     embedding_model="high_accuracy",  # または "intfloat/multilingual-e5-base"
    # )

    # Gemini APIを使用してクリップ検出精度を向上させる場合:
    # 詳細な設定方法については、doc/SAMPLE_CODE.mdの「Gemini APIを使用して精度を向上させる場合」セクションを参照してください。
    clipfinder = ClipFinder(
        min_clip_duration=10,
        max_clip_duration=60,
        cutoff_policy="average",
        embedding_model="japanese",
        use_gemini=True,  # Gemini APIを使用
        gemini_api_key=os.getenv("GEMINI_API_KEY"),  # 環境変数から取得（推奨）
        gemini_model="gemini-2.5-flash",  # または "gemini-2.5-pro"（高精度）
        gemini_priority=0.7,  # Geminiの提案を70%重視（0.0=TextTilingのみ, 1.0=Geminiのみ）
    )

    clips = clipfinder.find_clips(transcription=transcription)

    # 3. 見つかったクリップの情報を表示
    logger.info(f"\n見つかったクリップ数: {len(clips)}")
    for i, clip in enumerate(clips):
        logger.info(f"\nクリップ {i + 1}:")
        logger.info(f"  開始時間: {clip.start_time:.2f}秒")
        logger.info(f"  終了時間: {clip.end_time:.2f}秒")
        logger.info(f"  期間: {clip.end_time - clip.start_time:.2f}秒")

    # 4. クリップを動画ファイルとして保存
    logger.info("\nクリップを動画ファイルとして保存しています...")
    media_editor = MediaEditor()
    media_file = AudioVideoFile(video_file_path)

    for i, clip in enumerate(clips):
        clip_num = i + 1
        # ファイル名のベース（例: "test_clip_001"）
        clip_basename = f"{video_basename}_clip_{clip_num:03d}"

        # クリップ動画を保存
        clip_output_path = os.path.join(output_dir, f"{clip_basename}.mp4")
        try:
            clip_video = media_editor.trim(
                media_file=media_file,
                start_time=clip.start_time,
                end_time=clip.end_time,
                trimmed_media_file_path=clip_output_path,
            )
            if clip_video:
                logger.info(f"  クリップ {clip_num} を {clip_output_path} に保存しました")
            else:
                logger.error(f"  クリップ {clip_num} の保存に失敗しました")
        except Exception as e:
            logger.error(f"クリップ {clip_num} の保存中にエラーが発生しました: {e}")
            raise

        # クリップの文字起こしデータを取得
        clip_sentences = transcription.get_sentence_info(
            start_time=clip.start_time,
            end_time=clip.end_time,
        )

        clip_char_info = transcription.get_char_info(
            start_time=clip.start_time,
            end_time=clip.end_time,
        )
        clip_text = "".join([char["char"] for char in clip_char_info])

        # クリップの文字起こしデータをJSON形式で保存
        clip_transcription_data = {
            "clip_number": clip_num,
            "start_time": clip.start_time,
            "end_time": clip.end_time,
            "duration": clip.end_time - clip.start_time,
            "text": clip_text,
            "sentences": [
                {
                    "sentence": s["sentence"],
                    "start_time": s["start_time"],
                    "end_time": s["end_time"],
                }
                for s in clip_sentences
            ],
            "char_info": clip_char_info,
        }

        clip_json_path = os.path.join(
            output_dir, f"{clip_basename}_transcription.json"
        )
        try:
            with open(clip_json_path, "w", encoding="utf-8") as f:
                json.dump(clip_transcription_data, f, ensure_ascii=False, indent=2)
            logger.info(f"  クリップ {clip_num} の文字起こしJSON: {clip_json_path}")
        except IOError as e:
            logger.error(f"JSONファイル書き込みエラー: {e}")
            raise

        # クリップの文字起こしテキストを保存
        clip_text_path = os.path.join(
            output_dir, f"{clip_basename}_transcription.txt"
        )
        try:
            with open(clip_text_path, "w", encoding="utf-8") as f:
                f.write(clip_text)
            logger.info(f"  クリップ {clip_num} の文字起こしテキスト: {clip_text_path}")
        except IOError as e:
            logger.error(f"テキストファイル書き込みエラー: {e}")
            raise

        # SRT形式の字幕ファイルを生成
        srt_path = os.path.join(output_dir, f"{clip_basename}.srt")
        try:
            with open(srt_path, "w", encoding="utf-8") as f:
                for j, sentence in enumerate(clip_sentences, 1):
                    # クリップ開始時刻を0秒にオフセット
                    start_time_srt = format_time_srt(
                        sentence["start_time"] - clip.start_time
                    )
                    end_time_srt = format_time_srt(
                        sentence["end_time"] - clip.start_time
                    )
                    f.write(f"{j}\n")
                    f.write(f"{start_time_srt} --> {end_time_srt}\n")
                    f.write(f"{sentence['sentence']}\n\n")
            logger.info(f"  クリップ {clip_num} の字幕（SRT）: {srt_path}")
        except IOError as e:
            logger.error(f"SRTファイル書き込みエラー: {e}")
            raise

        # VTT形式の字幕ファイルを生成
        vtt_path = os.path.join(output_dir, f"{clip_basename}.vtt")
        try:
            with open(vtt_path, "w", encoding="utf-8") as f:
                f.write("WEBVTT\n\n")
                for sentence in clip_sentences:
                    start_time_vtt = format_time_vtt(
                        sentence["start_time"] - clip.start_time
                    )
                    end_time_vtt = format_time_vtt(
                        sentence["end_time"] - clip.start_time
                    )
                    f.write(f"{start_time_vtt} --> {end_time_vtt}\n")
                    f.write(f"{sentence['sentence']}\n\n")
            logger.info(f"  クリップ {clip_num} の字幕（VTT）: {vtt_path}")
        except IOError as e:
            logger.error(f"VTTファイル書き込みエラー: {e}")
            raise

    logger.info(f"\nすべての出力ファイルは {output_dir} に保存されました。")


if __name__ == "__main__":
    main()
