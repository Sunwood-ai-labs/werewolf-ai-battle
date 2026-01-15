#!/usr/bin/env python3
"""
werewolf-ai-battle Chat Server

リアルタイムチャットサーバー。
複数のチャンネル（public, werewolf, moderator）をサポート。
"""

import asyncio
import websockets
import json
from datetime import datetime
from typing import Dict, Set, Optional
import uuid


class Player:
    """プレイヤー情報"""

    def __init__(self, player_id: str, name: str, role: str = "villager"):
        self.id = player_id
        self.name = name
        self.role = role
        self.websocket = None
        self.channels: Set[str] = set()
        self.is_alive = True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "is_alive": self.is_alive,
        }


class ChatChannel:
    """チャットチャンネル"""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.messages: list = []

    def add_message(self, message: dict):
        message["timestamp"] = datetime.now().isoformat()
        self.messages.append(message)
        # 最新100件だけ保持
        if len(self.messages) > 100:
            self.messages = self.messages[-100:]


class WerewolfServer:
    """人狼ゲームチャットサーバー"""

    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.players: Dict[str, Player] = {}
        self.channels: Dict[str, ChatChannel] = {
            "public": ChatChannel("public", "全員が見れるチャンネル"),
            "werewolf": ChatChannel("werewolf", "人狼だけのチャンネル"),
            "moderator": ChatChannel("moderator", "ゲームマスター用チャンネル"),
        }
        self.godview_clients: Set = set()

    async def register_player(
        self, websocket, player_id: str, name: str, role: str = "villager"
    ):
        """プレイヤーを登録"""

        # 名前の重複チェック（先にチェックする）
        for pid, p in self.players.items():
            if p.name == name:
                # 同じplayer_idで、同じ名前なら再接続として許可
                if pid == player_id:
                    # 既存の接続を閉じる
                    if p.websocket and p.websocket != websocket:
                        try:
                            await p.websocket.close()
                        except:
                            pass
                    print(f"⚠️  プレイヤー再接続: {name} (既存の接続を置き換え)")
                    break
                else:
                    # 異なるplayer_idで同じ名前ならエラー
                    await websocket.send(json.dumps({
                        "type": "error",
                        "message": f"プレイヤー名 '{name}' は既に使用されています"
                    }))
                    print(f"❌ 登録エラー: 名前 '{name}' は既に使用中 (player_id: {pid})")
                    return None

        player = Player(player_id, name, role)
        player.websocket = websocket

        # 役職に応じてチャンネルを設定
        player.channels.add("public")
        if role == "werewolf":
            player.channels.add("werewolf")
        if role == "moderator":
            player.channels.add("moderator")

        self.players[player_id] = player

        # システムメッセージを送信
        await self.send_to_player(
            player_id,
            {
                "type": "system",
                "message": f"ようこそ {name} さん！役職: {role}",
            },
        )

        # 全体通知
        await self.broadcast_godview(
            {"type": "player_joined", "player": player.to_dict()}
        )

        print(f"✅ プレイヤー登録: {name} ({role})")

        return player

    async def unregister_player(self, player_id: str):
        """プレイヤーを削除"""
        if player_id in self.players:
            player = self.players[player_id]
            await self.broadcast_godview(
                {"type": "player_left", "player": player.to_dict()}
            )
            del self.players[player_id]
            print(f"❌ プレイヤー退出: {player.name}")

    async def send_to_player(self, player_id: str, message: dict):
        """特定のプレイヤーにメッセージを送信"""
        if player_id in self.players:
            player = self.players[player_id]
            if player.websocket:
                try:
                    await player.websocket.send(json.dumps(message))
                except:
                    pass

    async def broadcast_to_channel(self, channel_name: str, message: dict):
        """チャンネル内の全プレイヤーにブロードキャスト"""
        channel = self.channels.get(channel_name)
        if not channel:
            return

        channel.add_message(message)

        for player in self.players.values():
            if channel_name in player.channels:
                await self.send_to_player(player.id, message)

        # 神視点にも送信
        await self.broadcast_godview(
            {
                "type": "channel_message",
                "channel": channel_name,
                "message": message,
            }
        )

    async def broadcast_godview(self, message: dict):
        """神視点クライアントにブロードキャスト"""
        if self.godview_clients:
            removed = set()
            for ws in self.godview_clients:
                try:
                    await ws.send(json.dumps(message))
                except:
                    removed.add(ws)
            self.godview_clients -= removed

    async def start_game(self):
        """ゲームを開始し、全プレイヤーに挨拶と説明を送信"""
        welcome_message = """
🐺 **人狼ゲームへようこそ！**

私はこのゲームのゲームマスターです。
皆さんが役職を持ち、村人チームと人狼チームに分かれて対戦します。

━━━━━━━━━━━━━━━━━━━━━━━━━━

【ゲームの概要】

村人チームの勝利条件：全ての人狼を処刑する
人狼チームの勝利条件：人狼の数が村人の数以上になる

【役職一覧】

・村人：特殊能力を持たない一般市民
・占い師：夜に1人の正体を占うことができる
・霊媒師：処刑された人の正体を確認できる
・狩人：夜に1人を護衛できる
・人狼：夜に1人を選んで襲撃できる
・狂人：人狼チームですが、村人のふりをする

【ゲームの流れ】

1. 準備フェーズ：各プレイヤーが役職を知る
2. 昼フェーズ：自由議論 → 投票で処刑者を決定
3. 夜フェーズ：各役職が特殊能力を使用
4. 勝利判定：勝利条件を満たしているか判定

━━━━━━━━━━━━━━━━━━━━━━━━━━

それでは、まずは自己紹介をお願いします。
自分の名前と、（役職がわかるなら）簡単な挨拶をしてください。
"""

        await self.broadcast_to_channel(
            "public",
            {
                "type": "system",
                "content": welcome_message.strip(),
                "phase": "introduction",
            },
        )

        print("🎮 ゲームを開始しました - 挨拶メッセージを送信しました")

    async def handle_message(self, player_id: str, message: dict, websocket=None):
        """プレイヤーからのメッセージを処理"""
        msg_type = message.get("type")

        if msg_type == "chat":
            # チャットメッセージ
            channel = message.get("channel", "public")
            content = message.get("content", "")
            sender_name = message.get("name")  # メッセージ内の名前を取得

            # player_id からプレイヤーを探す
            player = self.players.get(player_id)
            if not player:
                # player_id がない場合、name から探す
                if sender_name:
                    for p in self.players.values():
                        if p.name == sender_name:
                            player = p
                            break
                if not player:
                    return

            chat_message = {
                "type": "chat",
                "channel": channel,
                "player": player.name,
                "role": player.role,
                "content": content,
            }

            await self.broadcast_to_channel(channel, chat_message)

            # websocket があれば過去ログを返す
            if websocket:
                channel_obj = self.channels.get(channel)
                if channel_obj:
                    # 最新10件を返す
                    recent_messages = channel_obj.messages[-10:]
                    await websocket.send(json.dumps({
                        "type": "history",
                        "channel": channel,
                        "messages": recent_messages,
                    }))

        elif msg_type == "action":
            # ゲームアクション（投票、襲撃など）
            await self.broadcast_godview(
                {"type": "action", "player_id": player_id, "action": message}
            )

    async def handle_client(self, websocket):
        """クライアント接続を処理"""
        client_type = None
        player_id = None

        try:
            async for message in websocket:
                data = json.loads(message)

                # 接続タイプの判定
                client_type = data.get("type")

                if client_type == "register":
                    # プレイヤー登録
                    player_id = data.get("player_id", str(uuid.uuid4()))
                    name = data.get("name", "Anonymous")
                    role = data.get("role", "villager")

                    player = await self.register_player(
                        websocket, player_id, name, role
                    )

                    # 登録に失敗した場合（重複など）
                    if player is None:
                        return

                    # メインループ
                    async for msg in websocket:
                        try:
                            msg_data = json.loads(msg)
                            await self.handle_message(player.id, msg_data, websocket)
                        except:
                            pass

                elif client_type == "chat":
                    # チャットメッセージ（name からプレイヤーを探す）
                    sender_name = data.get("name")
                    if sender_name:
                        # 名前からプレイヤーを探す
                        player = None
                        for p in self.players.values():
                            if p.name == sender_name:
                                player = p
                                break

                        if player:
                            await self.handle_message(player.id, data, websocket)
                            # メッセージを送ったら接続を閉じる（websocat対応）
                            return
                        else:
                            await websocket.send(json.dumps({
                                "type": "error",
                                "message": f"プレイヤー '{sender_name}' が見つかりません"
                            }))
                            print(f"❌ チャットエラー: プレイヤー '{sender_name}' が見つかりません")
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "チャットメッセージには 'name' フィールドが必要です"
                        }))
                        print("❌ チャットエラー: name フィールドがない")

                elif client_type == "get_history":
                    # 過去ログ取得コマンド
                    channel = data.get("channel", "public")
                    count = data.get("count", 10)  # デフォルト10件

                    channel_obj = self.channels.get(channel)
                    if channel_obj:
                        messages = channel_obj.messages[-count:] if count > 0 else channel_obj.messages
                        await websocket.send(json.dumps({
                            "type": "history",
                            "channel": channel,
                            "messages": messages,
                        }))
                        print(f"📜 過去ログ送信: {channel} ({len(messages)}件)")
                    else:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"チャンネル '{channel}' が見つかりません"
                        }))
                    return

                elif client_type == "godview":
                    # パスワードチェック
                    password = data.get("password")
                    if password != "wolf":
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "パスワードが違います"
                        }))
                        print("❌ Godview接続エラー: パスワードが違います")
                        return

                    # 神視点クライアント
                    self.godview_clients.add(websocket)

                    # 初期データを送信
                    await websocket.send(
                        json.dumps(
                            {
                                "type": "init",
                                "players": [
                                    p.to_dict() for p in self.players.values()
                                ],
                                "channels": {
                                    name: {
                                        "name": ch.name,
                                        "description": ch.description,
                                        "messages": ch.messages,
                                    }
                                    for name, ch in self.channels.items()
                                },
                            }
                        )
                    )

                    # 神視点ループ
                    async for msg in websocket:
                        # 神視点からのメッセージを処理（コマンドなど）
                        try:
                            cmd_data = json.loads(msg)
                            cmd_type = cmd_data.get("command")

                            if cmd_type == "start_game":
                                # ゲーム開始
                                await self.start_game()

                        except:
                            pass

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # クリーンアップ
            if client_type == "godview":
                self.godview_clients.discard(websocket)
            # プレイヤーは削除しない（再接続できるように）

    async def start(self):
        """サーバーを起動"""
        print(f"🐺 Werewolf Chat Server starting on {self.host}:{self.port}")
        print(f"   Channels: {', '.join(self.channels.keys())}")

        async with websockets.serve(self.handle_client, self.host, self.port):
            print(f"✅ Server started!")
            await asyncio.Future()  # 永久に実行


async def main():
    """メイン関数"""
    server = WerewolfServer()
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
