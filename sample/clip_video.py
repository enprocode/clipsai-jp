"""
動画からクリップを見つけるサンプルコード

このサンプルでは、動画を文字起こしして、そのトランスクリプトから
自動的にクリップを見つける方法を示します。

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

from clipsai import ClipFinder, Transcriber

# 動画ファイルのパス（絶対パスを指定してください）
video_file_path = "video.mp4"

# 1. トランスクリプターを作成して動画を文字起こし
print("動画を文字起こししています...")
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_file_path=video_file_path)

# 2. クリップファインダーを作成してクリップを見つける
print("クリップを検索しています...")
clipfinder = ClipFinder()
clips = clipfinder.find_clips(transcription=transcription)

# 3. 見つかったクリップの情報を表示
print(f"\n見つかったクリップ数: {len(clips)}")
for i, clip in enumerate(clips):
    print(f"\nクリップ {i + 1}:")
    print(f"  開始時間: {clip.start_time}秒")
    print(f"  終了時間: {clip.end_time}秒")
    print(f"  期間: {clip.end_time - clip.start_time:.2f}秒")