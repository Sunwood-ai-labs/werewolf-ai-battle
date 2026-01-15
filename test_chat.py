#!/usr/bin/env python3
"""
チャット接続のテストスクリプト
README.md に記載したサンプルコードが動くか確認します
"""

import asyncio
import websockets
import json

async def test_chat_connection():
    """チャットサーバーに接続してテストメッセージを送信"""
    uri = "ws://localhost:8765"

    print("🔗 チャットサーバーに接続中...")

    try:
        async with websockets.connect(uri) as websocket:
            print("✅ 接続成功！")

            # プレイヤー登録
            register_msg = {
                "type": "register",
                "name": "テストプレイヤー",
                "role": "villager"
            }
            await websocket.send(json.dumps(register_msg))
            print(f"📤 送信: {register_msg}")

            # メッセージ受信（登録確認）
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 受信: {response}")

            # チャットメッセージ送信
            chat_msg = {
                "type": "chat",
                "channel": "public",
                "content": "こんにちは、テストメッセージです！"
            }
            await websocket.send(json.dumps(chat_msg))
            print(f"📤 送信: {chat_msg}")

            # メッセージ受信（エコー確認）
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            print(f"📥 受信: {response}")

            print("\n✅ テスト成功！サンプルコードは正常に動作します。")

    except asyncio.TimeoutError:
        print("❌ タイムアウト: サーバーからの応答がありません")
    except Exception as e:
        print(f"❌ エラー: {e}")

if __name__ == "__main__":
    print("🧪 チャット接続テストを開始します...")
    print("=" * 50)
    asyncio.run(test_chat_connection())
