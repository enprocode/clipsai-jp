"""
ClipsAIの完全な使用例

このサンプルでは、動画の文字起こし、クリップ検出、リサイズの
一連の処理を実行する方法を示します。

【開発モードで使用する場合】
ローカルでビルドしたclipsaiを使用する場合は、以下のいずれかの方法で
セットアップしてください：

方法1: 開発モードでインストール（推奨）
    pip install -e .

方法2: パスを追加
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
"""

from clipsai import ClipFinder, Transcriber, resize

# 設定
video_file_path = "/abs/path/to/video.mp4"
pyannote_auth_token = "your_pyannote_token_here"  # リサイズ機能を使用する場合のみ必要

# ============================================
# ステップ1: 動画を文字起こし
# ============================================
print("=" * 50)
print("ステップ1: 動画を文字起こし")
print("=" * 50)
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_file_path=video_file_path)
print("文字起こしが完了しました。\n")

# ============================================
# ステップ2: クリップを見つける
# ============================================
print("=" * 50)
print("ステップ2: クリップを検索")
print("=" * 50)
clipfinder = ClipFinder()
clips = clipfinder.find_clips(transcription=transcription)

print(f"見つかったクリップ数: {len(clips)}")
for i, clip in enumerate(clips[:5]):  # 最初の5つを表示
    print(f"\nクリップ {i + 1}:")
    print(f"  開始時間: {clip.start_time:.2f}秒")
    print(f"  終了時間: {clip.end_time:.2f}秒")
    print(f"  期間: {clip.end_time - clip.start_time:.2f}秒")

if len(clips) > 5:
    print(f"\n... 他に {len(clips) - 5} 個のクリップがあります。\n")

# ============================================
# ステップ3: 動画をリサイズ（オプション）
# ============================================
print("=" * 50)
print("ステップ3: 動画をリサイズ（オプション）")
print("=" * 50)

# リサイズ機能を使用する場合は、以下のコメントを外してください
# print("動画をリサイズしています...")
# crops = resize(
#     video_file_path=video_file_path,
#     pyannote_auth_token=pyannote_auth_token,
#     aspect_ratio=(9, 16)  # 縦型（9:16）
# )
# print(f"リサイズセグメント数: {len(crops.segments)}")
# print("リサイズが完了しました。")

print("\n処理が完了しました！")

