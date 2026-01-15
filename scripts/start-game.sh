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

# プロジェクトディレクトリを取得（現在のディレクトリを使用）
PROJECT_DIR="$(pwd)"

# 既存のセッションがあれば削除
tmux has-session -t $SESSION_NAME 2>/dev/null || true
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "既存のセッションを削除します: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
fi

# チャットサーバーのプロセスがあれば停止
sudo -u aslan pkill -f "python.*server.server" 2>/dev/null || true
sleep 1

# 新しいセッションを作成（serverペインから開始）
echo "tmuxセッションを作成中: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME -n "game"
tmux send-keys -t $SESSION_NAME:0.0 "cd '$PROJECT_DIR'" Enter
tmux send-keys -t $SESSION_NAME:0.0 "uv run python -m server.server" Enter

# 横に分割して右側にgodviewを作成
tmux split-window -h -t $SESSION_NAME:0.0
tmux send-keys -t $SESSION_NAME:0.1 "cd '$PROJECT_DIR'" Enter
tmux send-keys -t $SESSION_NAME:0.1 "uv run python -m server.godview" Enter

# 少し待ってサーバーが起動するのを待つ
sleep 3

# 正しいレイアウトを作成
# まず左右に分割した状態で、それぞれを縦に3分割

# 左側（server）を縦に3分割
tmux select-pane -t $SESSION_NAME:0.0
tmux split-window -v -p 50
tmux select-pane -t $SESSION_NAME:0.2
tmux split-window -v -p 50

# 右側（godview）を縦に3分割
tmux select-pane -t $SESSION_NAME:0.1
tmux split-window -v -p 50
tmux select-pane -t $SESSION_NAME:0.4
tmux split-window -v -p 50

# tiledレイアウトで均等配置
tmux select-layout -t $SESSION_NAME:0 tiled

# serverとgodviewを上段に配置するためにペインを入れ替え
# godviewはpane 3にあるので、それをpane 1の位置に移動
tmux swap-pane -t $SESSION_NAME:0.1 -s $SESSION_NAME:0.3

# 再びtiledレイアウトを適用して配置を整える
tmux select-layout -t $SESSION_NAME:0 tiled

# レイアウトの確認
# serverはpane 0、godviewはpane 1
# プレイヤーペインはpane 2, 3, 4, 5

# 各プレイヤーペインにccd-glmを送信して実行
# serverはpane 0、godviewはpane 1
# プレイヤーペインはpane 2, 3, 4, 5
for pane in 2 3 4 5; do
    tmux send-keys -t $SESSION_NAME:0.$pane "cd '$PROJECT_DIR'" Enter
    sleep 1
    tmux send-keys -t $SESSION_NAME:0.$pane "ccd-glm" Enter
    sleep 5
done

# 各プレイヤーに役割を割り当て（Enterを押す）
# プレイヤー1
tmux send-keys -t $SESSION_NAME:0.2 "あなたは人狼ゲームの「村人1」です。他のプレイヤーと協力して人狼を見つけ出してください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー2
tmux send-keys -t $SESSION_NAME:0.3 "あなたは人狼ゲームの「人狼」です。村人のふりをして、誰も気づかないようにしてください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー3
tmux send-keys -t $SESSION_NAME:0.4 "あなたは人狼ゲームの「占い師」です。夜に誰か1人の正体を占います。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー4
tmux send-keys -t $SESSION_NAME:0.5 "あなたは人狼ゲームの「ゲームマスター」です。ゲームを進行してください。まずプレイヤー全員に挨拶をして、ゲームの説明をしてください。" Enter

echo ""
echo "✅ ゲームが開始されました！"
echo ""
echo "レイアウト:"
echo "  +----------+----------+"
echo "  |  server  | godview  |"
echo "  +----------+----------+"
echo "  | player1  | player2  |"
echo "  +----------+----------+"
echo "  | player3  | player4  |"
echo "  +----------+----------+"
echo ""
echo "次のコマンドでゲームに参加できます:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "ペイン移動: Ctrl+b → 矢印キー"
echo "ゲームを終了するには: tmux kill-session -t $SESSION_NAME"
echo ""
