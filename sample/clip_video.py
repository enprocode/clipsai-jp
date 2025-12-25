"""
動画からクリップを見つけるサンプルコード

このサンプルでは、動画を文字起こしして、そのトランスクリプトから
自動的にクリップを見つける方法を示します。

詳細な使用方法については、doc/SAMPLE_CODE.mdを参照してください。
"""

from clipsai_jp import ClipFinder, Transcriber, MediaEditor, AudioVideoFile

# 動画ファイルのパス（絶対パスを指定してください）
import os

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
video_file_path = os.path.join(os.path.dirname(__file__), "video.mp4")

# 出力ディレクトリ（必要に応じて変更してください）
output_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(output_dir, exist_ok=True)

# 1. トランスクリプターを作成して動画を文字起こし
print("動画を文字起こししています...")
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_file_path=video_file_path)

# 文字起こし結果を保存
print("文字起こし結果を保存しています...")
# JSON形式で保存（タイムスタンプ情報を含む）
json_file = transcription.store_as_json_file(
    os.path.join(output_dir, "transcription.json")
)
print(f"  JSON形式: {json_file.path}")

# テキスト形式で保存
text_file_path = os.path.join(output_dir, "transcription.txt")
with open(text_file_path, "w", encoding="utf-8") as f:
    f.write(transcription.text)
print(f"  テキスト形式: {text_file_path}")

# 2. クリップファインダーを作成してクリップを見つける
print("\nクリップを検索しています...")

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
print(f"\n見つかったクリップ数: {len(clips)}")
for i, clip in enumerate(clips):
    print(f"\nクリップ {i + 1}:")
    print(f"  開始時間: {clip.start_time:.2f}秒")
    print(f"  終了時間: {clip.end_time:.2f}秒")
    print(f"  期間: {clip.end_time - clip.start_time:.2f}秒")

# 4. クリップを動画ファイルとして保存（オプション）
print("\nクリップを動画ファイルとして保存しています...")
media_editor = MediaEditor()
media_file = AudioVideoFile(video_file_path)

for i, clip in enumerate(clips):
    clip_output_path = os.path.join(output_dir, f"clip_{i+1:03d}.mp4")
    clip_video = media_editor.trim(
        media_file=media_file,
        start_time=clip.start_time,
        end_time=clip.end_time,
        trimmed_media_file_path=clip_output_path,
    )
    if clip_video:
        print(f"  クリップ {i+1} を {clip_output_path} に保存しました")
    else:
        print(f"  クリップ {i+1} の保存に失敗しました")

print(f"\nすべての出力ファイルは {output_dir} に保存されました。")