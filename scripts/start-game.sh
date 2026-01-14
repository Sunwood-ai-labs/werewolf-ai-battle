#!/bin/bash

# cc-werewolf ゲーム開始スクリプト
# tmuxで複数のClaude Codeインスタンスを起動して人狼ゲームを開始します

set -e

SESSION_NAME="werewolf"
DEFAULT_PLAYERS=4

# プレイヤー数の設定
PLAYERS=${1:-$DEFAULT_PLAYERS}

echo "🐺 cc-werewolf ゲーム開始..."
echo "プレイヤー数: $PLAYERS"

# 既存のセッションがあれば削除
tmux has-session -t $SESSION_NAME 2>/dev/null
if [ $? -eq 0 ]; then
    echo "既存のセッションを削除します: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
fi

# 新しいセッションを作成
echo "tmuxセッションを作成中: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME

# 最初のウィンドウの名前を変更
tmux rename-window -t $SESSION_NAME:0 "moderator"

# 2x2グリッドレイアウトを作成
if [ $PLAYERS -ge 4 ]; then
    # 左右分割
    tmux split-window -h -t $SESSION_NAME:0

    # 左ペインを上下分割
    tmux select-pane -t $SESSION_NAME:0.0
    tmux split-window -v -t $SESSION_NAME:0.0

    # 右ペインを上下分割
    tmux select-pane -t $SESSION_NAME:0.2
    tmux split-window -v -t $SESSION_NAME:0.2

    # 4つのペインにccd-glmを送信
    for i in {0..3}; do
        tmux send-keys -t $SESSION_NAME:0.$i "ccd-glm" Enter
    done
fi

# 各ペインに異なるプロンプトを送信
# プレイヤー1（左上）
tmux send-keys -t $SESSION_NAME:0.0 "あなたは人狼ゲームのプレイヤー1です。これからゲームを開始します。" Enter

# プレイヤー2（左下）
tmux send-keys -t $SESSION_NAME:0.1 "あなたは人狼ゲームのプレイヤー2です。これからゲームを開始します。" Enter

# プレイヤー3（右上）
tmux send-keys -t $SESSION_NAME:0.2 "あなたは人狼ゲームのプレイヤー3です。これからゲームを開始します。" Enter

# プレイヤー4（右下）
tmux send-keys -t $SESSION_NAME:0.3 "あなたは人狼ゲームのゲームマスターです。ゲームを進行してください。" Enter

echo ""
echo "✅ ゲームが開始されました！"
echo ""
echo "次のコマンドでゲームに参加できます:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "ゲームを終了するには:"
echo "  tmux kill-session -t $SESSION_NAME"
