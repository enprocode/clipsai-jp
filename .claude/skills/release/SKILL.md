---
name: release
description: clipsai-jp の新バージョンを PyPI に公開する手順とチェックリスト。リリース、バージョンアップ、PyPI公開を頼まれたときに使用。
---

# PyPI リリース手順

リリースは **`VERSION` を上げて main にマージするだけ**で全自動化されている。

## リリースのやり方（通常）

1. バージョンブランチ（例: `v1.0.6`）を作成
2. `VERSION` を新バージョンに更新（**同一バージョンの再アップロードは不可**。setup.py・CI・`clipsai_jp.__version__` はすべてここから読む）
3. ルート直下の `CHANGELOG.md` に `## [x.y.z] - YYYY-MM-DD` セクションを追記（この本文が GitHub Release ノートに使われる）
4. 依存を変えたら `setup.py` と `requirements.txt` の**両方**を更新
5. PR → main へマージ

マージ後は GitHub Actions が自動で:

- **Tests 成功 → TestPyPI に公開**（`python-publish-testpypi.yml`。既存バージョンならスキップ）
- **Tests 成功 → GitHub Release を自動作成 → 本番 PyPI に公開**（`python-publish.yml`。`v<VERSION>` の Release が無ければ作成し、`pypi` 環境で trusted publishing。既存バージョンはスキップ）

つまり手動での `twine upload` や GitHub Release 作成は不要。

## 手動リリース（必要時のみ）

GitHub UI で `v<VERSION>` タグの Release を作成すると `python-publish.yml` の `release: published` 経路が発火し、タグと `VERSION` の一致を検証して公開する。

## 安全弁

本番公開を手動承認にしたい場合は、リポジトリの **Settings → Environments → `pypi`** に **Required reviewers** を設定する。設定すると `pypi-publish` ジョブが承認待ちで止まる（自動リリース経路でも有効）。

## 公開後の確認

- `pip install clipsai-jp==<新バージョン>` で本番インストール確認
- GitHub の Releases に `v<新バージョン>` が作成されていること
