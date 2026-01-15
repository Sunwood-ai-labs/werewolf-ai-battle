#!/usr/bin/env python3
"""
ゲーム開始スクリプト
神視点モードで接続し、ゲーム開始コマンドを送信
"""

import asyncio
import websockets
import json


async def start_game():
    """ゲームを開始"""
    uri = "ws://localhost:8765"

    try:
        async with websockets.connect(uri) as websocket:
            # 神視点モードで登録
            await websocket.send(json.dumps({"type": "godview"}))

            # 初期データを受信
            response = await websocket.recv()
            print(f"サーバー接続: {json.loads(response)['type']}")

            # ゲーム開始コマンドを送信
            await websocket.send(json.dumps({"command": "start_game"}))
            print("🎮 ゲーム開始コマンドを送信しました！")

    except Exception as e:
        print(f"エラー: {e}")


if __name__ == "__main__":
    asyncio.run(start_game())
