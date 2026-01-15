#!/usr/bin/env python3
"""
切断・再接続テストスクリプト

新しい挙動：
- プレイヤーが切断されても、プレイヤー情報は保持される
- 再接続したら、既存のWebSocketを新しいもので置き換え
- 同じplayer_idとnameなら、同じ人として扱う
"""

import asyncio
import websockets
import json


async def test_disconnect_and_reconnect():
    """切断と再接続のテスト"""
    uri = "ws://localhost:8765"

    print("🧪 切断・再接続テスト")
    print("新しい挙動：切断されてもプレイヤー情報は保持される")

    # 1. プレイヤーを登録
    print("\n1. プレイヤーを登録...")
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
        print("✅ 登録成功！")
    else:
        print(f"❌ 登録失敗: {data}")
        return

    # 2. 接続を切断
    print("\n2. 接続を切断...")
    await ws1.close()
    print("✅ 切断完了")

    # 少し待つ
    await asyncio.sleep(1)

    # 3. 同じ名前で再登録（成功するはず）
    print("\n3. 同じ名前で再登録（成功するはず）...")
    ws2 = await websockets.connect(uri)
    register_msg = {
        "type": "register",
        "player_id": "test-player-1",  # 同じID
        "name": "アキラ",  # 同じ名前
        "role": "villager"
    }
    await ws2.send(json.dumps(register_msg))
    print(f"📤 送信: {register_msg}")

    response = await ws2.recv()
    data = json.loads(response)
    print(f"📥 応答: {data}")

    if data.get("type") == "system":
        print("✅ 再登録成功！（同じplayer_idとnameなので同じ人として扱われました）")
    elif data.get("type") == "error":
        print(f"❌ 再登録失敗: {data.get('message')}")

    await ws2.close()

    # 4. Godviewでプレイヤーが残っているか確認
    print("\n4. Godviewでプレイヤー情報を確認...")
    ws3 = await websockets.connect(uri)
    await ws3.send(json.dumps({"type": "godview"}))

    response = await ws3.recv()
    data = json.loads(response)

    if data.get("type") == "init":
        players = data.get("players", [])
        print(f"  プレイヤー数: {len(players)}")
        for p in players:
            print(f"    - {p.get('name')} ({p.get('role')}) [ID: {p.get('id')}]")

        # アキラが残っているか確認
        akira_found = any(p.get("name") == "アキラ" for p in players)
        if akira_found:
            print("✅ 切断後もプレイヤー情報が保持されています")
        else:
            print("❌ プレイヤー情報が消えてしまっています")

    await ws3.close()

    print("\n✅ テスト完了！")


if __name__ == "__main__":
    print("🧪 切断・再接続テストを開始します...")
    print("=" * 50)
    asyncio.run(test_disconnect_and_reconnect())
