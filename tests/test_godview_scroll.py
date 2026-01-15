#!/usr/bin/env python3
"""
Godview表示テストスクリプト
複数のチャットメッセージを送信して、最新が下に表示されるか確認します
"""

import asyncio
import websockets
import json


async def test_godview_display():
    """Godviewの表示をテスト"""
    uri = "ws://localhost:8765"

    print("🧪 Godview表示テスト")

    # プレイヤーを登録
    print("\n1. プレイヤーを登録...")
    ws = await websockets.connect(uri)
    register_msg = {
        "type": "register",
        "player_id": "test-player-scroll",
        "name": "テスト君",
        "role": "villager"
    }
    await ws.send(json.dumps(register_msg))
    print(f"📤 送信: {register_msg}")

    response = await ws.recv()
    data = json.loads(response)
    print(f"📥 応答: {data}")

    if data.get("type") == "system":
        print("✅ 登録成功！")
    else:
        print(f"❌ 登録失敗: {data}")
        return

    # 複数のチャットメッセージを送信（様々な長さ）
    print("\n2. 様々な長さのチャットメッセージを送信...")
    messages = []

    # 短いメッセージ（1-10）
    for i in range(1, 11):
        messages.append(f"{i}: 短い")

    # 中くらいのメッセージ（11-20）
    for i in range(11, 21):
        messages.append(f"{i}: これは中くらいの長さのメッセージです。少し長めにしています。")

    # 長いメッセージ（21-30）
    for i in range(21, 31):
        messages.append(f"{i}: これは長いメッセージです。人狼ゲームでは、論理的な思考と慎重な発言が重要です。"
                       f"特に投票の際には、これまでの発言内容を総合的に判断する必要があります。"
                       f"私の考えでは、まずは全員が自己紹介をして、その後で議論を進めるべきだと思います。")

    # とても長いメッセージ（31-40）
    for i in range(31, 41):
        messages.append(f"{i}: これはとても長いメッセージです。ターミナルの表示幅に合わせて、"
                       f"メッセージが適切に折り返されるかどうかを確認するために、"
                       f"わざと長い文章を作成しています。RichライブラリのPanelコンポーネントは、"
                       f"通常、テキストの折り返しを自動的に処理してくれますが、固定高さのPanelでは、"
                       f"テキストがはみ出す可能性があります。このメッセージが最後まで正しく表示されるか、"
                       f"それとも途中で切れてしまうのかを確認することで、Godviewの表示品質を検証できます。"
                       f"プレイヤー同士の会話がスムーズに表示されることは、ゲーム体験にとって非常に重要です。")

    for i, msg in enumerate(messages, 1):
        chat_msg = {
            "type": "chat",
            "channel": "public",
            "content": msg
        }
        await ws.send(json.dumps(chat_msg))
        print(f"📤 [{i}/22] 送信: {msg}")
        await asyncio.sleep(0.1)  # 少し待機

    print("\n✅ メッセージ送信完了！")
    print("\n📝 Godviewで確認してください：")
    print("   - 最新20件が表示されていること")
    print("   - 最新のメッセージ（22つ目）が一番下にあること")
    print("   - 1〜2つ目のメッセージは表示されていないこと")

    await ws.close()

    print("\n💡 Godviewを起動するには:")
    print("   uv run python -m server.godview")


if __name__ == "__main__":
    print("🧪 Godview表示テストを開始します...")
    print("=" * 50)
    asyncio.run(test_godview_display())
