#!/bin/bash

# cc-werewolf ゲーム開始スクリプト
# チャットサーバーを起動し、tmuxで複数のClaude Codeインスタンスを起動して人狼ゲームを開始します

set -e

SESSION_NAME="werewolf"
DEFAULT_PLAYERS=6

# プレイヤー数の設定
PLAYERS=${1:-$DEFAULT_PLAYERS}

echo "🐺 cc-werewolf ゲーム開始..."
echo "プレイヤー数: $PLAYERS"

# プロジェクトディレクトリを取得（現在のディレクトリを使用）
PROJECT_DIR="$(pwd)"

# ccd-glm 実行用ディレクトリ
WEREWOLF_DIR="$PROJECT_DIR/werewolf"

# プレイヤーディレクトリがなければセットアップスクリプトを実行
if [ ! -d "$WEREWOLF_DIR/player1" ]; then
    echo "プレイヤーディレクトリを初期化中..."
    bash "$PROJECT_DIR/scripts/setup-players.sh"
fi

# 既存のセッションがあれば削除
tmux has-session -t $SESSION_NAME 2>/dev/null || true
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
    echo "既存のセッションを削除します: $SESSION_NAME"
    tmux kill-session -t $SESSION_NAME
fi

# チャットサーバーのプロセスがあれば停止
sudo -u aslan pkill -f "python.*server.server" 2>/dev/null || true
sleep 1

# サーバーを裏で起動
echo "チャットサーバーを裏で起動中..."
cd "$PROJECT_DIR"
nohup uv run python -m server.server > /tmp/werewolf-server.log 2>&1 &
SERVER_PID=$!
echo "サーバーPID: $SERVER_PID"
echo "ログ: tail -f /tmp/werewolf-server.log"

# サーバーが起動するのを待つ
sleep 3

# 新しいセッションを作成（godviewペインから開始）
echo "tmuxセッションを作成中: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME -n "game"
tmux send-keys -t $SESSION_NAME:0 "cd '$PROJECT_DIR'" Enter
tmux send-keys -t $SESSION_NAME:0 "uv run python -m server.godview" Enter

# 縦に2分割して上下を作る
tmux split-window -v -t $SESSION_NAME:0  # pane 1

# 上の行（pane 0）を横に3分割
tmux split-window -h -t $SESSION_NAME:0.0  # pane 2
tmux split-window -h -t $SESSION_NAME:0.0  # pane 3

# 下の行（pane 1）を横に3分割
tmux split-window -h -t $SESSION_NAME:0.1  # pane 4
tmux split-window -h -t $SESSION_NAME:0.1  # pane 5

# 合計6ペイン: pane 0, 2, 3, 1, 4, 5
# まだgodviewとplayer1-5しかない

# tiledレイアウトで均等配置
tmux select-layout -t $SESSION_NAME:0 tiled

# さらに分割してplayer6用のスペースを作る
# どれかの大きなペインを分割
tmux split-window -v -t $SESSION_NAME:0.0

# 各プレイヤーペインにccd-glmを送信して実行
# godviewはpane 0（ccd-glmは実行しない）
# プレイヤーペインはpane 1, 2, 3, 4, 5, 6
for pane in 1 2 3 4 5 6; do
    tmux send-keys -t $SESSION_NAME:0.$pane "cd '$WEREWOLF_DIR/player$pane'" Enter
    sleep 1
    tmux send-keys -t $SESSION_NAME:0.$pane "ccd-glm" Enter
    sleep 5
done

# 各プレイヤーに役割を割り当て（Enterを押す）
# CLAUDE.md で設定された名前と口調は保持したまま、役職のみを伝える

# プレイヤー1（pane 1）- 村人1
tmux send-keys -t $SESSION_NAME:0.1 "【システム通知】あなたは人狼ゲームの「村人」です。他のプレイヤーと協力して人狼を見つけ出してください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー2（pane 2）- 人狼1
tmux send-keys -t $SESSION_NAME:0.2 "【システム通知】あなたは人狼ゲームの「人狼」です。村人のふりをして、誰も気づかないようにしてください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー3（pane 3）- 占い師
tmux send-keys -t $SESSION_NAME:0.3 "【システム通知】あなたは人狼ゲームの「占い師」です。夜に誰か1人の正体を占います。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー4（pane 4）- 霊媒師
tmux send-keys -t $SESSION_NAME:0.4 "【システム通知】あなたは人狼ゲームの「霊媒師」です。処刑された人の正体を確認できます。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー5（pane 5）- 人狼2
tmux send-keys -t $SESSION_NAME:0.5 "【システム通知】あなたは人狼ゲームの「人狼」です。村人のふりをして、誰も気づかないようにしてください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー6（pane 6）- GM
tmux send-keys -t $SESSION_NAME:0.6 "【システム通知】あなたは人狼ゲームの「ゲームマスター」です。ゲームを進行してください。まずプレイヤー全員に挨拶をして、ゲームの説明をしてください。" Enter
sleep 1

echo ""
echo "✅ ゲームが開始されました！"
echo ""
echo "レイアウト:"
echo "  +----------+----------+----------+"
echo "  | godview  | player1  | player2  |"
echo "  +----------+----------+----------+"
echo "  | player3  | player4  | player5  |"
echo "  +----------+----------+----------+"
echo "  | player6  |          |          |"
echo "  +----------+----------+----------+"
echo ""
echo "次のコマンドでゲームに参加できます:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "ペイン移動: Ctrl+b → 矢印キー"
echo "ゲームを終了するには: tmux kill-session -t $SESSION_NAME"
echo ""
