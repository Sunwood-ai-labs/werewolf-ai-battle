<div align="center">

<img src="assets/header.svg" alt="Werewolf AI Battle Header" width="800"/>

</div>

<div align="center">

### Claude Codeで遊ぶ人狼ゲーム。tmuxで複数AIと同時対戦！

[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-View-success?style=flat-square&logo=github)](https://github.com/Sunwood-ai-labs/werewolf-ai-battle)

tmuxで複数のClaude Codeインスタンスを起動し、AI同士が人狼ゲームで対戦します。
リアルタイムチャットサーバーで全ての会話を神視点で監視できます。

</div>

---

## 概要

**werewolf-ai-battle**（通称：**cc-werewolf**）は、Claude Codeのマルチインスタンス環境で実現する人狼ゲームシミュレーターです。

tmuxの分割ペイン機能とWebSocketチャットサーバーを使って、複数のAIプレイヤーが同時にゲームを進行します。各AIは独立したプロセスで動作し、お互いの発言を観察して推理し、投票を行います。

### 特徴

- **マルチAI対戦**: tmuxで4つ以上のAIプレイヤーが同時対戦
- **リアルタイムチャット**: WebSocketサーバーで全ての会話を管理
- **神視点機能**: richベースの美しいTUIで全ての会話をリアルタイム監視
- **複数チャンネル**: public、werewolf（人狼専用）、moderator（GM専用）
- **tmux連携**: 視覚的に分かりやすい画面分割

---

## セットアップ

### 要件

- [tmux](https://github.com/tmux/tmux/wiki) インストール済み
- [Claude Code](https://claude.ai/code) が動作する環境
- [uv](https://github.com/astral-sh/uv) Pythonパッケージマネージャー
- Python 3.10+

### インストール

1. リポジトリをクローン

```bash
git clone https://github.com/Sunwood-ai-labs/werewolf-ai-battle.git
cd werewolf-ai-battle
```

2. 依存関係をインストール（uv）

```bash
uv sync
```

---

## 使用法

### クイックスタート

```bash
# ゲーム開始
./scripts/start-game.sh

# tmuxセッションにアタッチ
tmux attach -t werewolf
```

### ウィンドウ構成

ゲームを開始すると、3つのウィンドウが作成されます：

| ウィンドウ | 説明 | キー操作 |
|:---------:|------|----------|
| 0: server | チャットサーバー | `Ctrl+b 0` |
| 1: godview | 神視点（全ての会話が見れる） | `Ctrl+b 1` |
| 2: players | プレイヤー（2x2分割） | `Ctrl+b 2` |

### プレイヤー配置

```
┌─────────────┬─────────────┐
│ 村人1       │ 占い師      │
│ (左上)      │ (右上)      │
├─────────────┼─────────────┤
│ 人狼        │ GM          │
│ (左下)      │ (右下)      │
└─────────────┴─────────────┘
```

### ゲームを終了する

```bash
# スクリプトで終了
./scripts/stop-game.sh

# または手動で
tmux kill-session -t werewolf
```

### tmuxキー操作

| キー | 説明 |
|:---:|------|
| `Ctrl+b d` | セッションからデタッチ |
| `Ctrl+b 0/1/2` | ウィンドウを切り替え |
| `Ctrl+b o` | ペインを順に移動 |
| `Ctrl+b q` | ペイン番号を表示して移動 |

---

## 神視点CLI

神視点CLI（`godview`）を使うと、全ての会話をリアルタイムで監視できます。

### 別の端末で神視点を起動

```bash
cd werewolf-ai-battle
uv run python -m server.godview
```

### 機能

- **プレイヤー一覧**: 全プレイヤーの役職と状態を表示
- **チャットログ**: 全チャンネルの会話をリアルタイム表示
- **イベントログ**: プレイヤーの参加/退出などを記録

### websocat で最新チャットを確認

```bash
# 最新5件のチャットを確認（パスワード: wolf）
echo '{"type":"godview","password":"wolf"}' | websocat ws://localhost:8765 | jq '.channels.public.messages[-5:]'

# プレイヤー一覧を確認
echo '{"type":"godview","password":"wolf"}' | websocat ws://localhost:8765 | jq '.players'
```

> **注意**: 神視点にはパスワード `wolf` が必要です。プレイヤーには知らせないでください。

---

## ゲームルール

### 役職

- **村人**: 人狼を探し出す
- **人狼**: 夜に村人を襲撃する
- **占い師**: 夜に1人のプレイヤーを占える
- **ゲームマスター**: ゲームを進行

### 進行

1. **準備フェーズ**: 各プレイヤーの役職が割り当てられる
2. **夜フェーズ**: 人狼が襲撃、占い師が占い
3. **朝フェーズ**: 死亡者の発表、議論開始
4. **投票フェーズ**: 処刑対象を投票で決定
5. **勝利判定**: 人狼の勝利か村人の勝利かを判定

---

## プロジェクト構造

```
werewolf-ai-battle/
├── assets/           # 画像等のリソース
│   └── header.svg    # ヘッダー画像
├── server/           # チャットサーバー
│   ├── server.py     # WebSocketサーバー
│   ├── godview.py    # 神視点CLI
│   └── client.py     # クライアントライブラリ
├── scripts/          # ゲームスクリプト
│   ├── start-game.sh # ゲーム開始スクリプト
│   └── stop-game.sh  # ゲーム終了スクリプト
├── pyproject.toml    # Python依存関係
├── README.md
└── LICENSE
```

---

## 開発計画

- [x] リポジトリの初期化
- [x] チャットサーバーの実装
- [x] 神視点CLIの実装
- [x] tmux自動セットアップ
- [ ] ゲームエンジンの高度化
- [ ] 勝利判定ロジック
- [ ] ログ機能

---

## トラブルシューティング

### ゲームが開始できない

```bash
# 既存のセッションを削除
./scripts/stop-game.sh

# もう一度開始
./scripts/start-game.sh
```

### チャットサーバーが起動しない

```bash
# Pythonの依存関係を確認
uv sync

# サーバー単体でテスト
uv run python -m server.server
```

### tmuxセッションが残っている

```bash
# セッション一覧を確認
tmux list-sessions

# 全てのセッションを削除
tmux kill-server
```

---

## 貢献

貢献を歓迎します！

1. リポジトリをフォーク
2. ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. コミット (`git commit -m 'Add amazing feature'`)
4. プッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

---

## ライセンス

MIT License - see the [LICENSE](LICENSE) file for details.

---

## 謝辞

- [Claude Code](https://claude.ai/code) - AIコーディングアシスタント
- [tmux](https://github.com/tmux/tmux) - ターミナルマルチプレクサ
- [websockets](https://github.com/python-websockets/websockets) - WebSocketライブラリ
- [rich](https://github.com/Textualize/rich) - 美しいTUIライブラリ
- 人狼ゲームのすべての愛好家の皆様

---

<div align="center">

Made with 🐺 by Sunwood-ai-labs

</div>
