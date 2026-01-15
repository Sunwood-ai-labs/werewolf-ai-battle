#!/usr/bin/env python3
"""
werewolf-ai-battle Chat Client

チャットサーバーに接続するクライアントライブラリ。
"""

import asyncio
import websockets
import json
from typing import Optional, Callable


class WerewolfClient:
    """人狼ゲームチャットクライアント"""

    def __init__(
        self,
        server_url: str = "ws://localhost:8765",
        name: str = "Anonymous",
        role: str = "villager",
    ):
        self.server_url = server_url
        self.name = name
        self.role = role
        self.player_id = None
        self.websocket = None
        self.on_message: Optional[Callable] = None

    async def connect(self):
        """サーバーに接続"""
        try:
            self.websocket = await websockets.connect(self.server_url)

            # プレイヤーとして登録
            register_msg = {
                "type": "register",
                "name": self.name,
                "role": self.role,
            }
            await self.websocket.send(json.dumps(register_msg))

            # メッセージ受信ループ
            async for message in self.websocket:
                if self.on_message:
                    await self.on_message(json.loads(message))

        except Exception as e:
            print(f"接続エラー: {e}")

    async def send_chat(self, content: str, channel: str = "public"):
        """チャットメッセージを送信"""
        if self.websocket:
            message = {
                "type": "chat",
                "channel": channel,
                "content": content,
            }
            await self.websocket.send(json.dumps(message))

    async def send_action(self, action: str, **kwargs):
        """ゲームアクションを送信"""
        if self.websocket:
            message = {
                "type": "action",
                "action": action,
                **kwargs,
            }
            await self.websocket.send(json.dumps(message))

    async def get_time_remaining(self) -> dict:
        """残り時間と現在のフェーズを取得"""
        if self.websocket:
            message = {
                "type": "get_time_remaining",
            }
            await self.websocket.send(json.dumps(message))

    async def get_history(self, channel: str = "public", count: int = 10) -> dict:
        """過去ログを取得"""
        if self.websocket:
            message = {
                "type": "get_history",
                "channel": channel,
                "count": count,
            }
            await self.websocket.send(json.dumps(message))

    async def close(self):
        """接続を閉じる"""
        if self.websocket:
            await self.websocket.close()


# 簡易テスト用の関数
async def test_chat(name: str, role: str):
    """テスト用チャットクライアント"""

    async def on_message(msg):
        msg_type = msg.get("type")
        if msg_type == "chat":
            print(f"[{name}] {msg.get('player')}: {msg.get('content')}")
        elif msg_type == "system":
            print(f"[{name}] システム: {msg.get('message')}")

    client = WerewolfClient(name=name, role=role)
    client.on_message = on_message

    # 接続タスク
    connect_task = asyncio.create_task(client.connect())

    # 少し待ってからメッセージを送信
    await asyncio.sleep(1)
    await client.send_chat(f"こんにちは、{name}です！")

    # 維持
    await connect_task


if __name__ == "__main__":
    # テスト実行
    print("テストクライアントを起動します...")
    asyncio.run(test_chat("TestPlayer", "villager"))
