#!/bin/bash

# cc-werewolf ゲーム開始スクリプト
# チャットサーバーを起動し、tmuxで複数のClaude Codeインスタンスを起動して人狼ゲームを開始します

set -e

SESSION_NAME="werewolf"
DEFAULT_PLAYERS=4

# プレイヤー数の設定
PLAYERS=${1:-$DEFAULT_PLAYERS}

echo "🐺 cc-werewolf ゲーム開始..."
echo "プレイヤー数: $PLAYERS"

# プロジェクトディレクトリを取得
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# 既存のセッションがあれば削除
tmux has-session -t $SESSION_NAME 2>/dev/null || true
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "既存のセッションを削除します: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
fi

# チャットサーバーのプロセスがあれば停止
pkill -f "python.*server.server" || true
sleep 1

# 新しいセッションを作成
echo "tmuxセッションを作成中: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME

# チャットサーバーを起動（ウィンドウ0）
echo "チャットサーバーを起動中..."
tmux rename-window -t $SESSION_NAME:0 "server"
tmux send-keys -t $SESSION_NAME:0 "cd '$PROJECT_DIR'" Enter
tmux send-keys -t $SESSION_NAME:0 "uv run python -m server.server" Enter

# 少し待ってサーバーが起動するのを待つ
sleep 3

# 神視点ウィンドウを作成（ウィンドウ1）
echo "神視点CLIを起動中..."
tmux new-window -t $SESSION_NAME:1 -n "godview"
tmux send-keys -t $SESSION_NAME:1 "cd '$PROJECT_DIR'" Enter
tmux send-keys -t $SESSION_NAME:1 "uv run python -m server.godview" Enter

# プレイヤーウィンドウを作成（ウィンドウ2）
echo "プレイヤーを起動中..."
tmux new-window -t $SESSION_NAME:2 -n "players"

# 2x2グリッドレイアウトを作成
if [ $PLAYERS -ge 4 ]; then
    # 左右分割
    tmux split-window -h -t $SESSION_NAME:2

    # 左ペインを上下分割
    tmux select-pane -t $SESSION_NAME:2.0
    tmux split-window -v -t $SESSION_NAME:2.0

    # 右ペインを上下分割
    tmux select-pane -t $SESSION_NAME:2.2
    tmux split-window -v -t $SESSION_NAME:2.2
fi

# 各ペインにccd-glmを送信して実行
for i in {0..3}; do
    tmux send-keys -t $SESSION_NAME:2.$i "cd '$PROJECT_DIR'" Enter
    sleep 0.5
    tmux send-keys -t $SESSION_NAME:2.$i "ccd-glm" Enter
    sleep 2
done

# 各ペインに異なるプロンプトを送信
# プレイヤー1（左上） - 村人
tmux send-keys -t $SESSION_NAME:2.0 "あなたは人狼ゲームの「村人1」です。他のプレイヤーと協力して人狼を見つけ出してください。まず自己紹介をしてください。" Enter

# プレイヤー2（左下） - 人狼
tmux send-keys -t $SESSION_NAME:2.1 "あなたは人狼ゲームの「人狼」です。村人のふりをして、誰も気づかないようにしてください。まず自己紹介をしてください。" Enter

# プレイヤー3（右上） - 占い師
tmux send-keys -t $SESSION_NAME:2.2 "あなたは人狼ゲームの「占い師」です。夜に誰か1人の正体を占います。まず自己紹介をしてください。" Enter

# プレイヤー4（右下） - ゲームマスター
tmux send-keys -t $SESSION_NAME:2.3 "あなたは人狼ゲームの「ゲームマスター」です。ゲームを進行してください。まずプレイヤー全員に挨拶をして、ゲームの説明をしてください。" Enter

echo ""
echo "✅ ゲームが開始されました！"
echo ""
echo "ウィンドウ構成:"
echo "  0: server    - チャットサーバー"
echo "  1: godview   - 神視点（全ての会話が見れる）"
echo "  2: players   - プレイヤー（2x2分割）"
echo ""
echo "次のコマンドでゲームに参加できます:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "ウィンドウ切り替え:"
echo "  Ctrl+b 0 - サーバー"
echo "  Ctrl+b 1 - 神視点"
echo "  Ctrl+b 2 - プレイヤー"
echo ""
echo "ゲームを終了するには:"
echo "  tmux kill-session -t $SESSION_NAME"
echo ""
echo "神視点のみを別の端末で見るには:"
echo "  cd '$PROJECT_DIR' && uv run python -m server.godview"
