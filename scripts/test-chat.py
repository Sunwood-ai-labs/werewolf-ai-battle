#!/usr/bin/env python3
"""
チャットサーバーのテストスクリプト

複数のテストクライアントを作成し、チャット機能をテストします。
"""

import asyncio
import sys
import os

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from server.client import WerewolfClient


async def test_client(name: str, role: str, messages: list):
    """テストクライアント"""

    async def on_message(msg):
        msg_type = msg.get("type")
        if msg_type == "chat":
            print(f"[{name}] {msg.get('player')}: {msg.get('content')}")
        elif msg_type == "system":
            print(f"[{name}] システム: {msg.get('message')}")
        elif msg_type == "action":
            print(f"[{name}] アクション: {msg.get('action')}")

    client = WerewolfClient(name=name, role=role)
    client.on_message = on_message

    # 接続タスク
    connect_task = asyncio.create_task(client.connect())

    # 少し待ってからメッセージを送信
    await asyncio.sleep(1)

    for msg in messages:
        await client.send_chat(msg)
        await asyncio.sleep(0.5)

    # 維持
    try:
        await connect_task
    except asyncio.CancelledError:
        pass


async def main():
    """メイン関数"""
    print("🐺 チャットサーバー テスト")
    print("サーバーが起動していることを確認してください！")
    print()

    # 複数のクライアントを同時に実行
    tasks = [
        test_client("村人A", "villager", [
            "こんにちは！",
            "今日はいい天気ですね",
            "人狼は誰だと思いますか？",
        ]),
        test_client("村人B", "villager", [
            "はじめまして！",
            "私はみんなを信じてます",
            "でも怪しい人はいるかも...",
        ]),
        test_client("人狼X", "werewolf", [
            "はじめまして！",
            "私は村人を守ります！",
            "(内心: だませたな)",
        ],),
    ]

    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        print("\nテストを終了します")


if __name__ == "__main__":
    asyncio.run(main())
