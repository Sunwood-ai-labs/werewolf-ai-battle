#!/usr/bin/env python3
"""
Godview接続テストスクリプト
Godviewに接続して、チャットメッセージが表示されるか確認します
"""

import asyncio
import websockets
import json


async def test_godview():
    """Godviewに接続して初期データを確認"""
    uri = "ws://localhost:8765"

    print("🔗 Godviewに接続中...")

    try:
        async with websockets.connect(uri) as websocket:
            # 神視点として登録
            await websocket.send(json.dumps({"type": "godview"}))
            print("✅ 接続成功！")

            # 初期データを受信
            init_data = await websocket.recv()
            data = json.loads(init_data)

            print(f"\n📊 初期データ:")
            print(f"  タイプ: {data.get('type')}")

            # プレイヤー情報
            players = data.get("players", [])
            print(f"  プレイヤー数: {len(players)}")
            for p in players:
                print(f"    - {p.get('name')} ({p.get('role')})")

            # チャンネル情報
            channels = data.get("channels", {})
            print(f"\n  チャンネル数: {len(channels)}")
            for ch_name, ch_info in channels.items():
                messages = ch_info.get("messages", [])
                print(f"    [{ch_name}] {len(messages)} 件のメッセージ")
                for msg in messages[-3:]:  # 最新3件を表示
                    player = msg.get("player", "Unknown")
                    content = msg.get("content", "")
                    print(f"      - {player}: {content[:50]}...")

            # 少し待ってリアルタイムメッセージも確認
            print("\n⏱️  リアルタイムメッセージを待機中...")

            try:
                # 3秒間だけ待機
                for _ in range(3):
                    msg = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                    data = json.loads(msg)
                    msg_type = data.get("type")
                    print(f"📥 メッセージタイプ: {msg_type}")

                    if msg_type == "channel_message":
                        channel = data.get("channel")
                        msg_data = data.get("message", {})
                        player = msg_data.get("player", "Unknown")
                        content = msg_data.get("content", "")
                        print(f"   [{channel}] {player}: {content[:50]}...")

            except asyncio.TimeoutError:
                print("⏱️  待機終了")

            print("\n✅ テスト完了！")

    except ConnectionRefusedError:
        print("❌ 接続失敗。サーバーが起動しているか確認してください。")
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🧪 Godview接続テストを開始します...")
    print("=" * 50)
    asyncio.run(test_godview())
