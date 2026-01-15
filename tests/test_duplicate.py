#!/usr/bin/env python3
"""
重複登録テストスクリプト
同じ名前での重複登録が拒否されるか確認します
"""

import asyncio
import websockets
import json


async def test_duplicate_registration():
    """重複登録のテスト"""
    uri = "ws://localhost:8765"

    print("🧪 重複登録テスト")

    # 1つ目のプレイヤーを登録
    print("\n1. 最初のプレイヤーを登録...")
    try:
        ws1 = await websockets.connect(uri)
        register_msg = {
            "type": "register",
            "player_id": "test-player-1",
            "name": "アキラ",
            "role": "villager"
        }
        await ws1.send(json.dumps(register_msg))
        print(f"📤 送信: {register_msg}")

        response = await ws1.recv()
        data = json.loads(response)
        print(f"📥 応答: {data}")

        if data.get("type") == "system":
            print("✅ 1人目の登録成功！")
        elif data.get("type") == "error":
            print(f"❌ エラー: {data.get('message')}")
            return

    except Exception as e:
        print(f"❌ エラー: {e}")
        return

    # 2つ目のプレイヤー（同じ名前）を登録しようとする
    print("\n2. 同じ名前で2人目のプレイヤーを登録（失敗するはず）...")
    try:
        ws2 = await websockets.connect(uri)
        register_msg = {
            "type": "register",
            "player_id": "test-player-2",  # 別のID
            "name": "アキラ",  # 同じ名前
            "role": "werewolf"
        }
        await ws2.send(json.dumps(register_msg))
        print(f"📤 送信: {register_msg}")

        response = await ws2.recv()
        data = json.loads(response)
        print(f"📥 応答: {data}")

        if data.get("type") == "error":
            print(f"✅ 重複登録が拒否されました: {data.get('message')}")
        else:
            print("❌ 重複登録が拒否されませんでした（バグです）")

        await ws2.close()

    except Exception as e:
        print(f"❌ エラー: {e}")
        return

    # 別の名前なら登録できるはず
    print("\n3. 別の名前でプレイヤーを登録（成功するはず）...")
    try:
        ws3 = await websockets.connect(uri)
        register_msg = {
            "type": "register",
            "player_id": "test-player-3",
            "name": "ハルト",  # 別の名前
            "role": "seer"
        }
        await ws3.send(json.dumps(register_msg))
        print(f"📤 送信: {register_msg}")

        response = await ws3.recv()
        data = json.loads(response)
        print(f"📥 応答: {data}")

        if data.get("type") == "system":
            print("✅ 別の名前で登録成功！")
        else:
            print("❌ 登録に失敗しました")

        await ws3.close()

    except Exception as e:
        print(f"❌ エラー: {e}")

    # 同じplayer_idで再接続
    print("\n4. 同じplayer_idで再接続（置き換えられるはず）...")
    try:
        ws4 = await websockets.connect(uri)
        register_msg = {
            "type": "register",
            "player_id": "test-player-1",  # 1人目と同じID
            "name": "アキラ",
            "role": "villager"
        }
        await ws4.send(json.dumps(register_msg))
        print(f"📤 送信: {register_msg}")

        response = await ws4.recv()
        data = json.loads(response)
        print(f"📥 応答: {data}")

        if data.get("type") == "system":
            print("✅ 再接続成功（既存の接続が置き換えられました）")
        else:
            print(f"❌ 再接続に失敗しました: {data}")

        await ws4.close()

    except Exception as e:
        print(f"❌ エラー: {e}")

    # クリーンアップ
    await ws1.close()

    print("\n✅ テスト完了！")


if __name__ == "__main__":
    print("🧪 重複登録テストを開始します...")
    print("=" * 50)
    asyncio.run(test_duplicate_registration())
