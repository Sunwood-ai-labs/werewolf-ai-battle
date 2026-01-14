#!/bin/bash

# cc-werewolf セットアップスクリプト
# Claude Codeで人狼ゲームをプレイするための初期設定を行います

set -e

PROJECT_NAME="werewolf-ai-battle"
SESSION_NAME="werewolf"

echo "🐺 cc-werewolf セットアップ開始..."

# tmuxがインストールされているか確認
if ! command -v tmux &> /dev/null; then
    echo "❌ tmuxがインストールされていません"
    echo "インストールしてください: sudo apt-get install tmux"
    exit 1
fi

echo "✅ tmuxがインストールされています"

# Claude Codeの確認
if ! command -v claude &> /dev/null; then
    echo "⚠️  Claude Codeコマンドが見つかりません"
    echo "Claude Codeがインストールされているか確認してください"
fi

echo "✅ セットアップ完了！"
echo ""
echo "次のコマンドでゲームを開始できます:"
echo "  ./scripts/start-game.sh"
