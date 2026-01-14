#!/bin/bash

# cc-werewolf ゲーム終了スクリプト
# tmuxセッションとチャットサーバーを停止します

SESSION_NAME="werewolf"

echo "🐺 cc-werewolf ゲームを終了します..."

# tmuxセッションを削除
tmux has-session -t $SESSION_NAME 2>/dev/null
if [ $? -eq 0 ]; then
    echo "tmuxセッションを削除中: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
    echo "✅ tmuxセッションを削除しました"
else
    echo "⚠️  tmuxセッションが見つかりません: $SESSION_NAME"
fi

# チャットサーバーのプロセスを停止
if pgrep -f "python.*server.server" > /dev/null; then
    echo "チャットサーバーを停止中..."
    pkill -f "python.*server.server"
    echo "✅ チャットサーバーを停止しました"
else
    echo "⚠️  チャットサーバーが動いていません"
fi

# 神視点CLIのプロセスを停止
if pgrep -f "python.*server.godview" > /dev/null; then
    echo "神視点CLIを停止中..."
    pkill -f "python.*server.godview"
    echo "✅ 神視点CLIを停止しました"
fi

echo ""
echo "✅ ゲームを終了しました"
echo ""
echo "確認:"
echo "  tmux list-sessions  - セッション一覧を確認"
echo "  ps aux | grep server  - プロセスを確認"
