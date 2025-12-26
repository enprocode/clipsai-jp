"""
ClipsAI-JPの完全な使用例

このサンプルでは、動画の文字起こし、クリップ検出、リサイズの
一連の処理を実行する方法を示します。

【開発モードで使用する場合】
ローカルでビルドしたclipsai-jpを使用する場合は、以下のいずれかの方法で
セットアップしてください：

方法1: 開発モードでインストール（推奨）
    pip install -e .

方法2: パスを追加
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""
# 標準ライブラリ
import logging
import os

# ローカルパッケージ
from clipsai_jp import ClipFinder, Transcriber, resize, MediaEditor, AudioVideoFile

# logging設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    """ClipsAI-JPの完全な使用例のメイン処理"""
    # 設定
    video_file_path = "video.mp4"
    pyannote_auth_token = "your_pyannote_token_here"  # リサイズ機能を使用する場合のみ必要

    # ファイル存在確認
    if not os.path.exists(video_file_path):
        logger.error(f"動画ファイルが見つかりません: {video_file_path}")
        raise FileNotFoundError(f"動画ファイルが見つかりません: {video_file_path}")

    # 出力ディレクトリ（必要に応じて変更してください）
    output_dir = "output"
    try:
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"出力ディレクトリの作成に失敗しました: {e}")
        raise

    # ============================================
    # ステップ1: 動画を文字起こし
    # ============================================
    logger.info("=" * 50)
    logger.info("ステップ1: 動画を文字起こし")
    logger.info("=" * 50)
    transcriber = Transcriber()
    transcription = transcriber.transcribe(audio_file_path=video_file_path)
    logger.info("文字起こしが完了しました。")

    # 文字起こし結果を保存
    logger.info("文字起こし結果を保存しています...")
    # JSON形式で保存（タイムスタンプ情報を含む）
    json_file = transcription.store_as_json_file(
        os.path.join(output_dir, "transcription.json")
    )
    logger.info(f"  JSON形式: {json_file.path}")

    # テキスト形式で保存
    text_file_path = os.path.join(output_dir, "transcription.txt")
    try:
        with open(text_file_path, "w", encoding="utf-8") as f:
            f.write(transcription.text)
        logger.info(f"  テキスト形式: {text_file_path}")
    except IOError as e:
        logger.error(f"ファイル書き込みエラー: {e}")
        raise
    logger.info("")

    # ============================================
    # ステップ2: クリップを見つける
    # ============================================
    logger.info("=" * 50)
    logger.info("ステップ2: クリップを検索")
    logger.info("=" * 50)

    # デフォルト設定（15秒〜15分のクリップ）
    clipfinder = ClipFinder()

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

    clips = clipfinder.find_clips(transcription=transcription)

    logger.info(f"見つかったクリップ数: {len(clips)}")
    for i, clip in enumerate(clips[:5]):  # 最初の5つを表示
        logger.info(f"\nクリップ {i + 1}:")
        logger.info(f"  開始時間: {clip.start_time:.2f}秒")
        logger.info(f"  終了時間: {clip.end_time:.2f}秒")
        logger.info(f"  期間: {clip.end_time - clip.start_time:.2f}秒")

    if len(clips) > 5:
        logger.info(f"\n... 他に {len(clips) - 5} 個のクリップがあります。")

    # クリップを動画ファイルとして保存（オプション）
    logger.info("\nクリップを動画ファイルとして保存しています...")
    media_editor = MediaEditor()
    media_file = AudioVideoFile(video_file_path)

    for i, clip in enumerate(clips):
        clip_output_path = os.path.join(output_dir, f"clip_{i+1:03d}.mp4")
        try:
            clip_video = media_editor.trim(
                media_file=media_file,
                start_time=clip.start_time,
                end_time=clip.end_time,
                trimmed_media_file_path=clip_output_path,
            )
            if clip_video:
                logger.info(f"  クリップ {i+1} を {clip_output_path} に保存しました")
            else:
                logger.error(f"  クリップ {i+1} の保存に失敗しました")
        except Exception as e:
            logger.error(f"クリップ {i+1} の保存中にエラーが発生しました: {e}")
            raise
    logger.info("")

    # ============================================
    # ステップ3: 動画をリサイズ（オプション）
    # ============================================
    logger.info("=" * 50)
    logger.info("ステップ3: 動画をリサイズ（オプション）")
    logger.info("=" * 50)

    # リサイズ機能を使用する場合は、以下のコメントを外してください
    # logger.info("動画をリサイズしています...")
    # crops = resize(
    #     video_file_path=video_file_path,
    #     pyannote_auth_token=pyannote_auth_token,
    #     aspect_ratio=(9, 16)  # 縦型（9:16）
    # )
    # logger.info(f"リサイズセグメント数: {len(crops.segments)}")
    # logger.info("リサイズが完了しました。")

    logger.info("\n処理が完了しました！")


if __name__ == "__main__":
    main()
