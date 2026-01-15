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

# ccd-glm 実行用ディレクトリ（ローカル）
WEREWOLF_DIR="$PROJECT_DIR/werewolf"

# ccd-glm 実行用ディレクトリ（グローバル /werewolf）
GLOBAL_WEREWOLF_DIR="/werewolf"

# プレイヤーディレクトリがなければセットアップスクリプトを実行
if [ ! -d "$WEREWOLF_DIR/player1" ]; then
    echo "プレイヤーディレクトリを初期化中..."
    bash "$PROJECT_DIR/scripts/setup-players.sh"
fi

# /werewolf に werewolf ディレクトリをコピー
echo "グローバル /werewolf にファイルをコピー中..."
sudo mkdir -p "$GLOBAL_WEREWOLF_DIR"
sudo cp -r "$WEREWOLF_DIR"/* "$GLOBAL_WEREWOLF_DIR/"
sudo chown -R aslan:aslan "$GLOBAL_WEREWOLF_DIR"

# 各プレイヤーディレクトリに README.md をコピー
echo "各プレイヤーディレクトリに README.md をコピー中..."
for i in $(seq 1 $PLAYERS); do
    if [ -f "$PROJECT_DIR/werewolf/README.md" ]; then
        cp "$PROJECT_DIR/werewolf/README.md" "$GLOBAL_WEREWOLF_DIR/player$i/"
        echo "  player$i に README.md をコピーしました"
    fi
done

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

# 新しいセッションを作成
echo "tmuxセッションを作成中: $SESSION_NAME"
tmux new-session -d -s $SESSION_NAME -n "game"

# 2x3のグリッドレイアウトを作成
tmux split-window -v -t $SESSION_NAME:0.0  # pane 1
tmux split-window -h -t $SESSION_NAME:0.0  # pane 2
tmux split-window -h -t $SESSION_NAME:0.2  # pane 3

tmux split-window -v -t $SESSION_NAME:0.1  # pane 4
tmux split-window -h -t $SESSION_NAME:0.4  # pane 5

# tiledレイアウトで均等配置
tmux select-layout -t $SESSION_NAME:0 tiled

# 各プレイヤーペインにccd-glmを送信して実行
# paneとplayerのマッピング: 0->1, 2->2, 3->3, 1->4, 4->5, 5->6
tmux send-keys -t $SESSION_NAME:0.0 "cd '$GLOBAL_WEREWOLF_DIR/player1'" Enter
sleep 1
tmux send-keys -t $SESSION_NAME:0.0 "ccd-glm" Enter
sleep 5

tmux send-keys -t $SESSION_NAME:0.2 "cd '$GLOBAL_WEREWOLF_DIR/player2'" Enter
sleep 1
tmux send-keys -t $SESSION_NAME:0.2 "ccd-glm" Enter
sleep 5

tmux send-keys -t $SESSION_NAME:0.3 "cd '$GLOBAL_WEREWOLF_DIR/player3'" Enter
sleep 1
tmux send-keys -t $SESSION_NAME:0.3 "ccd-glm" Enter
sleep 5

tmux send-keys -t $SESSION_NAME:0.1 "cd '$GLOBAL_WEREWOLF_DIR/player4'" Enter
sleep 1
tmux send-keys -t $SESSION_NAME:0.1 "ccd-glm" Enter
sleep 5

tmux send-keys -t $SESSION_NAME:0.4 "cd '$GLOBAL_WEREWOLF_DIR/player5'" Enter
sleep 1
tmux send-keys -t $SESSION_NAME:0.4 "ccd-glm" Enter
sleep 5

tmux send-keys -t $SESSION_NAME:0.5 "cd '$GLOBAL_WEREWOLF_DIR/player6'" Enter
sleep 1
tmux send-keys -t $SESSION_NAME:0.5 "ccd-glm" Enter
sleep 5

# 各プレイヤーに役割を割り当て（Enterを押す）
# CLAUDE.md で設定された名前と口調は保持したまま、役職のみを伝える

# プレイヤー1（pane 0）- 村人1
tmux send-keys -t $SESSION_NAME:0.0 "【システム通知】あなたは人狼ゲームの「村人」です。まずREADME.mdのゲームルールを確認してください。その後、他のプレイヤーと協力して人狼を見つけ出してください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー2（pane 2）- 人狼1
tmux send-keys -t $SESSION_NAME:0.2 "【システム通知】あなたは人狼ゲームの「人狼」です。まずREADME.mdのゲームルールを確認してください。その後、村人のふりをして、誰も気づかないようにしてください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー3（pane 3）- 占い師
tmux send-keys -t $SESSION_NAME:0.3 "【システム通知】あなたは人狼ゲームの「占い師」です。まずREADME.mdのゲームルールを確認してください。その後、夜に誰か1人の正体を占います。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー4（pane 1）- 霊媒師
tmux send-keys -t $SESSION_NAME:0.1 "【システム通知】あなたは人狼ゲームの「霊媒師」です。まずREADME.mdのゲームルールを確認してください。その後、処刑された人の正体を確認できます。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー5（pane 4）- 人狼2
tmux send-keys -t $SESSION_NAME:0.4 "【システム通知】あなたは人狼ゲームの「人狼」です。まずREADME.mdのゲームルールを確認してください。その後、村人のふりをして、誰も気づかないようにしてください。まず自己紹介をしてください。" Enter
sleep 1

# プレイヤー6（pane 5）- GM
tmux send-keys -t $SESSION_NAME:0.5 "【システム通知】あなたは人狼ゲームの「ゲームマスター」です。まずREADME.mdのゲームルールを確認してください。その後、ゲームを進行してください。まずプレイヤー全員に挨拶をして、ゲームの説明をしてください。" Enter
sleep 1

echo ""
echo "✅ ゲームが開始されました！"
echo ""
echo "レイアウト（tmux）:"
echo "  +----------+----------+----------+"
echo "  | player1  | player2  | player3  |"
echo "  +----------+----------+----------+"
echo "  | player4  | player5  | player6  |"
echo "  +----------+----------+----------+"
echo ""
echo "🔍 神視点（別端末で起動）:"
echo "  cd $PROJECT_DIR"
echo "  uv run python -m server.godview"
echo ""
echo "次のコマンドでゲームに参加できます:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "ペイン移動: Ctrl+b → 矢印キー"
echo "ゲームを終了するには: tmux kill-session -t $SESSION_NAME"
echo ""
